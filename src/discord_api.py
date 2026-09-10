"""
Discord Quests API Client
Fetches quests, enrolls accounts, advances video quests, fetches game application data,
and claims completed quest rewards (Orbs / In-game items).
"""

import requests
import json
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

def get_headers(token: str) -> dict:
    return {
        "Authorization": token.strip(),
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
    }

class DiscordQuestsAPI:
    def __init__(self, token: str):
        self.token = token.strip()

    def get_user_quests(self) -> Dict[str, Any]:
        """Fetches raw quests payload from Discord API."""
        url = "https://discord.com/api/v9/quests/@me"
        r = requests.get(url, headers=get_headers(self.token), timeout=12)
        if r.status_code == 200:
            return r.json()
        raise Exception(f"Fehler beim Laden der Quests (HTTP {r.status_code}): {r.text[:200]}")

    def get_parsed_quests(self) -> List[Dict[str, Any]]:
        """Parses active and available quests with normalized structure."""
        data = self.get_user_quests()
        raw_quests = data.get("quests", [])
        now = datetime.now(timezone.utc)
        parsed = []

        for q in raw_quests:
            cfg = q.get("config", {})
            expires_str = cfg.get("expires_at")
            expires_at = datetime.fromisoformat(expires_str) if expires_str else None
            is_expired = expires_at and expires_at <= now
            if is_expired:
                continue

            qid = q.get("id")
            messages = cfg.get("messages", {})
            quest_name = messages.get("quest_name", "Unbekannte Quest")
            game_title = messages.get("game_title", "Unbekanntes Spiel")
            game_publisher = messages.get("game_publisher", "")

            app = cfg.get("application", {})
            app_id = app.get("id", "")
            app_name = app.get("name", game_title)

            # Task detection
            task_cfg = cfg.get("task_config_v2") or cfg.get("task_config") or {}
            tasks = task_cfg.get("tasks", {})
            
            task_type = "UNKNOWN"
            target_seconds = 900 # default 15 min
            
            # Prioritize fast video/mobile tasks over lengthy desktop play
            priority_tasks = ["WATCH_VIDEO", "WATCH_VIDEO_ON_MOBILE", "PLAY_ACTIVITY", "PLAY_ON_DESKTOP", "STREAM_ON_DESKTOP"]
            for t_name in priority_tasks:
                if t_name in tasks:
                    task_type = t_name
                    target_seconds = tasks[t_name].get("target", 900)
                    break
            if task_type == "UNKNOWN" and tasks:
                task_type = list(tasks.keys())[0]
                target_seconds = tasks[task_type].get("target", 900)

            # User Status & Progress
            user_status = q.get("user_status")
            enrolled = user_status is not None and user_status.get("enrolled_at") is not None
            completed = user_status is not None and user_status.get("completed_at") is not None
            claimed = user_status is not None and user_status.get("claimed_at") is not None

            current_seconds = 0
            if user_status and "progress" in user_status and isinstance(user_status["progress"], dict):
                p_dict = user_status["progress"]
                if task_type in p_dict and "value" in p_dict[task_type]:
                    current_seconds = int(p_dict[task_type]["value"])
                elif "PLAY_ON_DESKTOP" in p_dict and "value" in p_dict["PLAY_ON_DESKTOP"]:
                    current_seconds = int(p_dict["PLAY_ON_DESKTOP"]["value"])

            if user_status and user_status.get("stream_progress_seconds"):
                current_seconds = max(current_seconds, int(user_status["stream_progress_seconds"]))

            progress_percent = min(100.0, (current_seconds / target_seconds * 100.0)) if target_seconds > 0 else 0.0

            # Rewards
            rewards = cfg.get("rewards_config", {}).get("rewards", [])
            orb_count = 0
            reward_names = []
            for rw in rewards:
                if "orb_quantity" in rw:
                    orb_count += int(rw["orb_quantity"])
                    reward_names.append(f"{rw['orb_quantity']} Orbs")
                elif "messages" in rw and "name" in rw["messages"]:
                    reward_names.append(rw["messages"]["name"])

            parsed.append({
                "id": qid,
                "quest_name": quest_name,
                "game_title": game_title,
                "game_publisher": game_publisher,
                "app_id": app_id,
                "app_name": app_name,
                "task_type": task_type,
                "target_seconds": target_seconds,
                "current_seconds": current_seconds,
                "progress_percent": progress_percent,
                "enrolled": enrolled,
                "completed": completed,
                "claimed": claimed,
                "orb_count": orb_count,
                "rewards_text": ", ".join(reward_names) if reward_names else "Belohnung",
                "expires_at": expires_str,
                "raw_quest": q
            })

        return parsed

    def enroll_quest(self, quest_id: str, location: int = 1) -> bool:
        """Enrolls the account into the specified quest."""
        url = f"https://discord.com/api/v9/quests/{quest_id}/enroll"
        r = requests.post(url, headers=get_headers(self.token), json={"location": location}, timeout=10)
        return r.status_code in (200, 204)

    def claim_reward(self, quest_id: str, platform: int = 0) -> Dict[str, Any]:
        """Claims the completed quest reward."""
        url = f"https://discord.com/api/v9/quests/{quest_id}/claim"
        r = requests.post(url, headers=get_headers(self.token), json={"platform": platform}, timeout=10)
        if r.status_code == 200:
            return {"success": True, "data": r.json()}
        return {"success": False, "error": r.text, "status": r.status_code}

    def complete_video_quest(self, quest_id: str, target_seconds: int = 30, callback=None) -> bool:
        """Fast-completes video-based Discord quests."""
        url = f"https://discord.com/api/v9/quests/{quest_id}/video-progress"
        curr = 0
        speed = 7
        while curr < target_seconds:
            curr = min(target_seconds, curr + speed)
            r = requests.post(url, headers=get_headers(self.token), json={"timestamp": curr}, timeout=8)
            if callback:
                callback(curr, target_seconds)
            if r.status_code == 200 and r.json().get("completed_at"):
                return True
            time.sleep(1)
        # Final call
        r = requests.post(url, headers=get_headers(self.token), json={"timestamp": target_seconds}, timeout=8)
        return r.status_code == 200

    def get_application_executables(self, app_id: str) -> List[str]:
        """Fetches official Windows executable names for an application from Discord."""
        if not app_id:
            return []
        url = f"https://discord.com/api/v9/applications/public?application_ids={app_id}"
        try:
            r = requests.get(url, headers=get_headers(self.token), timeout=8)
            if r.status_code == 200:
                apps = r.json()
                if apps and isinstance(apps, list):
                    execs = apps[0].get("executables", [])
                    return [e.get("name", "").replace(">", "").strip() for e in execs if e.get("os") == "win32"]
        except Exception:
            pass
        return []
