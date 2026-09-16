/**
 * DQS // High-End Discord Quest Spoofer Engine
 * JavaScript Client Architecture, 3D Physics Tilt, Dual Video Bars, and PyWebView Bridge
 * 100% Emoji-free, Ultra-crisp High-DPI SVGs, Animated Discord Orbs
 */

// ================= 1. HIGH-END 3D COSMIC PARTICLE CANVAS =================
(function init3DParticleCanvas() {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let w = canvas.width = window.innerWidth;
    let h = canvas.height = window.innerHeight;

    let mouseX = w / 2;
    let mouseY = h / 2;

    window.addEventListener('resize', () => {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    });

    window.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    const nodeCount = 55;
    const nodes = [];
    const colors = [
        'rgba(255, 255, 255, ', // Diamond White
        'rgba(241, 245, 249, ', // Crisp White
        'rgba(203, 213, 225, ', // Titanium Silver
        'rgba(148, 163, 184, ', // Slate Grey
        'rgba(100, 116, 139, '  // Deep Charcoal
    ];

    for (let i = 0; i < nodeCount; i++) {
        nodes.push({
            x: Math.random() * w,
            y: Math.random() * h,
            z: Math.random() * 450 + 80, // 3D depth
            radius: Math.random() * 2.2 + 0.8,
            color: colors[Math.floor(Math.random() * colors.length)],
            vx: (Math.random() - 0.5) * 0.45,
            vy: (Math.random() - 0.5) * 0.45,
            pulse: Math.random() * Math.PI
        });
    }

    function render() {
        ctx.clearRect(0, 0, w, h);
        const fov = 380;

        for (let i = 0; i < nodeCount; i++) {
            const n = nodes[i];
            n.x += n.vx;
            n.y += n.vy;
            n.pulse += 0.025;

            const dx = (mouseX - w / 2) * 0.025;
            const dy = (mouseY - h / 2) * 0.025;

            if (n.x < 0) n.x = w;
            if (n.x > w) n.x = 0;
            if (n.y < 0) n.y = h;
            if (n.y > h) n.y = 0;

            const scale = fov / (fov + n.z);
            const projX = (n.x - w / 2 + dx) * scale + w / 2;
            const projY = (n.y - h / 2 + dy) * scale + h / 2;
            const pulseScale = 1 + Math.sin(n.pulse) * 0.25;
            const projRadius = Math.max(0.6, n.radius * scale * pulseScale);

            ctx.beginPath();
            ctx.arc(projX, projY, projRadius, 0, Math.PI * 2);
            ctx.fillStyle = n.color + '0.75)';
            ctx.shadowBlur = 10 * scale;
            ctx.shadowColor = n.color + '0.9)';
            ctx.fill();

            // Connect nearest nodes
            for (let j = i + 1; j < nodeCount; j++) {
                const n2 = nodes[j];
                const dist = Math.hypot(n.x - n2.x, n.y - n2.y);
                if (dist < 125) {
                    const scale2 = fov / (fov + n2.z);
                    const projX2 = (n2.x - w / 2 + dx) * scale2 + w / 2;
                    const projY2 = (n2.y - h / 2 + dy) * scale2 + h / 2;

                    const alpha = (1 - dist / 125) * 0.28;
                    ctx.beginPath();
                    ctx.moveTo(projX, projY);
                    ctx.lineTo(projX2, projY2);
                    ctx.strokeStyle = `rgba(226, 232, 240, ${alpha * 0.75})`;
                    ctx.lineWidth = 0.8 * scale;
                    ctx.stroke();
                }
            }
        }

        requestAnimationFrame(render);
    }

    render();
})();

// ================= 2. DQS APPLICATION CORE =================
const DQS = {
    activeTab: 'quests',
    cachedQuests: [],
    presets: [],
    currentUser: null,
    autoFarmRunning: false,
    questFilter: 'all',

    async init() {
        this.runStartupSplash();
        this.injectStaticIcons();
        this.renderBadges();
        this.setupWindowControls();
        this.setupNavigation();
        this.setupQuestFilters();
        this.setupProfileDrawer();
        this.setupSimulator();
        this.setupSimulatorSearch();
        this.setupConsoleTab();
        this.setupVideoModal();
        this.setupLiveSyncHUD();
        this.setupLicenseModal();
        this.setupTutorialModal();
        this.setupChangelogAndUpdateModals();
        this.setupOrbsLinks();
        this.initNotificationBadges();

        // Load data from bridge
        await this.loadCurrentUser();
        await this.loadPresets();
        await this.refreshQuests();

        // Simulator status polling (1-second heartbeat live sync)
        this.pollSimStatus();
        setInterval(() => this.pollSimStatus(), 1000);

        // Auto-refresh quests periodically and on window focus (throttled to 30s)
        setInterval(() => this.refreshQuests(true), 45000);
        let lastFocusRefresh = Date.now();
        window.addEventListener('focus', () => {
            const now = Date.now();
            if (now - lastFocusRefresh > 30000) {
                lastFocusRefresh = now;
                this.refreshQuests(true);
            }
        });

        // Background auto-update check on startup (after 2.5s)
        setTimeout(() => this.checkForUpdates(false), 2500);
    },

    // --- V6.3.0 Atmospheric Cinema Sound Engine ---
    _audioCtx: null,
    _ambientAudio: null,
    _synthNodes: [],
    _masterFilter: null,
    _ambientGain: null,

    getAudioCtx() {
        if (!this._audioCtx) {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (AudioCtx) {
                this._audioCtx = new AudioCtx();
            }
        }
        if (this._audioCtx && this._audioCtx.state === 'suspended') {
            this._audioCtx.resume();
        }
        return this._audioCtx;
    },

    playStartupAmbient(duration = 8) {
        // High-End Procedural Cinema Cyber Soundscape (Zero External Pop/Cutoff)
        try {
            const ctx = this.getAudioCtx();
            if (!ctx) return;
            const now = ctx.currentTime;

            // Stop any lingering previous synth nodes
            if (this._synthNodes && this._synthNodes.length > 0) {
                this._synthNodes.forEach(n => {
                    try { n.stop(); } catch (e) {}
                    try { n.disconnect(); } catch (e) {}
                });
                this._synthNodes = [];
            }

            // Master Filter for warm, organic cinematic power-up
            const filter = ctx.createBiquadFilter();
            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(220, now);
            filter.frequency.exponentialRampToValueAtTime(2400, now + duration * 0.9);
            filter.Q.setValueAtTime(1.8, now);
            filter.connect(ctx.destination);
            this._masterFilter = filter;

            const masterGain = ctx.createGain();
            masterGain.gain.setValueAtTime(0.0001, now);
            masterGain.gain.exponentialRampToValueAtTime(0.16, now + 1.2);
            masterGain.gain.setValueAtTime(0.16, now + Math.max(0.5, duration - 1.2));
            masterGain.connect(filter);
            this._ambientGain = masterGain;

            // 1. Warm Sub-Bass Reactor Foundation (36Hz -> 48Hz)
            const sub = ctx.createOscillator();
            sub.type = 'sine';
            sub.frequency.setValueAtTime(36.0, now);
            sub.frequency.linearRampToValueAtTime(48.0, now + duration);
            const subGain = ctx.createGain();
            subGain.gain.value = 0.5;
            sub.connect(subGain);
            subGain.connect(masterGain);
            sub.start(now);
            sub.stop(now + duration + 3.0);
            this._synthNodes.push(sub);

            // 2. Cyber Ethereal Harmonizer Pad Chords (D2, A2, D3, F#3, A3, C#4)
            const chordFreqs = [73.42, 110.00, 146.83, 185.00, 220.00, 277.18];
            chordFreqs.forEach((baseF, idx) => {
                [-0.035, 0.035].forEach(detuneRatio => {
                    const osc = ctx.createOscillator();
                    osc.type = (idx % 2 === 0) ? 'sine' : 'triangle';
                    const targetF = baseF * (1 + detuneRatio);
                    osc.frequency.setValueAtTime(targetF, now);
                    osc.frequency.linearRampToValueAtTime(targetF * 1.015, now + duration);

                    const g = ctx.createGain();
                    g.gain.value = (0.055 / (idx + 1));
                    osc.connect(g);
                    g.connect(masterGain);

                    osc.start(now);
                    osc.stop(now + duration + 3.0);
                    this._synthNodes.push(osc);
                });
            });

            // 3. Shimmer Spatial LFO modulation
            const lfo = ctx.createOscillator();
            lfo.type = 'sine';
            lfo.frequency.value = 0.45;
            const lfoGain = ctx.createGain();
            lfoGain.gain.value = 160;
            lfo.connect(lfoGain);
            lfoGain.connect(filter.frequency);
            lfo.start(now);
            lfo.stop(now + duration + 3.0);
            this._synthNodes.push(lfo);

        } catch (err) {
            console.warn('Audio ambient synthesis notice:', err);
        }
    },

    playTransitionCrescendo() {
        const ctx = this.getAudioCtx();
        if (!ctx) return;
        const now = ctx.currentTime;

        // Smooth crossfade out of existing ambient drone over 1.6s without pop or abrupt stop
        if (this._ambientGain) {
            try {
                this._ambientGain.gain.setValueAtTime(this._ambientGain.gain.value, now);
                this._ambientGain.gain.exponentialRampToValueAtTime(0.0001, now + 1.6);
            } catch (e) {}
        }
        if (this._masterFilter) {
            try {
                this._masterFilter.frequency.setValueAtTime(this._masterFilter.frequency.value, now);
                this._masterFilter.frequency.exponentialRampToValueAtTime(150, now + 1.6);
            } catch (e) {}
        }

        // Seamless glide & celestial chime resolution
        try {
            // 1. Aerodynamic Glide Swoosh (160Hz -> 42Hz)
            const glideOsc = ctx.createOscillator();
            glideOsc.type = 'sine';
            glideOsc.frequency.setValueAtTime(160, now);
            glideOsc.frequency.exponentialRampToValueAtTime(42, now + 0.85);

            const glideGain = ctx.createGain();
            glideGain.gain.setValueAtTime(0.001, now);
            glideGain.gain.exponentialRampToValueAtTime(0.32, now + 0.12);
            glideGain.gain.exponentialRampToValueAtTime(0.0001, now + 1.0);

            glideOsc.connect(glideGain);
            glideGain.connect(ctx.destination);
            glideOsc.start(now);
            glideOsc.stop(now + 1.1);

            // 2. Pristine C-Major-9 Resolution Chime (C5, E5, G5, B5, D6, G6)
            const chimeNotes = [523.25, 659.25, 783.99, 987.77, 1174.66, 1567.98];
            chimeNotes.forEach((f, idx) => {
                const noteTime = now + idx * 0.04;
                const chime = ctx.createOscillator();
                chime.type = 'sine';
                chime.frequency.setValueAtTime(f, noteTime);

                const cGain = ctx.createGain();
                cGain.gain.setValueAtTime(0.0001, noteTime);
                cGain.gain.exponentialRampToValueAtTime(0.13 / (idx + 1), noteTime + 0.04);
                cGain.gain.exponentialRampToValueAtTime(0.0001, noteTime + 2.0);

                chime.connect(cGain);
                cGain.connect(ctx.destination);
                chime.start(noteTime);
                chime.stop(noteTime + 2.1);
            });
        } catch (e) {}
    },

    // --- Startup Splash Screen Animation (Atmospheric Cinema Transition) ---
    runStartupSplash() {
        const splash = document.getElementById('dqs-startup-splash');
        const bar = document.getElementById('splash-progress-bar');
        const status = document.getElementById('splash-status-text');
        const subTelemetry = document.getElementById('splash-sub-telemetry');
        const root = document.getElementById('app-root');
        if (!splash || !bar || !status) return;

        // Duration between 4200ms and 9500ms
        const totalDuration = Math.floor(Math.random() * (9500 - 4200 + 1)) + 4200;
        let elapsed = 0;
        const intervalMs = 50;

        // Play cinema-grade atmospheric ambient
        this.playStartupAmbient(totalDuration / 1000);

        const stages = [
            { pct: 15, title: 'INITIALISIERE 4D TESSERACT-SYSTEME...', sub: '[4D HYPERCUBE ACTIVE] • [RUST NATIVE ENGINE]' },
            { pct: 34, title: 'LADE DISCORD QUEST ENGINE (V6.3.0)...', sub: '[KERNEL HOOK] • [RPC STEALTH CLOAK ENGAGED]' },
            { pct: 54, title: 'SYNCHRONISIERE 24.323 DETECTABLE GAMES...', sub: '[CACHE SYNC] • [STEAM & DISCORD ASSETS READY]' },
            { pct: 72, title: 'KALIBRIERUNG DISCORD HEARTBEATS & RPC...', sub: '[IPC HANDSHAKE] • [LATENCY: 0.12ms]' },
            { pct: 88, title: 'VERIFIZIERE TOKEN-SCHUTZ & INTEGRITÄT...', sub: '[SECURITY] • [ZERO-LEAK RUNTIME VERIFIED]' },
            { pct: 98, title: 'FINALE ATMOSPHÄRISCHE HARMONIE...', sub: '[CROSSFADE READY] • [DISPENSING TO VIEWPORT]' },
            { pct: 100, title: 'WILLKOMMEN BEI DQS V6.3.0 - READY...', sub: '[ULTIMATE EDITION ACTIVE]' }
        ];

        const timer = setInterval(() => {
            elapsed += intervalMs;
            const progressRatio = Math.min(1.0, elapsed / totalDuration);
            const easedRatio = 1 - Math.pow(1 - progressRatio, 3);
            const currentPct = Math.min(100, Math.round(easedRatio * 100));

            if (bar) bar.style.width = `${currentPct}%`;

            const currentStage = stages.find(s => currentPct <= s.pct) || stages[stages.length - 1];
            if (status) status.innerText = currentStage.title;
            if (subTelemetry) subTelemetry.innerText = currentStage.sub;

            if (elapsed >= totalDuration) {
                clearInterval(timer);
                if (bar) bar.style.width = '100%';
                if (status) status.innerText = 'WILLKOMMEN BEI DQS V6.3.0 - POPPING UP...';
                if (subTelemetry) subTelemetry.innerText = '[ULTIMATE EDITION ACTIVE]';

                setTimeout(() => {
                    // Trigger harmonic cinema crescendo with smooth crossfade
                    this.playTransitionCrescendo();
                    if (splash) splash.classList.add('splash-pop-exit');
                    if (root) root.classList.add('app-pop-enter');
                    setTimeout(() => {
                        if (splash && splash.parentNode) {
                            splash.parentNode.removeChild(splash);
                        }
                    }, 850);
                }, 120);
            }
        }, intervalMs);
    },

    // --- Notification Ping Badges (First-Launch & Changelogs) ---
    initNotificationBadges() {
        const brandPing = document.getElementById('first-launch-ping-dot');
        const brandTrigger = document.getElementById('app-logo-trigger');
        const profilePing = document.getElementById('profile-changelog-ping-dot');
        const btnChangelogPing = document.getElementById('btn-changelog-ping-dot');
        const currentVersion = '6.3.0';

        // 1. First-Launch Yellow Ping Dot on Top-Left App Icon (ALWAYS after install / first launch)
        const hasSeenFirstLaunch = localStorage.getItem('dqs_first_launch_seen');
        if (!hasSeenFirstLaunch) {
            if (brandPing) brandPing.classList.remove('hidden');
        } else {
            if (brandPing) brandPing.classList.add('hidden');
        }

        if (brandTrigger) {
            brandTrigger.addEventListener('click', () => {
                localStorage.setItem('dqs_first_launch_seen', 'true');
                if (brandPing) {
                    brandPing.style.transition = 'opacity 0.3s ease';
                    brandPing.style.opacity = '0';
                    setTimeout(() => brandPing.classList.add('hidden'), 300);
                }
            });
        }

        // 2. Unread Changelog Yellow Ping Dot (Top-Right Profile Corner + Changelog Button)
        const lastReadVer = localStorage.getItem('dqs_read_changelog_ver');
        if (lastReadVer !== currentVersion) {
            if (profilePing) profilePing.classList.remove('hidden');
            if (btnChangelogPing) btnChangelogPing.classList.remove('hidden');
        } else {
            if (profilePing) profilePing.classList.add('hidden');
            if (btnChangelogPing) btnChangelogPing.classList.add('hidden');
        }
    },

    markChangelogAsRead() {
        const profilePing = document.getElementById('profile-changelog-ping-dot');
        const btnChangelogPing = document.getElementById('btn-changelog-ping-dot');
        localStorage.setItem('dqs_read_changelog_ver', '6.3.0');

        [profilePing, btnChangelogPing].forEach(el => {
            if (el) {
                el.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
                el.style.opacity = '0';
                el.style.transform = 'scale(0.4)';
                setTimeout(() => el.classList.add('hidden'), 350);
            }
        });
    },

    // --- Inject Vector SVGs (100% Emoji-free) ---
    injectStaticIcons() {
        const I = window.DQS_ICONS || {};
        const setHtml = (id, html) => {
            const el = document.getElementById(id);
            if (el) el.innerHTML = html;
        };

        setHtml('ico-shield', I.shield);
        setHtml('ico-nav-quests', I.quest);
        setHtml('ico-nav-videos', I.video);
        setHtml('ico-nav-simulator', I.gamepad);
        setHtml('ico-nav-console', I.console);
        setHtml('ico-nav-logs', I.logs);

        setHtml('ico-hdr-gear', I.gear);
        setHtml('btn-win-min', I.min);
        setHtml('btn-win-close', I.close);

        setHtml('ico-hdr-quests', I.quest);
        setHtml('ico-disclaimer-shield', I.shield);
        setHtml('ico-btn-refresh', I.refresh);
        setHtml('ico-btn-enroll', I.quest);
        setHtml('ico-btn-autofarm', I.autofarm);
        setHtml('ico-hero-autofarm', I.autofarm);
        setHtml('ico-btn-orbs-farm', I.autofarm);
        setHtml('ico-hero-play', I.play);

        setHtml('ico-hdr-videos', I.video);
        setHtml('ico-hdr-sim', I.gamepad);
        setHtml('ico-btn-start-sim', I.play);
        setHtml('ico-sim-monitor', I.monitor || I.gamepad);

        setHtml('ico-hdr-console', I.console);
        setHtml('ico-console-warn', I.shield);
        setHtml('ico-btn-copy', I.copy);

        setHtml('ico-hdr-logs', I.logs);
        setHtml('ico-btn-clear', I.clear);

        setHtml('btn-close-popout', I.close);
        setHtml('act-gamepad-icon', I.gamepad);
        setHtml('ico-btn-user-switch', I.users);
        setHtml('ico-btn-copy-id', I.copy);
        setHtml('ico-btn-github', I.github);
        setHtml('ico-btn-changelog', I.changelog || I.logs);
        setHtml('ico-btn-update', I.update || I.refresh);
        setHtml('btn-close-account-modal', I.close);
        setHtml('btn-close-changelog-modal', I.close);
        setHtml('btn-close-update-modal', I.close);
        setHtml('ico-modal-changelog', I.changelog || I.logs);
        setHtml('ico-changelog-gh', I.github);
        setHtml('ico-modal-update', I.update || I.refresh);
        setHtml('ico-asset-box', I.box || I.quest);
        setHtml('ico-notes-doc', I.changelog || I.logs);
        setHtml('ico-btn-update-gh', I.github);
        setHtml('ico-recheck-spin', I.refresh);
        setHtml('ico-notes-spinner', I.gear);

        setHtml('ico-modal-video', I.video);
        setHtml('btn-close-video-modal', I.close);
        setHtml('ico-modal-express', I.autofarm);
        setHtml('ico-modal-sim', I.play || I.gamepad);

        // License & Security Modal
        setHtml('ico-license-warn-de', I.shield);
        setHtml('ico-license-info-de', I.quest);
        setHtml('ico-gh-logo-de', I.github);
        setHtml('btn-close-license-modal', I.close);
        setHtml('ico-license-warn-en', I.shield);
        setHtml('ico-license-info-en', I.quest);
        setHtml('ico-gh-logo-en', I.github);

        // Tutorial Modal & Header
        setHtml('ico-tutorial-hdr', I.tutorial || I.help);
        setHtml('ico-tutorial-modal-title', I.tutorial || I.help);
        setHtml('btn-close-tutorial-modal', I.close);
        setHtml('ico-tut-tab-rocket', I.sparkles || I.play);
        setHtml('ico-tut-tab-clock', I.shield || I.refresh);
        setHtml('ico-tut-tab-tools', I.gear || I.console);
        setHtml('ico-tut-tab-dev', I.friend || I.users);
        setHtml('ico-fact-server', I.shield);
        setHtml('ico-fact-instant', I.sparkles || I.play);
        setHtml('ico-fact-benefit', I.quest);
        setHtml('ico-btn-friend-req', I.friend || I.users);
        setHtml('ico-tut-gh', I.github);
        setHtml('ico-tut-bug', I.alert || I.shield);
    },

    // --- Render Discord Badges (Dynamic with Live CDN Support) ---
    renderBadges(badgesList) {
        const container = document.getElementById('badges-container');
        if (!container) return;
        container.innerHTML = '';

        const badges = (badgesList && badgesList.length > 0) ? badgesList : (this.currentUser?.badges || []);
        if (!badges || badges.length === 0) {
            container.style.display = 'none';
            return;
        }

        container.style.display = 'inline-flex';
        badges.forEach(b => {
            const img = document.createElement('img');
            img.className = 'badge-icon';
            img.title = b.description || b.id || 'Discord Badge';
            img.alt = b.id || 'badge';
            
            const b64 = window.DQS_EMBEDDED_ASSETS?.[b.id];
            img.src = b.icon_url || b64 || `assets/badges/${b.id}.png`;
            img.onerror = () => {
                if (b64) img.src = b64;
                else img.style.display = 'none';
            };
            container.appendChild(img);
        });
    },

    // --- Window Controls ---
    setupWindowControls() {
        const btnMin = document.getElementById('btn-win-min');
        if (btnMin) {
            btnMin.addEventListener('click', () => {
                window.pywebview?.api?.minimize_window();
            });
        }
        const btnClose = document.getElementById('btn-win-close');
        if (btnClose) {
            btnClose.addEventListener('click', () => {
                window.pywebview?.api?.close_window();
            });
        }
    },

    // --- Navigation Tabs ---
    setupNavigation() {
        const tabs = document.querySelectorAll('.nav-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.getAttribute('data-tab');
                this.switchTab(target);
            });
        });
    },

    switchTab(tabId) {
        if (this.activeTab === tabId && document.getElementById(`tab-${tabId}`)?.classList.contains('active')) {
            return;
        }

        const oldTabId = this.activeTab;
        this.activeTab = tabId;

        // Immediately update navbar buttons
        document.querySelectorAll('.nav-tab').forEach(t => {
            if (t.getAttribute('data-tab') === tabId) {
                t.classList.add('active');
            } else {
                t.classList.remove('active');
            }
        });

        const currentTabEl = document.getElementById(`tab-${oldTabId}`);
        const nextTabEl = document.getElementById(`tab-${tabId}`);

        if (currentTabEl && currentTabEl !== nextTabEl && currentTabEl.classList.contains('active')) {
            // Trigger exit plopp animation
            currentTabEl.classList.remove('tab-plop-enter');
            currentTabEl.classList.add('tab-plop-exit');

            setTimeout(() => {
                currentTabEl.classList.remove('active', 'tab-plop-exit');

                if (nextTabEl) {
                    nextTabEl.classList.remove('tab-plop-exit');
                    nextTabEl.classList.add('active', 'tab-plop-enter');

                    setTimeout(() => {
                        nextTabEl.classList.remove('tab-plop-enter');
                    }, 400);
                }
            }, 140);
        } else {
            // Immediate activation (e.g. startup / direct call)
            document.querySelectorAll('.tab-view').forEach(v => {
                if (v.id === `tab-${tabId}`) {
                    v.classList.remove('tab-plop-exit');
                    v.classList.add('active', 'tab-plop-enter');
                    setTimeout(() => v.classList.remove('tab-plop-enter'), 400);
                } else {
                    v.classList.remove('active', 'tab-plop-enter', 'tab-plop-exit');
                }
            });
        }
    },

    // --- Quests Filter Controls (All / Open / Completed) ---
    setupQuestFilters() {
        const pills = document.querySelectorAll('.filter-pill');
        pills.forEach(pill => {
            pill.addEventListener('click', () => {
                const filter = pill.getAttribute('data-filter');
                if (this.questFilter === filter) return;
                this.setQuestFilter(filter);
            });
        });
    },

    setQuestFilter(filterName) {
        this.questFilter = filterName;
        document.querySelectorAll('.filter-pill').forEach(pill => {
            if (pill.getAttribute('data-filter') === filterName) {
                pill.classList.add('active');
            } else {
                pill.classList.remove('active');
            }
        });
        this.renderQuestsList();
    },

    // --- 3D Profile Popout ---
    setupProfileDrawer() {
        const pill = document.getElementById('header-user-pill');
        const popout = document.getElementById('discord-profile-popout');
        const backdrop = document.getElementById('popout-backdrop');
        const closeBtn = document.getElementById('btn-close-popout');

        const openPopout = () => {
            this.pollSimStatus();
            this.loadCurrentUser();
            popout.classList.remove('hidden');
            backdrop.classList.remove('hidden');
        };

        const closePopout = () => {
            popout.classList.add('hidden');
            backdrop.classList.add('hidden');
        };

        pill.addEventListener('click', (e) => {
            e.stopPropagation();
            if (popout.classList.contains('hidden')) {
                openPopout();
            } else {
                closePopout();
            }
        });

        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closePopout();
        });

        backdrop.addEventListener('click', () => {
            closePopout();
        });

        // Discord profile card is strictly static (no tilt / wobble)

        // Copy ID
        const btnCopyId = document.getElementById('btn-copy-id');
        btnCopyId.addEventListener('click', async () => {
            const uid = this.currentUser ? this.currentUser.id : '405441217766359051';
            await window.pywebview?.api?.copy_to_clipboard(uid);
            btnCopyId.innerHTML = `${window.DQS_ICONS.check} ID KOPIERT!`;
            setTimeout(() => {
                btnCopyId.innerHTML = `${window.DQS_ICONS.copy} NUTZER-ID KOPIEREN`;
            }, 2000);
        });

        // GitHub Link
        document.getElementById('btn-open-github').addEventListener('click', () => {
            window.pywebview?.api?.open_url('https://github.com/TentixTV/Discord-Quest-Spoofer');
        });

        const linkTentix = document.getElementById('link-tentix-space');
        if (linkTentix) {
            linkTentix.addEventListener('click', (e) => {
                e.preventDefault();
                window.pywebview?.api?.open_url('https://tentix.space');
            });
        }

        // Account Switcher Modal
        document.getElementById('btn-switch-account')?.addEventListener('click', () => {
            this.openAccountModal();
        });
        document.getElementById('btn-close-account-modal')?.addEventListener('click', () => {
            document.getElementById('account-modal')?.classList.add('hidden');
        });

        // Changelog Button
        document.getElementById('btn-open-changelog')?.addEventListener('click', () => {
            this.openChangelogModal();
        });

        // Manual Update Checker Button
        document.getElementById('btn-manual-update')?.addEventListener('click', () => {
            this.checkForUpdates(true);
        });
    },

    // --- 3D Physics Tilt Helper ---
    attach3DTilt(el) {
        if (!el) return;
        el.addEventListener('mousemove', (e) => {
            const rect = el.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -6;
            const rotateY = ((x - centerX) / centerX) * 6;

            el.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(8px)`;
            el.style.setProperty('--glare-x', `${(x / rect.width) * 100}%`);
            el.style.setProperty('--glare-y', `${(y / rect.height) * 100}%`);
        });

        el.addEventListener('mouseleave', () => {
            el.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
        });
    },

    async loadCurrentUser() {
        if (!window.pywebview?.api) return;
        const user = await window.pywebview.api.get_current_user();
        if (user) {
            this.syncUserProfile(user);
        }
    },

    syncUserProfile(user) {
        if (!user) return;
        this.currentUser = user;
        const displayName = user.global_name || user.username || 'TΞП†1Ж ツ';

        // 1. Header & Popout Names
        const hdrName = document.getElementById('hdr-username');
        if (hdrName) hdrName.innerText = displayName;
        const popName = document.getElementById('popout-name');
        if (popName) popName.innerText = displayName;

        // 1.5 Header User Pill Custom Status / Bio / Presence
        const hdrStatus = document.getElementById('hdr-user-status');
        if (hdrStatus) {
            const cs = user.custom_status;
            if (cs && (cs.text || cs.emoji_name || cs.emoji_url)) {
                let sHtml = '';
                if (cs.emoji_url) {
                    sHtml += `<img src="${cs.emoji_url}" class="mini-status-emoji" alt="">`;
                } else if (cs.emoji_name && !cs.emoji_id) {
                    sHtml += `<span class="mini-status-emoji-txt">${cs.emoji_name}</span>`;
                }
                sHtml += `<span class="mini-status-text">${cs.text || cs.emoji_name || ''}</span>`;
                hdrStatus.innerHTML = sHtml;
                hdrStatus.title = cs.text || '';
            } else if (user.bio && user.bio.trim()) {
                const firstLine = user.bio.trim().split('\n')[0].trim();
                hdrStatus.innerHTML = `<span class="mini-status-text">${firstLine}</span>`;
                hdrStatus.title = user.bio.trim();
            } else {
                const st = (user.status || 'online').toLowerCase();
                const stMap = {
                    'online': 'ONLINE',
                    'dnd': 'BITTE NICHT STÖREN',
                    'idle': 'ABWESEND',
                    'invisible': 'UNSICHTBAR',
                    'offline': 'OFFLINE'
                };
                hdrStatus.innerHTML = `<span class="mini-status-text">${stMap[st] || 'BEREIT'}</span>`;
                hdrStatus.title = `Status: ${stMap[st] || st}`;
            }
        }

        // Header Avatar status dot
        const hdrDot = document.getElementById('hdr-status-indicator');
        const hdrIcon = document.getElementById('hdr-status-icon');
        if (hdrDot) {
            const st = (user.status || 'online').toLowerCase();
            hdrDot.className = `status-indicator ${st}`;
            if (hdrIcon) {
                if (st === 'dnd') hdrIcon.className = 'dnd-minus';
                else if (st === 'idle') hdrIcon.className = 'idle-moon';
                else hdrIcon.className = '';
            }
        }

        // 2. Handle & Pronouns
        const popHandle = document.getElementById('popout-handle');
        if (popHandle) {
            if (user.pronouns && user.pronouns.trim()) {
                popHandle.innerText = `${user.username || 'discord'} • ${user.pronouns.trim()}`;
            } else {
                popHandle.innerText = user.username ? `@${user.username}` : 'discord';
            }
        }

        // 3. Avatar (Header & Popout)
        const avUrl = user.avatar_url || (user.avatar && user.id ? `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.${user.avatar.startsWith('a_') ? 'gif' : 'png'}?size=256` : 'assets/tentix_avatar.gif');
        const hdrAv = document.getElementById('hdr-avatar');
        if (hdrAv) hdrAv.src = avUrl;
        const popAv = document.getElementById('pop-avatar');
        if (popAv) popAv.src = avUrl;

        // 4. Banner (Live Image, Accent Hex Gradient, or Mesh Fallback)
        const bannerWrap = document.getElementById('pop-banner-wrap');
        const bannerImg = document.getElementById('pop-banner');
        if (bannerWrap && bannerImg) {
            if (user.banner_url) {
                bannerImg.style.display = 'block';
                bannerImg.src = user.banner_url;
                bannerWrap.style.background = 'transparent';
            } else if (user.accent_hex) {
                bannerImg.style.display = 'none';
                bannerWrap.style.background = `linear-gradient(135deg, ${user.accent_hex} 0%, rgba(15, 17, 26, 0.95) 100%)`;
            } else {
                bannerImg.style.display = 'none';
                bannerWrap.style.background = 'linear-gradient(135deg, #1e202e 0%, #0d0e15 100%)';
            }
        }

        // 5. Presence / Online Status on Avatar Badge
        const statusBadge = document.getElementById('popout-status-badge');
        if (statusBadge) {
            const st = (user.status || 'online').toLowerCase();
            statusBadge.className = `popout-status-badge ${st}`;
        }

        // 6. Custom Status Speech Bubble
        const statusBubble = document.getElementById('popout-status-bubble');
        const bubbleEmojiWrap = document.getElementById('bubble-emoji-container');
        const bubbleText = document.getElementById('bubble-text');
        const cs = user.custom_status;
        if (statusBubble && bubbleText) {
            if (cs && (cs.text || cs.emoji_name || cs.emoji_id || cs.emoji_url)) {
                statusBubble.style.display = 'flex';
                if (bubbleEmojiWrap) {
                    if (cs.emoji_url) {
                        bubbleEmojiWrap.innerHTML = `<img src="${cs.emoji_url}" class="bubble-custom-emoji" alt="${cs.emoji_name || ''}">`;
                    } else if (cs.emoji_name && !cs.emoji_id) {
                        bubbleEmojiWrap.innerHTML = `<span style="font-size: 13px; margin-right: 4px;">${cs.emoji_name}</span>`;
                    } else {
                        bubbleEmojiWrap.innerHTML = '';
                    }
                }
                bubbleText.innerText = cs.text || '';
            } else {
                statusBubble.style.display = 'none';
            }
        }

        // 7. Badges
        this.renderBadges(user.badges);

        // 8. Bio ("ÜBER MICH")
        const bioBox = document.getElementById('popout-bio');
        const bioSection = document.getElementById('popout-bio-section');
        if (bioBox) {
            if (user.bio && user.bio.trim()) {
                if (bioSection) bioSection.style.display = 'block';
                const escapeHtml = (str) => {
                    const div = document.createElement('div');
                    div.textContent = str;
                    return div.innerHTML;
                };
                const escaped = escapeHtml(user.bio.trim());
                // Auto-link URLs cleanly and format line breaks
                let linked = escaped.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" class="bio-link" target="_blank">$1</a>');
                linked = linked.replace(/\n/g, '<br>');
                bioBox.innerHTML = linked;
                bioBox.querySelectorAll('.bio-link').forEach(link => {
                    link.addEventListener('click', (e) => {
                        e.preventDefault();
                        const url = link.getAttribute('href');
                        window.pywebview?.api?.open_url(url);
                    });
                });
            } else {
                if (bioSection) bioSection.style.display = 'block';
                bioBox.innerHTML = '<p class="bio-empty-text">Keine Biografie hinterlegt.</p>';
            }
        }
    },

    async openAccountModal() {
        const modal = document.getElementById('account-modal');
        const list = document.getElementById('modal-accounts-list');
        list.innerHTML = '<div style="padding:16px;text-align:center;color:#94a3b8;"><span style="display:inline-block;margin-right:8px;animation:spin 1s linear infinite;">⚙</span> Lade Accounts...</div>';
        modal.classList.remove('hidden');

        const accs = await window.pywebview?.api?.get_accounts();
        list.innerHTML = '';

        if (!accs || accs.length === 0) {
            list.innerHTML = '<div style="padding:16px;text-align:center;color:#8e92a4;">Keine aktiven Accounts lokal gefunden.<br><span style="font-size:11px;opacity:0.8;">Füge oben manuell einen Token ein.</span></div>';
            return;
        }

        accs.forEach(acc => {
            const row = document.createElement('div');
            const isCurrent = acc.is_current || (this.currentUser && this.currentUser.id === acc.id);
            row.className = `account-row ${isCurrent ? 'active-account' : ''}`;
            const name = acc.global_name || acc.username;
            const handle = acc.username;
            const avUrl = acc.avatar_url || (acc.avatar && acc.id ? `https://cdn.discordapp.com/avatars/${acc.id}/${acc.avatar}.${acc.avatar.startsWith('a_') ? 'gif' : 'png'}?size=96` : 'assets/tentix_avatar.gif');
            
            row.innerHTML = `
                <div class="account-row-left">
                    <img src="${avUrl}" class="account-row-avatar" alt="Avatar" onerror="this.src='assets/tentix_avatar.gif'">
                    <div class="account-row-info">
                        <span class="account-row-name">${name}</span>
                        <span class="account-row-handle">@${handle}</span>
                    </div>
                </div>
                <div class="account-row-right">
                    ${isCurrent 
                        ? '<span class="account-status-active-tag">AKTIV</span>' 
                        : '<button class="btn btn-blurple btn-small btn-account-select">AUSWÄHLEN</button>'}
                </div>
            `;

            const btn = row.querySelector('.btn-account-select');
            if (btn) {
                btn.addEventListener('click', async () => {
                    btn.disabled = true;
                    btn.innerText = 'LÄDT...';
                    const res = await window.pywebview.api.switch_account(acc.token);
                    if (res.success) {
                        modal.classList.add('hidden');
                        if (res.user) this.syncUserProfile(res.user);
                        else await this.loadCurrentUser();
                        await this.refreshQuests();
                    } else {
                        btn.disabled = false;
                        btn.innerText = 'AUSWÄHLEN';
                        alert('Fehler beim Account-Wechsel: ' + (res.error || 'Unbekannt'));
                    }
                });
            }

            list.appendChild(row);
        });

        document.getElementById('btn-load-custom-token').onclick = async () => {
            const tok = document.getElementById('input-custom-token').value.trim();
            if (tok) {
                const btn = document.getElementById('btn-load-custom-token');
                btn.disabled = true;
                btn.innerText = 'LÄDT...';
                const res = await window.pywebview.api.switch_account(tok);
                btn.disabled = false;
                btn.innerText = 'LADEN';
                if (res.success) {
                    modal.classList.add('hidden');
                    document.getElementById('input-custom-token').value = '';
                    if (res.user) this.syncUserProfile(res.user);
                    else await this.loadCurrentUser();
                    await this.refreshQuests();
                } else {
                    alert('Fehler: ' + (res.error || 'Ungültiger Token'));
                }
            }
        };
    },

    // --- Quests & Cards Rendering ---
    async refreshQuests(silent = false) {
        const I = window.DQS_ICONS;
        const container = document.getElementById('quests-list');

        const hasCards = this.cachedQuests && this.cachedQuests.length > 0;
        if (!silent && !hasCards) {
            // Futuristic Cyber Loading Screen with Skeleton Cards (only on initial empty load)
            container.innerHTML = `
                <div class="api-loading-card card-3d">
                    <div class="loading-cyber-core">
                        <div class="loading-ring outer"></div>
                        <div class="loading-ring inner"></div>
                        <span class="loading-center-icon">${I.quest}</span>
                    </div>
                    <div class="loading-text-content">
                        <h3 class="loading-headline">SYNCHRONISIERE MIT DISCORD API</h3>
                        <p class="loading-subtitle">Lade aktive Quests, Belohnungs-Orbs und Heartbeat-Verbindungen...</p>
                        <div class="loading-bar-track">
                            <div class="loading-bar-sweep"></div>
                        </div>
                    </div>
                </div>
                <div class="skeleton-card">
                    <div class="skeleton-tile"></div>
                    <div class="skeleton-info">
                        <div class="skeleton-bar title"></div>
                        <div class="skeleton-bar sub"></div>
                        <div class="skeleton-bar progress"></div>
                    </div>
                </div>
                <div class="skeleton-card">
                    <div class="skeleton-tile"></div>
                    <div class="skeleton-info">
                        <div class="skeleton-bar title"></div>
                        <div class="skeleton-bar sub"></div>
                        <div class="skeleton-bar progress"></div>
                    </div>
                </div>
            `;
        }

        if (!window.pywebview?.api) return;
        const quests = await window.pywebview.api.get_quests();
        if (quests && Array.isArray(quests) && quests.length > 0) {
            this.cachedQuests = quests;
        } else if (!this.cachedQuests || this.cachedQuests.length === 0) {
            this.cachedQuests = quests || [];
        }

        const badge = document.getElementById('quests-badge');
        if (badge) badge.innerText = this.cachedQuests.length;

        // Fetch duration and auto-quest overview
        try {
            const overview = await window.pywebview.api.get_auto_quest_overview();
            this.updateAutoQuestOverviewUI(overview);
        } catch (e) {
            console.error("Failed to load auto quest overview:", e);
        }

        // Update Discord Orbs Balance & Hub
        try {
            await this.updateOrbsUI();
        } catch (e) {
            console.error("Failed to update Orbs UI:", e);
        }

        this.renderQuestsList();
        this.renderVideosTab(this.cachedQuests);
    },

    renderQuestsList() {
        const I = window.DQS_ICONS;
        const container = document.getElementById('quests-list');
        if (!container) return;

        const totalCount = this.cachedQuests.length;
        const openQuests = this.cachedQuests.filter(q => !q.completed && !q.claimed);
        const completedQuests = this.cachedQuests.filter(q => q.completed || q.claimed);

        const openCount = openQuests.length;
        const completedCount = completedQuests.length;

        // Update count badges
        const countAll = document.getElementById('filter-count-all');
        const countOpen = document.getElementById('filter-count-open');
        const countCompleted = document.getElementById('filter-count-completed');
        const summary = document.getElementById('filter-status-summary');

        if (countAll) countAll.innerText = totalCount;
        if (countOpen) countOpen.innerText = openCount;
        if (countCompleted) countCompleted.innerText = completedCount;
        if (summary) {
            summary.innerText = `${totalCount} Quests (${openCount} offen, ${completedCount} erledigt)`;
        }

        let displayList = this.cachedQuests;
        if (this.questFilter === 'open') {
            displayList = openQuests;
        } else if (this.questFilter === 'completed') {
            displayList = completedQuests;
        }

        container.innerHTML = '';

        if (totalCount === 0) {
            container.innerHTML = `
                <div class="quests-empty-state card-3d">
                    <div class="empty-icon-wrap">${I.quest}</div>
                    <h3>KEINE AKTIVEN QUESTS GEFUNDEN</h3>
                    <p>Auf diesem Account sind zurzeit keine Discord-Quests verfügbar.</p>
                </div>
            `;
            return;
        }

        // Celebratory State when user filters for open quests and ALL are finished!
        if (this.questFilter === 'open' && openCount === 0) {
            container.innerHTML = `
                <div class="quests-all-done-card card-3d">
                    <div class="all-done-icon-stage">
                        <div class="all-done-energy-ring"></div>
                        <div class="all-done-energy-ring-pulsing"></div>
                        <div class="all-done-icon-circle">
                            ${I.check}
                        </div>
                    </div>
                    <h3 class="all-done-headline">DU HAST ALLE QUESTS ABGESCHLOSSEN!</h3>
                    <p class="all-done-desc">
                        Alle verfügbaren Discord-Quests auf diesem Account wurden vollständig erfüllt. Deine Discord Orbs und Belohnungen warten in Discord auf dich!
                    </p>
                    <div class="all-done-stats-row">
                        <div class="all-done-stat-pill">
                            <span class="stat-label">ERLEDIGTE QUESTS:</span>
                            <strong class="stat-val emerald">${completedCount} / ${totalCount}</strong>
                        </div>
                        <div class="all-done-stat-pill">
                            <span class="stat-label">STATUS:</span>
                            <strong class="stat-val cyan">100% SYNCHRONISIERT</strong>
                        </div>
                    </div>
                    <div class="all-done-actions">
                        <button class="btn btn-secondary" id="btn-show-completed-quests">
                            ${I.quest} ALLE ABGESCHLOSSENEN QUESTS ANZEIGEN (${completedCount})
                        </button>
                        <button class="btn btn-blurple" id="btn-check-new-quests">
                            ${I.refresh} JETZT AKTUALISIEREN
                        </button>
                    </div>
                </div>
            `;

            document.getElementById('btn-show-completed-quests')?.addEventListener('click', () => {
                this.setQuestFilter('completed');
            });
            document.getElementById('btn-check-new-quests')?.addEventListener('click', () => {
                this.refreshQuests();
            });
            return;
        }

        if (this.questFilter === 'completed' && completedCount === 0) {
            container.innerHTML = `
                <div class="quests-empty-state card-3d">
                    <div class="empty-icon-wrap">${I.quest}</div>
                    <h3>NOCH KEINE ABGESCHLOSSENEN QUESTS</h3>
                    <p>Du hast aktuell noch ${openCount} offene Quests vor dir. Wähle eine Quest oder nutze den Auto-Quest Completer!</p>
                    <button class="btn btn-blurple" id="btn-show-open-from-empty">
                        ${I.quest} OFFENE QUESTS ANZEIGEN (${openCount})
                    </button>
                </div>
            `;
            document.getElementById('btn-show-open-from-empty')?.addEventListener('click', () => {
                this.setQuestFilter('open');
            });
            return;
        }

        displayList.forEach((q, idx) => {
            const card = this.createQuestCard(q);
            card.classList.add('quest-card-plop-in');
            card.style.animationDelay = `${idx * 0.04}s`;
            if (q.completed || q.claimed) {
                card.classList.add('quest-completed');
            }
            container.appendChild(card);
            this.attach3DTilt(card);
        });
    },

    createDynamicGameBadge(gameTitle) {
        const safeTitle = (gameTitle || 'DISCORD QUEST').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        const initials = safeTitle.split(/\s+/).map(w => w[0]).join('').substring(0, 3).toUpperCase() || 'DQS';
        const seed = Array.from(safeTitle).reduce((acc, c) => acc + c.charCodeAt(0), 0);
        const hues = [
            ['#6366f1', '#38bdf8', '#10b981'],
            ['#ec4899', '#8b5cf6', '#3b82f6'],
            ['#f59e0b', '#ef4444', '#8b5cf6'],
            ['#10b981', '#06b6d4', '#3b82f6'],
            ['#8b5cf6', '#d946ef', '#06b6d4']
        ];
        const theme = hues[seed % hues.length];

        const svg = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 338" width="600" height="338">
            <defs>
                <linearGradient id="bgG_${seed}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#0b0f19"/>
                    <stop offset="50%" stop-color="#111827"/>
                    <stop offset="100%" stop-color="#070a12"/>
                </linearGradient>
                <linearGradient id="neonG_${seed}" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="${theme[0]}"/>
                    <stop offset="50%" stop-color="${theme[1]}"/>
                    <stop offset="100%" stop-color="${theme[2]}"/>
                </linearGradient>
                <linearGradient id="cardBorderG_${seed}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="${theme[0]}" stop-opacity="0.85"/>
                    <stop offset="100%" stop-color="${theme[1]}" stop-opacity="0.25"/>
                </linearGradient>
                <pattern id="circuitGrid_${seed}" width="28" height="28" patternUnits="userSpaceOnUse">
                    <path d="M 28 0 L 0 0 0 28" fill="none" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
                    <circle cx="0" cy="0" r="1.5" fill="${theme[0]}" fill-opacity="0.25"/>
                </pattern>
                <filter id="glowF_${seed}" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="8" result="blur"/>
                    <feComposite in="SourceGraphic" in2="blur" operator="over"/>
                </filter>
            </defs>
            <rect width="600" height="338" fill="url(#bgG_${seed})" rx="16"/>
            <rect width="600" height="338" fill="url(#circuitGrid_${seed})" rx="16"/>
            <rect x="1.5" y="1.5" width="597" height="335" fill="none" stroke="url(#cardBorderG_${seed})" stroke-width="3" rx="15"/>

            <!-- Ambient Glow Spheres -->
            <circle cx="120" cy="110" r="90" fill="${theme[0]}" fill-opacity="0.2" filter="url(#glowF_${seed})"/>
            <circle cx="480" cy="220" r="110" fill="${theme[1]}" fill-opacity="0.16" filter="url(#glowF_${seed})"/>

            <!-- Hexagonal Gaming Badge Embellishment -->
            <polygon points="300,75 355,107 355,170 300,202 245,170 245,107" fill="#0f172a" stroke="url(#neonG_${seed})" stroke-width="2.5" filter="url(#glowF_${seed})"/>
            <text x="300" y="148" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="900" font-size="28" text-anchor="middle" letter-spacing="2">${initials}</text>

            <!-- Gamepad Graphic silhouette below initials -->
            <g transform="translate(285, 172) scale(1.2)" fill="none" stroke="${theme[1]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <rect x="0" y="2" width="24" height="13" rx="3"/>
                <line x1="4" y1="8" x2="8" y2="8"/>
                <line x1="6" y1="6" x2="6" y2="10"/>
                <circle cx="16" cy="7" r="0.75" fill="${theme[1]}"/>
                <circle cx="19" cy="9" r="0.75" fill="${theme[1]}"/>
            </g>

            <!-- Title and Subtitle -->
            <text x="300" y="252" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="800" font-size="21" text-anchor="middle" letter-spacing="0.5">${safeTitle.length > 30 ? safeTitle.substring(0, 28) + '...' : safeTitle}</text>
            <rect x="180" y="272" width="240" height="24" rx="12" fill="rgba(16,185,129,0.14)" stroke="rgba(16,185,129,0.4)" stroke-width="1"/>
            <text x="300" y="288" fill="#34d399" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="10.5" text-anchor="middle" letter-spacing="1.5">DISCORD VERIFIED GAME</text>
        </svg>
        `.trim();
        return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
    },

    createQuestCard(q) {
        const I = window.DQS_ICONS;
        const card = document.createElement('div');
        card.className = 'quest-card';

        const qid = q.id;
        const gameTitle = q.game_title || 'Unbekanntes Spiel';
        const questName = q.quest_name || 'Quest';
        const taskType = q.task_type || 'PLAY_ON_DESKTOP';
        const targetSeconds = q.target_seconds || 900;
        const currentSeconds = q.current_seconds || 0;
        const percent = Math.min(100, Math.round(q.progress_percent || 0));
        const enrolled = q.enrolled;
        const completed = q.completed;
        const claimed = q.claimed;
        const orbCount = q.orb_count || 0;
        const appId = q.app_id || '';
        const videoUrl = q.video_url;
        const isVideo = Boolean(q.is_video_task || taskType.includes('WATCH_VIDEO'));
        const isMobile = Boolean(q.is_mobile_task || taskType.includes('MOBILE'));
        const hasTrailer = Boolean(q.has_trailer && q.trailer_url);
        const rewardType = q.primary_reward_type || 'ITEM';
        const rewardName = q.primary_reward_name || q.rewards_text || '';
        const isMultiGame = Boolean(q.is_multi_game && q.supported_applications && q.supported_applications.length > 1);

        // Universal Multi-CDN Artwork Fallback Chain
        const b64Tile = window.DQS_EMBEDDED_ASSETS?.tiles?.[qid];
        const candidateUrls = [
            b64Tile,
            q.best_artwork_url,
            q.hero_url,
            q.tile_url,
            q.game_cover_url,
            q.game_icon_url,
            `assets/quests/tiles/${qid}.png`
        ].filter(Boolean);

        const tileSrc = candidateUrls.length > 0 ? candidateUrls[0] : this.createDynamicGameBadge(gameTitle);

        // Animated Discord Orbs Logo
        const orbImgSrc = window.DQS_EMBEDDED_ASSETS?.animated_orb || 'assets/discord_orbs_animated.gif';

        const taskIcon = isVideo ? I.video : I.gamepad;
        let taskLabel = `${Math.round(targetSeconds / 60)} Min. Spielzeit`;
        if (isVideo) {
            taskLabel = isMobile ? 'Mobilgerät Video' : 'Video-Quest';
        } else if (taskType === 'PLAY_ACTIVITY') {
            taskLabel = 'Discord Activity';
        }

        const curMin = Math.floor(currentSeconds / 60);
        const tgtMin = Math.round(targetSeconds / 60);
        let progressTxt = `${curMin}/${tgtMin} MIN. (${percent}%)`;
        if (completed || claimed) progressTxt += ' - QUEST ERFÜLLT!';

        // Multi-Game Selector HTML
        let multiGameHtml = '';
        if (isMultiGame) {
            const options = q.supported_applications.map(app => {
                const isSel = (q.selected_app && q.selected_app.id === app.id) ? 'selected' : '';
                return `<option value="${app.id}" ${isSel}>${app.name}</option>`;
            }).join('');

            multiGameHtml = `
                <div class="multi-game-wrapper">
                    <div class="multi-game-badge">
                        ${I.gamepad} <span>AUSWÄHLBARE SPIELE (${q.supported_applications.length})</span>
                    </div>
                    <div class="multi-game-select-row">
                        <span class="multi-game-label">AKTIVES SPIEL:</span>
                        <select class="multi-game-select" id="multi-sel-${qid}">
                            ${options}
                        </select>
                    </div>
                </div>
            `;
        }

        // Build Progress Bars (2 Bars if Video, 1 Bar if Desktop)
        let progressHtml = '';
        if (isVideo) {
            progressHtml = `
                <div class="dual-progress-container" id="dual-progress-${qid}">
                    <div class="progress-bar-block">
                        <div class="progress-bar-header">
                            <span class="progress-bar-label">${I.video} STREAM BUFFER & HEARTBEAT</span>
                            <span class="progress-bar-value" id="val-buffer-${qid}">${completed || claimed ? 'SYNCHRONISIERT (100%)' : 'STREAM BEREIT (100%)'}</span>
                        </div>
                        <div class="progress-track buffer" id="track-buffer-${qid}">
                            <div class="progress-fill buffer" id="fill-buffer-${qid}" style="width: 100%"></div>
                        </div>
                    </div>
                    <div class="progress-bar-block">
                        <div class="progress-bar-header">
                            <span class="progress-bar-label">${I.quest} QUEST-FORTSCHRITT</span>
                            <span class="progress-bar-value ${completed || claimed ? 'completed' : ''}" id="val-quest-${qid}">${progressTxt}</span>
                        </div>
                        <div class="progress-track" id="track-quest-${qid}">
                            <div class="progress-fill ${completed || claimed ? 'completed' : ''}" id="fill-quest-${qid}" style="width: ${percent}%"></div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            progressHtml = `
                <div class="quest-progress-row">
                    <div class="progress-track" id="track-quest-${qid}">
                        <div class="progress-fill ${completed || claimed ? 'completed' : ''}" id="fill-quest-${qid}" style="width: ${percent}%"></div>
                    </div>
                    <span class="progress-text ${completed || claimed ? 'completed' : ''}" id="val-quest-${qid}">${progressTxt}</span>
                </div>
            `;
        }

        let rewardBadgeHtml = '';
        if (rewardType === 'AVATAR_DECO') {
            rewardBadgeHtml = `<span class="badge-tag avatar-deco">${I.gift} AVATAR-DEKO: <strong>${rewardName}</strong></span>`;
        } else if (rewardType === 'INGAME_ITEM') {
            rewardBadgeHtml = `<span class="badge-tag ingame-item">${I.gift} ITEM/SKIN: <strong>${rewardName}</strong></span>`;
        }

        card.innerHTML = `
            <div class="quest-tile-wrap">
                <img src="${tileSrc}" alt="${gameTitle}" class="quest-tile-img" id="tile-img-${qid}">
            </div>
            <div class="quest-info-wrap">
                <div class="quest-header-row">
                    <span class="quest-game-title">${gameTitle}</span>
                    ${completed || claimed ? `<span class="badge-tag completed-badge">${I.check} ERFÜLLT</span>` : ''}
                    <span class="badge-tag task">${taskIcon} ${taskLabel}</span>
                    ${rewardBadgeHtml}
                    ${isMobile ? `<span class="badge-tag mobile-task">${I.gamepad} MOBILGERÄT (ANDROID)</span>` : ''}
                    ${isMultiGame ? `<span class="badge-tag multi">${I.gamepad} MULTI-GAME (${q.supported_applications.length})</span>` : ''}
                    <span class="badge-tag required-game">${I.gamepad} BENÖTIGT: <strong class="req-game-name">${q.required_game_name || gameTitle}</strong></span>
                    ${!isVideo && q.required_exe ? `<span class="badge-tag process-exe">PROZESS: <code class="req-exe-name">${q.required_exe}</code></span>` : ''}
                    <span class="badge-tag duration">${I.clock} DAUER: <strong>${q.duration_text || (isVideo ? '(ca. 30 Sek.)' : '(ca. 15 Min.)')}</strong></span>
                    ${orbCount > 0 ? `<span class="badge-tag orbs"><img src="${orbImgSrc}" class="discord-orb-icon" alt="Orbs"> <span>${orbCount} ORBS</span></span>` : ''}
                </div>
                <div class="quest-name-sub">${questName}</div>
                ${multiGameHtml}
                ${progressHtml}
            </div>
            <div class="quest-actions-wrap" id="act-box-${qid}"></div>
        `;

        // Wire image fallback sequence
        const tileImg = card.querySelector('.quest-tile-img');
        if (tileImg) {
            let candidateIdx = 0;
            tileImg.onerror = () => {
                candidateIdx++;
                if (candidateIdx < candidateUrls.length) {
                    tileImg.src = candidateUrls[candidateIdx];
                } else {
                    tileImg.onerror = null;
                    tileImg.src = this.createDynamicGameBadge(gameTitle);
                }
            };
        }

        if (isMultiGame) {
            const multiSel = card.querySelector(`#multi-sel-${qid}`);
            if (multiSel) {
                multiSel.addEventListener('change', (e) => {
                    const chosenId = e.target.value;
                    const found = q.supported_applications.find(a => a.id === chosenId);
                    if (found) {
                        q.selected_app = found;
                        q.app_id = found.id;
                        q.sim_game_title = found.name;
                        q.required_game_name = found.name;
                        q.required_exe = found.exe;
                        const reqNameEl = card.querySelector('.req-game-name');
                        if (reqNameEl) reqNameEl.textContent = found.name;
                        const reqExeEl = card.querySelector('.req-exe-name');
                        if (reqExeEl && found.exe) reqExeEl.textContent = found.exe;
                    }
                });
            }
        }

        const actBox = card.querySelector(`#act-box-${qid}`);

        if (claimed) {
            actBox.innerHTML = `<button class="btn btn-claimed" disabled>${I.check} EINGELÖST</button>`;
        } else if (completed) {
            const btnClaim = document.createElement('button');
            btnClaim.className = 'btn btn-emerald';
            btnClaim.innerHTML = `${I.gift} BELOHNUNG ABHOLEN`;
            btnClaim.onclick = async () => {
                btnClaim.innerHTML = `Löst ein...`;
                const res = await window.pywebview.api.claim_quest(qid);
                if (res && res.code) {
                    try {
                        await navigator.clipboard.writeText(res.code);
                    } catch (err) {}
                    alert(`In-Game Belohnung freigeschaltet!\n\nFreischalt-Code: ${res.code}\n(Code wurde automatisch in die Zwischenablage kopiert!)`);
                } else if (rewardType === 'AVATAR_DECO') {
                    alert(`Avatar-Dekoration "${rewardName}" erfolgreich und dauerhaft in deinem Discord-Inventar freigeschaltet!`);
                }
                this.refreshQuests();
            };
            actBox.appendChild(btnClaim);
        } else {
            // 1. If it's a real video task
            if (isVideo) {
                const btnExp = document.createElement('button');
                btnExp.id = `btn-exp-${qid}`;
                btnExp.className = 'btn btn-cyan';
                btnExp.innerHTML = `${I.autofarm} ${isMobile ? 'EXPRESS (MOBIL)' : 'EXPRESS (5s)'}`;
                btnExp.onclick = () => {
                    this.startExpressQuest(qid, targetSeconds || 30, gameTitle, isMobile);
                };
                actBox.appendChild(btnExp);

                if (videoUrl) {
                    const btnVid = document.createElement('button');
                    btnVid.className = 'btn btn-secondary';
                    btnVid.innerHTML = `${I.video} VIDEO ANSCHAUEN`;
                    btnVid.onclick = () => {
                        this.openVideoModal(qid, gameTitle, questName, videoUrl, targetSeconds, true, isMobile, q);
                    };
                    actBox.appendChild(btnVid);
                }
            } else {
                // Desktop Game Simulation
                const btnSim = document.createElement('button');
                btnSim.className = 'btn btn-emerald';
                btnSim.innerHTML = `${I.play} SIMULIEREN`;
                btnSim.onclick = () => {
                    const targetAppId = q.selected_app?.id || q.required_app_id || appId;
                    const targetTitle = q.selected_app?.name || q.required_game_name || q.sim_game_title || gameTitle;
                    const targetExe = q.selected_app?.exe || q.required_exe || '';
                    this.simulateQuest(targetAppId, targetTitle, targetExe);
                };
                actBox.appendChild(btnSim);

                // Trailer preview button if game has promotional video
                if (hasTrailer && q.trailer_url) {
                    const btnTrailer = document.createElement('button');
                    btnTrailer.className = 'btn btn-trailer-watch';
                    btnTrailer.innerHTML = `${I.video} TRAILER`;
                    btnTrailer.onclick = () => {
                        this.openVideoModal(qid, gameTitle, `${questName} (Trailer)`, q.trailer_url, 30, false, false, q);
                    };
                    actBox.appendChild(btnTrailer);
                }
            }

            // Enroll button if not yet enrolled
            if (!enrolled) {
                const btnEnroll = document.createElement('button');
                btnEnroll.className = 'btn btn-blurple';
                btnEnroll.innerHTML = `${I.quest} ANNEHMEN`;
                btnEnroll.onclick = async () => {
                    btnEnroll.innerHTML = `Nimmt an...`;
                    await window.pywebview.api.enroll_quest(qid);
                    this.refreshQuests();
                };
                actBox.appendChild(btnEnroll);
            }
        }

        return card;
    },

    // --- Interactive Moving Express Quest Completer & Live Sync ---
    startExpressQuest(qid, targetSeconds = 30, gameTitle = '', isMobile = false) {
        const I = window.DQS_ICONS;
        this.activeExpressVideoTitle = gameTitle ? `Video: ${gameTitle}` : 'Express Video Stream';
        this.activeExpressQuestId = qid;
        this.updateProfileActivity(false, null, 0);

        const devName = isMobile ? 'Google Pixel 8 (Android 14)' : 'Discord Desktop (Windows 11)';
        this.showLiveSyncHUD({
            device: devName,
            isMobile: isMobile,
            statusTitle: isMobile ? 'LIVE DISCORD ANDROID SYNC' : 'LIVE DISCORD API SYNC',
            statusText: `[${devName}] Initialisiere verschlüsselte Verbindung für "${gameTitle || 'Quest'}"...`,
            percent: 5,
            status: 'CONNECTING'
        });

        const fillQuest = document.getElementById(`fill-quest-${qid}`);
        const valQuest = document.getElementById(`val-quest-${qid}`);
        const trackQuest = document.getElementById(`track-quest-${qid}`);
        const fillBuffer = document.getElementById(`fill-buffer-${qid}`);
        const valBuffer = document.getElementById(`val-buffer-${qid}`);
        const btnExp = document.getElementById(`btn-exp-${qid}`) || document.getElementById(`exp-btn-${qid}`);

        if (btnExp) {
            btnExp.disabled = true;
            btnExp.classList.add('btn-glow');
            btnExp.innerHTML = `${I.autofarm} SYNC LÄUFT...`;
        }

        if (fillQuest) {
            fillQuest.classList.add('express-animating');
            fillQuest.style.width = '8%';
        }
        if (trackQuest) trackQuest.classList.add('express-active');
        if (fillBuffer) {
            fillBuffer.classList.add('express-animating');
            fillBuffer.style.width = '8%';
        }

        // Call backend completion asynchronously with isMobile
        window.pywebview?.api?.complete_video_quest(qid, targetSeconds, isMobile);
    },

    // --- Live Sync HUD Control Methods ---
    setupLiveSyncHUD() {
        const closeBtn = document.getElementById('btn-close-sync-hud');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.hideLiveSyncHUD();
            });
        }
    },

    showLiveSyncHUD(opts = {}) {
        const hud = document.getElementById('mobile-sync-hud');
        if (!hud) return;
        this.updateLiveSyncHUD(opts);
        hud.classList.remove('hidden', 'hud-hiding');
    },

    updateLiveSyncHUD(opts = {}) {
        const hud = document.getElementById('mobile-sync-hud');
        if (!hud) return;
        hud.classList.remove('hidden', 'hud-hiding');

        const badge = document.getElementById('sync-hud-badge');
        const iconEl = document.getElementById('sync-device-icon');
        const nameEl = document.getElementById('sync-device-name');
        const titleEl = document.getElementById('sync-status-title');
        const questEl = document.getElementById('sync-quest-name');
        const fillEl = document.getElementById('sync-progress-fill');
        const pctEl = document.getElementById('sync-pct-text');

        if (opts.device && nameEl) nameEl.innerText = opts.device;
        if (iconEl) iconEl.innerText = opts.isMobile ? '📱' : '💻';
        if (badge) {
            badge.className = `sync-device-badge ${opts.isMobile ? 'badge-android' : 'badge-desktop'}`;
        }
        if (opts.statusTitle && titleEl) titleEl.innerText = opts.statusTitle;
        if (opts.statusText && questEl) questEl.innerText = opts.statusText;
        if (opts.percent !== undefined) {
            const p = Math.min(100, Math.max(0, Math.round(opts.percent)));
            if (fillEl) fillEl.style.width = `${p}%`;
            if (pctEl) pctEl.innerText = `${p}%`;
        }
        if (opts.status === 'SUCCESS' && fillEl) {
            fillEl.classList.add('completed');
        } else if (fillEl) {
            fillEl.classList.remove('completed');
        }
    },

    hideLiveSyncHUD() {
        const hud = document.getElementById('mobile-sync-hud');
        if (!hud || hud.classList.contains('hidden')) return;
        hud.classList.add('hud-hiding');
        setTimeout(() => {
            hud.classList.remove('hud-hiding');
            hud.classList.add('hidden');
        }, 350);
    },

    handleExpressProgress(data) {
        const I = window.DQS_ICONS;
        if (!data) return;

        let qid, percent, status, statusText, device, isMobile, gameTitle;
        if (typeof data === 'object') {
            qid = String(data.quest_id || '');
            percent = typeof data.percent === 'number' ? data.percent : 0;
            status = data.status || 'SYNCING';
            statusText = data.status_text || '';
            device = data.device || (data.is_mobile ? 'Google Pixel 8 (Android 14)' : 'Discord Desktop (Windows 11)');
            isMobile = Boolean(data.is_mobile);
            gameTitle = data.game_title || '';
        } else {
            qid = String(arguments[0] || '');
            percent = Number(arguments[1]) || 0;
            status = percent >= 100 ? 'SUCCESS' : 'SYNCING';
            statusText = `Sende Video-Fortschritt (${percent}%)...`;
            device = 'Google Pixel 8 (Android 14)';
            isMobile = true;
        }

        const pctRounded = Math.min(100, Math.max(0, Math.round(percent)));

        let statusTitle = isMobile ? 'LIVE DISCORD ANDROID SYNC' : 'LIVE DISCORD API SYNC';
        if (status === 'SUCCESS' || pctRounded >= 100) {
            statusTitle = '✓ DISCORD SYNC ERFOLGREICH';
        } else if (status === 'GAME_QUEST') {
            statusTitle = '🎮 SPIEL-SIMULATION GESTARTET';
        } else if (status === 'ERROR') {
            statusTitle = '⚠️ SYNC-FEHLER';
        }

        this.updateLiveSyncHUD({
            device,
            isMobile,
            statusTitle,
            statusText: statusText || `${gameTitle}: ${pctRounded}%`,
            percent: pctRounded,
            status
        });

        const fillQuest = document.getElementById(`fill-quest-${qid}`);
        const valQuest = document.getElementById(`val-quest-${qid}`);
        const fillBuffer = document.getElementById(`fill-buffer-${qid}`);
        const valBuffer = document.getElementById(`val-buffer-${qid}`);
        const btnExp = document.getElementById(`btn-exp-${qid}`) || document.getElementById(`exp-btn-${qid}`);

        if (fillQuest) {
            fillQuest.style.width = `${pctRounded}%`;
            if (pctRounded >= 100) {
                fillQuest.classList.remove('express-animating');
                fillQuest.classList.add('completed');
            }
        }
        if (valQuest) {
            if (status === 'SUCCESS' || pctRounded >= 100) {
                valQuest.innerText = `100% - QUEST ERFÜLLT!`;
                valQuest.classList.add('completed');
            } else if (status === 'GAME_QUEST') {
                valQuest.innerText = `GAME-TRAILER: SIMULATION AKTIV`;
            } else if (status === 'ERROR') {
                valQuest.innerText = `FEHLER BEI SYNC`;
            } else {
                valQuest.innerText = `FORTSCHRITT: ${pctRounded}% (${isMobile ? 'Pixel 8' : 'Desktop'})`;
            }
        }
        if (fillBuffer) fillBuffer.style.width = `${pctRounded}%`;
        if (valBuffer) {
            valBuffer.innerText = `BUFFER: ${pctRounded}% (${isMobile ? 'MOBIL' : 'DESKTOP'})`;
        }
        if (btnExp) {
            if (status === 'SUCCESS' || pctRounded >= 100) {
                btnExp.innerHTML = `${I.check} ERFOLGREICH!`;
                btnExp.className = 'btn btn-claimed';
                btnExp.disabled = false;
            } else if (status === 'GAME_QUEST') {
                btnExp.innerHTML = `${I.gamepad} SIMULATION GESTARTET`;
                btnExp.className = 'btn btn-emerald';
                btnExp.disabled = false;
            } else if (status === 'ERROR') {
                btnExp.innerHTML = `FEHLER BEI SYNC`;
                btnExp.disabled = false;
            } else {
                btnExp.innerHTML = `${I.autofarm} SYNC: ${pctRounded}%`;
            }
        }

        if (status === 'SUCCESS' || pctRounded >= 100) {
            this.activeExpressVideoTitle = null;
            this.activeExpressQuestId = null;
            window.pywebview?.api?.play_success_sound();
            setTimeout(() => {
                this.refreshQuests();
            }, 1200);
            setTimeout(() => {
                this.hideLiveSyncHUD();
            }, 4500);
        } else if (status === 'GAME_QUEST') {
            this.activeExpressVideoTitle = null;
            this.activeExpressQuestId = null;
            setTimeout(() => {
                this.pollSimStatus();
                this.refreshQuests();
            }, 1000);
            setTimeout(() => {
                this.hideLiveSyncHUD();
            }, 4000);
        } else if (status === 'ERROR') {
            this.activeExpressVideoTitle = null;
            this.activeExpressQuestId = null;
            setTimeout(() => {
                this.hideLiveSyncHUD();
            }, 5000);
        }
    },

    handleGameSimulationStarted(questId, appId, gameTitle) {
        this.updateLiveSyncHUD({
            device: 'Discord Desktop (Windows 11)',
            isMobile: false,
            statusTitle: '🎮 SPIEL-SIMULATION GESTARTET',
            statusText: `Trailer erkannt: Win32 Heartbeat-Simulation für "${gameTitle}" aktiv.`,
            percent: 100,
            status: 'GAME_QUEST'
        });
        this.pollSimStatus();
        setTimeout(() => {
            this.refreshQuests();
        }, 1000);
        setTimeout(() => {
            this.hideLiveSyncHUD();
        }, 4000);
    },

    // --- 720p HD Video Player Modal ---
    setupVideoModal() {
        const modal = document.getElementById('video-modal');
        const closeBtn = document.getElementById('btn-close-video-modal');
        const pillMobile = document.getElementById('btn-pill-mobile');
        const pillDesktop = document.getElementById('btn-pill-desktop');
        const btnExp = document.getElementById('btn-modal-express-finish');
        const btnSim = document.getElementById('btn-modal-sim-start');

        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.closeVideoModal();
            });
        }
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeVideoModal();
                }
            });
        }

        if (pillMobile && pillDesktop) {
            pillMobile.addEventListener('click', () => {
                this.videoModalIsMobile = true;
                pillMobile.classList.add('active');
                pillDesktop.classList.remove('active');
                if (btnExp) {
                    const I = window.DQS_ICONS;
                    btnExp.innerHTML = `${I.autofarm} 📱 MOBIL ABSCHLIESSEN (5s)`;
                }
            });

            pillDesktop.addEventListener('click', () => {
                this.videoModalIsMobile = false;
                pillDesktop.classList.add('active');
                pillMobile.classList.remove('active');
                if (btnExp) {
                    const I = window.DQS_ICONS;
                    btnExp.innerHTML = `${I.autofarm} ⚡ EXPRESS-ABSCHLUSS (5s)`;
                }
            });
        }

        if (btnExp) {
            btnExp.addEventListener('click', () => {
                if (!this.currentModalQuest) return;
                const { qid, gameTitle, targetSec } = this.currentModalQuest;
                const isMobile = Boolean(this.videoModalIsMobile);
                this.closeVideoModal();
                this.startExpressQuest(qid, targetSec || 30, gameTitle, isMobile);
            });
        }

        if (btnSim) {
            btnSim.addEventListener('click', () => {
                if (!this.currentModalQuest) return;
                const { qid, gameTitle, questObj } = this.currentModalQuest;
                this.closeVideoModal();
                const targetAppId = questObj?.selected_app?.id || questObj?.required_app_id || questObj?.app_id || '';
                const targetTitle = questObj?.selected_app?.name || questObj?.required_game_name || questObj?.sim_game_title || gameTitle;
                const targetExe = questObj?.selected_app?.exe || questObj?.required_exe || '';
                this.simulateQuest(targetAppId, targetTitle, targetExe);
            });
        }
    },

    openVideoModal(qid, gameTitle, questName, videoUrl, targetSec = 30, isVideoTask = true, isMobile = false, questObj = null) {
        const modal = document.getElementById('video-modal');
        const titleEl = document.getElementById('video-modal-title');
        const videoEl = document.getElementById('discord-video-player');
        const statusText = document.getElementById('video-modal-status-text');
        const deviceSelector = document.getElementById('video-device-selector');
        const btnExp = document.getElementById('btn-modal-express-finish');
        const btnSim = document.getElementById('btn-modal-sim-start');
        const pillMobile = document.getElementById('btn-pill-mobile');
        const pillDesktop = document.getElementById('btn-pill-desktop');
        const I = window.DQS_ICONS;

        if (!modal || !videoEl) return;

        this.currentModalQuest = { qid, gameTitle, questName, videoUrl, targetSec, isVideoTask, isMobile, questObj };
        this.videoModalIsMobile = Boolean(isMobile);

        if (isVideoTask) {
            titleEl.innerText = `${gameTitle} - ${questName} (720p HD Stream)`;
            if (statusText) statusText.innerText = 'DISCORD CDN 720P STREAM AKTIV';
            if (deviceSelector) deviceSelector.classList.remove('hidden');
            if (btnExp) {
                btnExp.classList.remove('hidden');
                btnExp.innerHTML = `${I.autofarm} ${this.videoModalIsMobile ? '📱 MOBIL ABSCHLIESSEN (5s)' : '⚡ EXPRESS-ABSCHLUSS (5s)'}`;
            }
            if (btnSim) btnSim.classList.add('hidden');

            if (this.videoModalIsMobile) {
                pillMobile?.classList.add('active');
                pillDesktop?.classList.remove('active');
            } else {
                pillDesktop?.classList.add('active');
                pillMobile?.classList.remove('active');
            }
        } else {
            // Game Quest Trailer
            titleEl.innerText = `${gameTitle} - Offizieller HD Trailer`;
            if (statusText) statusText.innerText = 'SPIEL-QUEST TRAILER • DISCORD STREAM';
            if (deviceSelector) deviceSelector.classList.add('hidden');
            if (btnExp) btnExp.classList.add('hidden');
            if (btnSim) {
                btnSim.classList.remove('hidden');
                btnSim.innerHTML = `${I.gamepad} IM SIMULATOR STARTEN`;
            }
        }

        videoEl.src = videoUrl;
        videoEl.currentTime = 0;
        videoEl.play().catch(() => {});

        modal.classList.remove('hidden');
    },

    closeVideoModal() {
        const modal = document.getElementById('video-modal');
        const videoEl = document.getElementById('discord-video-player');
        if (videoEl) {
            videoEl.pause();
            videoEl.src = '';
        }
        if (modal) modal.classList.add('hidden');
        this.currentModalQuest = null;
    },

    // --- License & Security Modal (T3X / Sandro) ---
    setupLicenseModal() {
        const modal = document.getElementById('license-modal');
        const trigger = document.getElementById('app-logo-trigger');
        const closeHeader = document.getElementById('btn-close-license-modal');
        const closeFooter = document.getElementById('btn-close-license-modal-footer');
        const btnDe = document.getElementById('btn-license-lang-de');
        const btnEn = document.getElementById('btn-license-lang-en');
        const paneDe = document.getElementById('license-pane-de');
        const paneEn = document.getElementById('license-pane-en');
        const linkGhDe = document.getElementById('link-github-repo-de');
        const linkGhEn = document.getElementById('link-github-repo-en');

        const openModal = () => {
            if (modal) modal.classList.remove('hidden');
        };
        const closeModal = () => {
            if (modal) modal.classList.add('hidden');
        };

        if (trigger) trigger.addEventListener('click', openModal);
        if (closeHeader) closeHeader.addEventListener('click', closeModal);
        if (closeFooter) closeFooter.addEventListener('click', closeModal);

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) closeModal();
            });
        }

        const setLang = (lang) => {
            if (lang === 'de') {
                btnDe?.classList.add('active');
                btnEn?.classList.remove('active');
                paneDe?.classList.add('active');
                paneEn?.classList.remove('active');
            } else {
                btnEn?.classList.add('active');
                btnDe?.classList.remove('active');
                paneEn?.classList.add('active');
                paneDe?.classList.remove('active');
            }
        };

        if (btnDe) btnDe.addEventListener('click', () => setLang('de'));
        if (btnEn) btnEn.addEventListener('click', () => setLang('en'));

        const openGh = () => {
            const repoUrl = 'https://github.com/TentixTV/Discord-Quest-Spoofer';
            if (window.pywebview?.api?.open_external_url) {
                window.pywebview.api.open_external_url(repoUrl);
            } else {
                window.open(repoUrl, '_blank');
            }
        };

        if (linkGhDe) linkGhDe.addEventListener('click', openGh);
        if (linkGhEn) linkGhEn.addEventListener('click', openGh);
    },

    // --- Tutorial & Interactive Help Modal (15-Min Explanation & Sandro Support) ---
    setupTutorialModal() {
        const modal = document.getElementById('tutorial-modal');
        const trigger = document.getElementById('btn-open-tutorial');
        const closeHeader = document.getElementById('btn-close-tutorial-modal');
        const closeFooter = document.getElementById('btn-close-tutorial-modal-footer');
        const tabBtns = document.querySelectorAll('.tut-tab-btn');
        const panes = document.querySelectorAll('.tutorial-pane');
        const btnAddTentix = document.getElementById('btn-add-tentix');
        const tentixStatus = document.getElementById('add-tentix-status');
        const linkGh = document.getElementById('btn-tut-open-github');
        const linkIssues = document.getElementById('btn-tut-open-issues');

        const openModal = () => {
            if (modal) modal.classList.remove('hidden');
        };
        const closeModal = () => {
            if (modal) modal.classList.add('hidden');
        };

        if (trigger) trigger.addEventListener('click', openModal);
        if (closeHeader) closeHeader.addEventListener('click', closeModal);
        if (closeFooter) closeFooter.addEventListener('click', closeModal);

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) closeModal();
            });
        }

        // Tab Switching
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetPaneId = btn.getAttribute('data-pane');
                tabBtns.forEach(b => b.classList.remove('active'));
                panes.forEach(p => p.classList.remove('active'));

                btn.classList.add('active');
                const targetPane = document.getElementById(targetPaneId);
                if (targetPane) targetPane.classList.add('active');
            });
        });

        // 1-Click Friend Request to tentix (Sandro)
        if (btnAddTentix) {
            btnAddTentix.addEventListener('click', async () => {
                btnAddTentix.disabled = true;
                const origHtml = btnAddTentix.innerHTML;
                btnAddTentix.innerHTML = `<span class="spinner-border spinner-border-sm"></span> ANFRAGE WIRD GESENDET...`;

                if (tentixStatus) {
                    tentixStatus.className = 'friend-status-msg info';
                    tentixStatus.innerText = 'Verbindung zu Discord wird hergestellt...';
                    tentixStatus.classList.remove('hidden');
                }

                try {
                    let res = null;
                    if (window.pywebview?.api?.send_friend_request_to_dev) {
                        res = await window.pywebview.api.send_friend_request_to_dev();
                    } else {
                        // Browser preview simulation
                        await new Promise(r => setTimeout(r, 600));
                        res = { success: true, message: "Freundschaftsanfrage erfolgreich an tentix gesendet!" };
                    }

                    if (tentixStatus) {
                        tentixStatus.classList.remove('hidden');
                        if (res && res.success) {
                            tentixStatus.className = 'friend-status-msg success';
                            tentixStatus.innerText = res.message || 'Freundschaftsanfrage an Sandro (tentix) erfolgreich gesendet!';
                        } else {
                            const isFallback = res && res.fallback_copied;
                            tentixStatus.className = isFallback ? 'friend-status-msg warning' : 'friend-status-msg error';
                            tentixStatus.innerText = res?.message || 'Fehler beim Senden. Tag "tentix" kopiert!';
                        }
                    }
                } catch (err) {
                    if (tentixStatus) {
                        tentixStatus.className = 'friend-status-msg error';
                        tentixStatus.innerText = `Fehler: ${err?.message || err}`;
                        tentixStatus.classList.remove('hidden');
                    }
                } finally {
                    btnAddTentix.disabled = false;
                    btnAddTentix.innerHTML = origHtml;
                }
            });
        }

        // Links
        const openUrl = (url) => {
            if (window.pywebview?.api?.open_external_url) {
                window.pywebview.api.open_external_url(url);
            } else {
                window.open(url, '_blank');
            }
        };

        if (linkGh) linkGh.addEventListener('click', () => openUrl('https://github.com/TentixTV/Discord-Quest-Spoofer'));
        if (linkIssues) linkIssues.addEventListener('click', () => openUrl('https://github.com/TentixTV/Discord-Quest-Spoofer/issues'));
    },

    // --- Helper: Lightweight Markdown to Clean HTML Parser ---
    _parseMarkdownToHtml(md) {
        if (!md) return '<p>Keine Release-Notizen verfügbar.</p>';
        const escapeHtml = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        
        const lines = md.split('\n');
        let html = '';
        let inList = false;

        for (let line of lines) {
            let trimmed = line.trim();
            if (!trimmed) {
                if (inList) {
                    html += '</ul>';
                    inList = false;
                }
                continue;
            }

            if (trimmed.startsWith('### ')) {
                if (inList) { html += '</ul>'; inList = false; }
                html += `<h4>${escapeHtml(trimmed.slice(4))}</h4>`;
            } else if (trimmed.startsWith('## ')) {
                if (inList) { html += '</ul>'; inList = false; }
                html += `<h3>${escapeHtml(trimmed.slice(3))}</h3>`;
            } else if (trimmed.startsWith('# ')) {
                if (inList) { html += '</ul>'; inList = false; }
                html += `<h2>${escapeHtml(trimmed.slice(2))}</h2>`;
            } else if (trimmed.startsWith('---') || trimmed.startsWith('___')) {
                if (inList) { html += '</ul>'; inList = false; }
                html += '<hr>';
            } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ') || trimmed.startsWith('• ')) {
                if (!inList) {
                    html += '<ul>';
                    inList = true;
                }
                let itemContent = escapeHtml(trimmed.slice(2));
                itemContent = itemContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                itemContent = itemContent.replace(/`([^`]+)`/g, '<code>$1</code>');
                itemContent = itemContent.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="bio-link" target="_blank">$1</a>');
                html += `<li>${itemContent}</li>`;
            } else {
                if (inList) { html += '</ul>'; inList = false; }
                let para = escapeHtml(trimmed);
                para = para.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                para = para.replace(/`([^`]+)`/g, '<code>$1</code>');
                para = para.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="bio-link" target="_blank">$1</a>');
                html += `<p style="margin: 5px 0;">${para}</p>`;
            }
        }
        if (inList) html += '</ul>';
        return html;
    },

    // --- Helper: Universal Smooth Wheel Scrolling for WebView2 Containers ---
    makeScrollableOnWheel(el) {
        if (!el || el._hasWheelHandler) return;
        el._hasWheelHandler = true;
        el.addEventListener('wheel', (e) => {
            if (!e.deltaY) return;
            const prevTop = el.scrollTop;
            el.scrollTop += e.deltaY;
            if (el.scrollTop !== prevTop) {
                e.preventDefault();
                e.stopPropagation();
            }
        }, { passive: false });
    },

    // --- Changelog & GitHub Updater Modals ---
    setupChangelogAndUpdateModals() {
        const changelogModal = document.getElementById('changelog-modal');
        const btnCloseChangelogModal = document.getElementById('btn-close-changelog-modal');
        const btnCloseChangelogAction = document.getElementById('btn-close-changelog-action');
        const btnChangelogGh = document.getElementById('btn-changelog-open-github');
        
        const closeChangelog = () => {
            if (changelogModal) changelogModal.classList.add('hidden');
        };

        if (btnCloseChangelogModal) btnCloseChangelogModal.addEventListener('click', closeChangelog);
        if (btnCloseChangelogAction) btnCloseChangelogAction.addEventListener('click', closeChangelog);
        if (changelogModal) {
            changelogModal.addEventListener('click', (e) => {
                if (e.target === changelogModal) closeChangelog();
            });
        }
        if (btnChangelogGh) {
            btnChangelogGh.addEventListener('click', () => {
                window.pywebview?.api?.open_url('https://github.com/TentixTV/Discord-Quest-Spoofer');
            });
        }

        const updateModal = document.getElementById('update-modal');
        const btnCloseUpdateModal = document.getElementById('btn-close-update-modal');
        const btnUpdateCancel = document.getElementById('btn-update-cancel');

        const closeUpdate = () => {
            if (updateModal) updateModal.classList.add('hidden');
        };

        if (btnCloseUpdateModal) btnCloseUpdateModal.addEventListener('click', closeUpdate);
        if (btnUpdateCancel) btnUpdateCancel.addEventListener('click', closeUpdate);
        if (updateModal) {
            updateModal.addEventListener('click', (e) => {
                if (e.target === updateModal) closeUpdate();
            });
        }

        // Enable smooth wheel scrolling for update modal containers
        const updateBody = document.querySelector('.update-modal-body-v2');
        const updateNotesBox = document.querySelector('.update-notes-container');
        const updateNotesContent = document.getElementById('update-live-notes-content');
        if (updateBody) this.makeScrollableOnWheel(updateBody);
        if (updateNotesBox) this.makeScrollableOnWheel(updateNotesBox);
        if (updateNotesContent) this.makeScrollableOnWheel(updateNotesContent);

        // Live Recheck button
        const btnRecheck = document.getElementById('btn-update-recheck');
        if (btnRecheck) {
            btnRecheck.addEventListener('click', async () => {
                const spin = document.getElementById('ico-recheck-spin');
                if (spin) spin.style.animation = 'spin 0.8s linear infinite';
                await this.checkForUpdates(true);
                if (spin) spin.style.animation = '';
            });
        }

        // Open GitHub Repo / Release
        const btnOpenGh = document.getElementById('btn-update-open-github');
        if (btnOpenGh) {
            btnOpenGh.addEventListener('click', () => {
                const url = this._latestReleaseUrl || 'https://github.com/TentixTV/Discord-Quest-Spoofer/releases';
                window.pywebview?.api?.open_url(url);
            });
        }

        // Toast Banner actions
        const btnToastUpdate = document.getElementById('btn-toast-update-now');
        const btnToastDismiss = document.getElementById('btn-toast-update-dismiss');
        const toastBanner = document.getElementById('update-toast-banner');

        if (btnToastUpdate) {
            btnToastUpdate.addEventListener('click', () => {
                if (toastBanner) toastBanner.classList.add('hidden');
                this.checkForUpdates(true);
            });
        }
        if (btnToastDismiss) {
            btnToastDismiss.addEventListener('click', () => {
                if (toastBanner) toastBanner.classList.add('hidden');
            });
        }
    },

    // --- Discord Orbs Link & Live Counter ---
    setupOrbsLinks() {
        const questsOrbsWidget = document.getElementById('quests-orbs-widget');
        const popoutOrbsBtn = document.getElementById('btn-popout-orbs-hub');
        const hdrOrbsChip = document.getElementById('hdr-orbs-chip');

        const handleOrbsClick = () => {
            const popout = document.getElementById('discord-profile-popout');
            const backdrop = document.getElementById('popout-backdrop');
            if (popout) popout.classList.add('hidden');
            if (backdrop) backdrop.classList.add('hidden');
            this.openDiscordOrbsHub();
        };

        if (questsOrbsWidget) {
            questsOrbsWidget.addEventListener('click', handleOrbsClick);
        }
        if (popoutOrbsBtn) {
            popoutOrbsBtn.addEventListener('click', handleOrbsClick);
        }
        if (hdrOrbsChip) {
            hdrOrbsChip.addEventListener('click', handleOrbsClick);
        }
    },

    async openDiscordOrbsHub() {
        try {
            if (window.pywebview?.api?.open_discord_orbs_hub) {
                const res = await window.pywebview.api.open_discord_orbs_hub();
                if (res && res.success) return;
            }
            window.open('discord://-/quest-home', '_blank');
        } catch (err) {
            console.warn("Failed to open Discord Orbs Hub:", err);
            try {
                window.open('discord://-/quest-home', '_blank');
            } catch (_) {}
        }
    },

    async updateOrbsUI() {
        if (!window.pywebview?.api?.get_orbs_overview) return;
        try {
            const overview = await window.pywebview.api.get_orbs_overview();
            const liveBalance = overview.live_orbs !== undefined ? overview.live_orbs : (overview.earned_orbs || 0);
            const formattedLive = Number(liveBalance).toLocaleString('de-DE');

            const questsCount = document.getElementById('quests-orbs-count');
            if (questsCount) {
                questsCount.innerText = formattedLive;
            }
            const popoutCount = document.getElementById('popout-orbs-count');
            if (popoutCount) {
                popoutCount.innerText = `${formattedLive} ORBS`;
            }
            const hdrCount = document.getElementById('hdr-orbs-count');
            if (hdrCount) {
                hdrCount.innerText = formattedLive;
            }
        } catch (e) {
            console.error("updateOrbsUI error:", e);
        }
    },

    async openChangelogModal() {
        const modal = document.getElementById('changelog-modal');
        const listContainer = document.getElementById('changelog-content-list');
        const I = window.DQS_ICONS || {};
        if (!modal || !listContainer) return;

        this.makeScrollableOnWheel(listContainer);

        listContainer.innerHTML = `<div style="padding:24px;text-align:center;color:#94a3b8;"><span style="display:inline-block;animation:spin 1s linear infinite;margin-right:8px;">${I.gear || ''}</span> Lade Live-Changelog von GitHub...</div>`;
        modal.classList.remove('hidden');
        this.markChangelogAsRead();

        try {
            const data = await window.pywebview?.api?.get_changelog();
            const entries = (data && Array.isArray(data.entries) && data.entries.length > 0) ? data.entries : [];
            
            if (entries.length > 0) {
                listContainer.innerHTML = '';
                entries.forEach((item, idx) => {
                    const isCurrent = idx === 0;
                    const card = document.createElement('div');
                    card.className = `changelog-entry-card ${isCurrent ? 'card-latest' : ''}`;

                    let itemsHtml = '';
                    if (Array.isArray(item.changes)) {
                        itemsHtml = item.changes.map(ch => {
                            let clean = String(ch || '').trim().replace(/^[•\-\*\s]+/, '');
                            let formatted = clean.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                            formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
                            return `
                                <li class="changelog-point">
                                    <span class="changelog-point-bullet"></span>
                                    <span class="changelog-point-text">${formatted}</span>
                                </li>
                            `;
                        }).join('');
                    } else if (item.body) {
                        itemsHtml = `<div class="changelog-body-text">${this._parseMarkdownToHtml(item.body)}</div>`;
                    }

                    card.innerHTML = `
                        <div class="changelog-entry-header">
                            <div class="changelog-version-tag ${isCurrent ? 'version-current' : ''}">
                                ${item.version || 'Version'} ${isCurrent ? '<span class="changelog-badge-current">LIVE GITHUB</span>' : ''}
                            </div>
                            <span class="changelog-date">${item.date || ''}</span>
                        </div>
                        <h4 class="changelog-title">${item.title || ''}</h4>
                        <ul class="changelog-list">
                            ${itemsHtml}
                        </ul>
                    `;

                    // Enable smooth scrolling on the individual box/list
                    const innerList = card.querySelector('.changelog-list');
                    if (innerList) this.makeScrollableOnWheel(innerList);
                    const innerBody = card.querySelector('.changelog-body-text');
                    if (innerBody) this.makeScrollableOnWheel(innerBody);

                    listContainer.appendChild(card);
                });
            } else {
                listContainer.innerHTML = '<div style="padding:20px;text-align:center;color:#94a3b8;">Keine Changelog-Einträge gefunden.</div>';
            }
        } catch (e) {
            console.error('Failed to load changelog:', e);
            listContainer.innerHTML = '<div style="padding:20px;text-align:center;color:#f87171;">Changelog konnte nicht geladen werden.</div>';
        }
    },

    _updateDownloadUrl: null,
    _latestReleaseUrl: null,
    async checkForUpdates(isManual = false) {
        const modal = document.getElementById('update-modal');
        const toastBanner = document.getElementById('update-toast-banner');
        const I = window.DQS_ICONS || {};
        
        // Element bindings
        const statCur = document.getElementById('stat-cur-ver');
        const statLatest = document.getElementById('stat-latest-ver');
        const statState = document.getElementById('stat-release-state');
        const tagLatestSource = document.getElementById('tag-latest-source');
        const tagStatePill = document.getElementById('tag-state-pill');
        const relTitle = document.getElementById('update-release-title');
        const relMeta = document.getElementById('update-release-meta');
        const authorAvatar = document.getElementById('update-author-avatar');
        const assetName = document.getElementById('update-asset-name');
        const assetSize = document.getElementById('update-asset-size');
        const liveNotesContent = document.getElementById('update-live-notes-content');
        const progContainer = document.getElementById('update-progress-container');
        const btnAction = document.getElementById('btn-update-action');
        const btnCancel = document.getElementById('btn-update-cancel');

        if (isManual && modal) {
            modal.classList.remove('hidden');
            if (progContainer) progContainer.classList.add('hidden');
            if (liveNotesContent) {
                liveNotesContent.innerHTML = `<div class="update-loading-spinner"><span class="spin-icon">${I.gear || ''}</span> Verbinde mit GitHub Releases API (Live)...</div>`;
            }
        }

        try {
            const res = await window.pywebview?.api?.check_update();
            if (!res || !res.success) {
                if (isManual && modal) {
                    if (statState) {
                        statState.innerText = 'OFFLINE';
                        statState.className = 'stat-card-val status-val';
                        statState.style.color = '#f87171';
                    }
                    if (liveNotesContent) {
                        liveNotesContent.innerHTML = `<div style="padding:20px;text-align:center;color:#f87171;">Konnte GitHub API nicht erreichen (${res?.error || 'Netzwerkfehler'}). Bitte prüfe deine Internetverbindung.</div>`;
                    }
                }
                return;
            }

            // Populate live data
            this._updateDownloadUrl = res.download_url;
            this._latestReleaseUrl = res.html_url || 'https://github.com/TentixTV/Discord-Quest-Spoofer/releases';

            if (statCur) statCur.innerText = res.current_version || 'V6.3.0';
            if (statLatest) statLatest.innerText = res.latest_version || res.current_version;
            if (tagLatestSource) tagLatestSource.innerText = 'GitHub Live API';

            const hasNewer = Boolean(res.has_update || res.update_available);

            if (statState) {
                if (hasNewer) {
                    statState.innerText = 'UPDATE VERFÜGBAR';
                    statState.className = 'stat-card-val status-val update-ready';
                    statState.style.color = '#38bdf8';
                } else {
                    statState.innerText = '✓ AKTUELL';
                    statState.className = 'stat-card-val status-val';
                    statState.style.color = '#10b981';
                }
            }

            if (tagStatePill) {
                tagStatePill.innerText = hasNewer ? 'Neuer Build' : 'Verifiziert';
                tagStatePill.className = hasNewer ? 'stat-card-tag latest' : 'stat-card-tag pulse-tag';
            }

            if (relTitle) relTitle.innerText = res.release_name || `DQS // Release ${res.latest_version}`;
            if (relMeta) {
                const dateStr = res.published_date || 'Gerade eben';
                relMeta.innerHTML = `Erstellt von <strong>@${res.author?.login || 'TentixTV'}</strong> • Veröffentlicht am ${dateStr} • GitHub Live Stream`;
            }
            if (authorAvatar && res.author?.avatar_url) {
                authorAvatar.src = res.author.avatar_url;
            }
            if (assetName) assetName.innerText = res.asset_name || 'DQS_Installer.exe';
            if (assetSize) assetSize.innerText = `${res.asset_size_mb || 119.6} MB`;

            // Live rendered markdown notes
            if (liveNotesContent) {
                const renderedHtml = this._parseMarkdownToHtml(res.changelog);
                liveNotesContent.innerHTML = renderedHtml;
                liveNotesContent.querySelectorAll('a').forEach(a => {
                    a.addEventListener('click', (e) => {
                        e.preventDefault();
                        window.pywebview?.api?.open_url(a.getAttribute('href'));
                    });
                });
            }

            // Buttons - 100% SVG Icons, 0% Emojis
            if (hasNewer) {
                if (!isManual && toastBanner) {
                    const toastVer = document.getElementById('toast-new-version');
                    if (toastVer) toastVer.innerText = res.latest_version;
                    toastBanner.classList.remove('hidden');
                }
                if (btnAction) {
                    btnAction.style.display = 'inline-flex';
                    btnAction.innerHTML = `${I.rocket || I.update} JETZT AKTUALISIEREN (${res.asset_size_mb || 119.6} MB)`;
                    btnAction.onclick = () => this.startUpdateProcess(res.download_url);
                }
                if (btnCancel) btnCancel.innerText = 'SPÄTER';
            } else {
                if (btnAction) {
                    btnAction.style.display = 'inline-flex';
                    btnAction.innerHTML = `${I.download || I.refresh} NEU INSTALLIEREN`;
                    btnAction.onclick = () => this.startUpdateProcess(res.download_url);
                }
                if (btnCancel) btnCancel.innerText = 'SCHLIESSEN';
            }
        } catch (e) {
            console.error('Update check error:', e);
            if (isManual && modal && liveNotesContent) {
                liveNotesContent.innerHTML = `<div style="padding:20px;text-align:center;color:#f87171;">Fehler beim Laden von GitHub: ${e.message || e}</div>`;
            }
        }
    },

    async startUpdateProcess(downloadUrl) {
        const progContainer = document.getElementById('update-progress-container');
        const progFill = document.getElementById('update-progress-fill');
        const progText = document.getElementById('update-progress-text');
        const progBytes = document.getElementById('update-download-bytes');
        const progTask = document.getElementById('update-progress-task');
        const btnAction = document.getElementById('btn-update-action');
        const btnCancel = document.getElementById('btn-update-cancel');

        if (btnAction) btnAction.style.display = 'none';
        if (btnCancel) btnCancel.style.display = 'none';
        if (progContainer) progContainer.classList.remove('hidden');

        if (progFill) progFill.style.width = '3%';
        if (progText) progText.innerText = '0%';
        if (progBytes) progBytes.innerText = '0 MB / 119.7 MB';
        if (progTask) progTask.innerText = 'Verbinde mit GitHub CDN... Starte Download...';

        // Real-time callbacks from Python updater
        window.onUpdateDownloadProgress = (pct, downloaded, total) => {
            const clamped = Math.max(0, Math.min(100, Math.round(pct)));
            if (progFill) progFill.style.width = `${clamped}%`;
            if (progText) progText.innerText = `${clamped}%`;
            const dlMb = (downloaded / (1024 * 1024)).toFixed(1);
            const totMb = (total / (1024 * 1024)).toFixed(1);
            if (progBytes) progBytes.innerText = `${dlMb} MB / ${totMb} MB`;
            if (progTask) progTask.innerText = `Lade DQS_Installer.exe herunter... (${clamped}%)`;
        };

        window.onUpdateDownloadFinished = () => {
            if (progFill) progFill.style.width = '100%';
            if (progText) progText.innerText = '100%';
            if (progTask) progTask.innerText = '✓ Download abgeschlossen! Starte Neuinstallation... Beende DQS...';
        };

        try {
            const res = await window.pywebview?.api?.download_and_install_update(downloadUrl);
            if (!res || !res.success) {
                if (progTask) progTask.innerText = 'Fehler beim Update: ' + (res?.error || 'Download fehlgeschlagen');
                if (btnCancel) {
                    btnCancel.style.display = 'inline-block';
                    btnCancel.innerText = 'SCHLIESSEN';
                }
            }
        } catch (e) {
            if (progTask) progTask.innerText = 'Fehler: ' + (e.message || e);
            if (btnCancel) {
                btnCancel.style.display = 'inline-block';
                btnCancel.innerText = 'SCHLIESSEN';
            }
        }
    },

    // --- Videos Tab ---
    renderVideosTab(quests) {
        const I = window.DQS_ICONS;
        const container = document.getElementById('videos-list');
        container.innerHTML = '';

        quests.forEach(q => {
            const card = document.createElement('div');
            card.className = 'quest-card';
            const qid = q.id;
            const gameTitle = q.game_title;
            const questName = q.quest_name;
            const videoUrl = q.video_url || q.trailer_url;
            const isVideoTask = Boolean(q.is_video_task);
            const isMobile = Boolean(q.is_mobile_task);
            const targetSec = q.target_seconds || 30;

            const b64Tile = window.DQS_EMBEDDED_ASSETS?.tiles?.[qid];
            const tileSrc = b64Tile || `assets/quests/tiles/${qid}.png`;

            let formatDesc = '';
            if (isVideoTask) {
                formatDesc = isMobile 
                    ? 'Format: Mobilgerät Video-Aufgabe (Android) | Express: ~5 Sek.' 
                    : 'Format: 720p HD MP4 (Offizieller Discord Video-Stream) | Express: ~5 Sek.';
            } else if (videoUrl) {
                formatDesc = 'Format: Offizieller HD Trailer & Vorschau | Gameplay-Quest: ~15 Min.';
            } else {
                formatDesc = 'Format: Standard Discord Game Quest | Gameplay-Quest: ~15 Min.';
            }

            card.innerHTML = `
                <div class="quest-tile-wrap">
                    <img src="${tileSrc}" alt="${gameTitle}" class="quest-tile-img" onerror="if(window.DQS_EMBEDDED_ASSETS?.tiles?.['${qid}']) this.src=window.DQS_EMBEDDED_ASSETS.tiles['${qid}']; else this.src='DQS.png';">
                </div>
                <div class="quest-info-wrap">
                    <div class="quest-header-row">
                        <span class="quest-game-title">${gameTitle} - ${questName}</span>
                        ${isMobile ? `<span class="badge-tag mobile-task">${I.gamepad} MOBILGERÄT</span>` : ''}
                    </div>
                    <div class="quest-name-sub" style="margin-top:4px;">${formatDesc}</div>
                </div>
                <div class="quest-actions-wrap">
                    ${isVideoTask ? `
                        ${videoUrl ? `
                            <button class="btn btn-secondary" id="vid-play-${qid}">
                                ${I.play} 720P HD VIDEO ANSCHAUEN
                            </button>
                        ` : ''}
                        <button class="btn btn-cyan" id="exp-btn-${qid}">
                            ${I.autofarm} ${isMobile ? 'EXPRESS (MOBIL)' : 'EXPRESS-ABSCHLUSS (5s)'}
                        </button>
                    ` : `
                        ${videoUrl ? `
                            <button class="btn btn-secondary" id="vid-play-${qid}">
                                ${I.play} TRAILER ANSEHEN
                            </button>
                        ` : ''}
                        <button class="btn btn-emerald" id="sim-btn-${qid}">
                            ${I.gamepad} IM SIMULATOR STARTEN
                        </button>
                    `}
                </div>
            `;

            if (videoUrl) {
                const vidBtn = card.querySelector(`#vid-play-${qid}`);
                if (vidBtn) {
                    vidBtn.onclick = () => {
                        this.openVideoModal(qid, gameTitle, questName, videoUrl, targetSec, isVideoTask, isMobile, q);
                    };
                }
            }
            if (isVideoTask) {
                const expBtn = card.querySelector(`#exp-btn-${qid}`);
                if (expBtn) {
                    expBtn.onclick = () => {
                        this.startExpressQuest(qid, targetSec, gameTitle, isMobile);
                    };
                }
            } else {
                const simBtn = card.querySelector(`#sim-btn-${qid}`);
                if (simBtn) {
                    simBtn.onclick = () => {
                        const targetAppId = q.selected_app?.id || q.required_app_id || q.app_id || '';
                        const targetTitle = q.selected_app?.name || q.required_game_name || q.sim_game_title || gameTitle;
                        const targetExe = q.selected_app?.exe || q.required_exe || '';
                        this.simulateQuest(targetAppId, targetTitle, targetExe);
                    };
                }
            }

            container.appendChild(card);
            this.attach3DTilt(card);
        });
    },

    // --- Simulator & Auto-Presets ---
    setupSimulator() {
        const presetSelect = document.getElementById('sim-preset-select');
        if (presetSelect) {
            presetSelect.addEventListener('change', (e) => {
                const val = e.target.value;
                const preset = this.presets.find(p => p.app_id === val);
                if (preset) {
                    const inpTitle = document.getElementById('sim-input-title');
                    const inpExe = document.getElementById('sim-input-exe');
                    const inpAppId = document.getElementById('sim-input-appid');
                    if (inpTitle) inpTitle.value = preset.title;
                    if (inpExe) inpExe.value = preset.exe;
                    if (inpAppId) inpAppId.value = preset.app_id;
                    const searchInput = document.getElementById('sim-search-input');
                    if (searchInput) searchInput.value = preset.title;
                    this.updateSimulatorPreview(preset);
                }
            });
        }

        document.getElementById('btn-start-sim')?.addEventListener('click', async () => {
            const title = document.getElementById('sim-input-title').value.trim();
            const exe = document.getElementById('sim-input-exe').value.trim();
            const appid = document.getElementById('sim-input-appid').value.trim();

            const res = await window.pywebview.api.start_simulation(appid, title, exe);
            if (res && res.success) {
                this.updateSimUI(true, title);
            }
        });

        document.getElementById('btn-stop-sim')?.addEventListener('click', async () => {
            await window.pywebview.api.stop_simulation();
            this.updateSimUI(false);
        });
    },

    setupSimulatorSearch() {
        const searchInput = document.getElementById('sim-search-input');
        const clearBtn = document.getElementById('btn-sim-search-clear');
        const dropdown = document.getElementById('sim-search-dropdown');
        const inputTitle = document.getElementById('sim-input-title');
        const inputExe = document.getElementById('sim-input-exe');
        const inputAppId = document.getElementById('sim-input-appid');
        if (!searchInput || !dropdown) return;

        let debounceTimer = null;

        const performSearch = async (val) => {
            const query = (val || '').trim();
            if (!query) {
                dropdown.innerHTML = '';
                dropdown.classList.add('hidden');
                if (clearBtn) clearBtn.classList.add('hidden');
                return;
            }
            if (clearBtn) clearBtn.classList.remove('hidden');

            let results = [];
            if (window.pywebview?.api?.search_games) {
                results = await window.pywebview.api.search_games(query, 14);
            } else {
                const qLower = query.toLowerCase();
                results = (this.presets || []).filter(p => 
                    p.name.toLowerCase().includes(qLower) || 
                    (p.exe && p.exe.toLowerCase().includes(qLower)) || 
                    p.app_id.includes(query)
                );
            }

            if (!results || results.length === 0) {
                const cleanExe = query.toLowerCase().replace(/[^a-z0-9]/g, '_') + '.exe';
                dropdown.innerHTML = `
                    <div class="sim-search-item custom-match" data-id="1205090671527071784" data-title="${query}" data-exe="${cleanExe}">
                        <img src="DQS.png" class="sim-search-item-art" alt="Art">
                        <div class="sim-search-item-info">
                            <div class="sim-search-item-name">${query}</div>
                            <div class="sim-search-item-sub">Prozess: ${cleanExe} • Neues Spiel simulieren</div>
                        </div>
                        <span class="sim-search-item-badge" style="background: rgba(99,102,241,0.2); color: #818cf8;">BENUTZERDEFINIERT</span>
                    </div>
                `;
                dropdown.classList.remove('hidden');
            } else {
                dropdown.innerHTML = results.map(r => {
                    const cover = r.game_cover_url || r.game_icon_url || 'DQS.png';
                    const exe = r.exe || (r.executables && r.executables[0]) || 'Game.exe';
                    const isVerified = Boolean(r.verified !== false);
                    return `
                        <div class="sim-search-item ${!isVerified ? 'custom-match' : ''}" data-id="${r.id || r.app_id}" data-title="${r.name || r.title}" data-exe="${exe}" data-cover="${cover}">
                            <img src="${cover}" class="sim-search-item-art" alt="Cover" onerror="this.src='DQS.png'">
                            <div class="sim-search-item-info">
                                <div class="sim-search-item-name">${r.name || r.title}</div>
                                <div class="sim-search-item-sub">Exe: ${exe} • ID: ${r.id || r.app_id}</div>
                            </div>
                            <span class="sim-search-item-badge ${isVerified ? '' : 'custom'}">${isVerified ? 'VERIFIZIERT' : 'SPOOF'}</span>
                        </div>
                    `;
                }).join('');
                dropdown.classList.remove('hidden');
            }

            dropdown.querySelectorAll('.sim-search-item').forEach(item => {
                item.addEventListener('click', () => {
                    const id = item.dataset.id;
                    const title = item.dataset.title;
                    const exe = item.dataset.exe;
                    const cover = item.dataset.cover || 'DQS.png';

                    if (inputTitle) inputTitle.value = title;
                    if (inputExe) inputExe.value = exe;
                    if (inputAppId) inputAppId.value = id;
                    searchInput.value = title;

                    const select = document.getElementById('sim-preset-select');
                    if (select) {
                        const optExists = Array.from(select.options).some(o => o.value === id);
                        if (optExists) select.value = id;
                    }

                    this.updateSimulatorPreview({
                        app_id: id,
                        title: title,
                        name: title,
                        exe: exe,
                        game_cover_url: cover,
                        verified: !item.classList.contains('custom-match')
                    });

                    dropdown.classList.add('hidden');
                });
            });
        };

        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => performSearch(e.target.value), 160);
        });

        searchInput.addEventListener('focus', () => {
            if (searchInput.value.trim().length > 0) {
                performSearch(searchInput.value);
            }
        });

        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                searchInput.value = '';
                dropdown.innerHTML = '';
                dropdown.classList.add('hidden');
                clearBtn.classList.add('hidden');
            });
        }

        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.classList.add('hidden');
            }
        });

        if (inputTitle) {
            inputTitle.addEventListener('input', () => {
                const titleVal = inputTitle.value.trim();
                const exeVal = inputExe ? inputExe.value.trim() : (titleVal.toLowerCase().replace(/[^a-z0-9]/g, '_') + '.exe');
                const appIdVal = inputAppId ? inputAppId.value.trim() : '1205090671527071784';
                this.updateSimulatorPreview({
                    app_id: appIdVal,
                    title: titleVal || 'Game Simulation',
                    name: titleVal || 'Game Simulation',
                    exe: exeVal,
                    game_cover_url: null
                });
            });
        }
    },

    updateSimulatorPreview(gameInfo) {
        if (!gameInfo) return;
        const banner = document.getElementById('sim-game-preview-banner');
        const backdrop = document.getElementById('sim-preview-backdrop');
        const coverImg = document.getElementById('sim-preview-cover');
        const titleEl = document.getElementById('sim-preview-title');
        const tagVer = document.getElementById('sim-tag-verified');
        const tagExe = document.getElementById('sim-tag-exe');
        const tagAppId = document.getElementById('sim-tag-appid');

        const title = gameInfo.title || gameInfo.name || 'Spiel-Simulation';
        const exe = gameInfo.exe || 'Game.exe';
        const appId = gameInfo.app_id || gameInfo.id || '1205090671527071784';
        const cover = gameInfo.game_cover_url || gameInfo.game_icon_url || this.createDynamicGameBadge(title);

        if (titleEl) titleEl.innerText = title;
        if (tagExe) tagExe.innerText = exe;
        if (tagAppId) tagAppId.innerText = `ID: ${appId}`;
        if (tagVer) {
            tagVer.innerHTML = gameInfo.verified !== false ? `<span class="tag-icon">✔</span> VERIFIZIERT` : `<span class="tag-icon">⚡</span> CUSTOM APP`;
            tagVer.className = gameInfo.verified !== false ? 'sim-tag verified' : 'sim-tag custom';
        }

        if (coverImg) {
            coverImg.src = cover;
            coverImg.onerror = () => {
                coverImg.onerror = null;
                coverImg.src = this.createDynamicGameBadge(title);
            };
        }
        if (backdrop) {
            backdrop.style.backgroundImage = `url("${cover}")`;
        }
        if (banner) {
            banner.style.display = 'block';
        }
    },

    async loadPresets() {
        if (!window.pywebview?.api) return;
        const presets = await window.pywebview.api.get_presets();
        this.presets = presets || [];

        const select = document.getElementById('sim-preset-select');
        if (select) {
            select.innerHTML = '';
            this.presets.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.app_id;
                opt.innerText = `${p.name} (${p.category})`;
                select.appendChild(opt);
            });
        }

        if (this.presets.length > 0) {
            this.updateSimulatorPreview(this.presets[0]);
        }
    },

    simulateQuest(appId, gameTitle, customExe) {
        this.switchTab('simulator');

        // Match preset
        let matched = this.presets.find(p => String(p.app_id) === String(appId) || p.name.toLowerCase().includes(gameTitle.toLowerCase()) || gameTitle.toLowerCase().includes(p.name.toLowerCase()));
        if (!matched) {
            for (const q of (this.cachedQuests || [])) {
                const found = (q.supported_applications || []).find(a => String(a.id) === String(appId));
                if (found && found.exe) {
                    matched = {
                        app_id: found.id,
                        title: found.title || found.name,
                        exe: found.exe
                    };
                    break;
                }
            }
        }

        const finalExe = customExe || (matched ? matched.exe : (gameTitle.toLowerCase().replace(/[^a-z0-9]/g, '_') + '.exe'));
        const finalTitle = matched ? matched.title : gameTitle;
        const finalAppId = appId || (matched ? matched.app_id : '1205090671527071784');

        if (matched && document.getElementById('sim-preset-select')) {
            document.getElementById('sim-preset-select').value = matched.app_id;
        }
        document.getElementById('sim-input-title').value = finalTitle;
        document.getElementById('sim-input-exe').value = finalExe;
        document.getElementById('sim-input-appid').value = finalAppId;

        // Auto start simulation
        document.getElementById('btn-start-sim').click();
    },

    async pollSimStatus() {
        if (!window.pywebview?.api) return;
        const st = await window.pywebview.api.get_sim_status();
        if (st) {
            this.updateSimUI(st.running, st.game_name, st.elapsed_seconds, st);
        }
    },

    updateSimUI(running, gameName, elapsedSec = 0, st = null) {
        const badge = document.getElementById('sim-status-badge');
        const startBtn = document.getElementById('btn-start-sim');
        const stopBtn = document.getElementById('btn-stop-sim');
        const actTitle = document.getElementById('sim-active-title');
        const actState = document.getElementById('sim-active-state');
        const actTimer = document.getElementById('sim-active-timer');

        const simFill = document.getElementById('sim-progress-fill');
        const simVal = document.getElementById('sim-progress-val');
        const simStatus = document.getElementById('sim-footer-status');
        const simSyncTag = document.getElementById('sim-status-sync-tag');

        const tgtSec = (st && st.target_seconds) ? st.target_seconds : 900;
        // Keep active simulation time and live quest progress in 100% exact sync:
        const curSec = (st && typeof st.current_seconds === 'number' && st.current_seconds > 0)
            ? st.current_seconds
            : elapsedSec;
        const pct = Math.min(100, Math.max(0, (curSec / tgtSec) * 100));

        if (running) {
            this._standaloneSimRunning = true;
            badge.innerText = 'SIMULATION LÄUFT';
            badge.style.color = 'var(--emerald)';
            badge.style.borderColor = 'var(--emerald)';
            startBtn.disabled = true;
            stopBtn.disabled = false;

            const gName = (gameName || 'Spiel').toUpperCase();
            actTitle.innerText = gName;
            actState.innerText = 'Win32 Prozess & Rich Presence Heartbeats an Discord aktiv.';

            const m = String(Math.floor(elapsedSec / 60)).padStart(2, '0');
            const s = String(elapsedSec % 60).padStart(2, '0');
            actTimer.innerText = `Zeit: ${m}:${s} Min.`;

            // Simulator Live Sync Progress Bar - synchronized 1:1 with running time
            if (simSyncTag) {
                simSyncTag.innerHTML = '<span class="pulse-dot"></span> LIVE-SYNC MIT DISCORD AKTIV';
                simSyncTag.style.borderColor = 'rgba(0, 240, 255, 0.6)';
                simSyncTag.style.color = '#38bdf8';
            }
            if (simFill) {
                simFill.style.width = `${pct.toFixed(1)}%`;
                simFill.classList.add('active-glow');
                if (pct >= 100) simFill.classList.add('completed');
                else simFill.classList.remove('completed');
            }
            const cm = String(Math.floor(curSec / 60)).padStart(2, '0');
            const cs = String(curSec % 60).padStart(2, '0');
            const tm = String(Math.floor(tgtSec / 60)).padStart(2, '0');

            if (simVal) {
                if (pct >= 100) {
                    simVal.innerText = '100% - QUEST ERFÜLLT! (BELOHNUNG IN DISCORD BEREIT)';
                    simVal.classList.add('completed');
                } else {
                    simVal.innerText = `${cm}:${cs} / ${tm}:00 MIN. (${pct.toFixed(0)}%)`;
                    simVal.classList.remove('completed');
                }
            }
            if (simStatus) {
                if (pct >= 100) {
                    simStatus.innerText = 'STATUS: 100% ERREICHT • BELOHNUNG IM DISCORD QUESTS-TAB ABHOLBAR';
                    simStatus.style.color = 'var(--emerald)';
                } else {
                    simStatus.innerText = `STATUS: LIVE-SYNC AKTIV • FORTSCHRITT: ${cm}:${cs} / ${tm}:00 MIN. (${pct.toFixed(0)}%)`;
                    simStatus.style.color = '#38bdf8';
                }
            }

            // Live-Sync progress in Quests Tab simultaneously
            if (st && st.quest_id) {
                const qFill = document.getElementById(`fill-quest-${st.quest_id}`);
                const qVal = document.getElementById(`val-quest-${st.quest_id}`);
                if (qFill) {
                    qFill.style.width = `${pct}%`;
                    qFill.classList.add('active-glow');
                    if (pct >= 100) qFill.classList.add('completed');
                }
                if (qVal) {
                    const cm = Math.floor(curSec / 60);
                    const tm = Math.round(tgtSec / 60);
                    if (pct >= 100) {
                        qVal.innerText = `${tm}/${tm} MIN. (100%) - QUEST ERFÜLLT!`;
                        qVal.classList.add('completed');
                    } else {
                        qVal.innerText = `${cm}/${tm} MIN. (${Math.round(pct)}%)`;
                    }
                }
            }
        } else {
            badge.innerText = 'BEREIT';
            badge.style.color = 'var(--text-muted)';
            badge.style.borderColor = 'var(--card-border)';
            startBtn.disabled = false;
            stopBtn.disabled = true;

            actTitle.innerText = 'Keine aktive Simulation';
            actState.innerText = 'Wähle ein Spiel und klicke auf Simulation starten.';
            actTimer.innerText = 'Zeit: 00:00 Min.';

            if (simSyncTag) {
                simSyncTag.innerHTML = '<span class="pulse-dot"></span> LIVE-SYNC STANDBY';
                simSyncTag.style.borderColor = 'rgba(255, 255, 255, 0.15)';
                simSyncTag.style.color = '#94a3b8';
            }
            if (simFill) {
                simFill.style.width = '0%';
                simFill.classList.remove('active-glow', 'completed');
            }
            if (simVal) {
                simVal.innerText = '00:00 / 15:00 MIN. (0%)';
                simVal.classList.remove('completed');
            }
            if (simStatus) {
                simStatus.innerText = 'STATUS: STANDBY • WARTET AUF SPIEL-START';
                simStatus.style.color = '#64748b';
            }
        }

        // Live Sync Quest Cards in Quests Tab
        if (this.cachedQuests && this.cachedQuests.length > 0) {
            this.cachedQuests.forEach(q => {
                const qid = q.id;
                const actBox = document.getElementById(`act-box-${qid}`);
                const card = actBox ? actBox.closest('.quest-card') : null;
                const fill = document.getElementById(`fill-quest-${qid}`);
                const val = document.getElementById(`val-quest-${qid}`);

                const isThisActive = running && (
                    (st?.quest_id && st.quest_id === qid) ||
                    (st?.app_id && (String(q.app_id) === String(st.app_id) || q.supported_applications?.some(a => String(a.id) === String(st.app_id))))
                );

                if (isThisActive) {
                    if (card) card.classList.add('live-synced-active');
                    const qTgt = q.target_seconds || 900;
                    const qCur = Math.min(qTgt, (q.current_seconds || 0) + elapsedSec);
                    const qPct = Math.min(100, Math.max(0, Math.round((qCur / qTgt) * 100)));

                    if (fill) {
                        fill.style.width = `${qPct}%`;
                        fill.classList.add('express-animating');
                        if (qPct >= 100) fill.classList.add('completed');
                    }
                    if (val) {
                        const curM = Math.floor(qCur / 60);
                        const tgtM = Math.round(qTgt / 60);
                        if (qPct >= 100 || q.completed || q.claimed) {
                            val.innerText = `${curM}/${tgtM} MIN. (100%) - QUEST ERFÜLLT!`;
                            val.classList.add('completed');
                        } else {
                            val.innerText = `${curM}/${tgtM} MIN. (${qPct}%) - LIVE GESYNCT`;
                            val.classList.add('live-sync');
                        }
                    }
                } else {
                    if (card) card.classList.remove('live-synced-active');
                    if (val) val.classList.remove('live-sync');
                    if (fill && !fill.classList.contains('buffer')) fill.classList.remove('express-animating');
                }
            });
        }

        // Live update Discord Profile Popout activity
        this.updateProfileActivity(running, gameName, elapsedSec);
    },

    updateProfileActivity(simRunning, gameName, elapsedSec = 0) {
        const card = document.getElementById('profile-activity-card');
        const popGame = document.getElementById('pop-act-game');
        const popState = document.getElementById('pop-act-state');
        const popTimer = document.getElementById('pop-act-timer');
        if (!popGame || !popState || !popTimer) return;

        if (simRunning) {
            if (card) {
                card.classList.remove('activity-idle');
                card.classList.add('activity-active');
            }
            const gName = (gameName || 'Spiel').toUpperCase();
            popGame.innerText = gName;
            popState.innerText = 'In Mission (Quest läuft • RP aktiv)';
            const m = String(Math.floor(elapsedSec / 60)).padStart(2, '0');
            const s = String(elapsedSec % 60).padStart(2, '0');
            popTimer.innerText = `Laufzeit: ${m}:${s} Min.`;
        } else if (this.autoFarmRunning) {
            if (card) {
                card.classList.remove('activity-idle');
                card.classList.add('activity-active');
            }
            popGame.innerText = this.currentFarmQuestName || 'AUTO-QUEST COMPLETER';
            popState.innerText = 'Automatische Quest-Bearbeitung aktiv';
            popTimer.innerText = this.currentFarmDurationText ? `Dauer: ${this.currentFarmDurationText}` : 'In Bearbeitung...';
        } else if (this.activeExpressVideoTitle) {
            if (card) {
                card.classList.remove('activity-idle');
                card.classList.add('activity-active');
            }
            popGame.innerText = this.activeExpressVideoTitle;
            popState.innerText = 'Express-Abschluss läuft...';
            popTimer.innerText = 'Status: Live CDN Synchronisation';
        } else {
            if (card) {
                card.classList.remove('activity-active');
                card.classList.add('activity-idle');
            }
            popGame.innerText = 'DQS // Discord Quest Spoofer (V6.3.0)';
            popState.innerText = 'Bereit für Quest-Simulation';
            popTimer.innerText = 'Status: Standby • Discord RPC & Rust Core aktiv';
        }
    },

    // --- Console Tab ---
    async setupConsoleTab() {
        const I = window.DQS_ICONS;
        const codeArea = document.getElementById('console-code-area');
        const copyBtn = document.getElementById('btn-copy-console');

        if (window.pywebview?.api) {
            const script = await window.pywebview.api.get_console_script();
            codeArea.value = script;
        }

        copyBtn.addEventListener('click', async () => {
            await window.pywebview?.api?.copy_to_clipboard(codeArea.value);
            copyBtn.innerHTML = `${I.check} IN ZWISCHENABLAGE KOPIERT! Jetzt in Discord Strg+Shift+I -> Console -> Enter`;
            setTimeout(() => {
                copyBtn.innerHTML = `${I.copy} 1-KLICK SKRIPT IN ZWISCHENABLAGE KOPIEREN`;
            }, 3500);
        });

        // Top Toolbar Buttons
        document.getElementById('btn-refresh-quests').onclick = () => this.refreshQuests();
        document.getElementById('btn-enroll-all').onclick = async () => {
            await window.pywebview?.api?.enroll_all_quests();
            this.refreshQuests();
        };

        const btnAutoFarm = document.getElementById('btn-toggle-autofarm');
        if (btnAutoFarm) btnAutoFarm.onclick = () => this.toggleAutoFarm();

        const btnHeroAutoFarm = document.getElementById('btn-hero-autofarm');
        if (btnHeroAutoFarm) btnHeroAutoFarm.onclick = () => this.toggleAutoFarm();

        // Clear Logs
        document.getElementById('btn-clear-logs').onclick = () => {
            document.getElementById('terminal-logs').innerHTML = '';
        };
    },

    async toggleAutoFarm() {
        if (!window.pywebview?.api) return;
        const res = await window.pywebview.api.toggle_auto_farm();
        if (res) {
            this.updateAutoQuestOverviewUI(res);
        }
    },

    updateAutoQuestOverviewUI(overview) {
        if (!overview) return;
        const durText = overview.duration_text || '(0 Min.)';

        const durTag = document.getElementById('btn-autofarm-duration');
        if (durTag) durTag.innerText = durText;

        const heroDurVal = document.getElementById('hero-duration-val');
        if (heroDurVal) heroDurVal.innerText = durText;

        const heroBtnDur = document.getElementById('hero-btn-duration');
        if (heroBtnDur) heroBtnDur.innerText = durText;

        const pill = document.getElementById('autofarm-status-pill');
        const heroBtn = document.getElementById('btn-hero-autofarm');
        const toolBtn = document.getElementById('btn-toggle-autofarm');
        const heroLabel = document.getElementById('hero-btn-label');
        const toolLabel = document.getElementById('btn-autofarm-label');
        const tracker = document.getElementById('autofarm-live-tracker');

        if (overview.running) {
            if (pill) {
                pill.className = 'autofarm-status-pill running';
                pill.innerText = 'LÄUFT';
            }
            if (heroBtn) {
                heroBtn.className = 'btn btn-crimson btn-lg btn-hero-autofarm';
            }
            if (toolBtn) {
                toolBtn.className = 'btn btn-crimson btn-glow';
            }
            if (heroLabel) heroLabel.innerText = 'AUTO-QUEST STOPPEN';
            if (toolLabel) toolLabel.innerText = 'STOPPEN';
            if (tracker) tracker.style.display = 'block';
        } else {
            if (pill) {
                pill.className = 'autofarm-status-pill idle';
                pill.innerText = (overview.open_count && overview.open_count > 0) ? 'BEREIT' : 'ERFÜLLT';
            }
            if (heroBtn) {
                heroBtn.className = 'btn btn-emerald btn-lg btn-hero-autofarm';
            }
            if (toolBtn) {
                toolBtn.className = 'btn btn-emerald btn-glow';
            }
            if (heroLabel) heroLabel.innerText = 'ALLE QUESTS JETZT STARTEN';
            if (toolLabel) toolLabel.innerText = 'ALLE QUESTS ERLEDIGEN';
            if (tracker) tracker.style.display = 'none';
        }
    }
};

// Global Callbacks invoked from Python
window.appendLog = function(msg, level) {
    const term = document.getElementById('terminal-logs');
    if (!term) return;
    const line = document.createElement('div');
    line.className = `log-line ${level.toLowerCase()}`;
    const t = new Date().toLocaleTimeString();
    line.innerText = `[${t}] [${level}] ${msg}`;
    term.appendChild(line);
    term.scrollTop = term.scrollHeight;
};

window.onQuestsUpdated = function() {
    if (window.DQS) DQS.refreshQuests();
};

window.onAutoQuestProgress = function(pInfo) {
    if (!pInfo) return;
    const tracker = document.getElementById('autofarm-live-tracker');
    if (tracker) tracker.style.display = 'block';

    const curQuest = document.getElementById('live-current-quest');
    if (curQuest) {
        curQuest.innerText = `Aktuell: [${pInfo.current_index}/${pInfo.total_count}] ${pInfo.game_title} (${pInfo.progress_percent.toFixed(0)}%)`;
    }

    const liveRem = document.getElementById('live-rem-val');
    if (liveRem) {
        liveRem.innerText = pInfo.overall_duration_text || `(ca. ${Math.ceil(pInfo.remaining_seconds / 60)} Min.)`;
    }

    const fill = document.getElementById('hero-progress-fill');
    if (fill && pInfo.total_count > 0) {
        const overallPct = ((pInfo.current_index - 1 + (pInfo.progress_percent / 100)) / pInfo.total_count * 100);
        fill.style.width = `${Math.min(100, Math.max(0, overallPct)).toFixed(1)}%`;
    }

    // Live update countdown in buttons
    const durTag = document.getElementById('btn-autofarm-duration');
    if (durTag && pInfo.overall_duration_text) durTag.innerText = pInfo.overall_duration_text;

    const heroBtnDur = document.getElementById('hero-btn-duration');
    if (heroBtnDur && pInfo.overall_duration_text) heroBtnDur.innerText = pInfo.overall_duration_text;

    const heroDurVal = document.getElementById('hero-duration-val');
    if (heroDurVal && pInfo.overall_duration_text) heroDurVal.innerText = pInfo.overall_duration_text;

    const pill = document.getElementById('autofarm-status-pill');
    if (pill) {
        pill.className = 'autofarm-status-pill running';
        pill.innerText = `LÄUFT [${pInfo.current_index}/${pInfo.total_count}]`;
    }

    const heroBtn = document.getElementById('btn-hero-autofarm');
    if (heroBtn) heroBtn.className = 'btn btn-crimson btn-lg btn-hero-autofarm';

    const toolBtn = document.getElementById('btn-toggle-autofarm');
    if (toolBtn) toolBtn.className = 'btn btn-crimson btn-glow';

    const heroLabel = document.getElementById('hero-btn-label');
    if (heroLabel) heroLabel.innerText = 'AUTO-QUEST STOPPEN';

    const toolLabel = document.getElementById('btn-autofarm-label');
    if (toolLabel) toolLabel.innerText = 'STOPPEN';

    if (window.DQS) {
        DQS.autoFarmRunning = true;
        DQS.currentFarmQuestName = pInfo.game_title ? `Auto: ${pInfo.game_title}` : 'Auto-Quest';
        DQS.currentFarmDurationText = pInfo.overall_duration_text || '';
        DQS.updateProfileActivity(false, null, 0);
    }
};

window.onAutoQuestFinished = function(totalOrbs) {
    if (window.DQS) {
        DQS.autoFarmRunning = false;
        DQS.currentFarmQuestName = null;
        DQS.currentFarmDurationText = null;
        DQS.updateProfileActivity(false, null, 0);
    }
    const pill = document.getElementById('autofarm-status-pill');
    if (pill) {
        pill.className = 'autofarm-status-pill idle';
        pill.innerText = 'ALLE ERLEDIGT!';
    }
    const heroLabel = document.getElementById('hero-btn-label');
    if (heroLabel) heroLabel.innerText = 'ALLE QUESTS ERLEDIGT!';
    const heroBtn = document.getElementById('btn-hero-autofarm');
    if (heroBtn) heroBtn.className = 'btn btn-emerald btn-lg btn-hero-autofarm';

    const toolLabel = document.getElementById('btn-autofarm-label');
    if (toolLabel) toolLabel.innerText = 'ALLE QUESTS ERLEDIGEN';
    const toolBtn = document.getElementById('btn-toggle-autofarm');
    if (toolBtn) toolBtn.className = 'btn btn-emerald btn-glow';

    setTimeout(() => {
        const tracker = document.getElementById('autofarm-live-tracker');
        if (tracker) tracker.style.display = 'none';
        if (window.DQS) window.DQS.refreshQuests(true);
    }, 3000);
};

window.onAutoQuestStopped = function() {
    if (window.DQS) {
        DQS.autoFarmRunning = false;
        DQS.currentFarmQuestName = null;
        DQS.currentFarmDurationText = null;
        DQS.updateProfileActivity(false, null, 0);
        window.DQS.refreshQuests(true);
    }
};

window.onFarmProgress = function(pInfo) {
    if (pInfo && pInfo.quest_id && window.DQS) {
        DQS.refreshQuests(true);
    }
};

window.onExpressProgress = function(data, p2) {
    if (typeof data === 'string' && typeof p2 === 'number') {
        window.DQS?.handleExpressProgress({ quest_id: data, percent: p2 });
    } else {
        window.DQS?.handleExpressProgress(data);
    }
};

window.onGameSimulationStarted = function(questId, appId, gameTitle) {
    window.DQS?.handleGameSimulationStarted(questId, appId, gameTitle);
};

// Start when PyWebView is ready (guaranteed single execution)
let dqsInitialized = false;
function initDQSOnce() {
    if (dqsInitialized) return;
    dqsInitialized = true;
    DQS.init();
}

if (window.pywebview && window.pywebview.api) {
    initDQSOnce();
} else {
    window.addEventListener('pywebviewready', () => {
        initDQSOnce();
    });
}
