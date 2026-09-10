"""
Discord Auto Quest Completer
Main Application Entry Point (Admin Elevation & Multi-Engine Edition)
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
                # Running as compiled .exe
                exe_path = sys.executable
                params = ""
            else:
                # Running as python script
                exe_path = sys.executable
                params = f'"{os.path.abspath(__file__)}"'

            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", exe_path, params, None, 1
            )
            if ret > 32:
                sys.exit(0)
        except Exception:
            pass

# Ensure src folder is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.gui import AutoQuestApp

def main():
    elevate_if_needed()
    app = AutoQuestApp()
    app.mainloop()

if __name__ == "__main__":
    main()
