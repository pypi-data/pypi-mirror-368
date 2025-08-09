import subprocess
import tempfile
import os
import json
import logging
import re
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Annotated, Optional
from uuid import uuid4

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS, INTERNAL_ERROR
from pydantic import BaseModel, Field

from .image_compression import compress_image
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_DIR = Path.home() / ".screeny"
CONFIG_FILE = CONFIG_DIR / "approved_windows.json"

# Runtime storage for served screenshots
SHOTS_DIR = Path("/tmp/screeny")
META_DIR = SHOTS_DIR / "meta"

# Serving and cleanup configuration
COMPRESSION_THRESHOLD_BYTES = 5 * 1024 * 1024
TTL_SECONDS = 5 * 60
SWEEP_INTERVAL_SECONDS = 5 * 60
HTTP_HOST = os.environ.get("SCREENY_HTTP_HOST", "127.0.0.1")
HTTP_PORT = int(os.environ.get("SCREENY_HTTP_PORT", "4404"))

# Globals for background services
_http_app: Optional[object] = None
_http_thread: Optional[threading.Thread] = None
_sweeper_thread: Optional[threading.Thread] = None
_services_started = False

mcp = FastMCP(
    "Screeny",
    instructions="""Use this server to capture screenshots of specific application windows on macOS, providing visual context for development and debugging tasks.

WORKFLOW:
1. Call 'list_windows' once to discover available windows and their IDs
2. Use 'take_screenshot' with any valid window ID from the list_windows results. The tool returns a local URL to the screenshot.
3. Immediately issue an image_query for the returned URL in the same assistant turn so the runtime fetches and caches the image for vision and UI preview.

Note: Server requires the user to setup (Screen Recording permission and window approval) before use.
Screenshots are URL-served from localhost with a 5-minute TTL and auto-compressed to JPEG when larger than 5MB."""
)


class WindowInfo(BaseModel):
    """Information about a macOS window."""

    id: Annotated[str, Field(description="Unique window ID")]
    app: Annotated[str, Field(
        description="Application name that owns the window")]
    title: Annotated[str, Field(description="Window title")]
    approved: Annotated[bool, Field(
        default=False, description="Whether this window is approved for screenshots")]


class ScreenshotRequest(BaseModel):
    """Parameters for taking a screenshot of a window."""

    window_id: Annotated[str, Field(
        description="The window ID from listWindows to capture")]


class WindowSetupRequest(BaseModel):
    """Parameters for window setup operations."""

    approve_all: Annotated[bool, Field(
        default=False, description="Approve all windows without prompting")]


def ensure_config_dir():
    """Ensure the config directory exists"""
    CONFIG_DIR.mkdir(exist_ok=True)


def ensure_runtime_dirs():
    """Ensure runtime directories for serving screenshots exist"""
    SHOTS_DIR.mkdir(parents=True, exist_ok=True)
    META_DIR.mkdir(parents=True, exist_ok=True)


def _valid_shot_filename(filename: str) -> bool:
    """Validate allowed shot filenames to prevent path traversal"""
    return re.fullmatch(r"shot_[0-9a-fA-F\-]+\.(png|jpg)", filename) is not None


def _start_http_server_if_needed():
    """Start FastAPI HTTP server in background if not already running"""
    global _http_app, _http_thread, _services_started
    if _http_thread and _http_thread.is_alive():
        return

    if FastAPI is None or uvicorn is None:
        logger.error(
            "FastAPI/uvicorn are not installed. Install with: pip install fastapi uvicorn")
        return

    ensure_runtime_dirs()

    _http_app = FastAPI(title="Screeny HTTP Server")

    @_http_app.get("/shots/{fname}")
    def get_shot(fname: str):
        if not _valid_shot_filename(fname):
            raise HTTPException(status_code=404, detail="Not found")
        file_path = SHOTS_DIR / fname
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Not found")

        media_type = "image/png" if file_path.suffix.lower() == ".png" else "image/jpeg"
        return FileResponse(str(file_path), media_type=media_type)

    def _run_uvicorn():
        try:
            uvicorn.run(_http_app, host=HTTP_HOST,
                        port=HTTP_PORT, log_level="warning")
        except Exception as e:
            logger.error(f"Failed to start HTTP server: {e}")

    _http_thread = threading.Thread(
        target=_run_uvicorn, name="screeny-http", daemon=True)
    _http_thread.start()
    _services_started = True


def _start_sweeper_if_needed():
    """Start background sweeper to delete expired shots"""
    global _sweeper_thread
    if _sweeper_thread and _sweeper_thread.is_alive():
        return

    ensure_runtime_dirs()

    def _sweep_loop():  # pragma: no cover - background maintenance
        while True:
            try:
                now = datetime.now(timezone.utc)
                # Iterate over images
                for image_path in list(SHOTS_DIR.glob("shot_*.png")) + list(SHOTS_DIR.glob("shot_*.jpg")):
                    meta_path = META_DIR / (image_path.stem + ".json")
                    expired = False

                    if meta_path.exists():
                        try:
                            meta = json.loads(meta_path.read_text())
                            ts_str = meta.get("ts")
                            if ts_str:
                                ts = datetime.strptime(
                                    ts_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                                if now - ts > timedelta(seconds=TTL_SECONDS):
                                    expired = True
                        except Exception:
                            # If meta unreadable, delete both to be safe
                            expired = True
                    else:
                        # Orphaned image without meta
                        expired = True

                    if expired:
                        try:
                            image_path.unlink(missing_ok=True)
                        except Exception:
                            pass

                        try:
                            meta_path.unlink(missing_ok=True)
                        except Exception:
                            pass

                # Also remove orphan metas
                for meta_path in META_DIR.glob("shot_*.json"):
                    image_png = SHOTS_DIR / (meta_path.stem + ".png")
                    image_jpg = SHOTS_DIR / (meta_path.stem + ".jpg")
                    if not image_png.exists() and not image_jpg.exists():
                        try:
                            meta_path.unlink(missing_ok=True)
                        except Exception:
                            pass
            except Exception as e:
                logger.warning(f"Sweeper encountered an error: {e}")

            try:
                threading.Event().wait(SWEEP_INTERVAL_SECONDS)
            except Exception:
                pass

    _sweeper_thread = threading.Thread(
        target=_sweep_loop, name="screeny-sweeper", daemon=True)
    _sweeper_thread.start()


def load_approved_windows() -> Dict[str, Dict[str, Any]]:
    """Load approved windows from persistent storage"""
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            return data.get('approved_windows', {})
    except Exception as e:
        logger.warning(f"Failed to load config: {e}")
        return {}


def save_approved_windows(windows: Dict[str, Dict[str, Any]]):
    """Save approved windows to persistent storage"""
    ensure_config_dir()
    try:
        config = {
            'approved_windows': windows,
            'last_updated': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save config: {e}")


def _is_user_application_window(window: Dict[str, Any]) -> bool:
    """
    Check if a window represents a user application window worth capturing.
    """
    owner_name = window.get("kCGWindowOwnerName", "")
    window_name = window.get("kCGWindowName", "")
    window_number = window.get("kCGWindowNumber")
    window_layer = window.get("kCGWindowLayer", 0)

    return (
        owner_name and
        window_name and
        window_number and
        window_layer <= 2 and
        len(window_name.strip()) > 0 and
        window_name != "Desktop" and
        not owner_name.startswith("com.apple.") and
        owner_name not in ["WindowServer", "Dock", "Wallpaper",
                           "SystemUIServer", "Control Center"]
    )


def get_all_windows() -> List[WindowInfo]:
    """
    Get all available windows using macOS Quartz framework.
    Returns real window IDs that work with screencapture -l.
    """
    try:
        from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionAll, kCGNullWindowID
        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionAll, kCGNullWindowID)

        windows = []
        for window in window_list:
            if _is_user_application_window(window):
                windows.append(
                    WindowInfo(
                        id=str(window.get("kCGWindowNumber")),
                        app=window.get("kCGWindowOwnerName", ""),
                        title=window.get("kCGWindowName", ""),
                        approved=False
                    )
                )

        # If no windows found, it's likely a permission issue
        if len(windows) == 0:
            raise RuntimeError(
                "No windows found. Most likely cause: Screen Capture permission not granted to MCP host.\n"
                "Fix: System Settings → Privacy & Security → Screen & System Audio Recording → '+' → Add your MCP host → Restart MCP host"
            )

        return windows

    except ImportError as e:
        logger.error("❌ Quartz framework not available!")
        logger.error(
            "   pyobjc-framework-Quartz is required but failed to import.")
        logger.error("   Try: pip install pyobjc-framework-Quartz")
        raise RuntimeError(
            "Quartz framework required but not available") from e
    except Exception as e:
        logger.error(f"❌ Failed to enumerate windows: {e}")
        raise RuntimeError(f"Window enumeration failed: {e}") from e


def setup_windows_interactive() -> Dict[str, Dict[str, Any]]:
    """Interactive terminal-based window approval with user prompts"""
    print("\n🪟 Screeny Window Approval Setup")
    print("=" * 40)

    try:
        current_windows = get_all_windows()
    except RuntimeError as e:
        print(f"❌ Cannot enumerate windows: {e}")
        return {}

    if not current_windows:
        print("❌ No windows found. Make sure you have applications open.")
        return {}

    print(f"Found {len(current_windows)} open windows:")
    print()

    approved = {}
    for i, window in enumerate(current_windows, 1):
        print(f"{i:2d}. {window.app} - {window.title}")

        while True:
            choice = input(
                f"    Approve this window? [y/n/s(kip remaining)/a(ll)/q(uit)]: ").lower().strip()
            if choice in ['y', 'yes']:
                window_dict = window.model_dump()
                window_dict['approved'] = True
                approved[window.id] = window_dict
                print("    ✅ Approved")
                break
            elif choice in ['n', 'no']:
                print("    ❌ Skipped")
                break
            elif choice in ['s', 'skip']:
                print(
                    f"\n⏭️ Skipping remaining {len(current_windows) - i} windows...")
                print(
                    f"✅ Setup complete with {len(approved)} approved windows.")
                return approved
            elif choice in ['a', 'all']:
                print("    ✅ Approving all remaining windows...")
                for remaining_window in current_windows[i-1:]:
                    window_dict = remaining_window.model_dump()
                    window_dict['approved'] = True
                    approved[remaining_window.id] = window_dict
                print(f"    ✅ Approved {len(current_windows) - i + 1} windows")
                return approved
            elif choice in ['q', 'quit']:
                print("\n🛑 Setup cancelled")
                return approved
            else:
                print(
                    "    Please enter y (yes), n (no), s (skip remaining), a (approve all), or q (quit)")

    print(f"\n✅ Setup complete! Approved {len(approved)} windows.")
    return approved


def setup_windows_approve_all() -> Dict[str, Dict[str, Any]]:
    """Auto-approve all current windows without prompting"""
    try:
        current_windows = get_all_windows()
    except RuntimeError as e:
        print(f"❌ Cannot enumerate windows: {e}")
        return {}

    if not current_windows:
        print("❌ No windows found. Make sure you have applications open.")
        return {}

    approved = {}
    for window in current_windows:
        window_dict = window.model_dump()
        window_dict['approved'] = True
        approved[window.id] = window_dict

    print(f"✅ Auto-approved all {len(approved)} windows.")
    return approved


def take_screenshot_direct(window_id: str, tmp_path: str) -> subprocess.CompletedProcess:
    """
    Take screenshot using direct window capture (requires Screen Recording permission).
    """
    logger.info(f"Taking screenshot of window {window_id}")
    result = subprocess.run(
        ['screencapture', '-x', '-l', window_id, tmp_path],
        capture_output=True, text=True, timeout=10
    )
    return result


def setup_mode(allow_all: bool = False):
    """Interactive setup mode for window approval"""
    print("🚀 Screeny Setup Mode")
    print("This will help you approve windows for screenshot capture.")
    print()

    if allow_all:
        print("🔓 Auto-approving all windows...")
        approved = setup_windows_approve_all()
    else:
        print("🔒 Interactive approval mode...")
        print("💡 Tip: Use 'a' to approve all remaining, or 's' to skip remaining")
        print()
        approved = setup_windows_interactive()

    if approved:
        save_approved_windows(approved)
        print(f"\n💾 Configuration saved to: {CONFIG_FILE}")
        print("\n📋 Summary:")
        for window in approved.values():
            print(f"   - {window['app']}: {window['title']}")
        print("\n💡 Grant Screen Recording permission when prompted!")
    else:
        print("\n❌ No windows approved. Run setup again when ready.")
        print("💡 Tip: Use --allow-all flag to approve all windows automatically:")
        print("   mcp-server-screeny --setup --allow-all")


def debug_mode():
    """Debug mode to test window enumeration and permissions"""
    print("🔍 Screeny Debug Mode")
    print("=" * 30)

    print("\n1. Testing Quartz framework...")
    try:
        windows = get_all_windows()
        print(f"✅ Quartz: Found {len(windows)} windows with real IDs")

        print("\n2. Current windows:")
        for w in windows[:10]:
            print(f"   - [{w.id}] {w.app}: {w.title}")
        if len(windows) > 10:
            print(f"   ... and {len(windows) - 10} more")

    except RuntimeError as e:
        print(f"❌ Quartz: {e}")
        return

    print("\n3. Recommendations:")
    print("   ✅ Quartz working optimally!")
    print("   💡 Grant Screen Recording permission when taking screenshots for best UX")


def get_current_approved_windows() -> Dict[str, Dict[str, Any]]:
    """Load approved windows from disk and validate they're still open"""
    approved = load_approved_windows()
    if not approved:
        return {}

    current_windows = get_all_windows()
    current_window_map = {w.id: w for w in current_windows}

    still_open_approved = {}

    for window_id, window_info in approved.items():
        if window_info.get('approved') and window_id in current_window_map:
            current_window = current_window_map[window_id]

            old_title = window_info['title']
            new_title = current_window.title

            if old_title != new_title:
                logger.info(
                    f"Updated title for window {window_id}: '{old_title}' -> '{new_title}'")
                window_info['title'] = new_title

            still_open_approved[window_id] = window_info

    save_approved_windows(still_open_approved)
    if len(still_open_approved) < len(approved):
        removed_count = len(approved) - len(still_open_approved)
        logger.info(
            f"Removed {removed_count} closed windows from approved list")

    return still_open_approved


@mcp.tool(
    annotations={
        "title": "List Approved Windows",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
def list_windows() -> list[TextContent]:
    """
    List all currently approved windows available for screenshot capture.

    Call this once per session to discover available window IDs for use with 'take_screenshot'.
    Re-call if encountering screenshot errors (window closed, new apps opened, etc.).

    Args: None

    Returns: JSON with:
    - approved_windows: Array of window objects (id, app, title, approved status)
    - total_approved: Count of approved windows  
    - message: Next steps guidance
    """
    try:
        approved_windows = get_current_approved_windows()
    except RuntimeError as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Unexpected error listing approved windows: {str(e)}"
        ))

    if not approved_windows:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message='No approved windows found. Run setup: "mcp-server-screeny --setup" or "uvx mcp-server-screeny --setup"'
        ))

    result_data = {
        'approved_windows': list(approved_windows.values()),
        'total_approved': len(approved_windows),
        'message': 'Use takeScreenshot with a window ID to capture.'
    }

    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]


@mcp.tool(
    annotations={
        "title": "Take Window Screenshot",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
def take_screenshot(request: ScreenshotRequest) -> list[ImageContent | TextContent]:
    """
    Take a screenshot of a specific window by its ID using direct capture.

    Flow:
    - Captures PNG to /tmp/screeny as shot_<uuid>.png
    - If file > 5MB, recompresses to JPEG and serves as .jpg
    - Writes sidecar meta JSON with UTC timestamp for TTL sweeper
    - Returns ImageContent with a local URL for clients to fetch

    Requires calling 'list_windows' once per session to obtain valid window IDs.
    If screenshot fails, re-call 'list_windows' to refresh available windows.
    After receiving the URL, immediately issue an image_query for that URL in the same assistant turn
    so the runtime fetches the image. 

    Args:
    - window_id (str): Exact window ID string from list_windows results

    Returns:
    - TextContent: JSON containing { url, mimeType, window info, timestamp }

    Note: Can capture windows in background but not minimized windows.
    """
    window_id = request.window_id

    if not window_id or not isinstance(window_id, str):
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="window_id must be a non-empty string"
        ))

    try:
        approved_windows = get_current_approved_windows()
    except RuntimeError as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=str(e)
        ))

    if not approved_windows:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message='No approved windows found. Run setup: "mcp-server-screeny --setup" or "uvx mcp-server-screeny --setup"'
        ))

    if window_id not in approved_windows:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message=f"Window ID '{window_id}' not found in currently open approved windows. Run listWindows to see available windows, or run setup to approve new windows."
        ))

    window_info = approved_windows[window_id]

    # Ensure background services are running
    _start_http_server_if_needed()
    _start_sweeper_if_needed()

    ensure_runtime_dirs()

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        result = take_screenshot_direct(window_id, tmp_path)

        if result.returncode != 0:
            if "not permitted" in result.stderr.lower() or "not authorized" in result.stderr.lower():
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Screen Capture permission required. Grant permission in System Settings → Privacy & Security → Screen & System Audio Recording"
                ))
            elif "can't create" in result.stderr.lower() or "doesn't exist" in result.stderr.lower():
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Cannot capture '{window_info['title']}' - window appears minimized or closed. Restore window from dock and try again."
                ))
            else:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Screenshot failed for '{window_info['title']}': {result.stderr}"
                ))

        tmp_file_path = Path(tmp_path)
        if not tmp_file_path.exists() or tmp_file_path.stat().st_size == 0:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Screenshot file empty or missing for '{window_info['title']}'"
            ))

        # Persist to /tmp/screeny as shot_<uuid>.(png|jpg)
        shot_id = f"shot_{uuid4()}"
        dest_png = SHOTS_DIR / f"{shot_id}.png"
        dest_jpg = SHOTS_DIR / f"{shot_id}.jpg"

        # Move temp PNG to destination
        dest_png.write_bytes(tmp_file_path.read_bytes())

        # Optional compression if > 5MB
        final_path = dest_png
        final_mime = "image/png"
        try:
            if dest_png.stat().st_size > COMPRESSION_THRESHOLD_BYTES:
                jpeg_bytes, _fmt = compress_image(
                    str(dest_png), COMPRESSION_THRESHOLD_BYTES)
                dest_jpg.write_bytes(jpeg_bytes)
                try:
                    dest_png.unlink(missing_ok=True)
                except Exception:
                    pass
                final_path = dest_jpg
                final_mime = "image/jpeg"
        except Exception as e:
            logger.warning(f"Compression attempt failed, serving PNG: {e}")

        # Write sidecar metadata with creation timestamp
        meta = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "window_id": window_id,
            "app": window_info['app'],
            "title": window_info['title']
        }
        meta_path = META_DIR / f"{shot_id}.json"
        try:
            meta_path.write_text(json.dumps(meta))
        except Exception as e:
            logger.warning(f"Failed to write meta file {meta_path}: {e}")

        # Return a URL for clients to fetch
        url = f"http://{HTTP_HOST}:{HTTP_PORT}/shots/{final_path.name}"

        metadata_text = json.dumps({
            "window_id": window_id,
            "app": window_info['app'],
            "title": window_info['title'],
            "url": url,
            "timestamp": meta["ts"]
        }, indent=2)

        payload = {
            "url": url,
            "mimeType": final_mime,
            "window_id": window_id,
            "app": window_info['app'],
            "title": window_info['title'],
            "timestamp": meta["ts"]
        }

        return [TextContent(type="text", text=json.dumps(payload))]

    except subprocess.TimeoutExpired:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Screenshot timed out for '{window_info['title']}'"
        ))
    except Exception as e:
        logger.error(f"Unexpected error taking screenshot: {e}")
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Unexpected error taking screenshot: {str(e)}"
        ))
    finally:
        try:
            if Path(tmp_path).exists():
                os.unlink(tmp_path)
        except Exception as e:
            logger.warning(f"Failed to clean up temp file {tmp_path}: {e}")


@mcp.resource("screeny://info")
def get_server_info() -> str:
    """Get information about the Screeny MCP server"""
    return json.dumps({
        "name": "Screeny MCP Server",
        "version": "0.2.1",
        "description": "Capture screenshots of specific application windows, providing visual context for development and debugging tasks",
        "capabilities": [
            "List application windows on macOS",
            "Capture screenshots of specific application windows",
            "Serve screenshots via local HTTP URL with 5-minute TTL",
            "Provide window metadata for analysis"
        ],
        "requirements": [
            "macOS only",
            "pyobjc-framework-Quartz",
            "Screen Recording permission",
            "fastapi",
            "uvicorn"
        ],
        "image_delivery": "url",
        "http": {"host": HTTP_HOST, "port": HTTP_PORT, "route": "/shots/{fname}"},
        "ttlSeconds": TTL_SECONDS,
        "compressionThresholdBytes": COMPRESSION_THRESHOLD_BYTES,
        "tools": ["listWindows", "takeScreenshot"],
        "resources": ["screeny://info"],
        "config_file": str(CONFIG_FILE)
    }, indent=2)


def serve() -> None:
    """Run the Screeny MCP server."""
    logger.info("Starting Screeny MCP Server...")
    _start_http_server_if_needed()
    _start_sweeper_if_needed()
    mcp.run()
