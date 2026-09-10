"""
DQS - Discord Quest Spoofer
Official Release by Sandro (T3X / TNTIX)
Sleek Discord dark aesthetic with animated gear, profile popout, live orbs animation,
and full administrator privileges.
"""

import os
import sys
import io
import time
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import requests
import webbrowser

from .discord_auth import find_all_valid_accounts, get_user_profile
from .discord_api import DiscordQuestsAPI
from .game_spoofer import GameSimulator
from .quest_farmer import QuestFarmer, generate_discord_console_snippet
from .database import QUEST_GAMES_DATABASE

# Appearance setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Discord Exact Palette
COLOR_BG_DARK = "#090a0f"          # Pitch Black
COLOR_BG_SIDEBAR = "#111218"       # Graphite Header
COLOR_CARD_BG = "#13141e"          # Dark Slate Container
COLOR_CARD_BORDER = "#232536"      # Tech Border
COLOR_CARD_BORDER_ACTIVE = "#5865F2" # Neon Blurple Highlight
COLOR_WHITE = "#ffffff"            # Pure Contrast White
COLOR_TEXT_PRIMARY = "#f3f4f6"     # Crisp Light Gray
COLOR_TEXT_MUTED = "#86899c"       # Soft Ash Gray

# Glowing Action Colors
COLOR_NEON_BLURPLE = "#5865F2"     # Neon Blurple (Primary)
COLOR_NEON_BLURPLE_HOVER = "#4752C4"
COLOR_EMERALD = "#23A55A"          # Emerald Green (Success)
COLOR_EMERALD_HOVER = "#1B8246"
COLOR_CRIMSON = "#F23F43"          # Crimson Red (Stop)
COLOR_CRIMSON_HOVER = "#C9282C"
COLOR_GOLD = "#FEE75C"             # Gold/Amber (Orbs / Video)
COLOR_GOLD_HOVER = "#E0C836"
COLOR_CYAN = "#00A8FC"             # Cyan (Script / Info)
COLOR_CYAN_HOVER = "#0082C4"
COLOR_INDIGO = "#6366F1"           # Indigo
COLOR_INDIGO_HOVER = "#4F46E5"
COLOR_DARK_BTN = "#1a1b24"         # Dark Button Surface
COLOR_DARK_BTN_HOVER = "#262836"   # Dark Button Hover

class AutoQuestApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DQS // Discord Quest Spoofer")
        self.geometry("1140x780")
        self.minsize(980, 680)
        self.configure(fg_color=COLOR_BG_DARK)
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Set Window Icon
        self._set_app_icon()

        # Core Engines
        self.simulator = GameSimulator()
        self.api: DiscordQuestsAPI = None
        self.farmer: QuestFarmer = None
        self.current_user = None
        self.detected_accounts = []
        self.cached_quests = []
        self.quest_cards = {}

        # Animation states
        self.gear_angle_idx = 0
        self.gear_images = []
        self.orbs_pulse_idx = 0
        self.orbs_sparkles = ["✦ ✧ ✦", "✧ ✦ ✧", "✦ ✦ ✧", "✧ ✧ ✦"]
        self._load_gear_assets()

        # UI Setup
        self._build_header()
        self._build_main_layout()

        # Start background animation loops
        self._animate_gear()
        self._animate_orbs_banner()

        # Initial Load
        self.after(100, self._initial_load)

    def _set_app_icon(self):
        candidates = [
            os.path.join(os.path.dirname(__file__), "..", "assets", "app_icon.ico"),
            os.path.join(os.path.dirname(__file__), "app_icon.ico"),
            os.path.join(os.getcwd(), "assets", "app_icon.ico"),
            os.path.join(os.getcwd(), "app_icon.ico"),
        ]
        for c in candidates:
            if os.path.exists(c):
                try:
                    self.iconbitmap(c)
                    break
                except Exception:
                    pass

    def _load_gear_assets(self):
        """Loads the 12 pre-rendered rotating gear frames."""
        gear_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "gear")
        if not os.path.exists(gear_dir):
            gear_dir = os.path.join(os.getcwd(), "assets", "gear")

        if os.path.exists(gear_dir):
            for i in range(12):
                fpath = os.path.join(gear_dir, f"gear_{i}.png")
                if os.path.exists(fpath):
                    try:
                        im = Image.open(fpath).convert("RGBA")
                        self.gear_images.append(ctk.CTkImage(light_image=im, dark_image=im, size=(24, 24)))
                    except Exception:
                        pass

    def _animate_gear(self):
        """Smoothly spins the settings gear in the header."""
        if self.gear_images and hasattr(self, "lbl_gear") and self.lbl_gear.winfo_exists():
            self.gear_angle_idx = (self.gear_angle_idx + 1) % len(self.gear_images)
            self.lbl_gear.configure(image=self.gear_images[self.gear_angle_idx])
        self.after(75, self._animate_gear)

    def _animate_orbs_banner(self):
        """Pulses the active Orbs animation if active."""
        if hasattr(self, "lbl_orbs_sparkle") and self.lbl_orbs_sparkle.winfo_exists():
            self.orbs_pulse_idx = (self.orbs_pulse_idx + 1) % len(self.orbs_sparkles)
            self.lbl_orbs_sparkle.configure(text=self.orbs_sparkles[self.orbs_pulse_idx])
        self.after(350, self._animate_orbs_banner)

    def _on_window_close(self):
        """Safely cleans up any running simulations and tasks before exiting."""
        try:
            if self.farmer and self.farmer.running:
                self.farmer.stop()
            if self.simulator and self.simulator.is_running():
                self.simulator.stop_simulation()
        except Exception:
            pass
        self.destroy()
        sys.exit(0)

    # ================= HEADER =================

    def _build_header(self):
        self.header_frame = ctk.CTkFrame(
            self, fg_color=COLOR_BG_SIDEBAR, height=75, corner_radius=0,
            border_width=1, border_color=COLOR_CARD_BORDER
        )
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        # Left Branding - NO DIAMOND ICON
        brand_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        brand_box.pack(side="left", padx=20, pady=10)

        # Clean Transparent App Logo
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "app_icon.png")
        if os.path.exists(icon_path):
            try:
                raw_logo = Image.open(icon_path).convert("RGBA")
                self.logo_img = ctk.CTkImage(light_image=raw_logo, dark_image=raw_logo, size=(38, 38))
                lbl_icon = ctk.CTkLabel(brand_box, text="", image=self.logo_img)
                lbl_icon.pack(side="left", padx=(0, 12))
            except Exception:
                pass

        title_sub = ctk.CTkFrame(brand_box, fg_color="transparent")
        title_sub.pack(side="left")

        app_title = ctk.CTkLabel(
            title_sub, text="DQS",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLOR_WHITE
        )
        app_title.pack(anchor="w")

        sub_row = ctk.CTkFrame(title_sub, fg_color="transparent")
        sub_row.pack(anchor="w")

        sub_badge = ctk.CTkLabel(
            sub_row, text="DISCORD QUEST SPOOFER",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        )
        sub_badge.pack(side="left", padx=(0, 8))

        admin_badge = ctk.CTkFrame(sub_row, fg_color="#102a18", border_width=1, border_color=COLOR_EMERALD, corner_radius=3)
        admin_badge.pack(side="left")
        ctk.CTkLabel(
            admin_badge, text=" 🛡️ ADMIN: AKTIV ",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=COLOR_EMERALD
        ).pack(padx=2, pady=1)

        # Right User Profile Bar (Clickable to open profile drawer)
        self.account_bar = ctk.CTkFrame(
            self.header_frame, fg_color=COLOR_CARD_BG, corner_radius=6,
            border_width=1, border_color=COLOR_CARD_BORDER, cursor="hand2"
        )
        self.account_bar.pack(side="right", padx=20, pady=12)
        self.account_bar.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        # Avatar with DND circle
        self.avatar_label = ctk.CTkLabel(self.account_bar, text="🎮", font=ctk.CTkFont(size=20), width=36, height=36)
        self.avatar_label.pack(side="left", padx=(10, 8), pady=6)
        self.avatar_label.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        user_info = ctk.CTkFrame(self.account_bar, fg_color="transparent")
        user_info.pack(side="left", padx=(0, 10), pady=6)
        user_info.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        self.username_label = ctk.CTkLabel(
            user_info, text="SUCHE ACCOUNT...",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLOR_WHITE
        )
        self.username_label.pack(anchor="w")
        self.username_label.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        self.status_label = ctk.CTkLabel(
            user_info, text="● BITTE NICHT STÖREN",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLOR_CRIMSON
        )
        self.status_label.pack(anchor="w")
        self.status_label.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        # Animated Rotating Gear
        self.lbl_gear = ctk.CTkLabel(self.account_bar, text="⚙", width=28, height=28, text_color=COLOR_TEXT_MUTED)
        self.lbl_gear.pack(side="left", padx=(4, 10))
        self.lbl_gear.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

    # ================= MAIN LAYOUT & PROFILE DRAWER =================

    def _build_main_layout(self):
        # Body frame holding tabs on left, collapsible drawer on right
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True, padx=15, pady=(10, 15))

        # Main Tabview on left
        self.tabview = ctk.CTkTabview(
            self.body_frame,
            fg_color=COLOR_BG_DARK,
            segmented_button_fg_color=COLOR_BG_SIDEBAR,
            segmented_button_selected_color=COLOR_NEON_BLURPLE,
            segmented_button_selected_hover_color=COLOR_NEON_BLURPLE_HOVER,
            segmented_button_unselected_color=COLOR_CARD_BG,
            segmented_button_unselected_hover_color=COLOR_CARD_BORDER,
            text_color=COLOR_WHITE,
            corner_radius=6
        )
        self.tabview.pack(side="left", fill="both", expand=True)

        self.tab_quests = self.tabview.add("QUESTS & FARMEN")
        self.tab_simulator = self.tabview.add("SIMULATOR")
        self.tab_console = self.tabview.add("1-KLICK SCHNELL-SCRIPT")
        self.tab_logs = self.tabview.add("PROTOKOLL")

        self._setup_quests_tab()
        self._setup_simulator_tab()
        self._setup_console_tab()
        self._setup_logs_tab()

        # Collapsible Profile Drawer (Right Side)
        self.drawer_visible = False
        self._build_profile_drawer()

    def _build_profile_drawer(self):
        """Creates the Discord User Profile popout matching Image 2."""
        self.drawer_frame = ctk.CTkFrame(
            self.body_frame, width=320, fg_color=COLOR_BG_SIDEBAR, corner_radius=8,
            border_width=1, border_color=COLOR_CARD_BORDER
        )
        # Initially not packed; toggled via _toggle_profile_drawer

        # Scrollable area inside drawer
        self.drawer_scroll = ctk.CTkScrollableFrame(self.drawer_frame, fg_color="transparent")
        self.drawer_scroll.pack(fill="both", expand=True, padx=8, pady=8)

        # Banner Box
        self.banner_frame = ctk.CTkFrame(self.drawer_scroll, height=110, fg_color="#1a1c29", corner_radius=6)
        self.banner_frame.pack(fill="x", pady=(0, 10))
        self.banner_frame.pack_propagate(False)

        self.lbl_banner_img = ctk.CTkLabel(self.banner_frame, text="")
        self.lbl_banner_img.pack(fill="both", expand=True)

        # Avatar Container (Overlapping banner)
        av_box = ctk.CTkFrame(self.drawer_scroll, fg_color="transparent")
        av_box.pack(fill="x", padx=10, pady=(0, 6))

        self.drawer_avatar = ctk.CTkLabel(
            av_box, text="👤", width=64, height=64, font=ctk.CTkFont(size=36),
            fg_color="#181922", corner_radius=32
        )
        self.drawer_avatar.pack(side="left")

        # Custom Status Speech Bubble
        self.status_bubble = ctk.CTkFrame(
            self.drawer_scroll, fg_color="#181924", border_width=1, border_color="#2b2d3d", corner_radius=6
        )
        self.status_bubble.pack(fill="x", padx=10, pady=(0, 10))

        self.lbl_custom_status = ctk.CTkLabel(
            self.status_bubble, text="🩸 BEHIND EVERY KISS IS A CLAW THAT CAN BITE",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#ffffff", justify="left"
        )
        self.lbl_custom_status.pack(padx=10, pady=8, anchor="w")

        # Display Name & Username
        name_box = ctk.CTkFrame(self.drawer_scroll, fg_color="transparent")
        name_box.pack(fill="x", padx=10, pady=(0, 6))

        self.lbl_drawer_display_name = ctk.CTkLabel(
            name_box, text="TΞП†1Ж ツ 🌙",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLOR_WHITE
        )
        self.lbl_drawer_display_name.pack(anchor="w")

        self.lbl_drawer_username = ctk.CTkLabel(
            name_box, text="tentix • - HEART/LESS/WITHOUT/YOU -",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_TEXT_MUTED
        )
        self.lbl_drawer_username.pack(anchor="w")

        # Badges Row
        self.badges_frame = ctk.CTkFrame(self.drawer_scroll, fg_color="#151620", corner_radius=4)
        self.badges_frame.pack(fill="x", padx=10, pady=(0, 10))

        badges_text = "💎 NITRO  |  🚀 BOOSTER  |  ⚔️ QUESTS  |  [çifr]"
        ctk.CTkLabel(
            self.badges_frame, text=badges_text,
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=COLOR_GOLD
        ).pack(padx=8, pady=5)

        # Bio Section
        bio_title = ctk.CTkLabel(
            self.drawer_scroll, text="ÜBER MICH",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        )
        bio_title.pack(anchor="w", padx=10, pady=(0, 3))

        self.bio_box = ctk.CTkFrame(self.drawer_scroll, fg_color="#151620", corner_radius=6)
        self.bio_box.pack(fill="x", padx=10, pady=(0, 10))

        bio_content = ("+-+ † https://tentix.space/ † - +\n"
                       "* o .+ ° † ~ 𝕯𝖊𝖛𝖎𝖑 † ~ ° +. *\n"
                       "°♡G°  ÷- Rule breaker -÷  °♡G...")
        self.lbl_bio = ctk.CTkLabel(
            self.bio_box, text=bio_content,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#d1d5db", justify="left"
        )
        self.lbl_bio.pack(padx=10, pady=8, anchor="w")

        # Activity Box ("SPIELT")
        act_title = ctk.CTkLabel(
            self.drawer_scroll, text="AKTIVITÄT",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        )
        act_title.pack(anchor="w", padx=10, pady=(0, 3))

        self.activity_box = ctk.CTkFrame(self.drawer_scroll, fg_color="#151620", border_width=1, border_color="#252736", corner_radius=6)
        self.activity_box.pack(fill="x", padx=10, pady=(0, 12))

        self.lbl_act_game = ctk.CTkLabel(
            self.activity_box, text="🎮 HELLDIVERS™ 2",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_WHITE
        )
        self.lbl_act_game.pack(anchor="w", padx=10, pady=(8, 2))

        self.lbl_act_state = ctk.CTkLabel(
            self.activity_box, text="In Mission (Quest läuft)",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLOR_EMERALD
        )
        self.lbl_act_state.pack(anchor="w", padx=10, pady=(0, 2))

        self.lbl_act_timer = ctk.CTkLabel(
            self.activity_box, text="⏱ Zeit: 03:21 Min.",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=COLOR_TEXT_MUTED
        )
        self.lbl_act_timer.pack(anchor="w", padx=10, pady=(0, 8))

        # Drawer Actions
        ctk.CTkButton(
            self.drawer_scroll, text="👤 ACCOUNT WECHSELN", height=32,
            fg_color=COLOR_INDIGO, hover_color=COLOR_INDIGO_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=4, command=self._open_account_modal
        ).pack(fill="x", padx=10, pady=3)

        self.btn_copy_id = ctk.CTkButton(
            self.drawer_scroll, text="🆔 NUTZER-ID KOPIEREN", height=32,
            fg_color=COLOR_DARK_BTN, hover_color=COLOR_DARK_BTN_HOVER,
            border_width=1, border_color=COLOR_CARD_BORDER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=4, command=self._copy_user_id
        )
        self.btn_copy_id.pack(fill="x", padx=10, pady=3)

        # Official GitHub & Release Info
        ctk.CTkButton(
            self.drawer_scroll, text="⭐ OFFIZIELLER GITHUB (V1)", height=32,
            fg_color="#2b1a38", hover_color="#3e2552",
            border_width=1, border_color="#9333ea",
            text_color="#c084fc", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=4, command=lambda: webbrowser.open("https://github.com/TentixTV/Discord-Quest-Spoofer")
        ).pack(fill="x", padx=10, pady=3)

        info_box = ctk.CTkFrame(self.drawer_scroll, fg_color="#10111a", border_width=1, border_color="#202235", corner_radius=6)
        info_box.pack(fill="x", padx=10, pady=(6, 4))
        ctk.CTkLabel(
            info_box, text="DQS Release V1 by Sandro (T3X / TNTIX)\n100% sauber wenn von GitHub geladen!\nWer es woanders her hat ist selber schuld.",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=COLOR_TEXT_MUTED, justify="center"
        ).pack(padx=6, pady=6)

        ctk.CTkButton(
            self.drawer_scroll, text="✕ SCHLIESSEN", height=30,
            fg_color="transparent", hover_color="#202230",
            text_color=COLOR_TEXT_MUTED, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            command=self._toggle_profile_drawer
        ).pack(fill="x", padx=10, pady=(4, 0))

    def _toggle_profile_drawer(self):
        """Toggles the Discord user profile popout drawer on the right side."""
        if self.drawer_visible:
            self.drawer_frame.pack_forget()
            self.drawer_visible = False
        else:
            self.drawer_frame.pack(side="right", fill="y", padx=(10, 0))
            self.drawer_visible = True

    def _copy_user_id(self):
        uid = self.current_user.get("id") if self.current_user else "405441217766359051"
        self.clipboard_clear()
        self.clipboard_append(uid)
        self.btn_copy_id.configure(text="✓ ID KOPIERT!")
        self.log(f"Nutzer-ID {uid} in Zwischenablage kopiert.", "SUCCESS")
        self.after(2500, lambda: self.btn_copy_id.configure(text="🆔 NUTZER-ID KOPIEREN"))

    # ---------------- TAB 1: Quests & Auto-Farm ----------------
    def _setup_quests_tab(self):
        # Action Bar Top
        top_bar = ctk.CTkFrame(
            self.tab_quests, fg_color=COLOR_CARD_BG, corner_radius=6,
            border_width=1, border_color=COLOR_CARD_BORDER
        )
        top_bar.pack(fill="x", padx=10, pady=(10, 8))

        self.orbs_banner = ctk.CTkLabel(
            top_bar, text="LADE DISCORD QUESTS...",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_WHITE
        )
        self.orbs_banner.pack(side="left", padx=18, pady=14)

        # Buttons Right
        btn_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_box.pack(side="right", padx=15, pady=10)

        self.btn_refresh = ctk.CTkButton(
            btn_box, text="🔄 AKTUALISIEREN", width=120, height=34,
            fg_color=COLOR_DARK_BTN, hover_color=COLOR_DARK_BTN_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=4,
            command=self.refresh_quests
        )
        self.btn_refresh.pack(side="left", padx=5)

        self.btn_enroll_all = ctk.CTkButton(
            btn_box, text="📥 ALLE ANNEHMEN", width=130, height=34,
            fg_color=COLOR_INDIGO, hover_color=COLOR_INDIGO_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=4,
            command=self.enroll_all_quests
        )
        self.btn_enroll_all.pack(side="left", padx=5)

        self.btn_auto_farm = ctk.CTkButton(
            btn_box, text="⚡ ALLE QUESTS FARMEN", width=180, height=34,
            fg_color=COLOR_NEON_BLURPLE, hover_color=COLOR_NEON_BLURPLE_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=4,
            command=self.toggle_auto_farm
        )
        self.btn_auto_farm.pack(side="left", padx=5)

        # Fast-Track Info Banner for Instant Live Progress
        fast_banner = ctk.CTkFrame(
            self.tab_quests, fg_color="#0e1322", corner_radius=6,
            border_width=1, border_color=COLOR_NEON_BLURPLE
        )
        fast_banner.pack(fill="x", padx=10, pady=(0, 8))

        fast_text = ctk.CTkLabel(
            fast_banner,
            text="💡 TIPP FÜR SOFORTIGEN %-ANSTIEG: Discord zählt Spielzeit via interne Heartbeats.\n"
                 "Nutze den 1-Klick Schnell-Starter (Tab 3) – damit steigen alle % sofort live & Orbs werden geholt!",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_GOLD,
            justify="left"
        )
        fast_text.pack(side="left", padx=15, pady=10)

        fast_btn = ctk.CTkButton(
            fast_banner, text="⚡ 1-KLICK SCHNELL-SCRIPT", width=220, height=32,
            fg_color=COLOR_EMERALD, hover_color=COLOR_EMERALD_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=4,
            command=self._jump_to_console_script
        )
        fast_btn.pack(side="right", padx=15, pady=10)

        # Animated Live Orbs Status Bar (Visible while farming or simulating)
        self.live_orbs_frame = ctk.CTkFrame(
            self.tab_quests, fg_color="#17122b", border_width=1, border_color="#8b5cf6", corner_radius=6
        )
        # Not packed by default, shown during farm/simulation

        orbs_left = ctk.CTkFrame(self.live_orbs_frame, fg_color="transparent")
        orbs_left.pack(side="left", padx=15, pady=8)

        self.lbl_orbs_icon = ctk.CTkLabel(
            orbs_left, text="🔮", font=ctk.CTkFont(size=20)
        )
        self.lbl_orbs_icon.pack(side="left", padx=(0, 8))

        self.lbl_orbs_status = ctk.CTkLabel(
            orbs_left, text="DISCORD ORBS-FARM AKTIV",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#c084fc"
        )
        self.lbl_orbs_status.pack(side="left")

        self.lbl_orbs_sparkle = ctk.CTkLabel(
            self.live_orbs_frame, text="✦ ✧ ✦",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color=COLOR_GOLD
        )
        self.lbl_orbs_sparkle.pack(side="right", padx=15, pady=8)

        # Quests Scrollable Container
        self.quests_scroll = ctk.CTkScrollableFrame(
            self.tab_quests, fg_color="transparent",
            label_text="OFFENE AUFGABEN // WARTESCHLANGE",
            label_font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            label_text_color=COLOR_TEXT_MUTED
        )
        self.quests_scroll.pack(fill="both", expand=True, padx=5, pady=5)

    def _jump_to_console_script(self):
        self._copy_console_script()
        self.tabview.set("1-KLICK SCHNELL-SCRIPT")

    # ---------------- TAB 2: Simulator ----------------
    def _setup_simulator_tab(self):
        container = ctk.CTkFrame(
            self.tab_simulator, fg_color=COLOR_CARD_BG, corner_radius=6,
            border_width=1, border_color=COLOR_CARD_BORDER
        )
        container.pack(fill="both", expand=True, padx=15, pady=15)

        title = ctk.CTkLabel(
            container, text="MANUELLE SPIELE-SIMULATION (OHNE INSTALLATION)",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLOR_WHITE
        )
        title.pack(anchor="w", padx=25, pady=(20, 5))

        desc = ctk.CTkLabel(
            container,
            text="Simuliert einen minimalen Windows-Spielprozess (~2MB RAM) mit passendem Dateinamen und Fenstertitel,\n"
                 "damit Discord das Spiel als aktiv erkennt, ohne dass du Gigabytes herunterladen musst.",
            font=ctk.CTkFont(family="Segoe UI", size=11), text_color=COLOR_TEXT_MUTED, justify="left"
        )
        desc.pack(anchor="w", padx=25, pady=(0, 20))

        # Preset Selector
        preset_box = ctk.CTkFrame(container, fg_color="transparent")
        preset_box.pack(fill="x", padx=25, pady=5)

        ctk.CTkLabel(
            preset_box, text="SPIEL-VORLAGE:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(side="left", padx=(0, 15))

        game_titles = [f"{info['name']} ({info['exe']})" for info in QUEST_GAMES_DATABASE.values()]
        self.combo_preset = ctk.CTkComboBox(
            preset_box, values=game_titles, width=380,
            fg_color=COLOR_BG_DARK, border_color=COLOR_CARD_BORDER,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            command=self._on_preset_selected
        )
        self.combo_preset.pack(side="left")
        if game_titles:
            self.combo_preset.set(game_titles[0])

        # Form Fields
        form_frame = ctk.CTkFrame(container, fg_color="transparent")
        form_frame.pack(fill="x", padx=25, pady=15)

        ctk.CTkLabel(
            form_frame, text="SPIEL-NAME / TITEL:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).grid(row=0, column=0, sticky="w", pady=6)
        self.entry_sim_title = ctk.CTkEntry(
            form_frame, width=380, fg_color=COLOR_BG_DARK, border_color=COLOR_CARD_BORDER,
            font=ctk.CTkFont(family="Segoe UI", size=11)
        )
        self.entry_sim_title.grid(row=0, column=1, sticky="w", padx=(15, 0), pady=6)

        ctk.CTkLabel(
            form_frame, text="DATEINAME (EXE):",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).grid(row=1, column=0, sticky="w", pady=6)
        self.entry_sim_exe = ctk.CTkEntry(
            form_frame, width=380, fg_color=COLOR_BG_DARK, border_color=COLOR_CARD_BORDER,
            font=ctk.CTkFont(family="Segoe UI", size=11)
        )
        self.entry_sim_exe.grid(row=1, column=1, sticky="w", padx=(15, 0), pady=6)

        ctk.CTkLabel(
            form_frame, text="DISCORD APP-ID:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).grid(row=2, column=0, sticky="w", pady=6)
        self.entry_sim_appid = ctk.CTkEntry(
            form_frame, width=380, fg_color=COLOR_BG_DARK, border_color=COLOR_CARD_BORDER,
            font=ctk.CTkFont(family="Segoe UI", size=11)
        )
        self.entry_sim_appid.grid(row=2, column=1, sticky="w", padx=(15, 0), pady=6)

        # Fill initial preset
        if game_titles:
            self._on_preset_selected(game_titles[0])

        # Control Buttons
        btn_action_box = ctk.CTkFrame(container, fg_color="transparent")
        btn_action_box.pack(anchor="w", padx=25, pady=15)

        self.btn_start_sim = ctk.CTkButton(
            btn_action_box, text="▶ SIMULATION STARTEN", width=220, height=38,
            fg_color=COLOR_EMERALD, hover_color=COLOR_EMERALD_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            corner_radius=4,
            command=self.start_manual_simulation
        )
        self.btn_start_sim.pack(side="left", padx=(0, 10))

        self.btn_stop_sim = ctk.CTkButton(
            btn_action_box, text="⏹ STOPPEN", width=140, height=38,
            fg_color=COLOR_CRIMSON, hover_color=COLOR_CRIMSON_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            corner_radius=4,
            command=self.stop_manual_simulation
        )
        self.btn_stop_sim.pack(side="left")

        self.lbl_sim_status = ctk.CTkLabel(
            container, text="Status: Bereit. Kein Spiel simuliert.",
            font=ctk.CTkFont(family="Segoe UI", size=11), text_color=COLOR_TEXT_MUTED
        )
        self.lbl_sim_status.pack(anchor="w", padx=25, pady=(5, 10))

    def _on_preset_selected(self, choice):
        for app_id, info in QUEST_GAMES_DATABASE.items():
            if info["name"] in choice:
                self.entry_sim_title.delete(0, "end")
                self.entry_sim_title.insert(0, info["title"])
                self.entry_sim_exe.delete(0, "end")
                self.entry_sim_exe.insert(0, info["exe"])
                self.entry_sim_appid.delete(0, "end")
                self.entry_sim_appid.insert(0, app_id)
                break

    # ---------------- TAB 3: Console Quick Snippet ----------------
    def _setup_console_tab(self):
        container = ctk.CTkFrame(
            self.tab_console, fg_color=COLOR_CARD_BG, corner_radius=6,
            border_width=1, border_color=COLOR_CARD_BORDER
        )
        container.pack(fill="both", expand=True, padx=15, pady=15)

        title = ctk.CTkLabel(
            container, text="1-KLICK IN-DISCORD TURBO ENGINE (100% GARANTIE)",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLOR_WHITE
        )
        title.pack(anchor="w", padx=25, pady=(18, 5))

        # Prominent Safety Warning Box as requested by User
        warning_box = ctk.CTkFrame(
            container, fg_color="#2b1414", border_width=1, border_color="#ef4444", corner_radius=6
        )
        warning_box.pack(fill="x", padx=25, pady=(0, 10))

        warn_text = (
            "⚠️ WICHTIGER SICHERHEITSHINWEIS & WARNUNG:\n"
            "Discord warnt in der Konsole standardmäßig vor dem Einfügen von Code ('Pasting anything in here could give attackers access...').\n"
            "Dieses Skript wurde von Sandro (T3X / TNTIX) entwickelt und ist zu 100% sauber: KEINE Backdoor, kein Phishing, kein Token-Stealing!\n"
            "Es klinkt sich ausschließlich lokal in Discords internen RunningGameStore ein, damit Discord Heartbeats sendet und die % hochgehen.\n"
            "Nutzung erfolgt auf eigene Verantwortung im Rahmen der Discord-Nutzungsrichtlinien."
        )
        ctk.CTkLabel(
            warning_box, text=warn_text,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#fca5a5", justify="left"
        ).pack(padx=12, pady=8, anchor="w")

        desc = ctk.CTkLabel(
            container,
            text="👑 SO STEIGEN DEINE % SOFORT UND ORBS WERDEN AUTOMATISCH ABGEHOLT:\n\n"
                 "1️⃣ In deinem Discord-Fenster drücken:  STRG + UMSCHALT + I  (öffnet die Entwicklertools)\n"
                 "2️⃣ Klicke oben auf den Reiter:  Console  (bzw. Konsole)\n"
                 "3️⃣ Drücke unten auf 'SCRIPT KOPIEREN', füge es in die Konsole ein (STRG + V) und drücke  ENTER!\n\n"
                 "✨ Discord blendet sofort ein Live-HUD ein, sendet alle 30s Heartbeats und holt alle Orbs automatisch ab!",
            font=ctk.CTkFont(family="Segoe UI", size=11), text_color=COLOR_TEXT_PRIMARY, justify="left"
        )
        desc.pack(anchor="w", padx=25, pady=(0, 10))

        self.txt_snippet = ctk.CTkTextbox(
            container, height=180, font=ctk.CTkFont(family="Consolas", size=10),
            fg_color=COLOR_BG_DARK, text_color="#d1d5db"
        )
        self.txt_snippet.pack(fill="both", expand=True, padx=25, pady=(0, 12))
        self.txt_snippet.insert("1.0", generate_discord_console_snippet())
        self.txt_snippet.configure(state="disabled")

        btn_box = ctk.CTkFrame(container, fg_color="transparent")
        btn_box.pack(anchor="w", padx=25, pady=(0, 15))

        self.btn_copy_script = ctk.CTkButton(
            btn_box, text="📋 1-KLICK SCRIPT IN ZWISCHENABLAGE KOPIEREN", width=380, height=38,
            fg_color=COLOR_NEON_BLURPLE, hover_color=COLOR_NEON_BLURPLE_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=4,
            command=self._copy_console_script
        )
        self.btn_copy_script.pack(side="left", padx=(0, 15))

        self.lbl_copy_notice = ctk.CTkLabel(btn_box, text="", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=COLOR_EMERALD)
        self.lbl_copy_notice.pack(side="left")

    def _copy_console_script(self):
        script = generate_discord_console_snippet()
        self.clipboard_clear()
        self.clipboard_append(script)
        self.lbl_copy_notice.configure(text="✓ IN ZWISCHENABLAGE KOPIERT! IN DISCORD KONSOLE EINFÜGEN.")
        self.log("1-Klick Script kopiert. Jetzt in Discord Console (STRG+UMSCHALT+I) einfügen!", "SUCCESS")
        self.after(5000, lambda: self.lbl_copy_notice.configure(text=""))

    # ---------------- TAB 4: Logs ----------------
    def _setup_logs_tab(self):
        container = ctk.CTkFrame(
            self.tab_logs, fg_color=COLOR_CARD_BG, corner_radius=6,
            border_width=1, border_color=COLOR_CARD_BORDER
        )
        container.pack(fill="both", expand=True, padx=15, pady=15)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header, text="ECHTZEIT-PROTOKOLL // EREIGNISSE",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(side="left")

        ctk.CTkButton(
            header, text="LEEREN", width=80, height=26,
            fg_color=COLOR_DARK_BTN, hover_color=COLOR_DARK_BTN_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=4,
            command=lambda: self.log_box.delete("1.0", "end")
        ).pack(side="right")

        self.log_box = ctk.CTkTextbox(
            container, font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLOR_BG_DARK, text_color="#e4e4e7"
        )
        self.log_box.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Tags
        self.log_box.tag_config("INFO", foreground="#ffffff")
        self.log_box.tag_config("SUCCESS", foreground="#22c55e")
        self.log_box.tag_config("WARN", foreground="#eab308")
        self.log_box.tag_config("ERROR", foreground="#ef4444")
        self.log_box.tag_config("TIME", foreground="#52525b")

    def log(self, message: str, level: str = "INFO"):
        def _append():
            timestamp = time.strftime("[%H:%M:%S] ")
            self.log_box.insert("end", timestamp, "TIME")
            self.log_box.insert("end", f"[{level}] ", level)
            self.log_box.insert("end", f"{message}\n")
            self.log_box.see("end")
        self.after(0, _append)

    # ================= LOGIC & AUTH =================

    def _initial_load(self):
        self.log("Initialisiere DQS (Discord Quest Spoofer) v1.0...", "INFO")
        threading.Thread(target=self._scan_and_authenticate, daemon=True).start()

    def _scan_and_authenticate(self):
        self.log("Suche nach aktiven Discord-Logins auf diesem PC...", "INFO")
        accounts = find_all_valid_accounts()
        self.detected_accounts = accounts

        if accounts:
            chosen = accounts[0]
            for a in accounts:
                if a.get("username") == "tentix":
                    chosen = a
                    break
            self._set_active_account(chosen)
        else:
            self.log("Kein aktiver Discord-Token gefunden. Bitte manuell anmelden.", "WARN")
            self.username_label.configure(text="NICHT ANGEMELDET")
            self.status_label.configure(text="○ OFFLINE", text_color=COLOR_TEXT_MUTED)

    def _set_active_account(self, account: dict):
        self.current_user = account
        token = account["token"]
        username = account.get("username", "Benutzer")
        global_name = account.get("global_name") or username

        self.username_label.configure(text=global_name.upper())
        self.status_label.configure(text="● BITTE NICHT STÖREN", text_color=COLOR_CRIMSON)

        # Update Drawer Profile details
        self.lbl_drawer_display_name.configure(text=f"{global_name} 🌙")
        self.lbl_drawer_username.configure(text=f"@{username} • - HEART/LESS/WITHOUT/YOU -")

        # Load avatar & banner asynchronously
        threading.Thread(target=self._load_avatar_image, args=(account,), daemon=True).start()
        threading.Thread(target=self._load_banner_image, args=(account,), daemon=True).start()

        self.api = DiscordQuestsAPI(token)
        self.farmer = QuestFarmer(self.api, self.simulator)
        self.farmer.on_log = self.log
        self.farmer.on_progress = self._on_farm_progress
        self.farmer.on_finished = self._on_farmer_finished

        self.log(f"Angemeldet als: {username} ({account.get('id')})", "SUCCESS")
        self.refresh_quests()

    def _load_avatar_image(self, account: dict):
        # Check local cached avatar
        local_av = os.path.join(os.path.dirname(__file__), "..", "assets", "tentix_avatar.png")
        if not os.path.exists(local_av):
            local_av = os.path.join(os.getcwd(), "assets", "tentix_avatar.png")

        img = None
        if os.path.exists(local_av):
            try:
                img = Image.open(local_av).convert("RGBA")
            except Exception:
                pass

        if not img and account.get("avatar_url"):
            try:
                r = requests.get(account["avatar_url"], timeout=6)
                if r.status_code == 200:
                    img = Image.open(io.BytesIO(r.content)).convert("RGBA")
            except Exception:
                pass

        if img:
            header_av = ctk.CTkImage(light_image=img, dark_image=img, size=(36, 36))
            drawer_av = ctk.CTkImage(light_image=img, dark_image=img, size=(64, 64))
            self.after(0, lambda: self.avatar_label.configure(image=header_av, text=""))
            self.after(0, lambda: self.drawer_avatar.configure(image=drawer_av, text=""))

    def _load_banner_image(self, account: dict):
        local_bn = os.path.join(os.path.dirname(__file__), "..", "assets", "tentix_banner.png")
        if not os.path.exists(local_bn):
            local_bn = os.path.join(os.getcwd(), "assets", "tentix_banner.png")

        img = None
        if os.path.exists(local_bn):
            try:
                img = Image.open(local_bn).convert("RGBA")
            except Exception:
                pass

        if not img and account.get("banner_url"):
            try:
                r = requests.get(account["banner_url"], timeout=6)
                if r.status_code == 200:
                    img = Image.open(io.BytesIO(r.content)).convert("RGBA")
            except Exception:
                pass

        if img:
            banner_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 110))
            self.after(0, lambda: self.lbl_banner_img.configure(image=banner_ctk, text=""))

    def refresh_quests(self):
        if not self.api:
            return
        self.btn_refresh.configure(state="disabled", text="LÄDT...")
        self.orbs_banner.configure(text="LADE AKTUELLE DISCORD QUESTS...", text_color=COLOR_WHITE)
        threading.Thread(target=self._async_fetch_quests, daemon=True).start()

    def _async_fetch_quests(self):
        try:
            quests = self.api.get_parsed_quests()
            self.cached_quests = quests
            self.after(0, lambda: self._render_quests(quests))
        except Exception as e:
            self.log(f"Fehler beim Aktualisieren der Quests: {e}", "ERROR")
            self.after(0, lambda: self.orbs_banner.configure(text="FEHLER BEIM LADEN DER QUESTS", text_color=COLOR_CRIMSON))
            self.after(0, lambda: self.btn_refresh.configure(state="normal", text="🔄 AKTUALISIEREN"))

    def _render_quests(self, quests):
        self.btn_refresh.configure(state="normal", text="🔄 AKTUALISIEREN")
        for widget in self.quests_scroll.winfo_children():
            widget.destroy()

        self.quest_cards.clear()
        total_orbs = sum(q.get("orb_count", 0) for q in quests)
        active_count = len(quests)
        self.orbs_banner.configure(
            text=f"VERFÜGBARE QUESTS: {active_count}  |  GESAMT-ORBS: {total_orbs}",
            text_color=COLOR_WHITE
        )

        if not quests:
            empty_lbl = ctk.CTkLabel(
                self.quests_scroll,
                text="Aktuell sind keine offenen Discord Quests verfügbar oder alle wurden bereits eingelöst.",
                font=ctk.CTkFont(family="Segoe UI", size=12), text_color=COLOR_TEXT_MUTED
            )
            empty_lbl.pack(pady=40)
            return

        for q in quests:
            self._create_quest_card(q)

    def _create_quest_card(self, q):
        qid = q["id"]
        qname = q["quest_name"]
        game_title = q["game_title"]
        app_id = q["app_id"]
        target_sec = q.get("target_seconds", 900)
        curr_sec = q.get("current_seconds", 0)
        pct = q.get("progress_percent", 0.0)
        enrolled = q.get("enrolled", False)
        completed = q.get("completed", False)
        claimed = q.get("claimed", False)
        rewards_text = q.get("rewards_text", "Belohnung")
        task_type = q.get("task_type", "PLAY_ON_DESKTOP")

        card = ctk.CTkFrame(
            self.quests_scroll, fg_color=COLOR_CARD_BG, corner_radius=6,
            border_width=1, border_color=COLOR_CARD_BORDER_ACTIVE if enrolled and not claimed else COLOR_CARD_BORDER
        )
        card.pack(fill="x", padx=10, pady=6)

        left_box = ctk.CTkFrame(card, fg_color="transparent")
        left_box.pack(side="left", padx=15, pady=12, fill="y")

        type_icon = "📺" if "VIDEO" in task_type else ("🎮" if "PLAY" in task_type else "⚔️")
        lbl_icon = ctk.CTkLabel(left_box, text=type_icon, font=ctk.CTkFont(size=22), width=32)
        lbl_icon.pack(side="left", padx=(0, 10))

        details = ctk.CTkFrame(left_box, fg_color="transparent")
        details.pack(side="left")

        lbl_qname = ctk.CTkLabel(
            details, text=qname,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_WHITE
        )
        lbl_qname.pack(anchor="w")

        info_line = f"Spiel: {game_title}  |  App-ID: {app_id}  |  Aufgabe: {task_type}"
        lbl_info = ctk.CTkLabel(
            details, text=info_line,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLOR_TEXT_MUTED
        )
        lbl_info.pack(anchor="w")

        # Right Action Area
        right_box = ctk.CTkFrame(card, fg_color="transparent")
        right_box.pack(side="right", padx=15, pady=12)

        p_text = f"{curr_sec // 60}/{target_sec // 60} MIN. ({pct:.0f}%)" if target_sec > 60 else f"{curr_sec}/{target_sec}S ({pct:.0f}%)"
        lbl_progress = ctk.CTkLabel(
            right_box, text=p_text,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        lbl_progress.pack(anchor="e", pady=(0, 4))

        prog_bar = ctk.CTkProgressBar(right_box, width=160, height=8, progress_color=COLOR_NEON_BLURPLE)
        prog_bar.set(pct / 100.0)
        prog_bar.pack(anchor="e", pady=(0, 8))

        btn_action = ctk.CTkButton(
            right_box, text="START", width=120, height=28,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            corner_radius=4
        )
        btn_action.pack(anchor="e")

        if claimed:
            btn_action.configure(text="✓ EINGELÖST", state="disabled", fg_color="#18281e", text_color=COLOR_EMERALD)
        elif completed:
            btn_action.configure(
                text="🎁 ABHOLEN", fg_color=COLOR_EMERALD, hover_color=COLOR_EMERALD_HOVER, text_color=COLOR_WHITE,
                command=lambda qid=qid, b=btn_action: self._claim_quest(qid, b)
            )
        elif not enrolled:
            btn_action.configure(
                text="📥 ANNEHMEN", fg_color=COLOR_INDIGO, hover_color=COLOR_INDIGO_HOVER, text_color=COLOR_WHITE,
                command=lambda qid=qid, b=btn_action: self._enroll_quest(qid, b)
            )
        elif "VIDEO" in task_type:
            btn_action.configure(
                text="⚡ VIDEO ABSCHLIESSEN", fg_color=COLOR_GOLD, hover_color=COLOR_GOLD_HOVER, text_color="#000000",
                command=lambda qid=qid, t=target_sec, b=btn_action: self._fast_video_quest(qid, t, b)
            )
        else:
            btn_action.configure(
                text="▶ SIMULIEREN", fg_color=COLOR_EMERALD, hover_color=COLOR_EMERALD_HOVER, text_color=COLOR_WHITE,
                command=lambda aid=app_id, gt=game_title: self._sim_single_quest(aid, gt)
            )

        self.quest_cards[qid] = {
            "card": card,
            "bar": prog_bar,
            "label": lbl_progress,
            "target_sec": target_sec,
            "button": btn_action
        }

    def _enroll_quest(self, qid: str, btn):
        btn.configure(state="disabled", text="NIMMT AN...")
        def _bg():
            ok = self.api.enroll_quest(qid)
            if ok:
                self.log("Erfolgreich in Quest eingeschrieben!", "SUCCESS")
                self.after(500, self.refresh_quests)
            else:
                self.log("Fehler bei der Quest-Einschreibung.", "ERROR")
                self.after(0, lambda: btn.configure(state="normal", text="📥 ANNEHMEN"))
        threading.Thread(target=_bg, daemon=True).start()

    def _claim_quest(self, qid: str, btn):
        btn.configure(state="disabled", text="FORDERT AN...")
        def _bg():
            res = self.api.claim_reward(qid)
            if res.get("success"):
                self.log(f"Belohnung erfolgreich erhalten!", "SUCCESS")
                self.after(500, self.refresh_quests)
            else:
                self.log(f"Belohnung konnte nicht geholt werden: {res.get('error')}", "ERROR")
                self.after(0, lambda: btn.configure(state="normal", text="🎁 ABHOLEN"))
        threading.Thread(target=_bg, daemon=True).start()

    def _fast_video_quest(self, qid: str, target_sec: int, btn):
        btn.configure(state="disabled", text="LÄUFT...")
        def _bg():
            self.log(f"Starte Express-Abschluss für Video-Aufgabe...", "INFO")
            ok = self.api.complete_video_quest(qid, target_sec)
            if ok:
                self.log(f"Video erfolgreich abgeschlossen! Fordere Belohnung an...", "SUCCESS")
                time.sleep(1)
                self.api.claim_reward(qid)
                self.after(500, self.refresh_quests)
            else:
                self.log(f"Video-Abschluss fehlgeschlagen.", "ERROR")
                self.after(0, lambda: btn.configure(state="normal", text="⚡ VIDEO ABSCHLIESSEN"))
        threading.Thread(target=_bg, daemon=True).start()

    def _sim_single_quest(self, app_id: str, game_title: str):
        self.tabview.set("SIMULATOR")
        self.entry_sim_appid.delete(0, "end")
        self.entry_sim_appid.insert(0, app_id)
        self.entry_sim_title.delete(0, "end")
        self.entry_sim_title.insert(0, game_title)
        self.start_manual_simulation()

    def enroll_all_quests(self):
        if not self.api or not self.cached_quests:
            return
        self.btn_enroll_all.configure(state="disabled", text="NIMMT AN...")
        def _bg():
            count = 0
            for q in self.cached_quests:
                if not q.get("enrolled"):
                    if self.api.enroll_quest(q["id"]):
                        count += 1
                    time.sleep(0.5)
            self.log(f"{count} Quests erfolgreich angenommen!", "SUCCESS")
            self.after(500, self.refresh_quests)
            self.after(0, lambda: self.btn_enroll_all.configure(state="normal", text="📥 ALLE ANNEHMEN"))
        threading.Thread(target=_bg, daemon=True).start()

    def toggle_auto_farm(self):
        if not self.farmer:
            return
        if self.farmer.running:
            self.farmer.stop()
            self.btn_auto_farm.configure(
                text="⚡ ALLE QUESTS FARMEN", fg_color=COLOR_NEON_BLURPLE, hover_color=COLOR_NEON_BLURPLE_HOVER
            )
            self.live_orbs_frame.pack_forget()
        else:
            if not self.cached_quests:
                messagebox.showinfo("Info", "Keine Quests zum Farmen vorhanden.")
                return
            self.btn_auto_farm.configure(
                text="⏹ STOPPEN", fg_color=COLOR_CRIMSON, hover_color=COLOR_CRIMSON_HOVER
            )
            # Show live orbs animation banner
            self.live_orbs_frame.pack(fill="x", padx=10, pady=(0, 8), before=self.quests_scroll)
            self.farmer.start_farm_all(self.cached_quests)

    def start_manual_simulation(self):
        app_id = self.entry_sim_appid.get().strip()
        title = self.entry_sim_title.get().strip()
        exe = self.entry_sim_exe.get().strip()

        if not app_id:
            messagebox.showerror("Fehler", "Bitte gib eine Discord App-ID an!")
            return

        res = self.simulator.start_simulation(app_id, title, exe)
        if res.get("success"):
            self.btn_start_sim.configure(state="disabled")
            self.btn_stop_sim.configure(state="normal")
            status_txt = f"Status: Simuliere '{res['game_name']}' ({res['exe_name']}) | PID: {res['pid']}"
            self.lbl_sim_status.configure(text=status_txt, text_color=COLOR_EMERALD)
            self.log(f"Manuelle Simulation für '{title}' aktiv gestartet.", "SUCCESS")
            # Update drawer activity
            self.lbl_act_game.configure(text=f"🎮 {title}")
            self.lbl_act_state.configure(text="Im Spiel (DQS Simulation aktiv)")
        else:
            messagebox.showerror("Fehler", "Simulation konnte nicht gestartet werden.")

    def stop_manual_simulation(self):
        self.simulator.stop_simulation()
        self.btn_start_sim.configure(state="normal")
        self.btn_stop_sim.configure(state="disabled")
        self.lbl_sim_status.configure(text="Status: Gestoppt. Kein Spiel simuliert.", text_color=COLOR_TEXT_MUTED)
        self.log("Manuelle Simulation beendet.", "INFO")
        self.lbl_act_game.configure(text="🎮 Kein Spiel aktiv")
        self.lbl_act_state.configure(text="Offline")

    def _on_farm_progress(self, p_data: dict):
        qid = p_data.get("quest_id")
        pct = p_data.get("progress_percent", 0.0)
        curr = p_data.get("current_seconds", 0)
        tgt = p_data.get("target_seconds", 900)

        # Update Orbs banner live status
        if hasattr(self, "lbl_orbs_status") and self.lbl_orbs_status.winfo_exists():
            game = p_data.get("game_title", "Spiel")
            rem_m = (tgt - curr) // 60
            self.lbl_orbs_status.configure(text=f"ORBS-FARM AKTIV // '{game}': {pct:.0f}% (Noch {rem_m} Min.)")

        # Update drawer activity timer
        if hasattr(self, "lbl_act_timer") and self.lbl_act_timer.winfo_exists():
            m = curr // 60
            s = curr % 60
            self.lbl_act_timer.configure(text=f"⏱ Zeit: {m:02d}:{s:02d} Min.")

        if qid in self.quest_cards:
            card_info = self.quest_cards[qid]
            done_s = p_data.get("current_seconds", 0)
            t_sec = card_info.get("target_sec", 900)
            p_text = f"{done_s // 60}/{t_sec // 60} MIN. ({pct:.0f}%)" if t_sec > 60 else f"{done_s}/{t_sec}S ({pct:.0f}%)"
            b = card_info["bar"]
            l = card_info["label"]
            self.after(0, lambda b=b, l=l, p=pct, t=p_text: [
                b.set(p / 100.0),
                l.configure(text=t)
            ])

    def _on_farmer_finished(self, total_orbs: int):
        self.after(0, lambda: self.btn_auto_farm.configure(
            text="⚡ ALLE QUESTS FARMEN", fg_color=COLOR_NEON_BLURPLE, hover_color=COLOR_NEON_BLURPLE_HOVER, text_color=COLOR_WHITE
        ))
        self.after(0, lambda: self.orbs_banner.configure(
            text=f"ABGESCHLOSSEN! INSGESAMT {total_orbs} ORBS EINGEFARMT.", text_color=COLOR_WHITE
        ))
        self.after(0, lambda: self.live_orbs_frame.pack_forget())
        self.after(1000, self.refresh_quests)

    # ---------------- ACCOUNT SWITCH MODAL ----------------
    def _open_account_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("DISCORD ACCOUNT WÄHLEN")
        modal.geometry("500x440")
        modal.configure(fg_color=COLOR_BG_DARK)
        modal.resizable(False, False)
        modal.transient(self)
        modal.grab_set()

        ctk.CTkLabel(
            modal, text="DISCORD ACCOUNT WÄHLEN",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(pady=(25, 10))

        acc_frame = ctk.CTkFrame(
            modal, fg_color=COLOR_CARD_BG, corner_radius=6,
            border_width=1, border_color=COLOR_CARD_BORDER
        )
        acc_frame.pack(fill="x", padx=25, pady=10)

        ctk.CTkLabel(
            acc_frame, text="GEFUNDENE LOKALE KONTEN:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=15, pady=(10, 5))

        if self.detected_accounts:
            for acc in self.detected_accounts:
                btn_txt = f"👤 {acc.get('username').upper()} (ID: {acc.get('id')})"
                btn = ctk.CTkButton(
                    acc_frame, text=btn_txt, anchor="w",
                    fg_color=COLOR_BG_DARK, hover_color=COLOR_DARK_BTN_HOVER,
                    text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11),
                    border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=4,
                    command=lambda a=acc, m=modal: [self._set_active_account(a), m.destroy()]
                )
                btn.pack(fill="x", padx=15, pady=4)
        else:
            ctk.CTkLabel(
                acc_frame, text="Keine lokalen Konten gefunden.",
                font=ctk.CTkFont(family="Segoe UI", size=11), text_color=COLOR_TEXT_MUTED
            ).pack(anchor="w", padx=15, pady=8)

        ctk.CTkLabel(
            modal, text="ODER TOKEN MANUELL EINGEBEN:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=25, pady=(15, 5))

        token_entry = ctk.CTkEntry(
            modal, placeholder_text="Discord Token hier einfügen...", show="*",
            fg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER,
            font=ctk.CTkFont(family="Segoe UI", size=11)
        )
        token_entry.pack(fill="x", padx=25, pady=5)

        def _use_token():
            tok = token_entry.get().strip()
            if not tok:
                return
            prof = get_user_profile(tok)
            if prof:
                self._set_active_account(prof)
                modal.destroy()
            else:
                messagebox.showerror("Fehler", "Ungültiger Discord Token!")

        ctk.CTkButton(
            modal, text="MIT TOKEN ANMELDEN", height=34,
            fg_color=COLOR_INDIGO, hover_color=COLOR_INDIGO_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=4,
            command=_use_token
        ).pack(fill="x", padx=25, pady=15)

if __name__ == "__main__":
    app = AutoQuestApp()
    app.mainloop()
