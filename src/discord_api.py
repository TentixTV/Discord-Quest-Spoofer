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
            from .discord_detectable import get_game_by_app_id
        except ImportError:
            from discord_detectable import get_game_by_app_id
        det_game = get_game_by_app_id(app_id_str, token)
        if det_game:
            return {
                "id": app_id_str,
                "name": det_game["name"],
                "exe": det_game["exe"],
                "title": det_game.get("title", det_game["name"])
            }
    except Exception:
        pass

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
        self._last_raw_quests = None
        self._last_raw_time = 0

    def get_user_quests(self) -> Dict[str, Any]:
        """Fetches raw quests payload from Discord API with intelligent caching and 429 protection."""
        now = time.time()
        # If fetched within last 15 seconds, return cached raw quests to protect against rate limits
        if self._last_raw_quests and (now - self._last_raw_time < 15):
            return self._last_raw_quests

        url = "https://discord.com/api/v9/quests/@me"
        try:
            r = requests.get(url, headers=get_headers(self.token), timeout=12)
            if r.status_code == 200:
                data = r.json()
                self._last_raw_quests = data
                self._last_raw_time = now
                return data
            
            # HTTP 429: Rate limited by Discord. Gracefully return cached data if available.
            if r.status_code == 429 and self._last_raw_quests:
                return self._last_raw_quests

            if self._last_raw_quests:
                return self._last_raw_quests

            raise Exception(f"Fehler beim Laden der Quests (HTTP {r.status_code}): {r.text[:200]}")
        except Exception as e:
            if self._last_raw_quests:
                return self._last_raw_quests
            raise e

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
            
            task_type = "PLAY_ON_DESKTOP"
            target_seconds = 900 # default 15 min
            
            # Prioritize tasks: If actual video task exists in tasks, use it
            priority_tasks = ["WATCH_VIDEO", "WATCH_VIDEO_ON_MOBILE", "PLAY_ACTIVITY", "PLAY_ON_DESKTOP", "STREAM_ON_DESKTOP"]
            for t_name in priority_tasks:
                if t_name in tasks:
                    task_type = t_name
                    target_seconds = tasks[t_name].get("target", 900)
                    break
            if task_type == "PLAY_ON_DESKTOP" and tasks:
                task_type = list(tasks.keys())[0]
                target_seconds = tasks[task_type].get("target", 900)

            # True Video Tasks have actual WATCH_VIDEO or WATCH_VIDEO_ON_MOBILE tasks
            is_video_task = ("VIDEO" in task_type) or any("VIDEO" in str(k) for k in tasks.keys())
            is_mobile_task = ("MOBILE" in task_type) or any("MOBILE" in str(k) for k in tasks.keys())

            # Extract ALL supported applications (Multi-Game Quest Detection)
            supported_applications = []
            seen_app_ids = set()

            # Universal Discord detectable game resolution
            req_info = None
            try:
                try:
                    from .discord_detectable import extract_quest_required_game
                except ImportError:
                    from discord_detectable import extract_quest_required_game
                req_info = extract_quest_required_game(q, self.token)
            except Exception:
                pass

            if req_info and req_info.get("supported_games"):
                for sg in req_info["supported_games"]:
                    aid = str(sg.get("id"))
                    if aid and aid not in seen_app_ids:
                        seen_app_ids.add(aid)
                        supported_applications.append(sg)

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
            if req_info and req_info.get("required_app_id"):
                req_aid = str(req_info["required_app_id"])
                for a in supported_applications:
                    if str(a.get("id")) == req_aid:
                        selected_app = a
                        break
                if not selected_app:
                    selected_app = {
                        "id": req_aid,
                        "name": req_info.get("required_game_name", game_title),
                        "exe": req_info.get("required_exe", "Game.exe"),
                        "title": req_info.get("required_game_name", game_title)
                    }

            if not selected_app and supported_applications:
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

            required_game_name = (selected_app.get("name") if selected_app else None) or (req_info.get("required_game_name") if req_info else None) or sim_game_title
            required_exe = (selected_app.get("exe") if selected_app else None) or (req_info.get("required_exe") if req_info else None) or "Game.exe"
            required_app_id = (selected_app.get("id") if selected_app else None) or (req_info.get("required_app_id") if req_info else None) or app_id

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
                elif "WATCH_VIDEO" in p_dict and "value" in p_dict["WATCH_VIDEO"]:
                    current_seconds = int(p_dict["WATCH_VIDEO"]["value"])
                elif "WATCH_VIDEO_ON_MOBILE" in p_dict and "value" in p_dict["WATCH_VIDEO_ON_MOBILE"]:
                    current_seconds = int(p_dict["WATCH_VIDEO_ON_MOBILE"]["value"])

            if user_status and user_status.get("stream_progress_seconds"):
                current_seconds = max(current_seconds, int(user_status["stream_progress_seconds"]))

            progress_percent = min(100.0, (current_seconds / target_seconds * 100.0)) if target_seconds > 0 else 0.0

            # Comprehensive Rewards Parsing (Orbs, Avatar Decorations, In-Game Items / Codes / Skins)
            rewards = cfg.get("rewards_config", {}).get("rewards", [])
            orb_count = 0
            reward_names = []
            primary_reward_type = "ORBS" if any("orb_quantity" in rw for rw in rewards) else "ITEM"
            primary_reward_name = ""
            reward_asset_url = None
            reward_instructions = ""

            for rw in rewards:
                rw_type = rw.get("type")
                rw_name = rw.get("messages", {}).get("name") or rw.get("messages", {}).get("name_with_article") or ""
                if "orb_quantity" in rw:
                    orb_count += int(rw["orb_quantity"])
                    reward_names.append(f"{rw['orb_quantity']} Orbs")
                    if not primary_reward_name:
                        primary_reward_name = f"{rw['orb_quantity']} Orbs"
                        primary_reward_type = "ORBS"
                elif rw_type == 3 or "avatar" in rw_name.lower() or "deko" in rw_name.lower():
                    # Avatar Decoration
                    reward_names.append(rw_name or "Avatardekoration")
                    primary_reward_name = rw_name or "Avatardekoration"
                    primary_reward_type = "AVATAR_DECO"
                elif rw_type == 1 or "code" in rw_name.lower() or "paket" in rw_name.lower() or "skin" in rw_name.lower() or "boost" in rw_name.lower():
                    # In-Game Item / Promo Code / Weapon Skin
                    reward_names.append(rw_name or "In-Game Belohnung")
                    primary_reward_name = rw_name or "In-Game Belohnung"
                    primary_reward_type = "INGAME_ITEM"
                elif rw_name:
                    reward_names.append(rw_name)
                    if not primary_reward_name:
                        primary_reward_name = rw_name

                if rw.get("asset"):
                    reward_asset_url = f"https://cdn.discordapp.com/{rw['asset']}"
                
                # Check redemption instructions
                instr_dict = rw.get("messages", {}).get("redemption_instructions_by_platform", {})
                if instr_dict and isinstance(instr_dict, dict):
                    reward_instructions = list(instr_dict.values())[0]

            if not primary_reward_name:
                primary_reward_name = ", ".join(reward_names) if reward_names else "Belohnung"

            # Media Assets (Hero Image, Trailer / Preview Video)
            assets = cfg.get("assets", {})
            hero_asset = assets.get("hero") or assets.get("quest_bar_hero")
            video_asset = assets.get("hero_video") or assets.get("quest_bar_hero_video")
            hero_url = f"https://cdn.discordapp.com/{hero_asset}" if hero_asset else None
            video_url = f"https://cdn.discordapp.com/{video_asset}" if video_asset else None
            has_trailer = video_url is not None

            parsed.append({
                "id": qid,
                "quest_name": quest_name,
                "game_title": game_title,
                "game_publisher": game_publisher,
                "app_id": app_id,
                "app_name": app_name,
                "sim_game_title": sim_game_title,
                "required_game_name": required_game_name,
                "required_exe": required_exe,
                "required_app_id": required_app_id,
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
                "primary_reward_type": primary_reward_type,
                "primary_reward_name": primary_reward_name,
                "reward_asset_url": reward_asset_url,
                "reward_instructions": reward_instructions,
                "rewards_text": ", ".join(reward_names) if reward_names else "Belohnung",
                "expires_at": expires_str,
                "hero_url": hero_url,
                "video_url": video_url,
                "trailer_url": video_url,
                "has_trailer": has_trailer,
                "has_video": is_video_task,
                "is_video_task": is_video_task,
                "is_mobile_task": is_mobile_task,
                "raw_quest": q
            })

        return parsed

    def enroll_quest(self, quest_id: str, location: int = 11) -> bool:
        """Enrolls the account into the specified quest."""
        url = f"https://discord.com/api/v9/quests/{quest_id}/enroll"
        payload = {"location": location, "is_targeted": False, "metadata_sealed": None}
        try:
            r = requests.post(url, headers=get_headers(self.token), json=payload, timeout=8)
            if r.status_code in (200, 204):
                return True
        except Exception:
            pass
        try:
            r = requests.post(url, headers=get_headers(self.token), json={"location": 1}, timeout=8)
            return r.status_code in (200, 204)
        except Exception:
            return False

    def claim_reward(self, quest_id: str, platform: int = 0) -> Dict[str, Any]:
        """Claims completed quest reward via /claim-reward and /claim endpoints."""
        payload = {
            "platform": platform,
            "location": 11 if platform == 0 else 2,
            "is_targeted": False,
            "metadata_sealed": None
        }

        # Try /claim-reward first (standard modern Discord web/desktop endpoint)
        url1 = f"https://discord.com/api/v9/quests/{quest_id}/claim-reward"
        try:
            r = requests.post(url1, headers=get_headers(self.token), json=payload, timeout=8)
            if r.status_code in (200, 201):
                data = r.json()
                code = data.get("code") or data.get("claim_code") or (data.get("reward") or {}).get("code")
                return {"success": True, "data": data, "code": code}
        except Exception:
            pass

        # Fallback to /claim endpoint
        url2 = f"https://discord.com/api/v9/quests/{quest_id}/claim"
        try:
            r = requests.post(url2, headers=get_headers(self.token), json={"platform": platform}, timeout=8)
            if r.status_code in (200, 201):
                data = r.json()
                code = data.get("code") or data.get("claim_code") or (data.get("reward") or {}).get("code")
                return {"success": True, "data": data, "code": code}
            return {"success": False, "error": r.text, "status": r.status_code}
        except Exception as e:
            return {"success": False, "error": str(e), "status": 500}

    def complete_video_quest(self, quest_id: str, target_seconds: int = 30, is_mobile: bool = False, callback=None) -> Dict[str, Any]:
        """Fast-completes video-based Discord quests with auto-enrollment, mobile simulation, and claim."""
        loc = 2 if is_mobile else 11
        try:
            self.enroll_quest(quest_id, location=loc)
        except Exception:
            try:
                self.enroll_quest(quest_id, location=1)
            except Exception:
                pass

        url = f"https://discord.com/api/v9/quests/{quest_id}/video-progress"
        ts = max(30, int(target_seconds or 30))

        mobile_headers = get_headers(self.token)
        if is_mobile:
            mobile_headers["User-Agent"] = "Discord-Android/220.18 (Android; 14; Mobile; Pixel 8)"
            mobile_headers["X-Discord-Platform"] = "android"

        steps = [
            round(ts * 0.25, 4),
            round(ts * 0.50, 4),
            round(ts * 0.75, 4),
            float(ts)
        ]

        last_resp = None
        for s in steps:
            if callback:
                callback(int(s), ts)
            try:
                headers = mobile_headers if is_mobile else get_headers(self.token)
                r = requests.post(url, headers=headers, json={"timestamp": s}, timeout=5)
                if r.status_code == 200:
                    last_resp = r.json()
                    if last_resp.get("completed_at") or (isinstance(last_resp.get("user_status"), dict) and last_resp["user_status"].get("completed_at")):
                        break
                elif r.status_code in (400, 404) and is_mobile:
                    r2 = requests.post(url, headers=get_headers(self.token), json={"timestamp": s}, timeout=5)
                    if r2.status_code == 200:
                        last_resp = r2.json()
            except Exception:
                pass
            time.sleep(0.35)

        time.sleep(1)
        claim_res = self.claim_reward(quest_id, platform=2 if is_mobile else 0)
        return {"completed": True, "claim": claim_res}

    def send_activity_heartbeat(self, quest_id: str, app_id: str = "", terminal: bool = False) -> Dict[str, Any]:
        """Sends an activity participation heartbeat to Discord."""
        url = f"https://discord.com/api/v9/quests/{quest_id}/heartbeat"
        body = {
            "application_id": str(app_id or ""),
            "terminal": terminal
        }
        try:
            r = requests.post(url, headers=get_headers(self.token), json=body, timeout=8)
            if r.status_code == 200:
                return {"success": True, "data": r.json()}
            return {"success": False, "status": r.status_code, "error": r.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

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
