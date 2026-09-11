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

def get_screen_center_coordinates(width, height):
    """Calculates x, y coordinates to center the window on the primary display."""
    try:
        user32 = ctypes.windll.user32
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass
        screen_w = user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_h = user32.GetSystemMetrics(1)  # SM_CYSCREEN
        if screen_w > 0 and screen_h > 0:
            x = max(0, (screen_w - width) // 2)
            y = max(0, (screen_h - height) // 2)
            return x, y
    except Exception:
        pass
    return None, None

def center_and_attach_window_icon(win_w, win_h):
    """Forces Windows to center the frameless window and apply high-res DQS icon."""
    try:
        time.sleep(0.5)
        hwnd = ctypes.windll.user32.FindWindowW(None, "DQS // Discord Quest Spoofer")
        if hwnd:
            pos_x, pos_y = get_screen_center_coordinates(win_w, win_h)
            if pos_x is not None and pos_y is not None:
                # SWP_NOZORDER = 0x0004, SWP_SHOWWINDOW = 0x0040
                ctypes.windll.user32.SetWindowPos(hwnd, 0, pos_x, pos_y, win_w, win_h, 0x0044)

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

    win_w = 1260
    win_h = 820
    pos_x, pos_y = get_screen_center_coordinates(win_w, win_h)

    kwargs = {
        "title": "DQS // Discord Quest Spoofer",
        "url": app_url,
        "js_api": bridge,
        "width": win_w,
        "height": win_h,
        "min_size": (1100, 700),
        "frameless": True,
        "easy_drag": False,
        "background_color": "#08090d"
    }
    if pos_x is not None and pos_y is not None:
        kwargs["x"] = pos_x
        kwargs["y"] = pos_y

    window = webview.create_window(**kwargs)
    bridge.set_window(window)

    threading.Thread(target=center_and_attach_window_icon, args=(win_w, win_h), daemon=True).start()
    webview.start(gui="edgechromium", debug=False)

if __name__ == "__main__":
    main()

