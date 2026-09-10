"""
Automated Quest Farmer Engine
Coordinates auto-enrollment, simulation sequencing, video completion,
progress tracking, and reward claiming.
"""

import os
import sys
import time
import threading
import ctypes
from typing import Callable, Optional, List, Dict, Any
from .discord_api import DiscordQuestsAPI
from .game_spoofer import GameSimulator

def play_beep(beep_type: int = 0):
    """Play notification sound safely via Windows user32 MessageBeep without external dependencies."""
    try:
        ctypes.windll.user32.MessageBeep(beep_type)
    except Exception:
        pass

def format_duration(seconds: int) -> str:
    """Formats seconds into human-readable duration in parentheses (...)"""
    if seconds <= 0:
        return "(0 Min.)"
    if seconds < 60:
        return f"(ca. {seconds} Sek.)"
    if seconds < 3600:
        m = max(1, round(seconds / 60))
        return f"(ca. {m} Min.)"
    h = seconds // 3600
    m = round((seconds % 3600) / 60)
    if m > 0:
        return f"(ca. {h} Std. {m} Min.)"
    return f"(ca. {h} Std.)"

def calculate_quests_duration(quests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculates total estimated remaining duration for a list of quests."""
    total_seconds = 0
    open_count = 0
    for q in quests:
        if q.get("claimed"):
            continue
        open_count += 1
        task_type = q.get("task_type", "UNKNOWN")
        target_sec = q.get("target_seconds", 900)
        curr_sec = q.get("current_seconds", 0)
        is_video = task_type in ("WATCH_VIDEO", "WATCH_VIDEO_ON_MOBILE", "PLAY_ACTIVITY") or bool(q.get("has_video"))
        
        if q.get("completed"):
            continue
        elif is_video:
            total_seconds += 10  # Express video completion takes ~10 seconds
        else:
            rem = max(0, target_sec - curr_sec)
            total_seconds += rem

    return {
        "total_seconds": total_seconds,
        "duration_text": format_duration(total_seconds),
        "open_count": open_count
    }

class QuestFarmer:
    def __init__(self, api: DiscordQuestsAPI, simulator: GameSimulator):
        self.api = api
        self.simulator = simulator
        self.running = False
        self.paused = False
        self.worker_thread: Optional[threading.Thread] = None

        # Callbacks
        self.on_log: Optional[Callable[[str, str], None]] = None
        self.on_progress: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_finished: Optional[Callable[[int], None]] = None

    def log(self, message: str, level: str = "INFO"):
        if self.on_log:
            self.on_log(message, level)
        else:
            print(f"[{level}] {message}")

    def start_farm_all(self, quests: List[Dict[str, Any]]):
        """Starts background worker to farm all active quests in sequence."""
        if self.running:
            return
        self.running = True
        self.paused = False
        self.worker_thread = threading.Thread(target=self._run_farm, args=(quests,), daemon=True)
        self.worker_thread.start()

    def stop(self):
        """Stops the active farming session."""
        self.running = False
        self.paused = False
        if self.simulator.is_running():
            self.simulator.stop_simulation()
        self.log("Auto-Farming wurde abgebrochen.", "WARN")

    def _run_farm(self, quests: List[Dict[str, Any]]):
        self.log("[START] Starte intelligenten Quest-Ablauf...", "INFO")
        total_orbs_gained = 0

        # Filter out already claimed quests
        eligible = [q for q in quests if not q.get("claimed")]
        if not eligible:
            self.log("Alle verfuegbaren Quests sind bereits abgeschlossen und abgeholt!", "SUCCESS")
            self.running = False
            if self.on_finished:
                self.on_finished(0)
            return

        total_count = len(eligible)
        def get_queue_remaining(curr_idx, curr_remaining):
            rem = curr_remaining
            for nxt in eligible[curr_idx:]:
                t_type = nxt.get("task_type", "UNKNOWN")
                is_vid = t_type in ("WATCH_VIDEO", "WATCH_VIDEO_ON_MOBILE", "PLAY_ACTIVITY") or bool(nxt.get("has_video"))
                if is_vid:
                    rem += 10
                else:
                    rem += max(0, nxt.get("target_seconds", 900) - nxt.get("current_seconds", 0))
            return rem

        initial_total = get_queue_remaining(0, 0)
        self.log(f"{total_count} offene Quests in der Warteschlange. Geschaetzte Gesamtdauer: {format_duration(initial_total)}", "INFO")

        for idx, q in enumerate(eligible, 1):
            if not self.running:
                break

            qid = q["id"]
            qname = q["quest_name"]
            
            # Game detection & selection
            supported_apps = q.get("supported_applications") or []
            selected_exe = q.get("required_exe") or (q.get("selected_app") or {}).get("exe", "")
            app_id = q.get("required_app_id") or q.get("app_id", "")
            game_title = q.get("required_game_name") or q.get("sim_game_title") or q.get("game_title", "Unbekanntes Spiel")

            if q.get("is_multi_game") and supported_apps:
                selected_app = q.get("selected_app") or supported_apps[0]
                app_id = selected_app.get("id") or app_id
                game_title = selected_app.get("name") or game_title
                selected_exe = selected_app.get("exe") or selected_exe
                self.log(f"[MULTI-GAME] '{qname}' bietet {len(supported_apps)} auswaehlbare Spiele. Waehle automatisch '{game_title}' (App-ID: {app_id}, Prozess: '{selected_exe}')...", "INFO")
            else:
                if selected_exe:
                    self.log(f"[SPIEL-ERKENNUNG] Erkanntes Spiel fuer '{qname}': '{game_title}' (Prozess: '{selected_exe}').", "INFO")

            task_type = q["task_type"]
            target_sec = q.get("target_seconds", 900)
            curr_sec = q.get("current_seconds", 0)
            reward_desc = q["rewards_text"]
            orb_amount = q.get("orb_count", 0)
            is_video_task = task_type in ("WATCH_VIDEO", "WATCH_VIDEO_ON_MOBILE", "PLAY_ACTIVITY") or bool(q.get("has_video"))
            needed_this_quest = 10 if is_video_task else max(0, target_sec - curr_sec)

            self.log(f"--------------------------------------------------", "TIME")
            self.log(f"[{idx}/{total_count}] Starte Quest: '{qname}' ({game_title})", "INFO")
            self.log(f"Dauer dieser Quest: {format_duration(needed_this_quest)} | Verbleibende Gesamtdauer: {format_duration(get_queue_remaining(idx, needed_this_quest))}", "INFO")

            # 1. Einschreiben falls noch nicht geschehen
            if not q.get("enrolled"):
                self.log(f"Schreibe Account in '{qname}' ein...", "INFO")
                enrolled = self.api.enroll_quest(qid)
                if enrolled:
                    self.log(f"Account erfolgreich eingeschrieben!", "SUCCESS")
                    q["enrolled"] = True
                else:
                    self.log(f"Einschreibung aktiv oder bereits registriert.", "INFO")

            # 2. Prüfen ob bereits 100% fertig, aber noch nicht geclaimt
            if q.get("completed") and not q.get("claimed"):
                self.log(f"Quest bereits erfuellt! Hole Belohnung ab...", "SUCCESS")
                res = self.api.claim_reward(qid)
                if res.get("success"):
                    self.log(f"[ERFOLG] Belohnung '{reward_desc}' erfolgreich erhalten!", "SUCCESS")
                    total_orbs_gained += orb_amount
                    q["claimed"] = True
                    play_beep(0)
                continue

            # 3. Task ausführen
            if is_video_task:
                self.log(f"Video/Express-Aufgabe erkannt ({format_duration(10)}). Führe Sofortabschluss aus...", "INFO")
                def video_cb(c, t):
                    pct = (c / t) * 100.0
                    self.log(f"Video-Fortschritt: {c}/{t}s ({pct:.0f}%)", "INFO")
                    if self.on_progress:
                        overall_rem = get_queue_remaining(idx, max(0, t - c))
                        self.on_progress({
                            "quest_id": qid,
                            "quest_name": qname,
                            "game_title": game_title,
                            "current_seconds": c,
                            "target_seconds": t,
                            "progress_percent": pct,
                            "remaining_seconds": max(0, t - c),
                            "current_index": idx,
                            "total_count": total_count,
                            "overall_remaining_seconds": overall_rem,
                            "overall_duration_text": format_duration(overall_rem)
                        })

                ok = self.api.complete_video_quest(qid, target_sec, video_cb)
                if ok:
                    self.log(f"Video abgeschlossen! Fordere Belohnung an...", "SUCCESS")
                    time.sleep(2)
                    res = self.api.claim_reward(qid)
                    if res.get("success"):
                        self.log(f"[ERFOLG] Belohnung '{reward_desc}' abgeholt!", "SUCCESS")
                        total_orbs_gained += orb_amount
                        play_beep(0)
                else:
                    self.log(f"Video-Abschluss fehlgeschlagen.", "ERROR")

            else:
                # Desktop Game Simulation
                needed_seconds = max(0, target_sec - curr_sec)
                self.log(f"Starte Spiel-Simulation für '{game_title}' ({format_duration(needed_seconds)})...", "INFO")
                sim_res = self.simulator.start_simulation(app_id, game_title, custom_exe=selected_exe)
                self.log(f"Simulierter Prozess '{sim_res['exe_name']}' laeuft aktiv (PID: {sim_res['pid']}).", "SUCCESS")
                self.log(f"Verbleibende Spielzeit dieser Quest: {format_duration(needed_seconds)}", "INFO")

                simulated = 0
                check_interval = 5
                last_poll = 0

                while simulated < needed_seconds and self.running:
                    while self.paused and self.running:
                        time.sleep(1)

                    time.sleep(check_interval)
                    simulated += check_interval
                    total_done = curr_sec + simulated
                    pct = min(100.0, (total_done / target_sec) * 100.0)
                    remaining = max(0, target_sec - total_done)
                    overall_rem = get_queue_remaining(idx, remaining)

                    if self.on_progress:
                        self.on_progress({
                            "quest_id": qid,
                            "quest_name": qname,
                            "game_title": game_title,
                            "current_seconds": total_done,
                            "target_seconds": target_sec,
                            "progress_percent": pct,
                            "remaining_seconds": remaining,
                            "current_index": idx,
                            "total_count": total_count,
                            "overall_remaining_seconds": overall_rem,
                            "overall_duration_text": format_duration(overall_rem)
                        })

                    # Discord API Status-Prüfung alle 45 Sekunden
                    if time.time() - last_poll >= 45:
                        last_poll = time.time()
                        try:
                            fresh_quests = self.api.get_parsed_quests()
                            for fq in fresh_quests:
                                if fq["id"] == qid:
                                    if fq.get("completed"):
                                        self.log(f"Discord meldet: Quest '{qname}' vorzeitig als fertig anerkannt!", "SUCCESS")
                                        simulated = needed_seconds
                                        break
                                    elif fq.get("current_seconds", 0) > total_done:
                                        curr_sec = fq["current_seconds"]
                                        simulated = 0
                                        needed_seconds = max(0, target_sec - curr_sec)
                        except Exception:
                            pass

                    # Status alle 30s protokollieren
                    if simulated % 30 == 0 or simulated >= needed_seconds:
                        rem_m = remaining // 60
                        rem_s = remaining % 60
                        self.log(f"'{game_title}': Noch {rem_m:02d}:{rem_s:02d} Min. verbleibend ({pct:.1f}% erreicht)", "INFO")

                self.simulator.stop_simulation()
                self.log(f"Spiel-Simulation für '{game_title}' planmäßig beendet.", "INFO")

                if self.running and simulated >= needed_seconds:
                    self.log(f"Laufzeit fuer '{qname}' abgeschlossen! Hole Belohnung ab...", "INFO")
                    time.sleep(3)
                    claim_res = self.api.claim_reward(qid)
                    if claim_res.get("success"):
                        self.log(f"[ERFOLG] Belohnung '{reward_desc}' erhalten!", "SUCCESS")
                        total_orbs_gained += orb_amount
                        play_beep(0)
                    else:
                        self.log(f"Belohnung noch nicht sofort freigeschaltet (Status: {claim_res.get('error', '')}).", "WARN")

            # Automatisch mit naechster Quest fortfahren
            if self.running and idx < total_count:
                next_quest = eligible[idx]
                self.log(f"[ABGESCHLOSSEN] Quest {idx}/{total_count} beendet! Wechsle in 5 Sekunden zu naechster Quest: '{next_quest['quest_name']}'...", "SUCCESS")
                time.sleep(5)

        self.running = False
        self.log(f"--------------------------------------------------", "TIME")
        self.log(f"[ERLEDIGT] Alle Quests wurden durchlaufen! Insgesamt {total_orbs_gained} Orbs eingefarmt.", "SUCCESS")
        play_beep(0x40)

        if self.on_finished:
            self.on_finished(total_orbs_gained)

def generate_discord_console_snippet() -> str:
    """Returns the full in-client Quest completion engine for Discord DevTools."""
    candidates = [
        os.path.join(getattr(sys, "_MEIPASS", ""), "src", "discord_hook.js"),
        os.path.join(os.path.dirname(__file__), "discord_hook.js"),
        os.path.join(os.getcwd(), "src", "discord_hook.js"),
        os.path.join(os.getcwd(), "discord_hook.js"),
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                with open(c, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content and len(content) > 1000:
                        return content
            except Exception:
                pass

    return """/* ✦ DQF by T3X - Smart In-Client Quest Engine ✦ */
(async () => {
    console.log("%c[DQF by T3X] ✦ Starte Discord Quest Automatisierung...", "color: #5865F2; font-weight: bold; font-size: 14px;");

    let req;
    window.webpackChunkdiscord_app.push([[Symbol()], {}, r => { req = r; }]);
    window.webpackChunkdiscord_app.pop();
    const modules = Object.values(req?.c || {});

    const RunningGameStore = modules.find(x => x?.exports?.ZP?.getRunningGames)?.exports.ZP || modules.find(x => x?.exports?.default?.getRunningGames)?.exports.default;
    const QuestsStore = modules.find(x => x?.exports?.Z?.__proto__?.getQuest)?.exports.Z || modules.find(x => x?.exports?.ZP?.__proto__?.getQuest)?.exports.ZP;
    const Dispatcher = modules.find(x => x?.exports?.Z?.__proto__?.flushWaitQueue)?.exports.Z || modules.find(x => x?.exports?.ZP?.__proto__?.flushWaitQueue)?.exports.ZP;
    const api = modules.find(x => x?.exports?.tn?.get)?.exports.tn || modules.find(x => x?.exports?.default?.get)?.exports.default;

    if (!RunningGameStore || !QuestsStore || !Dispatcher || !api) {
        console.error("[DQF by T3X] ❌ Discord Module konnten nicht geladen werden. Bitte Discord neu laden (STRG + R).");
        return;
    }

    const rawQuests = [...QuestsStore.quests.values()];
    const activeQuests = [];

    for (const q of rawQuests) {
        if (new Date(q.config?.expiresAt) <= Date.now()) continue;
        if (q.userStatus?.claimedAt) continue;

        if (!q.userStatus?.enrolledAt) {
            try {
                console.log(`%c[DQF by T3X] Schreibe automatisch in Quest '${q.config?.messages?.questName}' ein...`, "color: #FAA81A;");
                await api.post({ url: `/quests/${q.id}/enroll` });
            } catch (e) {}
        }
        activeQuests.push(q);
    }

    if (activeQuests.length === 0) {
        console.log("%c[DQF by T3X] ✨ Keine offenen Quests vorhanden oder alle bereits abgeholt!", "color: #23A55A; font-weight: bold; font-size: 13px;");
        return;
    }

    console.log(`%c[DQF by T3X] ${activeQuests.length} Quests gefunden. Starte Bearbeitung...`, "color: #5865F2; font-weight: bold;");

    const real = {
        getRunningGames: RunningGameStore.getRunningGames,
        getGameForPID: RunningGameStore.getGameForPID,
        getVisibleGame: RunningGameStore.getVisibleGame,
        getVisibleRunningGames: RunningGameStore.getVisibleRunningGames,
        getCandidateGames: RunningGameStore.getCandidateGames,
        getRunningDiscordApplicationIds: RunningGameStore.getRunningDiscordApplicationIds
    };

    const fakeGames = [];

    for (const quest of activeQuests) {
        const appId = String(quest.config?.application?.id || "");
        const appName = quest.config?.application?.name || quest.config?.messages?.gameTitle || "Game";
        const taskConfig = quest.config?.taskConfig ?? quest.config?.taskConfigV2;
        const taskName = ["WATCH_VIDEO", "PLAY_ON_DESKTOP", "STREAM_ON_DESKTOP"].find(x => taskConfig?.tasks?.[x] != null) || "PLAY_ON_DESKTOP";
        const target = taskConfig?.tasks?.[taskName]?.target ?? 900;

        if (taskName === "WATCH_VIDEO") {
            console.log(`%c[DQF by T3X] 📺 Schließe Video-Aufgabe '${appName}' sofort ab...`, "color: #FAA81A; font-weight: bold;");
            try {
                await api.post({ url: `/quests/${quest.id}/video-progress`, body: { timestamp: target } });
                console.log(`%c[DQF by T3X] 🎉 Video '${appName}' erfolgreich beendet! Hole Belohnung...`, "color: #23A55A; font-weight: bold;");
                await api.post({ url: `/quests/${quest.id}/claim` });
            } catch (e) {}
        } else {
            const pid = Math.floor(Math.random() * 25000) + 3000;
            const fg = {
                cmdLine: `C:\\Games\\${appName}\\${appName}.exe`,
                exeName: `${appName.replace(/[^a-zA-Z0-9]/g, '')}.exe`,
                exePath: `c:/games/${appName.toLowerCase()}/${appName.toLowerCase()}.exe`,
                hidden: false,
                isLauncher: false,
                id: appId,
                name: appName,
                pid: pid,
                pidPath: [pid],
                processName: appName,
                start: Date.now()
            };
            fakeGames.push(fg);
            console.log(`%c[DQF by T3X] 🎮 Simuliere '${appName}' (AppID: ${appId})...`, "color: #00A8FC;");
        }
    }

    if (fakeGames.length > 0) {
        RunningGameStore.getRunningGames = () => [...(real.getRunningGames?.() || []), ...fakeGames];
        RunningGameStore.getGameForPID = (pid) => fakeGames.find(g => g.pid === pid) || real.getGameForPID?.(pid);
        if (real.getVisibleGame) RunningGameStore.getVisibleGame = () => fakeGames[0] ?? real.getVisibleGame?.();
        if (real.getVisibleRunningGames) RunningGameStore.getVisibleRunningGames = () => [...(real.getVisibleRunningGames?.() || []), ...fakeGames];
        if (real.getCandidateGames) RunningGameStore.getCandidateGames = () => [...(real.getCandidateGames?.() || []), ...fakeGames];
        if (real.getRunningDiscordApplicationIds) {
            RunningGameStore.getRunningDiscordApplicationIds = () => {
                const orig = real.getRunningDiscordApplicationIds?.() || [];
                const ours = fakeGames.map(g => String(g.id));
                return orig instanceof Set ? new Set([...orig, ...ours]) : [...orig, ...ours];
            };
        }

        Dispatcher.dispatch({
            type: "RUNNING_GAMES_CHANGE",
            added: fakeGames,
            removed: [],
            games: RunningGameStore.getRunningGames()
        });

        console.log("%c[DQF by T3X] ✅ Spiel-Prozesse erfolgreich in Discord eingeklinkt!", "color: #23A55A; font-weight: bold;");
        console.log("%c[DQF by T3X] ⏳ Discord sendet jetzt im Hintergrund Heartbeats an die Server. Fortschritt steigt kontinuierlich!", "color: #5865F2;");

        const heartbeatHandler = async (evt) => {
            const q = activeQuests.find(x => x.id === evt?.questId);
            if (q) {
                const name = q.config?.messages?.questName || "Quest";
                console.log(`%c[Heartbeat] ❤️ Fortschritt aktualisiert für '${name}'!`, "color: #23A55A;");
                if (evt.userStatus?.completedAt && !evt.userStatus?.claimedAt) {
                    console.log(`%c[DQF by T3X] 🎉 100% erreicht! Hole Belohnung für '${name}' ab...`, "color: #FEE75C; font-weight: bold;");
                    try {
                        await api.post({ url: `/quests/${q.id}/claim` });
                        console.log(`%c[DQF by T3X] ✨ Belohnung erfolgreich abgeholt!`, "color: #23A55A; font-weight: bold;");
                    } catch (e) {}
                }
            }
        };

        Dispatcher.subscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", heartbeatHandler);

        window.stopQuestSpoofer = () => {
            for (const [k, v] of Object.entries(real)) {
                if (v) RunningGameStore[k] = v;
            }
            Dispatcher.unsubscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", heartbeatHandler);
            Dispatcher.dispatch({ type: "RUNNING_GAMES_CHANGE", added: [], removed: fakeGames, games: RunningGameStore.getRunningGames() });
            console.log("%c[DQF by T3X] ⏹ Quest-Spoofer beendet und ursprüngliche Discord-Funktionen wiederhergestellt.", "color: #F23F43;");
        };

        console.log("%c[Tipp] Tippe 'stopQuestSpoofer()' in die Konsole ein, falls du das Spoofing vorzeitig beenden möchtest.", "color: #888; font-style: italic;");
    }
})();"""

