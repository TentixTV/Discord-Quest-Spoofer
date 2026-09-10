/**
 * DQS // High-End Discord Quest Spoofer Engine
 * JavaScript Client Architecture, 3D Physics Tilt, Dual Video Bars, and PyWebView Bridge
 * 100% Emoji-free, Ultra-crisp High-DPI SVGs, Animated Discord Orbs
 */

// ================= 1. 3D INTERACTIVE PARTICLE CANVAS =================
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

    const nodeCount = 45;
    const nodes = [];
    const colors = [
        'rgba(88, 101, 242, ', // Blurple
        'rgba(147, 51, 234, ', // Purple
        'rgba(35, 165, 90, ',  // Emerald
        'rgba(56, 189, 248, ', // Cyan
        'rgba(254, 231, 92, '  // Gold
    ];

    for (let i = 0; i < nodeCount; i++) {
        nodes.push({
            x: Math.random() * w,
            y: Math.random() * h,
            z: Math.random() * 400 + 100, // 3D depth
            radius: Math.random() * 2 + 1,
            color: colors[Math.floor(Math.random() * colors.length)],
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4
        });
    }

    function render() {
        ctx.clearRect(0, 0, w, h);
        const fov = 350;

        for (let i = 0; i < nodeCount; i++) {
            const n = nodes[i];
            n.x += n.vx;
            n.y += n.vy;

            const dx = (mouseX - w / 2) * 0.02;
            const dy = (mouseY - h / 2) * 0.02;

            if (n.x < 0) n.x = w;
            if (n.x > w) n.x = 0;
            if (n.y < 0) n.y = h;
            if (n.y > h) n.y = 0;

            const scale = fov / (fov + n.z);
            const projX = (n.x - w / 2 + dx) * scale + w / 2;
            const projY = (n.y - h / 2 + dy) * scale + h / 2;
            const projRadius = n.radius * scale;

            ctx.beginPath();
            ctx.arc(projX, projY, Math.max(0.5, projRadius), 0, Math.PI * 2);
            ctx.fillStyle = n.color + '0.7)';
            ctx.shadowBlur = 8 * scale;
            ctx.shadowColor = n.color + '0.9)';
            ctx.fill();

            for (let j = i + 1; j < nodeCount; j++) {
                const n2 = nodes[j];
                const dist = Math.hypot(n.x - n2.x, n.y - n2.y);
                if (dist < 110) {
                    const scale2 = fov / (fov + n2.z);
                    const projX2 = (n2.x - w / 2 + dx) * scale2 + w / 2;
                    const projY2 = (n2.y - h / 2 + dy) * scale2 + h / 2;

                    const alpha = (1 - dist / 110) * 0.25;
                    ctx.beginPath();
                    ctx.moveTo(projX, projY);
                    ctx.lineTo(projX2, projY2);
                    ctx.strokeStyle = `rgba(88, 101, 242, ${alpha})`;
                    ctx.lineWidth = 0.75 * scale;
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

    async init() {
        this.injectStaticIcons();
        this.renderBadges();
        this.setupWindowControls();
        this.setupNavigation();
        this.setupProfileDrawer();
        this.setupSimulator();
        this.setupConsoleTab();

        // Load data from bridge
        await this.loadCurrentUser();
        await this.loadPresets();
        await this.refreshQuests();

        // Simulator status polling
        this.pollSimStatus();
        setInterval(() => this.pollSimStatus(), 2000);
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
    },

    // --- Render Discord Badges (Base64 Guaranteed) ---
    renderBadges() {
        const container = document.getElementById('badges-container');
        if (!container) return;
        container.innerHTML = '';

        const badges = [
            { key: 'nitro', title: 'Discord Nitro 3 Jahre' },
            { key: 'bravery', title: 'HypeSquad Bravery' },
            { key: 'booster', title: 'Server Booster Level 9' },
            { key: 'legacy', title: 'Ursprünglicher Name: tentix#0001' },
            { key: 'quest', title: 'Discord Quest Meister' },
            { key: 'orbs', title: 'Orbs Sammler' }
        ];

        badges.forEach(b => {
            const img = document.createElement('img');
            img.className = 'badge-icon';
            img.title = b.title;
            img.alt = b.key;
            const b64 = window.DQS_EMBEDDED_ASSETS?.[b.key];
            img.src = b64 || `assets/badges/${b.key}.png`;
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
        this.activeTab = tabId;
        document.querySelectorAll('.nav-tab').forEach(t => {
            if (t.getAttribute('data-tab') === tabId) {
                t.classList.add('active');
            } else {
                t.classList.remove('active');
            }
        });

        document.querySelectorAll('.tab-view').forEach(v => {
            if (v.id === `tab-${tabId}`) {
                v.classList.add('active');
            } else {
                v.classList.remove('active');
            }
        });
    },

    // --- 3D Profile Popout ---
    setupProfileDrawer() {
        const pill = document.getElementById('header-user-pill');
        const popout = document.getElementById('discord-profile-popout');
        const backdrop = document.getElementById('popout-backdrop');
        const closeBtn = document.getElementById('btn-close-popout');

        const openPopout = () => {
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

        // 3D Card tilt on popout
        this.attach3DTilt(popout);

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

        document.getElementById('link-tentix-space').addEventListener('click', (e) => {
            e.preventDefault();
            window.pywebview?.api?.open_url('https://tentix.space');
        });

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
            this.currentUser = user;
            const displayName = user.global_name || user.username || 'TΞП†1Ж ツ';
            document.getElementById('hdr-username').innerText = displayName;
            document.getElementById('popout-name').innerText = displayName;
            document.getElementById('popout-handle').innerText = `${user.username || 'tentix'} • - ʜᴇᴀʀᴛ/ʟᴇꜱꜱ/ᴡɪᴛʜᴏᴜᴛ/ʏᴏᴜ -`;

            if (user.avatar && user.id) {
                const ext = user.avatar.startsWith('a_') ? 'gif' : 'png';
                const avUrl = `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.${ext}?size=128`;
                const hdrAv = document.getElementById('hdr-avatar');
                if (hdrAv) hdrAv.src = avUrl;
                const popAv = document.getElementById('pop-avatar');
                if (popAv) popAv.src = avUrl;
            }
        }
    },

    async openAccountModal() {
        const modal = document.getElementById('account-modal');
        const list = document.getElementById('modal-accounts-list');
        list.innerHTML = '<div style="padding:10px;text-align:center;">Lade Accounts...</div>';
        modal.classList.remove('hidden');

        const accs = await window.pywebview?.api?.get_accounts();
        list.innerHTML = '';

        if (!accs || accs.length === 0) {
            list.innerHTML = '<div style="padding:10px;text-align:center;color:#8e92a4;">Keine aktiven Accounts gefunden.</div>';
            return;
        }

        accs.forEach(acc => {
            const row = document.createElement('div');
            row.className = 'account-row';
            const name = acc.global_name || acc.username;
            row.innerHTML = `
                <div class="account-row-left">
                    <span>${window.DQS_ICONS.users}</span>
                    <span>${name}</span>
                </div>
                <button class="btn btn-blurple btn-small">AUSWÄHLEN</button>
            `;
            row.querySelector('button').addEventListener('click', async () => {
                const res = await window.pywebview.api.switch_account(acc.token);
                if (res.success) {
                    modal.classList.add('hidden');
                    await this.loadCurrentUser();
                    await this.refreshQuests();
                }
            });
            list.appendChild(row);
        });

        document.getElementById('btn-load-custom-token').onclick = async () => {
            const tok = document.getElementById('input-custom-token').value.trim();
            if (tok) {
                const res = await window.pywebview.api.switch_account(tok);
                if (res.success) {
                    modal.classList.add('hidden');
                    await this.loadCurrentUser();
                    await this.refreshQuests();
                } else {
                    alert('Fehler: ' + (res.error || 'Ungültiger Token'));
                }
            }
        };
    },

    // --- Quests & Cards Rendering ---
    async refreshQuests() {
        const I = window.DQS_ICONS;
        const container = document.getElementById('quests-list');

        // Futuristic Cyber Loading Screen with Skeleton Cards
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

        if (!window.pywebview?.api) return;
        const quests = await window.pywebview.api.get_quests();
        this.cachedQuests = quests || [];

        const badge = document.getElementById('quests-badge');
        if (badge) badge.innerText = this.cachedQuests.length;

        // Fetch duration and auto-quest overview
        try {
            const overview = await window.pywebview.api.get_auto_quest_overview();
            this.updateAutoQuestOverviewUI(overview);
        } catch (e) {
            console.error("Failed to load auto quest overview:", e);
        }

        container.innerHTML = '';
        if (this.cachedQuests.length === 0) {
            container.innerHTML = '<div style="padding:50px;text-align:center;color:#8e92a4;">Keine aktiven Quests auf diesem Account gefunden!</div>';
            return;
        }

        this.cachedQuests.forEach(q => {
            const card = this.createQuestCard(q);
            container.appendChild(card);
            this.attach3DTilt(card);
        });

        this.renderVideosTab(this.cachedQuests);
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
        const isVideo = videoUrl || taskType.includes('VIDEO') || q.has_video;

        // Tile source: Base64 first, fallback to HTTP/file
        const b64Tile = window.DQS_EMBEDDED_ASSETS?.tiles?.[qid];
        const tileSrc = b64Tile || `assets/quests/tiles/${qid}.png`;

        // Animated Discord Orbs Logo
        const orbImgSrc = window.DQS_EMBEDDED_ASSETS?.animated_orb || 'assets/discord_orbs_animated.gif';

        const taskIcon = isVideo ? I.video : I.gamepad;
        const taskLabel = isVideo ? 'Video-Quest' : `${Math.round(targetSeconds / 60)} Min. Spielzeit`;

        const curMin = Math.floor(currentSeconds / 60);
        const tgtMin = Math.round(targetSeconds / 60);
        let progressTxt = `${curMin}/${tgtMin} MIN. (${percent}%)`;
        if (completed || claimed) progressTxt += ' - QUEST ERFÜLLT!';

        // Build Progress Bars (2 Bars if Video, 1 Bar if Desktop)
        let progressHtml = '';
        if (isVideo) {
            progressHtml = `
                <div class="dual-progress-container">
                    <div class="progress-bar-block">
                        <div class="progress-bar-header">
                            <span class="progress-bar-label">${I.video} STREAM BUFFER & HEARTBEAT</span>
                            <span class="progress-bar-value">${completed || claimed ? 'SYNCHRONISIERT (100%)' : 'STREAM BEREIT (100%)'}</span>
                        </div>
                        <div class="progress-track buffer">
                            <div class="progress-fill buffer" style="width: 100%"></div>
                        </div>
                    </div>
                    <div class="progress-bar-block">
                        <div class="progress-bar-header">
                            <span class="progress-bar-label">${I.quest} QUEST-FORTSCHRITT</span>
                            <span class="progress-bar-value ${completed || claimed ? 'completed' : ''}">${progressTxt}</span>
                        </div>
                        <div class="progress-track">
                            <div class="progress-fill ${completed || claimed ? 'completed' : ''}" style="width: ${percent}%"></div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            progressHtml = `
                <div class="quest-progress-row">
                    <div class="progress-track">
                        <div class="progress-fill ${completed || claimed ? 'completed' : ''}" style="width: ${percent}%"></div>
                    </div>
                    <span class="progress-text ${completed || claimed ? 'completed' : ''}">${progressTxt}</span>
                </div>
            `;
        }

        card.innerHTML = `
            <div class="quest-tile-wrap">
                <img src="${tileSrc}" alt="${gameTitle}" class="quest-tile-img" onerror="if(window.DQS_EMBEDDED_ASSETS?.tiles?.['${qid}']) this.src=window.DQS_EMBEDDED_ASSETS.tiles['${qid}']; else this.src='DQS.png';">
            </div>
            <div class="quest-info-wrap">
                <div class="quest-header-row">
                    <span class="quest-game-title">${gameTitle}</span>
                    <span class="badge-tag task">${taskIcon} ${taskLabel}</span>
                    <span class="badge-tag duration">${I.clock} DAUER: <strong>${q.duration_text || (isVideo ? '(ca. 30 Sek.)' : '(ca. 15 Min.)')}</strong></span>
                    ${orbCount > 0 ? `<span class="badge-tag orbs"><img src="${orbImgSrc}" class="discord-orb-icon" alt="Orbs"> <span>${orbCount} ORBS</span></span>` : ''}
                </div>
                <div class="quest-name-sub">${questName}</div>
                ${progressHtml}
            </div>
            <div class="quest-actions-wrap" id="act-box-${qid}"></div>
        `;

        const actBox = card.querySelector(`#act-box-${qid}`);

        if (claimed) {
            actBox.innerHTML = `<button class="btn btn-claimed" disabled>${I.check} EINGELÖST</button>`;
        } else if (completed) {
            const btnClaim = document.createElement('button');
            btnClaim.className = 'btn btn-emerald';
            btnClaim.innerHTML = `${I.gift} BELOHNUNG ABHOLEN`;
            btnClaim.onclick = async () => {
                btnClaim.innerHTML = `Löst ein...`;
                await window.pywebview.api.claim_quest(qid);
                this.refreshQuests();
            };
            actBox.appendChild(btnClaim);
        } else {
            // 1. Simulate button
            const btnSim = document.createElement('button');
            btnSim.className = 'btn btn-emerald';
            btnSim.innerHTML = `${I.play} SIMULIEREN`;
            btnSim.onclick = () => {
                this.simulateQuest(appId, gameTitle);
            };
            actBox.appendChild(btnSim);

            // 2. Video button
            if (videoUrl) {
                const btnVid = document.createElement('button');
                btnVid.className = 'btn btn-secondary';
                btnVid.innerHTML = `${I.video} VIDEO`;
                btnVid.onclick = () => {
                    window.pywebview.api.open_url(videoUrl);
                };
                actBox.appendChild(btnVid);
            }

            // 3. Express button for video quests
            if (isVideo) {
                const btnExp = document.createElement('button');
                btnExp.className = 'btn btn-cyan';
                btnExp.innerHTML = `${I.autofarm} EXPRESS (5s)`;
                btnExp.onclick = async () => {
                    btnExp.innerHTML = `${I.autofarm} LÄUFT...`;
                    await window.pywebview.api.complete_video_quest(qid, targetSeconds || 30);
                    btnExp.innerHTML = `${I.check} ERFÜLLT!`;
                    setTimeout(() => { this.refreshQuests(); }, 2500);
                };
                actBox.appendChild(btnExp);
            }

            // 4. Enroll button if not yet enrolled
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
            const videoUrl = q.video_url;
            const targetSec = q.target_seconds || 30;

            const b64Tile = window.DQS_EMBEDDED_ASSETS?.tiles?.[qid];
            const tileSrc = b64Tile || `assets/quests/tiles/${qid}.png`;

            const formatDesc = videoUrl 
                ? 'Format: 720p HD MP4 (Offizieller Discord Stream) | Dauer: ~30 Sek.' 
                : 'Format: Offizieller HD Gameplay Trailer & Stream | Dauer: ~15 Min.';

            card.innerHTML = `
                <div class="quest-tile-wrap">
                    <img src="${tileSrc}" alt="${gameTitle}" class="quest-tile-img" onerror="if(window.DQS_EMBEDDED_ASSETS?.tiles?.['${qid}']) this.src=window.DQS_EMBEDDED_ASSETS.tiles['${qid}']; else this.src='DQS.png';">
                </div>
                <div class="quest-info-wrap">
                    <div class="quest-header-row">
                        <span class="quest-game-title">${gameTitle} - ${questName}</span>
                    </div>
                    <div class="quest-name-sub" style="margin-top:4px;">${formatDesc}</div>
                </div>
                <div class="quest-actions-wrap">
                    ${videoUrl ? `
                        <button class="btn btn-secondary" onclick="window.pywebview.api.open_url('${videoUrl}')">
                            ${I.play} 720P HD VIDEO ABSPIELEN
                        </button>
                        <button class="btn btn-cyan" id="exp-btn-${qid}">
                            ${I.autofarm} EXPRESS-ABSCHLUSS (5s)
                        </button>
                    ` : `
                        <button class="btn btn-secondary" onclick="window.pywebview.api.open_url('https://www.youtube.com/results?search_query=${encodeURIComponent(gameTitle + ' official trailer')}')">
                            ${I.play} TRAILER ANSEHEN
                        </button>
                        <button class="btn btn-emerald" onclick="DQS.simulateQuest('${q.app_id}', '${gameTitle}')">
                            ${I.gamepad} IM SIMULATOR STARTEN
                        </button>
                    `}
                </div>
            `;

            if (videoUrl) {
                const expBtn = card.querySelector(`#exp-btn-${qid}`);
                if (expBtn) {
                    expBtn.onclick = async () => {
                        expBtn.innerHTML = `${I.autofarm} EXPRESS LÄUFT...`;
                        await window.pywebview.api.complete_video_quest(qid, targetSec);
                        expBtn.innerHTML = `${I.check} ERFÜLLT!`;
                        setTimeout(() => { this.refreshQuests(); }, 2500);
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

    simulateQuest(appId, gameTitle) {
        this.switchTab('simulator');

        // Match preset
        let matched = this.presets.find(p => p.app_id === appId || p.name.toLowerCase().includes(gameTitle.toLowerCase()) || gameTitle.toLowerCase().includes(p.name.toLowerCase()));
        if (matched) {
            document.getElementById('sim-preset-select').value = matched.app_id;
            document.getElementById('sim-input-title').value = matched.title;
            document.getElementById('sim-input-exe').value = matched.exe;
            document.getElementById('sim-input-appid').value = matched.app_id;
        } else {
            const cleanExe = gameTitle.toLowerCase().replace(/[^a-z0-9]/g, '_') + '.exe';
            document.getElementById('sim-input-title').value = gameTitle;
            document.getElementById('sim-input-exe').value = cleanExe;
            document.getElementById('sim-input-appid').value = appId || '1205090671527071784';
        }

        // Auto start simulation
        document.getElementById('btn-start-sim').click();
    },

    async pollSimStatus() {
        if (!window.pywebview?.api) return;
        const st = await window.pywebview.api.get_sim_status();
        if (st) {
            this.updateSimUI(st.running, st.game_name, st.elapsed_seconds);
        }
    },

    updateSimUI(running, gameName, elapsedSec = 0) {
        const badge = document.getElementById('sim-status-badge');
        const startBtn = document.getElementById('btn-start-sim');
        const stopBtn = document.getElementById('btn-stop-sim');
        const actTitle = document.getElementById('sim-active-title');
        const actState = document.getElementById('sim-active-state');
        const actTimer = document.getElementById('sim-active-timer');

        const popGame = document.getElementById('pop-act-game');
        const popState = document.getElementById('pop-act-state');
        const popTimer = document.getElementById('pop-act-timer');

        if (running) {
            badge.innerText = 'SIMULATION LÄUFT';
            badge.style.color = 'var(--emerald)';
            badge.style.borderColor = 'var(--emerald)';
            startBtn.disabled = true;
            stopBtn.disabled = false;

            const gName = (gameName || 'Spiel').toUpperCase();
            actTitle.innerText = gName;
            actState.innerText = 'Rich Presence Heartbeats an Discord aktiv.';

            if (popGame) popGame.innerText = gName;
            if (popState) popState.innerText = 'In Mission (Quest läuft)';

            const m = String(Math.floor(elapsedSec / 60)).padStart(2, '0');
            const s = String(elapsedSec % 60).padStart(2, '0');
            actTimer.innerText = `Zeit: ${m}:${s} Min.`;
            if (popTimer) popTimer.innerText = `Zeit: ${m}:${s} Min.`;
        } else {
            badge.innerText = 'BEREIT';
            badge.style.color = 'var(--text-muted)';
            badge.style.borderColor = 'var(--card-border)';
            startBtn.disabled = false;
            stopBtn.disabled = true;

            actTitle.innerText = 'Keine aktive Simulation';
            actState.innerText = 'Wähle ein Spiel und klicke auf Simulation starten.';
            actTimer.innerText = 'Zeit: 00:00 Min.';
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
};

window.onAutoQuestFinished = function(totalOrbs) {
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
        if (window.DQS) window.DQS.refreshQuests();
    }, 3000);
};

window.onAutoQuestStopped = function() {
    if (window.DQS) window.DQS.refreshQuests();
};

window.onFarmProgress = function(pInfo) {
    if (pInfo && pInfo.quest_id && window.DQS) {
        DQS.refreshQuests();
    }
};

// Start when PyWebView is ready
if (window.pywebview && window.pywebview.api) {
    DQS.init();
} else {
    window.addEventListener('pywebviewready', () => {
        DQS.init();
    });
}
