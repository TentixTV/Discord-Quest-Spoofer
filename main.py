"""
DQS // Discord Quest Spoofer
Main Application Entry Point (Edge Chromium / WebView2 GPU Edition with Local Server)
"""

import sys
import os
import ctypes
import http.server
import functools
import threading

def is_admin():
    """Checks if the current process has administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def elevate_if_needed():
    """Forces the application to relaunch with full administrator rights if not elevated."""
    if not is_admin():
        try:
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
                params = ""
            else:
                exe_path = sys.executable
                params = f'"{os.path.abspath(__file__)}"'

            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", exe_path, params, None, 1
            )
            if ret > 32:
                sys.exit(0)
        except Exception:
            pass

def get_base_dir():
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            base = sys._MEIPASS
            if os.path.exists(os.path.join(base, "ui", "index.html")):
                return base
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

base_dir = get_base_dir()
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def start_local_server(directory):
    handler = functools.partial(QuietHTTPHandler, directory=directory)
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    port = server.server_address[1]
    srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
    srv_thread.start()
    return f"http://127.0.0.1:{port}"

import webview
import time
from src.bridge import DQSBridge

def set_app_user_model_id():
    """Explicitly sets AppUserModelID so Windows taskbar registers the custom DQS icon."""
    try:
        app_id = "TentixTV.DiscordQuestSpoofer.App.V5"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass

def attach_window_icon():
    """Forces Windows to apply the high-res DQS icon directly to the taskbar and window."""
    try:
        time.sleep(0.6)
        hwnd = ctypes.windll.user32.FindWindowW(None, "DQS // Discord Quest Spoofer")
        if hwnd:
            h_inst = ctypes.windll.kernel32.GetModuleHandleW(None)
            hicon = ctypes.windll.shell32.ExtractIconW(h_inst, sys.executable, 0)
            if hicon and hicon != 0:
                WM_SETICON = 0x0080
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 0, hicon)  # ICON_SMALL
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 1, hicon)  # ICON_BIG
    except Exception:
        pass

def main():
    set_app_user_model_id()
    elevate_if_needed()

    bridge = DQSBridge()
    server_base = start_local_server(base_dir)
    app_url = f"{server_base}/ui/index.html"

    window = webview.create_window(
        title="DQS // Discord Quest Spoofer",
        url=app_url,
        js_api=bridge,
        width=1260,
        height=820,
        min_size=(1100, 700),
        frameless=True,
        easy_drag=False,
        background_color="#08090d"
    )
    bridge.set_window(window)

    threading.Thread(target=attach_window_icon, daemon=True).start()
    webview.start(gui="edgechromium", debug=False)

if __name__ == "__main__":
    main()

