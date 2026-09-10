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

_APP_CACHE: Dict[str, Dict[str, str]] = {}

def resolve_application_metadata(app_id: str, token: str = "") -> Dict[str, str]:
    """Resolves game name and process details from QUEST_GAMES_DATABASE or Discord API."""
    if not app_id:
        return {"id": "", "name": "Unbekanntes Spiel", "exe": "Game.exe", "title": "Game"}
    
    app_id_str = str(app_id)
    try:
        try:
            from .database import QUEST_GAMES_DATABASE
        except ImportError:
            from database import QUEST_GAMES_DATABASE
        if app_id_str in QUEST_GAMES_DATABASE:
            info = QUEST_GAMES_DATABASE[app_id_str]
            return {
                "id": app_id_str,
                "name": info["name"],
                "exe": info["exe"],
                "title": info["title"]
            }
    except Exception:
        pass

    if app_id_str in _APP_CACHE:
        return _APP_CACHE[app_id_str]

    if token:
        try:
            url = f"https://discord.com/api/v9/applications/{app_id_str}/rpc"
            r = requests.get(url, headers=get_headers(token), timeout=4)
            if r.status_code == 200:
                data = r.json()
                name = data.get("name") or f"Spiel {app_id_str[-4:]}"
                clean_exe = "".join(c for c in name if c.isalnum() or c in ("_", "-"))
                meta = {
                    "id": app_id_str,
                    "name": name,
                    "exe": f"{clean_exe}.exe" if clean_exe else "Game.exe",
                    "title": name
                }
                _APP_CACHE[app_id_str] = meta
                return meta
        except Exception:
            pass

    fallback = {
        "id": app_id_str,
        "name": f"Spiel ({app_id_str[-4:]})",
        "exe": "Game.exe",
        "title": f"Spiel ({app_id_str[-4:]})"
    }
    _APP_CACHE[app_id_str] = fallback
    return fallback

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
        """Parses active and available quests with normalized structure and multi-game detection."""
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
            app_id = str(app.get("id", "")) if app.get("id") else ""
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

            # Extract ALL supported applications (Multi-Game Quest Detection)
            supported_applications = []
            seen_app_ids = set()

            # 1. From tasks (e.g. PLAY_ON_DESKTOP.applications)
            for t_name, t_val in tasks.items():
                if isinstance(t_val, dict) and "applications" in t_val:
                    for item in t_val.get("applications", []):
                        if isinstance(item, dict) and item.get("id"):
                            aid = str(item["id"])
                            if aid not in seen_app_ids:
                                seen_app_ids.add(aid)
                                app_meta = resolve_application_metadata(aid, self.token)
                                supported_applications.append(app_meta)

            # 2. From config applications / application
            if isinstance(cfg.get("applications"), list):
                for item in cfg["applications"]:
                    if isinstance(item, dict) and item.get("id"):
                        aid = str(item["id"])
                        if aid not in seen_app_ids:
                            seen_app_ids.add(aid)
                            app_meta = resolve_application_metadata(aid, self.token)
                            supported_applications.append(app_meta)

            if app_id and app_id not in seen_app_ids:
                app_meta = resolve_application_metadata(app_id, self.token)
                if app_name and app_name != game_title:
                    app_meta["name"] = app_name
                supported_applications.insert(0, app_meta)
                seen_app_ids.add(app_id)

            is_multi_game = len(supported_applications) > 1

            # Pick a valid application for simulation (prioritize games verified in Discord detectable DB)
            selected_app = None
            if supported_applications:
                try:
                    try:
                        from .database import QUEST_GAMES_DATABASE
                    except ImportError:
                        from database import QUEST_GAMES_DATABASE

                    def app_priority(a):
                        aid = str(a.get("id"))
                        if aid in QUEST_GAMES_DATABASE:
                            exe = QUEST_GAMES_DATABASE[aid].get("exe", "").lower()
                            if "requiem" in exe or not exe:
                                return 99
                            if "street fighter" in exe or "re4" in exe or "monsterhunter" in exe or "re2" in exe or "re8" in exe:
                                return 1
                            return 10
                        return 50

                    supported_applications.sort(key=app_priority)
                    selected_app = supported_applications[0]
                except Exception as e:
                    selected_app = supported_applications[0]

            if selected_app:
                app_id = selected_app["id"]
                # If game_title was generic like "CAPCOM TGS Deals", use specific selected game title
                if any(w in game_title.lower() for w in ["deals", "ausgewählten", "ausgewaehlten", "bundle", "event"]):
                    sim_game_title = selected_app["name"]
                else:
                    sim_game_title = game_title
            else:
                sim_game_title = game_title

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

            # Media Assets (Hero Image, Trailer / Quest Video)
            assets = cfg.get("assets", {})
            hero_asset = assets.get("hero") or assets.get("quest_bar_hero")
            video_asset = assets.get("hero_video") or assets.get("quest_bar_hero_video")
            hero_url = f"https://cdn.discordapp.com/{hero_asset}" if hero_asset else None
            video_url = f"https://cdn.discordapp.com/{video_asset}" if video_asset else None
            has_video = (video_url is not None) or ("VIDEO" in task_type)

            parsed.append({
                "id": qid,
                "quest_name": quest_name,
                "game_title": game_title,
                "game_publisher": game_publisher,
                "app_id": app_id,
                "app_name": app_name,
                "sim_game_title": sim_game_title,
                "is_multi_game": is_multi_game,
                "supported_applications": supported_applications,
                "selected_app": selected_app,
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
                "hero_url": hero_url,
                "video_url": video_url,
                "has_video": has_video,
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
        """Fast-completes video-based Discord quests with auto-enrollment and stream simulation."""
        try:
            self.enroll_quest(quest_id)
        except Exception:
            pass

        url = f"https://discord.com/api/v9/quests/{quest_id}/video-progress"
        ts = max(30, int(target_seconds or 30))

        # Fast stepping (4 steps over ~1.2s for smooth UI feedback)
        steps = [round(ts * 0.25), round(ts * 0.5), round(ts * 0.75), ts]
        for s in steps:
            if callback:
                callback(s, ts)
            try:
                r = requests.post(url, headers=get_headers(self.token), json={"timestamp": s}, timeout=4)
                if r.status_code == 200:
                    data = r.json()
                    if data.get("completed_at") or (isinstance(data.get("user_status"), dict) and data["user_status"].get("completed_at")):
                        break
                elif r.status_code == 404:
                    # Not a native video endpoint; break immediately without hanging
                    break
            except Exception:
                pass
            time.sleep(0.3)

        # Attempt claim immediately upon express completion
        try:
            self.claim_reward(quest_id)
        except Exception:
            pass

        return True

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
