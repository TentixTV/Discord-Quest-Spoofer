"""
DQS // Discord Quest Spoofer
Main Application Entry Point (Edge Chromium / WebView2 GPU Edition)
"""

import sys
import os
import ctypes

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

import webview
from src.bridge import DQSBridge

def main():
    elevate_if_needed()

    bridge = DQSBridge()
    html_file = os.path.abspath(os.path.join(base_dir, "ui", "index.html"))

    if not os.path.exists(html_file):
        raise FileNotFoundError(f"UI HTML not found at: {html_file}")

    window = webview.create_window(
        title="DQS // Discord Quest Spoofer",
        url=html_file,
        js_api=bridge,
        width=1160,
        height=760,
        min_size=(980, 640),
        frameless=True,
        easy_drag=False,
        background_color="#08090d"
    )
    bridge.set_window(window)

    webview.start(gui="edgechromium", debug=False)

if __name__ == "__main__":
    main()
