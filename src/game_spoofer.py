"""
Game Process Spoofer & Simulator
Spawns lightweight dummy processes with real game executable names and window titles,
combined with Discord RPC Rich Presence to make Discord Desktop identify games as running.
"""

import os
import sys
import shutil
import tempfile
import subprocess
import threading
import time
from typing import Optional
from .discord_rpc import DiscordIPCClient
from .database import resolve_game_info

class GameSimulator:
    def __init__(self):
        self.current_process: Optional[subprocess.Popen] = None
        self.rpc_client: Optional[DiscordIPCClient] = None
        self.current_game_name: str = ""
        self.current_exe_name: str = ""
        self.current_app_id: str = ""
        self.start_time: float = 0.0
        self.sim_dir = os.path.join(tempfile.gettempdir(), "DiscordAutoQuest_Sim")
        os.makedirs(self.sim_dir, exist_ok=True)
        self._lock = threading.Lock()

    def _get_runner_executable(self) -> str:
        """Locates the base dummy runner executable or compiles/creates it."""
        # Check bundled dist
        candidates = [
            os.path.join(os.path.dirname(__file__), "..", "bin", "dummy_runner.exe"),
            os.path.join(os.path.dirname(__file__), "dummy_runner.exe"),
            os.path.join(os.getcwd(), "dummy_runner.exe"),
            os.path.join(self.sim_dir, "base_runner.exe")
        ]
        for c in candidates:
            if os.path.exists(c):
                return c

        # Fallback: create a python script launcher if python is available
        base_exe = os.path.join(self.sim_dir, "base_runner.exe")
        if os.path.exists(base_exe):
            return base_exe
        
        # If sys.executable exists, we can use it as fallback
        return sys.executable

    def start_simulation(self, app_id: str, game_title: str = "", custom_exe: str = "") -> dict:
        """Starts simulating a game using both process spoofer and Discord RPC."""
        with self._lock:
            if self.is_running():
                self.stop_simulation()

            info = resolve_game_info(app_id, game_title)
            exe_name = custom_exe if custom_exe else info.get("exe", "Game.exe")
            title = info.get("title", game_title or "Game Simulation")

            # Isolate per app to prevent locked file collision
            game_folder = os.path.join(self.sim_dir, f"app_{app_id}")
            os.makedirs(game_folder, exist_ok=True)
            target_exe_path = os.path.join(game_folder, os.path.normpath(exe_name))
            os.makedirs(os.path.dirname(target_exe_path), exist_ok=True)
            base_runner = self._get_runner_executable()

            try:
                if base_runner.lower().endswith(".exe") and base_runner != sys.executable:
                    if not os.path.exists(target_exe_path):
                        shutil.copyfile(base_runner, target_exe_path)
                    cmd = [target_exe_path, "--title", title]
                else:
                    # Fallback python command
                    py_script = os.path.join(game_folder, "run_dummy.py")
                    with open(py_script, "w", encoding="utf-8") as f:
                        f.write(f'''import time, ctypes
try:
    ctypes.windll.kernel32.SetConsoleTitleW("{title}")
except Exception:
    pass
while True:
    time.sleep(1)
''')
                    if not os.path.exists(target_exe_path):
                        shutil.copyfile(sys.executable, target_exe_path)
                    cmd = [target_exe_path, py_script]

                startupinfo = None
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = 6 # SW_MINIMIZE

                self.current_process = subprocess.Popen(
                    cmd,
                    startupinfo=startupinfo
                )
            except Exception:
                # If process launch fails, continue with RPC alone
                self.current_process = None

            # Start Discord RPC
            pid = self.current_process.pid if self.current_process else None
            self.rpc_client = DiscordIPCClient(app_id)
            rpc_connected = self.rpc_client.connect()
            if rpc_connected:
                state_str = "In Mission" if "helldivers" in title.lower() else "Im Spiel"
                self.rpc_client.set_activity(
                    details=title,
                    state=state_str,
                    start_time=int(time.time()),
                    pid=pid
                )

            self.current_game_name = title
            self.current_exe_name = exe_name
            self.current_app_id = app_id
            self.start_time = time.time()

            return {
                "success": True,
                "game_name": title,
                "exe_name": exe_name,
                "pid": pid,
                "rpc_connected": rpc_connected
            }

    def stop_simulation(self):
        """Stops the active game simulation and cleans up resources."""
        with self._lock:
            if self.rpc_client:
                try:
                    self.rpc_client.close()
                except Exception:
                    pass
                self.rpc_client = None

            if self.current_process:
                try:
                    self.current_process.terminate()
                    self.current_process.wait(timeout=2)
                except Exception:
                    try:
                        self.current_process.kill()
                    except Exception:
                        pass
                self.current_process = None

            self.current_game_name = ""
            self.current_exe_name = ""
            self.current_app_id = ""
            self.start_time = 0.0

    def is_running(self) -> bool:
        if self.current_process:
            if self.current_process.poll() is None:
                return True
            self.current_process = None
        if self.rpc_client and self.rpc_client.connected:
            return True
        return False

    def get_elapsed_seconds(self) -> int:
        if self.is_running() and self.start_time > 0:
            return int(time.time() - self.start_time)
        return 0
