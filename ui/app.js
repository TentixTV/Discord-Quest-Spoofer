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
        this.setupConsoleTab();
        this.setupVideoModal();
        this.setupLicenseModal();
        this.setupTutorialModal();

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
    },

    // --- High-Fidelity V6 Sound Engine (Ambient Drone & Joy-Con Snap Click) ---
    _audioCtx: null,
    _ambientAudio: null,
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
        try {
            if (window.DQS_EMBEDDED_ASSETS?.startup_ambient) {
                const aud = new Audio(window.DQS_EMBEDDED_ASSETS.startup_ambient);
                aud.volume = 0.35; // Comfortable, rich atmospheric drone
                aud.play().catch(() => {});
                this._ambientAudio = aud;
                return;
            }
        } catch (e) {}

        // Web Audio API procedural synthesis fallback
        try {
            const ctx = this.getAudioCtx();
            if (!ctx) return;
            const now = ctx.currentTime;
            const masterGain = ctx.createGain();
            masterGain.gain.setValueAtTime(0.001, now);
            masterGain.gain.exponentialRampToValueAtTime(0.18, now + 1.2);
            masterGain.gain.setValueAtTime(0.18, now + Math.max(0.5, duration - 0.8));
            masterGain.gain.exponentialRampToValueAtTime(0.001, now + duration);
            masterGain.connect(ctx.destination);

            const sub = ctx.createOscillator();
            sub.type = 'sine';
            sub.frequency.setValueAtTime(55, now);
            sub.frequency.exponentialRampToValueAtTime(65, now + duration);
            sub.connect(masterGain);
            sub.start(now);
            sub.stop(now + duration);

            [110, 164.81, 220].forEach((f, idx) => {
                const osc = ctx.createOscillator();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(f, now);
                osc.frequency.linearRampToValueAtTime(f * 1.05, now + duration);
                const g = ctx.createGain();
                g.gain.value = 0.10 / (idx + 1);
                osc.connect(g);
                g.connect(masterGain);
                osc.start(now);
                osc.stop(now + duration);
            });
        } catch (err) {}
    },

    playTransitionClick() {
        if (this._ambientAudio) {
            try {
                this._ambientAudio.pause();
                this._ambientAudio = null;
            } catch (e) {}
        }

        // 1. Try embedded warm/stumpf transition snap & mechanical lock
        try {
            if (window.DQS_EMBEDDED_ASSETS?.transition_click) {
                const click = new Audio(window.DQS_EMBEDDED_ASSETS.transition_click);
                click.volume = 0.88;
                click.play().catch(() => {});
                return;
            }
        } catch (e) {}

        // 2. Procedural Warm/Stumpf Transition Thud & Lock Fallback (~380ms)
        try {
            const ctx = this.getAudioCtx();
            if (!ctx) return;
            const now = ctx.currentTime;

            // Damped mechanical click (rounded, stumpf)
            const osc1 = ctx.createOscillator();
            osc1.type = 'triangle';
            osc1.frequency.setValueAtTime(650, now);
            osc1.frequency.exponentialRampToValueAtTime(160, now + 0.04);
            const g1 = ctx.createGain();
            g1.gain.setValueAtTime(0.70, now);
            g1.gain.exponentialRampToValueAtTime(0.001, now + 0.045);
            osc1.connect(g1);
            g1.connect(ctx.destination);
            osc1.start(now);
            osc1.stop(now + 0.05);

            // Warm low-mid latch thud
            const t2 = now + 0.012;
            const osc2 = ctx.createOscillator();
            osc2.type = 'sine';
            osc2.frequency.setValueAtTime(280, t2);
            osc2.frequency.exponentialRampToValueAtTime(110, t2 + 0.06);
            const g2 = ctx.createGain();
            g2.gain.setValueAtTime(0.75, t2);
            g2.gain.exponentialRampToValueAtTime(0.001, t2 + 0.08);
            osc2.connect(g2);
            g2.connect(ctx.destination);
            osc2.start(t2);
            osc2.stop(t2 + 0.09);

            // Ambient matching harmonic body (165Hz & 220Hz)
            [164.81, 220.0].forEach((f, idx) => {
                const oscR = ctx.createOscillator();
                oscR.type = 'sine';
                oscR.frequency.setValueAtTime(f, now + 0.008);
                const gr = ctx.createGain();
                gr.gain.setValueAtTime(0.40 / (idx + 1), now + 0.008);
                gr.gain.exponentialRampToValueAtTime(0.0001, now + 0.38);
                oscR.connect(gr);
                gr.connect(ctx.destination);
                oscR.start(now + 0.008);
                oscR.stop(now + 0.40);
            });
        } catch (e) {}
    },

    // --- Startup Splash Screen Animation (Random 4 - 12 Seconds) ---
    runStartupSplash() {
        const splash = document.getElementById('dqs-startup-splash');
        const bar = document.getElementById('splash-progress-bar');
        const status = document.getElementById('splash-status-text');
        const root = document.getElementById('app-root');
        if (!splash || !bar || !status) return;

        // Random duration between 4000ms and 12000ms (4 - 12 Sekunden immer unterschiedlich)
        const totalDuration = Math.floor(Math.random() * (12000 - 4000 + 1)) + 4000;
        let elapsed = 0;
        const intervalMs = 60;

        // Play subtle atmospheric startup soundscape
        this.playStartupAmbient(totalDuration / 1000);

        const getStatusText = (pct) => {
            if (pct < 16) return 'INITIALISIERE QUANTUM KERN-SYSTEME...';
            if (pct < 34) return 'LADE DISCORD QUEST ENGINE (V6)...';
            if (pct < 52) return 'LOKALISIERE DETECTABLE GAMES & PROZESSE...';
            if (pct < 70) return 'SYNCHRONISIERE DISCORD RPC & HEARTBEATS...';
            if (pct < 86) return 'VERIFIZIERE SICHERHEITS-SCHUTZ & LOKALE TOKEN...';
            if (pct < 98) return 'FINALE KALIBRIERUNG DES CLIENTS...';
            return 'SYSTEM BEREIT - POPPING UP...';
        };

        const timer = setInterval(() => {
            elapsed += intervalMs;
            const progressRatio = Math.min(1.0, elapsed / totalDuration);
            // Ease-out cubic curve for natural, organic high-tech loading feel
            const easedRatio = 1 - Math.pow(1 - progressRatio, 3);
            const currentPct = Math.min(100, Math.round(easedRatio * 100));

            if (bar) bar.style.width = `${currentPct}%`;
            if (status) status.innerText = getStatusText(currentPct);

            if (elapsed >= totalDuration) {
                clearInterval(timer);
                if (bar) bar.style.width = '100%';
                if (status) status.innerText = 'SYSTEM BEREIT - POPPING UP...';

                setTimeout(() => {
                    // Play the satisfying Joy-Con snap click right at popup!
                    this.playTransitionClick();
                    if (splash) splash.classList.add('splash-pop-exit');
                    if (root) root.classList.add('app-pop-enter');
                    setTimeout(() => {
                        if (splash && splash.parentNode) {
                            splash.parentNode.removeChild(splash);
                        }
                    }, 600);
                }, 200);
            }
        }, intervalMs);
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
        setHtml('btn-win-max', I.max);
        setHtml('btn-win-close', I.close);

        setHtml('ico-hdr-quests', I.quest);
        setHtml('ico-disclaimer-shield', I.shield);
        setHtml('ico-btn-refresh', I.refresh);
        setHtml('ico-btn-enroll', I.quest);
        setHtml('ico-btn-autofarm', I.autofarm);
        setHtml('ico-hero-autofarm', I.autofarm);
        setHtml('ico-hero-play', I.play);

        setHtml('ico-hdr-videos', I.video);
        setHtml('ico-hdr-sim', I.gamepad);
        setHtml('ico-btn-start-sim', I.play);
        setHtml('ico-sim-monitor', I.gamepad);

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
        setHtml('btn-close-account-modal', I.close);

        setHtml('ico-modal-video', I.video);
        setHtml('btn-close-video-modal', I.close);
        setHtml('ico-modal-express', I.autofarm);

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
        document.getElementById('btn-win-min').addEventListener('click', () => {
            window.pywebview?.api?.minimize_window();
        });
        document.getElementById('btn-win-max').addEventListener('click', () => {
            window.pywebview?.api?.maximize_window();
        });
        document.getElementById('btn-win-close').addEventListener('click', () => {
            window.pywebview?.api?.close_window();
        });
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
        document.getElementById('btn-switch-account').addEventListener('click', () => {
            this.openAccountModal();
        });
        document.getElementById('btn-close-account-modal').addEventListener('click', () => {
            document.getElementById('account-modal').classList.add('hidden');
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
                // Auto-link URLs cleanly
                const linked = escaped.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" class="bio-link" target="_blank">$1</a>');
                bioBox.innerHTML = linked;
                bioBox.querySelectorAll('.bio-link').forEach(link => {
                    link.addEventListener('click', (e) => {
                        e.preventDefault();
                        const url = link.getAttribute('href');
                        window.pywebview?.api?.open_url(url);
                    });
                });
            } else {
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

        // Tile source: Base64 first, fallback to HTTP/file
        const b64Tile = window.DQS_EMBEDDED_ASSETS?.tiles?.[qid];
        const tileSrc = b64Tile || `assets/quests/tiles/${qid}.png`;

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
                <img src="${tileSrc}" alt="${gameTitle}" class="quest-tile-img" onerror="if(window.DQS_EMBEDDED_ASSETS?.tiles?.['${qid}']) this.src=window.DQS_EMBEDDED_ASSETS.tiles['${qid}']; else this.src='DQS.png';">
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
                        this.openVideoModal(qid, gameTitle, questName, videoUrl, targetSeconds);
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
                        this.openVideoModal(qid, gameTitle, `${questName} (Trailer)`, q.trailer_url, 30);
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

    // --- Interactive Moving Express Quest Completer ---
    startExpressQuest(qid, targetSeconds = 30, gameTitle = '', isMobile = false) {
        const I = window.DQS_ICONS;
        this.activeExpressVideoTitle = gameTitle ? `Video: ${gameTitle}` : 'Express Video Stream';
        this.updateProfileActivity(false, null, 0);

        const fillQuest = document.getElementById(`fill-quest-${qid}`);
        const valQuest = document.getElementById(`val-quest-${qid}`);
        const trackQuest = document.getElementById(`track-quest-${qid}`);
        const fillBuffer = document.getElementById(`fill-buffer-${qid}`);
        const valBuffer = document.getElementById(`val-buffer-${qid}`);
        const btnExp = document.getElementById(`btn-exp-${qid}`) || document.getElementById(`exp-btn-${qid}`);

        if (btnExp && btnExp.disabled) return;
        if (btnExp) {
            btnExp.disabled = true;
            btnExp.classList.add('btn-glow');
        }

        if (fillQuest) fillQuest.classList.add('express-animating');
        if (trackQuest) trackQuest.classList.add('express-active');
        if (fillBuffer) fillBuffer.classList.add('express-animating');

        // Call backend completion asynchronously with isMobile
        window.pywebview?.api?.complete_video_quest(qid, targetSeconds, isMobile);

        let elapsed = 0;
        const totalDuration = 4500; // 4.5 seconds for complete visual cycle
        const intervalMs = 150;
        const startPercent = fillQuest ? parseFloat(fillQuest.style.width) || 0 : 0;

        const timer = setInterval(() => {
            elapsed += intervalMs;
            const progressRatio = Math.min(1.0, elapsed / totalDuration);
            // Ease-out cubic curve
            const easedRatio = 1 - Math.pow(1 - progressRatio, 3);
            const currentPct = Math.min(100, Math.round(startPercent + (100 - startPercent) * easedRatio));
            const remSec = Math.max(1, Math.ceil((totalDuration - elapsed) / 1000));

            if (fillQuest) fillQuest.style.width = `${currentPct}%`;
            if (valQuest) {
                valQuest.innerText = `FORTSCHRITT: ${currentPct}% (ca. ${remSec}s)...`;
            }
            if (valBuffer) {
                valBuffer.innerText = `BUFFER: SYNCHRONISIERT (${currentPct}%)`;
            }
            if (btnExp) {
                btnExp.innerHTML = `${I.autofarm} EXPRESS LÄUFT... (${remSec}s)`;
            }

            if (elapsed >= totalDuration) {
                clearInterval(timer);
                if (fillQuest) {
                    fillQuest.style.width = '100%';
                    fillQuest.classList.remove('express-animating');
                    fillQuest.classList.add('completed');
                }
                if (valQuest) {
                    valQuest.innerText = `100% - QUEST ERFÜLLT!`;
                    valQuest.classList.add('completed');
                }
                if (valBuffer) {
                    valBuffer.innerText = `SYNCHRONISIERT (100%)`;
                }
                if (btnExp) {
                    btnExp.innerHTML = `${I.check} ERFOLGREICH!`;
                    btnExp.className = 'btn btn-claimed';
                }

                this.activeExpressVideoTitle = null;
                this.pollSimStatus();

                // Play notification
                window.pywebview?.api?.play_success_sound();

                setTimeout(() => {
                    this.refreshQuests();
                }, 1200);
            }
        }, intervalMs);
    },

    // --- 720p HD Video Player Modal ---
    setupVideoModal() {
        const modal = document.getElementById('video-modal');
        const closeBtn = document.getElementById('btn-close-video-modal');
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
    },

    openVideoModal(qid, gameTitle, questName, videoUrl, targetSec) {
        const modal = document.getElementById('video-modal');
        const titleEl = document.getElementById('video-modal-title');
        const videoEl = document.getElementById('discord-video-player');
        const btnExp = document.getElementById('btn-modal-express-finish');

        if (!modal || !videoEl) return;

        titleEl.innerText = `${gameTitle} - ${questName} (720p HD Stream)`;
        videoEl.src = videoUrl;
        videoEl.currentTime = 0;
        videoEl.play().catch(() => {});

        btnExp.onclick = () => {
            this.closeVideoModal();
            this.startExpressQuest(qid, targetSec || 30, gameTitle);
        };

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
                        <button class="btn btn-emerald" onclick="DQS.simulateQuest('${q.app_id}', '${gameTitle}')">
                            ${I.gamepad} IM SIMULATOR STARTEN
                        </button>
                    `}
                </div>
            `;

            if (videoUrl) {
                const vidBtn = card.querySelector(`#vid-play-${qid}`);
                if (vidBtn) {
                    vidBtn.onclick = () => {
                        this.openVideoModal(qid, gameTitle, questName, videoUrl, targetSec);
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
            }

            container.appendChild(card);
            this.attach3DTilt(card);
        });
    },

    // --- Simulator & Auto-Presets ---
    setupSimulator() {
        document.getElementById('sim-preset-select').addEventListener('change', (e) => {
            const val = e.target.value;
            const preset = this.presets.find(p => p.app_id === val);
            if (preset) {
                document.getElementById('sim-input-title').value = preset.title;
                document.getElementById('sim-input-exe').value = preset.exe;
                document.getElementById('sim-input-appid').value = preset.app_id;
            }
        });

        document.getElementById('btn-start-sim').addEventListener('click', async () => {
            const title = document.getElementById('sim-input-title').value.trim();
            const exe = document.getElementById('sim-input-exe').value.trim();
            const appid = document.getElementById('sim-input-appid').value.trim();

            const res = await window.pywebview.api.start_simulation(appid, title, exe);
            if (res && res.success) {
                this.updateSimUI(true, title);
            }
        });

        document.getElementById('btn-stop-sim').addEventListener('click', async () => {
            await window.pywebview.api.stop_simulation();
            this.updateSimUI(false);
        });
    },

    async loadPresets() {
        if (!window.pywebview?.api) return;
        const presets = await window.pywebview.api.get_presets();
        this.presets = presets || [];

        const select = document.getElementById('sim-preset-select');
        select.innerHTML = '';
        this.presets.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.app_id;
            opt.innerText = `${p.name} (${p.category})`;
            select.appendChild(opt);
        });
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

        const tgtSec = st?.target_seconds || 900;
        const curSec = st?.current_seconds ?? elapsedSec;
        const pct = Math.min(100, Math.max(0, st?.progress_percent ?? Math.round((curSec / tgtSec) * 100)));

        if (running) {
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

            // Simulator Live Sync Progress Bar
            if (simSyncTag) {
                simSyncTag.innerHTML = '<span class="pulse-dot"></span> LIVE-SYNC MIT DISCORD AKTIV';
                simSyncTag.style.borderColor = 'rgba(0, 240, 255, 0.6)';
                simSyncTag.style.color = '#38bdf8';
            }
            if (simFill) {
                simFill.style.width = `${pct}%`;
                simFill.classList.add('active-glow');
                if (pct >= 100) simFill.classList.add('completed');
                else simFill.classList.remove('completed');
            }
            if (simVal) {
                const cm = String(Math.floor(curSec / 60)).padStart(2, '0');
                const cs = String(curSec % 60).padStart(2, '0');
                const tm = String(Math.floor(tgtSec / 60)).padStart(2, '0');
                if (pct >= 100) {
                    simVal.innerText = '100% - QUEST ERFÜLLT! (BELOHNUNG IN DISCORD BEREIT)';
                    simVal.classList.add('completed');
                } else {
                    simVal.innerText = `${cm}:${cs} / ${tm}:00 MIN. (${Math.round(pct)}%)`;
                    simVal.classList.remove('completed');
                }
            }
            if (simStatus) {
                if (pct >= 100) {
                    simStatus.innerText = 'STATUS: 100% ERREICHT • BELOHNUNG IM DISCORD QUESTS-TAB ABHOLBAR';
                    simStatus.style.color = 'var(--emerald)';
                } else {
                    simStatus.innerText = `STATUS: LIVE-SYNC AKTIV • DISCORD DETEKTION BESTÄTIGT (${elapsedSec}s)`;
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
            popGame.innerText = 'DQS // Quest Engine (V5)';
            popState.innerText = 'Bereit für Quest-Simulation';
            popTimer.innerText = 'Status: Standby • Keine aktive Simulation';
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
