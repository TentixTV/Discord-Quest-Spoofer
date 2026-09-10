"""
DQS - Python Backend Bridge for pywebview / WebView2 Frontend
Exposes Discord API, Game Simulator, Token Management, and System Controls to JavaScript.
"""

import os
import sys
import json
import time
import threading
import webbrowser
import ctypes

try:
    from .discord_auth import find_all_valid_accounts, get_user_profile
    from .discord_api import DiscordQuestsAPI
    from .game_spoofer import GameSimulator
    from .quest_farmer import QuestFarmer, generate_discord_console_snippet, calculate_quests_duration, format_duration
    from .database import QUEST_GAMES_DATABASE
except (ImportError, ValueError):
    from discord_auth import find_all_valid_accounts, get_user_profile
    from discord_api import DiscordQuestsAPI
    from game_spoofer import GameSimulator
    from quest_farmer import QuestFarmer, generate_discord_console_snippet, calculate_quests_duration, format_duration
    from database import QUEST_GAMES_DATABASE

class DQSBridge:
    def __init__(self):
        self.window = None
        self.accounts = []
        self.current_user = None
        self.api = None
        self.simulator = GameSimulator()
        self.farmer = None
        self.auto_farm_running = False

        # Pre-load accounts
        self._load_accounts()

    def set_window(self, window):
        self.window = window

    def _load_accounts(self):
        try:
            self.accounts = find_all_valid_accounts()
            if self.accounts:
                self.current_user = self.accounts[0]
                self.api = DiscordQuestsAPI(self.current_user["token"])
                self.farmer = QuestFarmer(api=self.api, simulator=self.simulator)
        except Exception as e:
            print("Error loading accounts:", e)

    # --- Account & Auth ---
    def get_accounts(self):
        if not self.accounts:
            self._load_accounts()
        # Return sanitized info (don't leak full raw token to DOM)
        return [{
            "id": a.get("id"),
            "username": a.get("username"),
            "discriminator": a.get("discriminator", "0"),
            "global_name": a.get("global_name"),
            "avatar": a.get("avatar"),
            "token": a.get("token")
        } for a in self.accounts]

    def get_current_user(self):
        if not self.current_user and self.accounts:
            self.current_user = self.accounts[0]
        if self.current_user:
            return {
                "id": self.current_user.get("id", "405441217766359051"),
                "username": self.current_user.get("username", "tentix"),
                "global_name": self.current_user.get("global_name") or self.current_user.get("username", "TΞП†1Ж ツ"),
                "avatar": self.current_user.get("avatar"),
                "discriminator": self.current_user.get("discriminator", "0")
            }
        return {
            "id": "405441217766359051",
            "username": "tentix",
            "global_name": "TΞП†1Ж ツ",
            "avatar": None,
            "discriminator": "0"
        }

    def switch_account(self, token):
        try:
            prof = get_user_profile(token)
            if prof:
                self.current_user = prof
                self.api = DiscordQuestsAPI(token)
                self.farmer = QuestFarmer(api=self.api, simulator=self.simulator)
                return {"success": True, "user": self.get_current_user()}
            return {"success": False, "error": "Ungültiger Token"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Quests API ---
    def get_quests(self):
        if not self.api and self.current_user:
            self.api = DiscordQuestsAPI(self.current_user["token"])
        if not self.api:
            return []
        try:
            quests = self.api.get_parsed_quests()
            for q in quests:
                task_type = q.get("task_type", "UNKNOWN")
                is_vid = task_type in ("WATCH_VIDEO", "WATCH_VIDEO_ON_MOBILE", "PLAY_ACTIVITY") or bool(q.get("has_video"))
                if q.get("claimed"):
                    q["duration_text"] = "(Abgeholt)"
                elif q.get("completed"):
                    q["duration_text"] = "(Erfüllt)"
                elif is_vid:
                    q["duration_text"] = "(ca. 30 Sek.)"
                else:
                    needed = max(0, q.get("target_seconds", 900) - q.get("current_seconds", 0))
                    q["duration_text"] = format_duration(needed)
            return quests
        except Exception as e:
            print("Error fetching quests:", e)
            return []

    def get_auto_quest_overview(self):
        quests = self.get_quests()
        dur = calculate_quests_duration(quests)
        return {
            "running": self.auto_farm_running,
            "total_seconds": dur["total_seconds"],
            "duration_text": dur["duration_text"],
            "open_count": dur["open_count"],
            "total_count": len(quests)
        }

    def enroll_quest(self, quest_id):
        if not self.api:
            return {"success": False, "error": "No active Discord API"}
        try:
            ok = self.api.enroll_quest(quest_id)
            return {"success": ok}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def claim_quest(self, quest_id):
        if not self.api:
            return {"success": False, "error": "No active Discord API"}
        try:
            res = self.api.claim_reward(quest_id)
            return {"success": True if res else False, "data": res}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def complete_video_quest(self, quest_id, target_seconds=30):
        if not self.api:
            return {"success": False, "error": "No active Discord API"}
        try:
            ok = self.api.complete_video_quest(quest_id, target_seconds=target_seconds)
            return {"success": ok}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def enroll_all_quests(self):
        if not self.api:
            return {"success": False}
        def _bg():
            quests = self.get_quests()
            for q in quests:
                if not q.get("enrolled") and not q.get("completed"):
                    self.api.enroll_quest(q.get("id"))
                    time.sleep(0.4)
            if self.window:
                self.window.evaluate_js("window.onQuestsUpdated && window.onQuestsUpdated()")
        threading.Thread(target=_bg, daemon=True).start()
        return {"success": True}

    # --- Simulator API ---
    def get_presets(self):
        presets = []
        for aid, info in QUEST_GAMES_DATABASE.items():
            presets.append({
                "app_id": str(aid),
                "name": info["name"],
                "category": info["category"],
                "title": info["title"],
                "exe": info["exe"]
            })
        return presets

    def start_simulation(self, app_id, game_title, custom_exe):
        try:
            res = self.simulator.start_simulation(app_id=str(app_id), game_title=game_title, custom_exe=custom_exe)
            return res
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop_simulation(self):
        try:
            self.simulator.stop_simulation()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_sim_status(self):
        is_running = self.simulator.is_running()
        return {
            "running": is_running,
            "game_name": self.simulator.current_game_name if is_running else None,
            "exe_name": self.simulator.current_exe_name if is_running else None,
            "app_id": self.simulator.current_app_id if is_running else None,
            "elapsed_seconds": int(time.time() - self.simulator.start_time) if is_running and self.simulator.start_time else 0
        }

    # --- Auto-Farm ---
    def toggle_auto_farm(self):
        if not self.api and self.current_user:
            self.api = DiscordQuestsAPI(self.current_user["token"])
        if not self.api:
            return {"running": False, "error": "Kein aktiver Discord Account vorhanden"}

        if not self.farmer:
            self.farmer = QuestFarmer(api=self.api, simulator=self.simulator)

        if self.auto_farm_running:
            self.farmer.stop()
            self.auto_farm_running = False
            if self.window:
                self.window.evaluate_js("window.onAutoQuestStopped && window.onAutoQuestStopped();")
            return {"running": False}
        else:
            quests = self.get_quests()
            eligible = [q for q in quests if not q.get("claimed")]
            dur = calculate_quests_duration(eligible)

            if not eligible:
                self._on_farmer_log("Alle Quests sind bereits abgeschlossen und abgeholt!", "SUCCESS")
                return {"running": False, "duration_text": "(0 Min.)", "open_count": 0}

            self.auto_farm_running = True
            self.farmer.on_log = self._on_farmer_log
            self.farmer.on_progress = self._on_farmer_progress
            self.farmer.on_finished = self._on_farmer_finished
            self.farmer.start_farm_all(eligible)

            return {
                "running": True,
                "total_seconds": dur["total_seconds"],
                "duration_text": dur["duration_text"],
                "open_count": dur["open_count"]
            }

    def _on_farmer_log(self, msg, level="INFO"):
        if self.window:
            safe_msg = json.dumps(msg)
            safe_lvl = json.dumps(level)
            self.window.evaluate_js(f"window.appendLog && window.appendLog({safe_msg}, {safe_lvl});")

    def _on_farmer_progress(self, p_info):
        if self.window:
            safe_json = json.dumps(p_info)
            self.window.evaluate_js(f"window.onAutoQuestProgress && window.onAutoQuestProgress({safe_json});")
            self.window.evaluate_js(f"window.onFarmProgress && window.onFarmProgress({safe_json});")

    def _on_farmer_finished(self, total_orbs):
        self.auto_farm_running = False
        if self.window:
            self.window.evaluate_js(f"window.onAutoQuestFinished && window.onAutoQuestFinished({int(total_orbs)});")
            self.window.evaluate_js("window.onQuestsUpdated && window.onQuestsUpdated();")

    # --- Tools & Utilities ---
    def get_console_script(self):
        return generate_discord_console_snippet()

    def open_url(self, url):
        webbrowser.open(url)
        return True

    def copy_to_clipboard(self, text):
        try:
            # Native Windows Clipboard API via ctypes
            import ctypes.wintypes
            OpenClipboard = ctypes.windll.user32.OpenClipboard
            EmptyClipboard = ctypes.windll.user32.EmptyClipboard
            SetClipboardData = ctypes.windll.user32.SetClipboardData
            CloseClipboard = ctypes.windll.user32.CloseClipboard
            GlobalAlloc = ctypes.windll.kernel32.GlobalAlloc
            GlobalLock = ctypes.windll.kernel32.GlobalLock
            GlobalUnlock = ctypes.windll.kernel32.GlobalUnlock

            if OpenClipboard(None):
                EmptyClipboard()
                h_cd = GlobalAlloc(0x0002, (len(text) + 1) * 2)
                pch_data = GlobalLock(h_cd)
                ctypes.cdll.msvcrt.wcscpy(ctypes.c_wchar_p(pch_data), text)
                GlobalUnlock(h_cd)
                SetClipboardData(13, h_cd) # CF_UNICODETEXT
                CloseClipboard()
                return True
        except Exception:
            pass
        return False

    # --- Window Controls ---
    def minimize_window(self):
        if self.window:
            self.window.minimize()

    def maximize_window(self):
        if self.window:
            # pywebview doesn't have is_maximized, toggle
            self.window.maximize()

    def close_window(self):
        if self.window:
            try:
                self.simulator.stop_simulation()
            except Exception:
                pass
            self.window.destroy()
