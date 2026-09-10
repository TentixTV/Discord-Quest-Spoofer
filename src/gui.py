"""
DQS - Discord Quest Spoofer (Gothic Dark AAA Edition)
Official Release by Sandro (T3X / TNTIX)
Pixel-perfect Discord Dark Aesthetic, Overlapping Real Animated Avatar & Banner GIFs,
Full Video Gallery, Auto-Preset Simulation, and 100% Reliable Quest Synchronization.
"""

import os
import sys
import io
import time
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence, ImageDraw
import requests
import webbrowser

try:
    from .discord_auth import find_all_valid_accounts, get_user_profile
    from .discord_api import DiscordQuestsAPI
    from .game_spoofer import GameSimulator
    from .quest_farmer import QuestFarmer, generate_discord_console_snippet
    from .database import QUEST_GAMES_DATABASE
except (ImportError, ValueError):
    from discord_auth import find_all_valid_accounts, get_user_profile
    from discord_api import DiscordQuestsAPI
    from game_spoofer import GameSimulator
    from quest_farmer import QuestFarmer, generate_discord_console_snippet
    from database import QUEST_GAMES_DATABASE

# Appearance setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Discord Exact Palette
COLOR_BG_DARK = "#08090d"          # Deep Void Pitch Black
COLOR_BG_SIDEBAR = "#101118"       # Graphite Surface
COLOR_CARD_BG = "#11121c"          # Dark Slate Container
COLOR_CARD_BORDER = "#1f2233"      # Tech Border
COLOR_CARD_BORDER_ACTIVE = "#5865F2" # Neon Blurple Highlight
COLOR_WHITE = "#ffffff"            # Pure White
COLOR_TEXT_PRIMARY = "#f2f3f5"     # Crisp Light Gray
COLOR_TEXT_MUTED = "#8e92a4"       # Soft Ash Gray

# Glowing Action Colors
COLOR_NEON_BLURPLE = "#5865F2"     # Blurple Primary
COLOR_NEON_BLURPLE_HOVER = "#4752C4"
COLOR_EMERALD = "#23A55A"          # Emerald Green
COLOR_EMERALD_HOVER = "#1B8246"
COLOR_CRIMSON = "#F23F43"          # Crimson Red
COLOR_CRIMSON_HOVER = "#C9282C"
COLOR_GOLD = "#FEE75C"             # Gold/Amber
COLOR_GOLD_HOVER = "#E0C836"
COLOR_CYAN = "#00A8FC"             # Cyan
COLOR_CYAN_HOVER = "#0082C4"
COLOR_INDIGO = "#6366F1"           # Indigo
COLOR_INDIGO_HOVER = "#4F46E5"
COLOR_DARK_BTN = "#171824"         # Dark Button Surface
COLOR_DARK_BTN_HOVER = "#232638"

class AutoQuestApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DQS // Discord Quest Spoofer")
        self.geometry("1220x840")
        self.minsize(1050, 720)
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
        self.quest_thumbnails = {}

        # Animation states
        self.gear_angle_idx = 0
        self.gear_hovered = False
        self.gear_photos = []
        self.gear_photos_hover = []
        self.avatar_frames = []
        self.avatar_frame_idx = 0
        self.banner_frames = []
        self.banner_frame_idx = 0
        self.orbs_pulse_idx = 0
        self.orbs_sparkles = ["✦ ✧ ✦", "✧ ✦ ✧", "✦ ✦ ✧", "✧ ✧ ✦"]

        # Cache badge images
        self.badge_images = {}
        self._load_badge_assets()

        # Load Animation Frames
        self._load_gear_assets()
        self._load_profile_gif_assets()

        # UI Setup
        self._build_header()
        self._build_main_layout()

        # Start background animation loops (optimized & lag-free)
        self._animate_gear()
        self._animate_profile_gifs()
        self._animate_orbs_banner()

        # Initial Load
        self.after(100, self._initial_load)

    def _set_app_icon(self):
        """Sets the application window and taskbar icon cleanly using DQS.png (No .ico!)."""
        candidates = [
            os.path.join(os.path.dirname(__file__), "..", "DQS.png"),
            os.path.join(os.path.dirname(__file__), "..", "assets", "app_icon.png"),
            os.path.join(os.getcwd(), "DQS.png"),
            os.path.join(os.getcwd(), "assets", "app_icon.png"),
        ]
        for c in candidates:
            if os.path.exists(c):
                try:
                    im = Image.open(c)
                    self._app_icon_photo = ImageTk.PhotoImage(im)
                    self.iconphoto(True, self._app_icon_photo)
                    break
                except Exception:
                    pass
    def _load_badge_assets(self):
        """Loads official Discord badge PNGs."""
        badge_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "badges")
        if not os.path.exists(badge_dir):
            badge_dir = os.path.join(os.getcwd(), "assets", "badges")

        badge_names = ['nitro', 'bravery', 'booster', 'legacy', 'quest', 'orbs']
        if os.path.exists(badge_dir):
            for b in badge_names:
                p = os.path.join(badge_dir, f"{b}.png")
                if os.path.exists(p):
                    try:
                        im = Image.open(p).convert("RGBA").resize((20, 20), Image.Resampling.LANCZOS)
                        self.badge_images[b] = ImageTk.PhotoImage(im)
                    except Exception:
                        pass

    def _load_gear_assets(self):
        """Loads pre-rendered rotating gear frames as native PhotoImages for zero-lag rendering."""
        gear_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "gear")
        if not os.path.exists(gear_dir):
            gear_dir = os.path.join(os.getcwd(), "assets", "gear")

        if os.path.exists(gear_dir):
            for i in range(16):
                fpath = os.path.join(gear_dir, f"gear_{i}.png")
                if os.path.exists(fpath):
                    try:
                        im = Image.open(fpath).convert("RGBA").resize((22, 22), Image.Resampling.LANCZOS)
                        self.gear_photos.append(ImageTk.PhotoImage(im))
                    except Exception:
                        pass
                fpath_h = os.path.join(gear_dir, f"gear_h_{i}.png")
                if os.path.exists(fpath_h):
                    try:
                        im_h = Image.open(fpath_h).convert("RGBA").resize((22, 22), Image.Resampling.LANCZOS)
                        self.gear_photos_hover.append(ImageTk.PhotoImage(im_h))
                    except Exception:
                        pass

    def _load_profile_gif_assets(self):
        """Loads real animated avatar and banner GIFs into memory for silky smooth playback."""
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        if not os.path.exists(assets_dir):
            assets_dir = os.path.join(os.getcwd(), "assets")

        # 1. Avatar GIF (76x76 with clean circular cut & border ring)
        av_path = os.path.join(assets_dir, "tentix_avatar.gif")
        if os.path.exists(av_path):
            try:
                av = Image.open(av_path)
                mask = Image.new('L', (76, 76), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 76, 76), fill=255)

                for frame in ImageSequence.Iterator(av):
                    c = frame.convert("RGBA").resize((76, 76), Image.Resampling.LANCZOS)
                    c.putalpha(mask)
                    # Outer ring
                    bordered = Image.new('RGBA', (82, 82), (0, 0, 0, 0))
                    b_draw = ImageDraw.Draw(bordered)
                    b_draw.ellipse((0, 0, 82, 82), fill=(17, 18, 28, 255))
                    bordered.paste(c, (3, 3), c)
                    self.avatar_frames.append(ImageTk.PhotoImage(bordered))
            except Exception as e:
                print("Failed to load avatar GIF:", e)

        # 2. Banner GIF (340x120 edge-to-edge)
        ban_path = os.path.join(assets_dir, "tentix_banner.gif")
        if os.path.exists(ban_path):
            try:
                ban = Image.open(ban_path)
                for frame in ImageSequence.Iterator(ban):
                    c = frame.convert("RGBA").resize((340, 120), Image.Resampling.LANCZOS)
                    self.banner_frames.append(ImageTk.PhotoImage(c))
            except Exception as e:
                print("Failed to load banner GIF:", e)

    def _animate_gear(self):
        """Spins settings gear with zero CPU overhead and dynamic hover animation."""
        frames = self.gear_photos_hover if (self.gear_hovered and self.gear_photos_hover) else self.gear_photos
        if frames and hasattr(self, "lbl_gear_tk") and self.lbl_gear_tk.winfo_exists():
            if self.gear_hovered:
                self.gear_angle_idx = (self.gear_angle_idx + 1) % len(frames)
                self.lbl_gear_tk.configure(image=frames[self.gear_angle_idx])
            else:
                self.lbl_gear_tk.configure(image=frames[0])
        delay = 55 if self.gear_hovered else 300
        self.after(delay, self._animate_gear)

    def _animate_profile_gifs(self):
        """Plays avatar and banner GIFs when the drawer is visible."""
        if hasattr(self, "drawer_visible") and self.drawer_visible:
            # Avatar
            if self.avatar_frames and hasattr(self, "lbl_drawer_avatar_tk") and self.lbl_drawer_avatar_tk.winfo_exists():
                self.avatar_frame_idx = (self.avatar_frame_idx + 1) % len(self.avatar_frames)
                self.lbl_drawer_avatar_tk.configure(image=self.avatar_frames[self.avatar_frame_idx])
            # Banner
            if self.banner_frames and hasattr(self, "lbl_drawer_banner_tk") and self.lbl_drawer_banner_tk.winfo_exists():
                self.banner_frame_idx = (self.banner_frame_idx + 1) % len(self.banner_frames)
                self.lbl_drawer_banner_tk.configure(image=self.banner_frames[self.banner_frame_idx])

        self.after(60, self._animate_profile_gifs)

    def _animate_orbs_banner(self):
        """Pulses the active Orbs animation if visible."""
        if hasattr(self, "lbl_orbs_sparkle") and self.lbl_orbs_sparkle.winfo_exists():
            self.orbs_pulse_idx = (self.orbs_pulse_idx + 1) % len(self.orbs_sparkles)
            self.lbl_orbs_sparkle.configure(text=self.orbs_sparkles[self.orbs_pulse_idx])
        self.after(350, self._animate_orbs_banner)

    def _on_window_close(self):
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
        # 82px height ensures ZERO CLIPPING
        self.header_frame = ctk.CTkFrame(
            self, fg_color=COLOR_BG_SIDEBAR, height=82, corner_radius=0,
            border_width=1, border_color=COLOR_CARD_BORDER
        )
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        # Left Branding - Clean Transparent App Logo
        brand_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        brand_box.pack(side="left", padx=20, pady=12)

        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "app_icon.png")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.getcwd(), "assets", "app_icon.png")

        if os.path.exists(icon_path):
            try:
                raw_logo = Image.open(icon_path).convert("RGBA")
                self.logo_img = ctk.CTkImage(light_image=raw_logo, dark_image=raw_logo, size=(44, 44))
                lbl_icon = ctk.CTkLabel(brand_box, text="", image=self.logo_img)
                lbl_icon.pack(side="left", padx=(0, 14))
            except Exception:
                pass

        title_sub = ctk.CTkFrame(brand_box, fg_color="transparent")
        title_sub.pack(side="left")

        # Row 1: App Title + Admin Glow Pill SIDE BY SIDE (Never cut off!)
        top_row = ctk.CTkFrame(title_sub, fg_color="transparent")
        top_row.pack(anchor="w", pady=(0, 2))

        app_title = ctk.CTkLabel(
            top_row, text="DQS",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=COLOR_WHITE
        )
        app_title.pack(side="left", padx=(0, 12))

        admin_pill = ctk.CTkFrame(
            top_row, fg_color="#0c2314", border_width=1, border_color=COLOR_EMERALD, corner_radius=12
        )
        admin_pill.pack(side="left")

        ctk.CTkLabel(
            admin_pill, text="● ADMIN AKTIV",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=COLOR_EMERALD
        ).pack(padx=10, pady=3)

        # Row 2: Subtitle
        sub_badge = ctk.CTkLabel(
            title_sub, text="DISCORD QUEST SPOOFER • ULTIMATE EDITION",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        )
        sub_badge.pack(anchor="w")

        # Right User Profile Bar (Clickable to toggle profile drawer)
        self.account_bar = ctk.CTkFrame(
            self.header_frame, fg_color=COLOR_CARD_BG, corner_radius=8,
            border_width=1, border_color=COLOR_CARD_BORDER, cursor="hand2"
        )
        self.account_bar.pack(side="right", padx=20, pady=14)
        self.account_bar.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        # Native Tk Label for Gear to guarantee zero window lag
        gear_container = tk.Frame(self.account_bar, bg=COLOR_CARD_BG)
        gear_container.pack(side="left", padx=(12, 6))
        gear_container.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        initial_gear = self.gear_photos[0] if self.gear_photos else None
        self.lbl_gear_tk = tk.Label(gear_container, image=initial_gear, bg=COLOR_CARD_BG, bd=0, cursor="hand2")
        self.lbl_gear_tk.pack()
        self.lbl_gear_tk.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        # Avatar Preview
        self.avatar_label = ctk.CTkLabel(self.account_bar, text="👤", font=ctk.CTkFont(size=20), width=34, height=34)
        self.avatar_label.pack(side="left", padx=(4, 8), pady=6)
        self.avatar_label.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        user_info = ctk.CTkFrame(self.account_bar, fg_color="transparent")
        user_info.pack(side="left", padx=(0, 14), pady=6)
        user_info.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        self.lbl_username = ctk.CTkLabel(
            user_info, text="TΞП†1Ж ツ 🌙",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLOR_WHITE
        )
        self.lbl_username.pack(anchor="w")
        self.lbl_username.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        self.lbl_status = ctk.CTkLabel(
            user_info, text="🩸 BEHIND EVERY KISS...",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color="#f87171"
        )
        self.lbl_status.pack(anchor="w")
        self.lbl_status.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        # Account Bar & Gear Hover Glow Animation
        def _on_acc_enter(e):
            self.account_bar.configure(border_color=COLOR_CARD_BORDER_ACTIVE, fg_color="#181928")
            gear_container.configure(bg="#181928")
            self.lbl_gear_tk.configure(bg="#181928")
            self.gear_hovered = True

        def _on_acc_leave(e):
            self.account_bar.configure(border_color=COLOR_CARD_BORDER, fg_color=COLOR_CARD_BG)
            gear_container.configure(bg=COLOR_CARD_BG)
            self.lbl_gear_tk.configure(bg=COLOR_CARD_BG)
            self.gear_hovered = False

        self.account_bar.bind("<Enter>", _on_acc_enter)
        self.account_bar.bind("<Leave>", _on_acc_leave)
        gear_container.bind("<Enter>", _on_acc_enter)
        gear_container.bind("<Leave>", _on_acc_leave)
        self.lbl_gear_tk.bind("<Enter>", _on_acc_enter)
        self.lbl_gear_tk.bind("<Leave>", _on_acc_leave)

    # ================= BODY & TABS =================

    def _build_main_layout(self):
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Main Workspace on Left
        self.main_work_frame = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        self.main_work_frame.pack(side="left", fill="both", expand=True)

        # 5 Sleek Tabs
        self.tabview = ctk.CTkTabview(
            self.main_work_frame, fg_color=COLOR_BG_SIDEBAR,
            segmented_button_fg_color=COLOR_CARD_BG,
            segmented_button_selected_color=COLOR_NEON_BLURPLE,
            segmented_button_selected_hover_color=COLOR_NEON_BLURPLE_HOVER,
            segmented_button_unselected_color=COLOR_CARD_BG,
            segmented_button_unselected_hover_color=COLOR_DARK_BTN_HOVER,
            text_color=COLOR_WHITE,
            corner_radius=8
        )
        self.tabview.pack(fill="both", expand=True)

        self.tab_quests = self.tabview.add("⚔️ DISCORD QUESTS")
        self.tab_videos = self.tabview.add("🎬 VIDEOS & TRAILER")
        self.tab_simulator = self.tabview.add("🎮 SPIELE-SIMULATOR")
        self.tab_console = self.tabview.add("⚡ 1-KLICK SCHNELL-SCRIPT")
        self.tab_logs = self.tabview.add("📋 LIVE-PROTOKOLL")

        self._setup_quests_tab()
        self._setup_videos_tab()
        self._setup_simulator_tab()
        self._setup_console_tab()
        self._setup_logs_tab()

        # Collapsible Profile Drawer (Right Side)
        self.drawer_visible = False
        self._build_profile_drawer()

    # ================= DISCORD PROFILE DRAWER (ACCURATE & ANIMATED) =================

    def _build_profile_drawer(self):
        """Creates the authentic Discord User Profile popout matching Image 2 with real GIF animation."""
        self.drawer_frame = ctk.CTkFrame(
            self.body_frame, width=360, fg_color=COLOR_BG_SIDEBAR, corner_radius=10,
            border_width=1, border_color=COLOR_CARD_BORDER
        )

        self.drawer_scroll = ctk.CTkScrollableFrame(self.drawer_frame, fg_color="transparent")
        self.drawer_scroll.pack(fill="both", expand=True, padx=4, pady=6)

        # Profile Card Wrapper
        card_wrapper = ctk.CTkFrame(self.drawer_scroll, fg_color=COLOR_CARD_BG, corner_radius=10, border_width=1, border_color="#202336")
        card_wrapper.pack(fill="x", padx=4, pady=(0, 10))

        # 1. Top Banner & Overlapping Avatar Area (150px height)
        header_canvas_frame = tk.Frame(card_wrapper, bg=COLOR_CARD_BG, width=340, height=160)
        header_canvas_frame.pack(fill="x")
        header_canvas_frame.pack_propagate(False)

        # Banner at top (120px)
        init_banner = self.banner_frames[0] if self.banner_frames else None
        self.lbl_drawer_banner_tk = tk.Label(header_canvas_frame, image=init_banner, bg="#1a1c29", bd=0)
        self.lbl_drawer_banner_tk.place(x=0, y=0, width=340, height=120)

        # Overlapping Avatar placed at (18, 75)
        init_av = self.avatar_frames[0] if self.avatar_frames else None
        self.lbl_drawer_avatar_tk = tk.Label(header_canvas_frame, image=init_av, bg=COLOR_CARD_BG, bd=0)
        self.lbl_drawer_avatar_tk.place(x=18, y=74)

        # DND Status Badge (Red Dot with white bar) at (74, 132)
        dnd_badge = tk.Frame(header_canvas_frame, bg="#f23f43", width=18, height=18, highlightbackground=COLOR_CARD_BG, highlightthickness=3)
        dnd_badge.place(x=74, y=130)

        # 2. Content below header
        content_box = ctk.CTkFrame(card_wrapper, fg_color="transparent")
        content_box.pack(fill="x", padx=12, pady=(10, 12))

        # Status Speech Bubble (Fully visible, wrapping, no cutoff!)
        bubble_box = ctk.CTkFrame(content_box, fg_color="#181926", border_width=1, border_color="#2c2e44", corner_radius=8)
        bubble_box.pack(fill="x", pady=(0, 10))

        lbl_b_text = ctk.CTkLabel(
            bubble_box, text="🩸 BEHIND EVERY KISS IS A CLAW THAT CAN BITE",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=COLOR_WHITE, justify="left", wraplength=290
        )
        lbl_b_text.pack(padx=10, pady=8, anchor="w")

        # Name and Pronouns
        name_box = ctk.CTkFrame(content_box, fg_color="transparent")
        name_box.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            name_box, text="TΞП†1Ж ツ",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(anchor="w")

        ctk.CTkLabel(
            name_box, text="tentix • - ʜᴇᴀʀᴛ/ʟᴇꜱꜱ/ᴡɪᴛʜᴏᴜᴛ/ʏᴏᴜ -",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w")

        # 3. Badges Row (Authentic Discord badge PNGs)
        badges_pill = ctk.CTkFrame(content_box, fg_color="#141522", corner_radius=8, border_width=1, border_color="#222538")
        badges_pill.pack(fill="x", pady=(0, 12))

        badge_inner = tk.Frame(badges_pill, bg="#141522")
        badge_inner.pack(padx=10, pady=7, anchor="w")

        for b_name in ['nitro', 'bravery', 'booster', 'legacy', 'quest', 'orbs']:
            if b_name in self.badge_images:
                tk.Label(badge_inner, image=self.badge_images[b_name], bg="#141522", bd=0).pack(side="left", padx=5)

        # 4. Bio Section
        ctk.CTkLabel(
            content_box, text="ÜBER MICH",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(0, 3))

        bio_card = ctk.CTkFrame(content_box, fg_color="#141522", corner_radius=8, border_width=1, border_color="#222538")
        bio_card.pack(fill="x", pady=(0, 12))

        bio_content = (
            "ㅤ ㅤ ₊⊹ - ♱ https://tentix.space ♱ - ⊹₊\n"
            "ㅤㅤㅤㅤ      ⋆｡‧₊°♱༺𓆩❦︎𓆪༻♱༉‧₊˚.\n"
            "˚ʚ♡ɞ˚ ㅤ       ⊹ ࣪   𝕽𝖚𝖑𝖊 𝖇𝖗𝖊𝖆𝖐𝖊𝖗⊹ ࣪ ˖            ˚ʚ♡ɞ˚\n"
            "ㅤㅤㅤㅤ   ⛧°  。 ⋆༺♱༻⋆   。°⛧"
        )
        ctk.CTkLabel(
            bio_card, text=bio_content,
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color="#d1d5db", justify="center"
        ).pack(padx=10, pady=8, anchor="center")

        # 5. Activity Box ("SPIELT")
        ctk.CTkLabel(
            content_box, text="AKTIVITÄT",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(0, 3))

        activity_box = ctk.CTkFrame(content_box, fg_color="#141522", border_width=1, border_color="#222538", corner_radius=8)
        activity_box.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            activity_box, text="🎮 HELLDIVERS™ 2",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(anchor="w", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            activity_box, text="In Mission (Quest läuft)",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLOR_EMERALD
        ).pack(anchor="w", padx=12, pady=(0, 2))

        ctk.CTkLabel(
            activity_box, text="⏱ Zeit: 03:21 Min.",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=12, pady=(0, 10))

        # Drawer Actions
        ctk.CTkButton(
            content_box, text="👤 ACCOUNT WECHSELN", height=34,
            fg_color=COLOR_INDIGO, hover_color=COLOR_INDIGO_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=6, command=self._open_account_modal
        ).pack(fill="x", pady=4)

        self.btn_copy_id = ctk.CTkButton(
            content_box, text="🆔 NUTZER-ID KOPIEREN", height=34,
            fg_color=COLOR_DARK_BTN, hover_color=COLOR_DARK_BTN_HOVER,
            border_width=1, border_color=COLOR_CARD_BORDER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=6, command=self._copy_user_id
        )
        self.btn_copy_id.pack(fill="x", pady=4)

        # Official GitHub & Safety
        ctk.CTkButton(
            content_box, text="⭐ OFFIZIELLER GITHUB (V1)", height=34,
            fg_color="#2b1a38", hover_color="#3e2552",
            border_width=1, border_color="#9333ea",
            text_color="#c084fc", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=6, command=lambda: webbrowser.open("https://github.com/TentixTV/Discord-Quest-Spoofer")
        ).pack(fill="x", pady=4)

        info_box = ctk.CTkFrame(content_box, fg_color="#0e0f17", border_width=1, border_color="#1c1e2d", corner_radius=6)
        info_box.pack(fill="x", pady=(6, 4))
        ctk.CTkLabel(
            info_box, text="DQS Release V1 by Sandro (T3X / TNTIX)\n100% sauber wenn von GitHub geladen!\nWer es woanders her hat ist selber schuld.",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=COLOR_TEXT_MUTED, justify="center"
        ).pack(padx=6, pady=6)

        ctk.CTkButton(
            content_box, text="✕ SCHLIESSEN", height=30,
            fg_color="transparent", hover_color="#202230",
            text_color=COLOR_TEXT_MUTED, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            command=self._toggle_profile_drawer
        ).pack(fill="x", pady=(4, 0))

    def _toggle_profile_drawer(self):
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

    # ================= TAB 1: Quests & Auto-Farm =================

    def _setup_quests_tab(self):
        top_bar = ctk.CTkFrame(
            self.tab_quests, fg_color=COLOR_CARD_BG, corner_radius=8,
            border_width=1, border_color=COLOR_CARD_BORDER
        )
        top_bar.pack(fill="x", padx=10, pady=(10, 8))

        lbl_summary = ctk.CTkLabel(
            top_bar, text="AKTIVE DISCORD AUFGABEN",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_WHITE
        )
        lbl_summary.pack(side="left", padx=15, pady=10)

        btn_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_box.pack(side="right", padx=15, pady=10)

        ctk.CTkButton(
            btn_box, text="🔄 AKTUALISIEREN", width=130, height=34,
            fg_color=COLOR_DARK_BTN, hover_color=COLOR_DARK_BTN_HOVER,
            border_width=1, border_color=COLOR_CARD_BORDER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=4,
            command=self.refresh_quests
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_box, text="📥 ALLE ANNEHMEN", width=140, height=34,
            fg_color=COLOR_INDIGO, hover_color=COLOR_INDIGO_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=4,
            command=self.enroll_all_quests
        ).pack(side="left", padx=5)

        self.btn_auto_farm = ctk.CTkButton(
            btn_box, text="⚡ ALLE QUESTS FARMEN", width=180, height=34,
            fg_color=COLOR_NEON_BLURPLE, hover_color=COLOR_NEON_BLURPLE_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=4,
            command=self.toggle_auto_farm
        )
        self.btn_auto_farm.pack(side="left", padx=5)

        # Fast-Track Info Banner
        fast_banner = ctk.CTkFrame(
            self.tab_quests, fg_color="#0e1322", corner_radius=8,
            border_width=1, border_color=COLOR_NEON_BLURPLE
        )
        fast_banner.pack(fill="x", padx=10, pady=(0, 8))

        fast_text = ctk.CTkLabel(
            fast_banner,
            text="💡 TIPP FÜR SOFORTIGEN %-ANSTIEG: Discord zählt Spielzeit via interne Heartbeats.\n"
                 "Nutze das 1-Klick Schnell-Script (Tab 4) – damit steigen alle % sofort live & Orbs werden geholt!",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_GOLD, justify="left"
        )
        fast_text.pack(side="left", padx=15, pady=10)

        ctk.CTkButton(
            fast_banner, text="⚡ 1-KLICK SCHNELL-SCRIPT", width=220, height=32,
            fg_color=COLOR_EMERALD, hover_color=COLOR_EMERALD_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=4,
            command=self._jump_to_console_script
        ).pack(side="right", padx=15, pady=10)

        # Animated Live Orbs Status Bar
        self.live_orbs_frame = ctk.CTkFrame(
            self.tab_quests, fg_color="#17122b", border_width=1, border_color="#8b5cf6", corner_radius=8
        )

        orbs_left = ctk.CTkFrame(self.live_orbs_frame, fg_color="transparent")
        orbs_left.pack(side="left", padx=15, pady=8)

        ctk.CTkLabel(orbs_left, text="🔮", font=ctk.CTkFont(size=20)).pack(side="left", padx=(0, 8))

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
        self.tabview.set("⚡ 1-KLICK SCHNELL-SCRIPT")

    # ================= TAB 2: VIDEOS & TRAILER GALLERY =================

    def _setup_videos_tab(self):
        top_bar = ctk.CTkFrame(
            self.tab_videos, fg_color=COLOR_CARD_BG, corner_radius=8,
            border_width=1, border_color=COLOR_CARD_BORDER
        )
        top_bar.pack(fill="x", padx=10, pady=(10, 8))

        ctk.CTkLabel(
            top_bar, text="🎬 ALLE QUEST-VIDEOS & OFFIZIELLE TRAILER (720P HD)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(side="left", padx=15, pady=10)

        ctk.CTkLabel(
            top_bar, text="Klicke auf 'Abspielen', um das Video im Player/Browser zu sehen, oder 'Express-Abschluss' für sofortige Belohnung.",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLOR_TEXT_MUTED
        ).pack(side="right", padx=15, pady=10)

        self.videos_scroll = ctk.CTkScrollableFrame(
            self.tab_videos, fg_color="transparent",
            label_text="VERFÜGBARE QUEST-VIDEOS & STREAMS",
            label_font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            label_text_color=COLOR_TEXT_MUTED
        )
        self.videos_scroll.pack(fill="both", expand=True, padx=5, pady=5)

    def _render_videos_tab(self, quests):
        """Populates the Videos & Trailer gallery with ALL quest videos & official trailers."""
        for w in self.videos_scroll.winfo_children():
            w.destroy()

        vids_found = 0
        for q in quests:
            vid_url = q.get("video_url")
            qid = q.get("id")
            qname = q.get("quest_name")
            game_title = q.get("game_title")
            publisher = q.get("game_publisher", "")
            target_sec = q.get("target_seconds", 30)
            app_id = q.get("app_id", "")

            vids_found += 1
            card = ctk.CTkFrame(self.videos_scroll, fg_color=COLOR_CARD_BG, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=8)
            card.pack(fill="x", padx=10, pady=8)

            def _on_v_enter(e, c=card):
                if c.winfo_exists():
                    c.configure(border_color="#8b5cf6", fg_color="#181928")
            def _on_v_leave(e, c=card):
                if c.winfo_exists():
                    c.configure(border_color=COLOR_CARD_BORDER, fg_color=COLOR_CARD_BG)

            card.bind("<Enter>", _on_v_enter)
            card.bind("<Leave>", _on_v_leave)

            left_box = ctk.CTkFrame(card, fg_color="transparent")
            left_box.pack(side="left", padx=15, pady=12)

            thumb = self._get_quest_thumbnail(qid, (100, 56))
            if thumb:
                lbl_thumb = tk.Label(left_box, image=thumb, bg=COLOR_CARD_BG, bd=0)
                lbl_thumb.pack(side="left", padx=(0, 14))
            else:
                ctk.CTkLabel(left_box, text="🎬", font=ctk.CTkFont(size=28)).pack(side="left", padx=(0, 14))

            info_box = ctk.CTkFrame(left_box, fg_color="transparent")
            info_box.pack(side="left")

            ctk.CTkLabel(
                info_box, text=f"{game_title} - {qname}",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLOR_WHITE
            ).pack(anchor="w")

            if vid_url:
                sub_txt = f"Publisher: {publisher or 'Discord'}  |  Format: 720p HD MP4 (Offizieller Discord Stream)  |  Dauer: ~{target_sec} Sek."
            else:
                sub_txt = f"Publisher: {publisher or 'Discord'}  |  Format: Offizieller HD Trailer & Stream  |  Dauer: ~15 Min."

            ctk.CTkLabel(
                info_box, text=sub_txt,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=COLOR_TEXT_MUTED
            ).pack(anchor="w")

            btn_box = ctk.CTkFrame(card, fg_color="transparent")
            btn_box.pack(side="right", padx=15, pady=12)

            if vid_url:
                ctk.CTkButton(
                    btn_box, text="▶ 720P HD VIDEO ABSPIELEN", width=180, height=32,
                    fg_color=COLOR_INDIGO, hover_color=COLOR_INDIGO_HOVER,
                    text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    corner_radius=4, command=lambda u=vid_url: webbrowser.open(u)
                ).pack(side="left", padx=5)

                ctk.CTkButton(
                    btn_box, text="⚡ EXPRESS-ABSCHLUSS", width=160, height=32,
                    fg_color=COLOR_GOLD, hover_color=COLOR_GOLD_HOVER,
                    text_color="#000000", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    corner_radius=4, command=lambda qid=qid, t=target_sec: self._fast_video_quest(qid, t, None)
                ).pack(side="left", padx=5)
            else:
                yt_query = f"{game_title} official trailer".replace(' ', '+')
                trailer_url = f"https://www.youtube.com/results?search_query={yt_query}"
                ctk.CTkButton(
                    btn_box, text="▶ OFFIZIELLEN TRAILER ANSEHEN", width=190, height=32,
                    fg_color="#27273a", hover_color="#3b3b55",
                    border_width=1, border_color="#4f46e5",
                    text_color="#a5b4fc", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    corner_radius=4, command=lambda u=trailer_url: webbrowser.open(u)
                ).pack(side="left", padx=5)

                ctk.CTkButton(
                    btn_box, text="🎮 IM SIMULATOR STARTEN", width=170, height=32,
                    fg_color=COLOR_INDIGO, hover_color=COLOR_INDIGO_HOVER,
                    text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    corner_radius=4, command=lambda aid=app_id, gt=game_title: self._sim_single_quest(aid, gt)
                ).pack(side="left", padx=5)

        if vids_found == 0:
            ctk.CTkLabel(
                self.videos_scroll, text="Keine Quests gefunden. Bitte aktualisiere deine Quests.",
                font=ctk.CTkFont(family="Segoe UI", size=12), text_color=COLOR_TEXT_MUTED
            ).pack(pady=40)

    def _get_quest_thumbnail(self, qid, size=(100, 56)):
        """Returns PhotoImage thumbnail for quest banner if cached."""
        if qid in self.quest_thumbnails:
            return self.quest_thumbnails[qid]

        p = os.path.join(os.path.dirname(__file__), "..", "assets", "quests", f"{qid}.jpg")
        if not os.path.exists(p):
            p = os.path.join(os.getcwd(), "assets", "quests", f"{qid}.jpg")

        if os.path.exists(p):
            try:
                im = Image.open(p).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
                tk_im = ImageTk.PhotoImage(im)
                self.quest_thumbnails[qid] = tk_im
                return tk_im
            except Exception:
                pass
        return None

    # ================= TAB 3: SIMULATOR (WITH AUTO-PRESET) =================

    def _setup_simulator_tab(self):
        container = ctk.CTkFrame(
            self.tab_simulator, fg_color=COLOR_CARD_BG, corner_radius=8,
            border_width=1, border_color=COLOR_CARD_BORDER
        )
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # Modern Simulator Sub-Header / Nav
        sub_nav = ctk.CTkFrame(container, fg_color="#0d0e17", corner_radius=8, border_width=1, border_color="#1f2235")
        sub_nav.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            sub_nav, text="🎮 NATIVE WINDOWS SPIEL-EMULATION",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(side="left", padx=15, pady=10)

        self.lbl_sim_indicator = ctk.CTkLabel(
            sub_nav, text="● SIMULATOR BEREIT",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        )
        self.lbl_sim_indicator.pack(side="right", padx=15, pady=10)

        desc = ctk.CTkLabel(
            container,
            text="Simuliert einen echten Windows-Spielprozess (~2MB RAM) mit passendem Dateinamen, Fenstertitel und Win32-Handles,\n"
                 "damit Discord das Spiel zu 100% als aktiv erkennt und die Quests hochzählen.",
            font=ctk.CTkFont(family="Segoe UI", size=11), text_color=COLOR_TEXT_MUTED, justify="left"
        )
        desc.pack(anchor="w", padx=25, pady=(0, 15))

        # Preset Selector
        preset_box = ctk.CTkFrame(container, fg_color="transparent")
        preset_box.pack(fill="x", padx=25, pady=5)

        ctk.CTkLabel(
            preset_box, text="SPIELVORLAGE WÄHLEN:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_WHITE, width=160, anchor="w"
        ).pack(side="left")

        game_titles = [f"{info['name']} ({info['category']})" for app_id, info in QUEST_GAMES_DATABASE.items()]

        self.preset_menu = ctk.CTkOptionMenu(
            preset_box, values=game_titles, width=380, height=32,
            fg_color=COLOR_BG_DARK, button_color=COLOR_NEON_BLURPLE,
            button_hover_color=COLOR_NEON_BLURPLE_HOVER,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            command=self._on_preset_selected
        )
        self.preset_menu.pack(side="left", padx=10)

        # Fields Card
        fields_card = ctk.CTkFrame(container, fg_color="#0a0b12", corner_radius=8, border_width=1, border_color="#1c1e2d")
        fields_card.pack(fill="x", padx=25, pady=12)

        # Field 1: Window Title
        row1 = ctk.CTkFrame(fields_card, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(row1, text="Fenstertitel:", width=120, anchor="w", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=COLOR_TEXT_MUTED).pack(side="left")
        self.entry_sim_title = ctk.CTkEntry(row1, width=420, fg_color=COLOR_BG_DARK, border_color=COLOR_CARD_BORDER)
        self.entry_sim_title.pack(side="left")

        # Field 2: Executable
        row2 = ctk.CTkFrame(fields_card, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(row2, text="Prozess-Dateiname:", width=120, anchor="w", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=COLOR_TEXT_MUTED).pack(side="left")
        self.entry_sim_exe = ctk.CTkEntry(row2, width=420, fg_color=COLOR_BG_DARK, border_color=COLOR_CARD_BORDER)
        self.entry_sim_exe.pack(side="left")

        # Field 3: App ID
        row3 = ctk.CTkFrame(fields_card, fg_color="transparent")
        row3.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(row3, text="Discord App-ID:", width=120, anchor="w", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=COLOR_TEXT_MUTED).pack(side="left")
        self.entry_sim_appid = ctk.CTkEntry(row3, width=420, fg_color=COLOR_BG_DARK, border_color=COLOR_CARD_BORDER)
        self.entry_sim_appid.pack(side="left")

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

    # ================= TAB 4: CONSOLE QUICK SNIPPET =================

    def _setup_console_tab(self):
        container = ctk.CTkFrame(
            self.tab_console, fg_color=COLOR_CARD_BG, corner_radius=8,
            border_width=1, border_color=COLOR_CARD_BORDER
        )
        container.pack(fill="both", expand=True, padx=15, pady=15)

        title = ctk.CTkLabel(
            container, text="1-KLICK IN-DISCORD TURBO ENGINE (100% GARANTIE)",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLOR_WHITE
        )
        title.pack(anchor="w", padx=25, pady=(18, 5))

        # Prominent Safety Warning Box
        warning_box = ctk.CTkFrame(container, fg_color="#2b1414", border_width=1, border_color="#ef4444", corner_radius=8)
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
                 "3️⃣ Falls Discord das Einfügen blockiert: tippe  allow pasting  ein und drücke Enter\n"
                 "4️⃣ Klicke hier unten auf 'SKRIPT KOPIEREN' und füge es mit STRG + V in Discord ein\n"
                 "5️⃣ Drücke Enter -> Fertig! Alle Quests zählen sofort live hoch!",
            font=ctk.CTkFont(family="Segoe UI", size=11), text_color=COLOR_TEXT_PRIMARY, justify="left"
        )
        desc.pack(anchor="w", padx=25, pady=(0, 10))

        self.textbox_snippet = ctk.CTkTextbox(
            container, height=130, fg_color=COLOR_BG_DARK,
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color="#a5b4fc"
        )
        self.textbox_snippet.pack(fill="x", padx=25, pady=(0, 10))
        self.textbox_snippet.insert("1.0", generate_discord_console_snippet())
        self.textbox_snippet.configure(state="disabled")

        self.btn_copy_snippet = ctk.CTkButton(
            container, text="📋 SKRIPT IN ZWISCHENABLAGE KOPIEREN", height=38,
            fg_color=COLOR_CYAN, hover_color=COLOR_CYAN_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            corner_radius=4,
            command=self._copy_console_script
        )
        self.btn_copy_snippet.pack(anchor="w", padx=25, pady=(0, 10))

    def _copy_console_script(self):
        script = generate_discord_console_snippet()
        self.clipboard_clear()
        self.clipboard_append(script)
        self.btn_copy_snippet.configure(text="✓ SKRIPT KOPIERT! JETZT IN DISCORD EINFÜGEN (STRG + V)")
        self.log("Turbo-Skript in Zwischenablage kopiert.", "SUCCESS")
        self.after(3500, lambda: self.btn_copy_snippet.configure(text="📋 SKRIPT IN ZWISCHENABLAGE KOPIEREN"))

    # ================= TAB 5: LOGS =================

    def _setup_logs_tab(self):
        container = ctk.CTkFrame(
            self.tab_logs, fg_color=COLOR_CARD_BG, corner_radius=8,
            border_width=1, border_color=COLOR_CARD_BORDER
        )
        container.pack(fill="both", expand=True, padx=15, pady=15)

        top_log_bar = ctk.CTkFrame(container, fg_color="transparent")
        top_log_bar.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            top_log_bar, text="SYSTEM-PROTOKOLL",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(side="left")

        ctk.CTkButton(
            top_log_bar, text="🗑️ LEEREN", width=90, height=28,
            fg_color=COLOR_DARK_BTN, hover_color=COLOR_DARK_BTN_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            corner_radius=4,
            command=self.clear_logs
        ).pack(side="right")

        self.log_box = ctk.CTkTextbox(
            container, fg_color=COLOR_BG_DARK,
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=COLOR_TEXT_PRIMARY
        )
        self.log_box.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    def log(self, message: str, level: str = "INFO"):
        timestamp = time.strftime("%H:%M:%S")
        prefix = f"[{timestamp}] [{level.upper()}] "
        full_msg = f"{prefix}{message}\n"
        try:
            self.log_box.insert("end", full_msg)
            self.log_box.see("end")
        except Exception:
            pass

    def clear_logs(self):
        self.log_box.delete("1.0", "end")
        self.log("Protokoll geleert.", "INFO")

    # ================= CONTROLLERS & LOGIC =================

    def _initial_load(self):
        self.log("DQS gestartet. Prüfe Administrator-Rechte & Accounts...", "INFO")
        self.detected_accounts = find_all_valid_accounts()
        if self.detected_accounts:
            # Prioritize tentix if present
            tentix_acc = next((a for a in self.detected_accounts if a.get("username") == "tentix"), None)
            chosen = tentix_acc or self.detected_accounts[0]
            self._set_active_account(chosen)
        else:
            self.log("Keine aktiven Discord-Tokens lokal gefunden. Bitte manuell anmelden.", "WARNING")
            self._open_account_modal()

    def _set_active_account(self, acc_info: dict):
        self.current_user = acc_info
        username = acc_info.get("username", "Unbekannt")
        token = acc_info.get("token", "")

        disp_name = acc_info.get("global_name") or username
        self.lbl_username.configure(text=disp_name)

        self.api = DiscordQuestsAPI(token)
        # Fix QuestFarmer initialization bug (no log_callback arg!)
        self.farmer = QuestFarmer(api=self.api, simulator=self.simulator)
        self.farmer.on_log = self.log
        self.farmer.on_progress = self._on_farm_quest_progress

        self.log(f"Account gewechselt zu: {disp_name} (ID: {acc_info.get('id')})", "SUCCESS")
        self.refresh_quests()

    def refresh_quests(self):
        if not self.api:
            return
        self.log("Lade aktuelle Quests von Discord API...", "INFO")
        threading.Thread(target=self._async_fetch_quests, daemon=True).start()

    def _async_fetch_quests(self):
        try:
            quests = self.api.get_parsed_quests()
            self.cached_quests = quests
            self.after(0, lambda: self._render_quests(quests))
            self.after(0, lambda: self._render_videos_tab(quests))
            self.after(0, lambda: self.log(f"{len(quests)} Quests erfolgreich synchronisiert.", "SUCCESS"))
        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda m=err_msg: self.log(f"Fehler beim Laden der Quests: {m}", "ERROR"))

    def _render_quests(self, quests):
        for widget in self.quests_scroll.winfo_children():
            widget.destroy()

        self.quest_cards.clear()

        if not quests:
            empty_lbl = ctk.CTkLabel(
                self.quests_scroll,
                text="Keine aktiven Quests auf diesem Account gefunden!",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLOR_TEXT_MUTED
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
        vid_url = q.get("video_url")

        card = ctk.CTkFrame(
            self.quests_scroll, fg_color=COLOR_CARD_BG, corner_radius=8,
            border_width=1, border_color=COLOR_CARD_BORDER_ACTIVE if enrolled and not claimed else COLOR_CARD_BORDER
        )
        card.pack(fill="x", padx=10, pady=7)

        # Smooth Hover Glow Animation for Quest Card
        def _on_card_enter(e):
            if card.winfo_exists():
                card.configure(border_color=COLOR_NEON_BLURPLE, fg_color="#181928")
        def _on_card_leave(e):
            if card.winfo_exists():
                normal_b = COLOR_CARD_BORDER_ACTIVE if (enrolled and not claimed) else COLOR_CARD_BORDER
                card.configure(border_color=normal_b, fg_color=COLOR_CARD_BG)

        card.bind("<Enter>", _on_card_enter)
        card.bind("<Leave>", _on_card_leave)

        left_box = ctk.CTkFrame(card, fg_color="transparent")
        left_box.pack(side="left", padx=14, pady=12, fill="y")

        # Game Thumbnail Banner (Authentic 100x56)
        thumb = self._get_quest_thumbnail(qid, (100, 56))
        if thumb:
            lbl_thumb = tk.Label(left_box, image=thumb, bg=COLOR_CARD_BG, bd=0)
            lbl_thumb.pack(side="left", padx=(0, 14))
        else:
            type_icon = "🎬" if ("VIDEO" in task_type or vid_url) else ("🎮" if "PLAY" in task_type else "⚔️")
            lbl_icon = ctk.CTkLabel(left_box, text=type_icon, font=ctk.CTkFont(size=24), width=40)
            lbl_icon.pack(side="left", padx=(0, 14))

        details = ctk.CTkFrame(left_box, fg_color="transparent")
        details.pack(side="left")

        lbl_qname = ctk.CTkLabel(
            details, text=f"{game_title}: {qname}",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_WHITE
        )
        lbl_qname.pack(anchor="w")

        info_line = f"App-ID: {app_id}  |  Aufgabe: {task_type}  |  Belohnung: {rewards_text}"
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

        prog_bar = ctk.CTkProgressBar(right_box, width=170, height=8, progress_color=COLOR_NEON_BLURPLE)
        prog_bar.set(pct / 100.0)
        prog_bar.pack(anchor="e", pady=(0, 8))

        btn_row = ctk.CTkFrame(right_box, fg_color="transparent")
        btn_row.pack(anchor="e")

        # Optional "Video ansehen" button if video asset exists
        if vid_url:
            btn_vid = ctk.CTkButton(
                btn_row, text="▶ VIDEO", width=80, height=28,
                fg_color=COLOR_DARK_BTN, hover_color=COLOR_DARK_BTN_HOVER,
                border_width=1, border_color="#7c3aed",
                text_color="#c084fc", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                corner_radius=4, command=lambda u=vid_url: webbrowser.open(u)
            )
            btn_vid.pack(side="left", padx=(0, 6))

        btn_action = ctk.CTkButton(
            btn_row, text="START", width=120, height=28,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            corner_radius=4
        )
        btn_action.pack(side="left")

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
        if btn:
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
                if btn:
                    self.after(0, lambda: btn.configure(state="normal", text="⚡ VIDEO ABSCHLIESSEN"))
        threading.Thread(target=_bg, daemon=True).start()

    def _sim_single_quest(self, app_id: str, game_title: str):
        """Switches to Simulator Tab and AUTOMATICALLY UPDATES THE PRESET & VALUES as requested!"""
        self.tabview.set("🎮 SPIELE-SIMULATOR")

        # Find matching preset in QUEST_GAMES_DATABASE
        matched_key = None
        matched_info = None

        for k, info in QUEST_GAMES_DATABASE.items():
            if str(k) == str(app_id) or info["name"].lower() in game_title.lower() or game_title.lower() in info["name"].lower():
                matched_key = k
                matched_info = info
                break

        if matched_info:
            preset_title_str = f"{matched_info['name']} ({matched_info['category']})"
            self.preset_menu.set(preset_title_str)
            self.entry_sim_title.delete(0, "end")
            self.entry_sim_title.insert(0, matched_info["title"])
            self.entry_sim_exe.delete(0, "end")
            self.entry_sim_exe.insert(0, matched_info["exe"])
            self.entry_sim_appid.delete(0, "end")
            self.entry_sim_appid.insert(0, str(matched_key))
            self.log(f"Spielvorlage automatisch auf '{matched_info['name']}' gesetzt.", "SUCCESS")
        else:
            clean_exe = game_title.lower().replace(":", "").replace("'", "").replace(" ", "_") + ".exe"
            self.entry_sim_title.delete(0, "end")
            self.entry_sim_title.insert(0, game_title)
            self.entry_sim_exe.delete(0, "end")
            self.entry_sim_exe.insert(0, clean_exe)
            self.entry_sim_appid.delete(0, "end")
            self.entry_sim_appid.insert(0, app_id or "1205090671527071784")
            self.log(f"Spielvorlage dynamisch auf '{game_title}' ({clean_exe}) angepasst.", "INFO")

        # Automatically start the simulation!
        self.start_manual_simulation()

    def enroll_all_quests(self):
        if not self.cached_quests or not self.api:
            return
        def _bg():
            count = 0
            for q in self.cached_quests:
                if not q.get("enrolled"):
                    self.api.enroll_quest(q["id"])
                    count += 1
                    time.sleep(0.4)
            self.log(f"{count} Quests angenommen.", "SUCCESS")
            self.after(500, self.refresh_quests)
        threading.Thread(target=_bg, daemon=True).start()

    def toggle_auto_farm(self):
        if not self.farmer:
            return
        if self.farmer.running:
            self.farmer.stop()
            self.btn_auto_farm.configure(text="⚡ ALLE QUESTS FARMEN", fg_color=COLOR_NEON_BLURPLE)
            self.live_orbs_frame.pack_forget()
            self.log("Auto-Farm gestoppt.", "WARNING")
        else:
            self.btn_auto_farm.configure(text="⏹ FARM STOPPEN", fg_color=COLOR_CRIMSON)
            self.live_orbs_frame.pack(fill="x", padx=10, pady=(0, 8), before=self.quests_scroll)
            self.farmer.start_farm_all(self.cached_quests)

    def _on_farm_quest_progress(self, p_info):
        if isinstance(p_info, dict):
            qid = p_info.get("quest_id")
            pct = p_info.get("percent", 0)
            curr = p_info.get("current_seconds", 0)
            target = p_info.get("target_seconds", 900)
            if qid in self.quest_cards:
                cd = self.quest_cards[qid]
                self.after(0, lambda: cd["bar"].set(pct / 100.0))
                p_text = f"{curr // 60}/{target // 60} MIN. ({pct:.0f}%)" if target > 60 else f"{curr}/{target}S ({pct:.0f}%)"
                self.after(0, lambda: cd["label"].configure(text=p_text))

    # ================= SIMULATOR CONTROLS =================

    def start_manual_simulation(self):
        title = self.entry_sim_title.get().strip()
        exe = self.entry_sim_exe.get().strip()
        aid = self.entry_sim_appid.get().strip()

        if not title:
            messagebox.showwarning("Hinweis", "Bitte einen Fenstertitel eingeben.")
            return

        self.log(f"Starte Spiel-Simulation: '{title}' ({exe})...", "INFO")
        res = self.simulator.start_simulation(app_id=aid, game_title=title, custom_exe=exe)
        ok = res and res.get("success")
        if ok:
            self.lbl_sim_status.configure(
                text=f"Status: ● AKTIV - Simuliert '{title}' ({exe})",
                text_color=COLOR_EMERALD
            )
            self.lbl_sim_indicator.configure(text=f"● AKTIV: {title}", text_color=COLOR_EMERALD)
            self.btn_start_sim.configure(state="disabled")
            self.log(f"Simulation erfolgreich gestartet! Discord erkennt {title}.", "SUCCESS")
        else:
            self.lbl_sim_status.configure(text="Status: Fehler beim Starten.", text_color=COLOR_CRIMSON)
            self.lbl_sim_indicator.configure(text="● FEHLER", text_color=COLOR_CRIMSON)

    def stop_manual_simulation(self):
        self.simulator.stop_simulation()
        self.lbl_sim_status.configure(text="Status: Gestoppt. Bereit.", text_color=COLOR_TEXT_MUTED)
        self.lbl_sim_indicator.configure(text="● SIMULATOR BEREIT", text_color=COLOR_TEXT_MUTED)
        self.btn_start_sim.configure(state="normal")
        self.log("Simulation beendet.", "INFO")

    # ================= ACCOUNT MODAL =================

    def _open_account_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("DISCORD ACCOUNT WÄHLEN")
        modal.geometry("520x460")
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
