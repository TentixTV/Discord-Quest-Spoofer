"""
DQS - Discord Quest Spoofer (Gothic Dark AAA Edition)
Official Release by Sandro (T3X / TNTIX)
Pixel-perfect Discord Dark Aesthetic, Real Animated Avatar & Banner GIFs,
HD Official Cover Tiles, Custom Discord Nav-Bar, Auto-Preset Simulation, and 100% Reliable Quest Synchronization.
"""

import os
import sys
import io
import time
import tempfile
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
COLOR_BG_SIDEBAR = "#0e0f17"       # Graphite Surface
COLOR_CARD_BG = "#11121c"          # Dark Slate Container
COLOR_CARD_BG_HOVER = "#171827"    # Card Hover BG
COLOR_CARD_BORDER = "#1f2233"      # Tech Border
COLOR_CARD_BORDER_HOVER = "#5865F2" # Neon Blurple Highlight
COLOR_WHITE = "#ffffff"            # Pure White
COLOR_TEXT_PRIMARY = "#f2f3f5"     # Crisp Light Gray
COLOR_TEXT_MUTED = "#8e92a4"       # Soft Ash Gray

# Glowing Action Colors
COLOR_NEON_BLURPLE = "#5865F2"     # Blurple Primary
COLOR_NEON_BLURPLE_HOVER = "#4752C4"
COLOR_EMERALD = "#23A55A"          # Emerald Green
COLOR_EMERALD_HOVER = "#1B8246"
COLOR_CRIMSON = "#F23F43"          # Crimson Red
COLOR_GOLD = "#FEE75C"             # Gold/Amber
COLOR_GOLD_HOVER = "#E0C836"
COLOR_INDIGO = "#6366F1"           # Indigo
COLOR_INDIGO_HOVER = "#4F46E5"
COLOR_DARK_BTN = "#181926"         # Dark Button Surface
COLOR_DARK_BTN_HOVER = "#24263a"


class AutoQuestApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DQS // Discord Quest Spoofer")
        self.geometry("1240x860")
        self.minsize(1100, 750)
        self.configure(fg_color=COLOR_BG_DARK)

        # Apply Window Titlebar Icon
        self._set_window_icon()

        # State Variables
        self.accounts = []
        self.current_user = None
        self.cached_quests = []
        self.quest_cards = {}
        self.quest_tiles = {}
        self.current_tab = "quests"

        # Core Backend Instances
        self.api = None
        self.simulator = GameSimulator()
        self.farmer = None
        self.auto_farm_running = False

        # Profile Drawer Visibility
        self.drawer_visible = False

        # Asset Caches
        self.badge_images = {}
        self.gear_photos = []
        self.gear_hover_photos = []
        self.gear_frame_index = 0
        self.is_gear_hovered = False

        self.avatar_frames = []
        self.banner_frames = []
        self.avatar_frame_index = 0
        self.banner_frame_index = 0

        # Load Visual Assets
        self._load_badge_assets()
        self._load_gear_assets()
        self._load_profile_gif_assets()

        # Build UI Structure
        self._build_header()
        self._build_nav_bar()
        self._build_main_layout()
        self._build_profile_drawer()

        # Start Continuous Animation Loops
        self._animate_gear()
        self._animate_profile_gifs()

        # Handle Clean Window Teardown
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Initial Auto-Discovery
        self.after(100, self._initial_load)

    # ================= ASSET & ICON MANAGEMENT =================

    def _set_window_icon(self):
        """Applies the cracked Discord DQS icon to the Windows titlebar and taskbar."""
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "..", "DQS.png")
            if not os.path.exists(icon_path):
                icon_path = os.path.join(os.getcwd(), "DQS.png")
            if not os.path.exists(icon_path):
                icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "app_icon.png")
            if not os.path.exists(icon_path):
                icon_path = os.path.join(os.getcwd(), "assets", "app_icon.png")

            if os.path.exists(icon_path):
                # Dynamically generate multi-resolution ICO in system temp directory for Windows Titlebar
                temp_ico = os.path.join(tempfile.gettempdir(), "dqs_runtime_icon.ico")
                im = Image.open(icon_path)
                im.save(temp_ico, format='ICO', sizes=[(16,16), (24,24), (32,32), (48,48), (64,64), (128,128)])
                self.iconbitmap(temp_ico)

                # Set native Tkinter iconphoto
                self._app_icon_photo = ImageTk.PhotoImage(im.resize((32, 32), Image.Resampling.LANCZOS))
                self.iconphoto(True, self._app_icon_photo)
        except Exception as e:
            print(f"Notice: Icon load error: {e}")

    def _load_badge_assets(self):
        """Loads official Discord badge PNGs."""
        base_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "badges")
        if not os.path.exists(base_dir):
            base_dir = os.path.join(os.getcwd(), "assets", "badges")

        badge_files = {
            'nitro': 'nitro.png',
            'bravery': 'bravery.png',
            'booster': 'booster.png',
            'legacy': 'legacy.png',
            'quest': 'quest.png',
            'orbs': 'orbs.png'
        }

        for name, fname in badge_files.items():
            p = os.path.join(base_dir, fname)
            if os.path.exists(p):
                try:
                    im = Image.open(p).convert("RGBA").resize((22, 22), Image.Resampling.LANCZOS)
                    self.badge_images[name] = ImageTk.PhotoImage(im)
                except Exception:
                    pass

    def _load_gear_assets(self):
        """Pre-renders vector gear frames in memory for smooth window dragging."""
        gear_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "gear")
        if not os.path.exists(gear_dir):
            gear_dir = os.path.join(os.getcwd(), "assets", "gear")

        if os.path.exists(gear_dir):
            for i in range(16):
                fp = os.path.join(gear_dir, f"frame_{i}.png")
                if os.path.exists(fp):
                    try:
                        im = Image.open(fp).convert("RGBA").resize((20, 20), Image.Resampling.LANCZOS)
                        self.gear_photos.append(ImageTk.PhotoImage(im))
                    except Exception:
                        pass

                fp_h = os.path.join(gear_dir, f"hover_frame_{i}.png")
                if os.path.exists(fp_h):
                    try:
                        im_h = Image.open(fp_h).convert("RGBA").resize((20, 20), Image.Resampling.LANCZOS)
                        self.gear_hover_photos.append(ImageTk.PhotoImage(im_h))
                    except Exception:
                        pass

    def _load_profile_gif_assets(self):
        """Decodes animated GIF frames using canvas compositing to eliminate all noise artifacts."""
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        if not os.path.exists(assets_dir):
            assets_dir = os.path.join(os.getcwd(), "assets")

        # 1. Decode Banner GIF cleanly
        banner_path = os.path.join(assets_dir, "tentix_banner.gif")
        if os.path.exists(banner_path):
            try:
                im = Image.open(banner_path)
                last_frame = Image.new("RGBA", im.size)
                for frame in ImageSequence.Iterator(im):
                    curr = frame.convert("RGBA")
                    canvas = last_frame.copy()
                    canvas.paste(curr, (0, 0), curr)
                    resized = canvas.resize((340, 125), Image.Resampling.LANCZOS)
                    self.banner_frames.append(ImageTk.PhotoImage(resized))
                    last_frame = canvas
            except Exception as e:
                print(f"Notice: Banner load error: {e}")

        # 2. Decode Avatar GIF with Anti-Aliased Circular Mask & 3px Border
        avatar_path = os.path.join(assets_dir, "tentix_avatar.gif")
        if os.path.exists(avatar_path):
            try:
                im = Image.open(avatar_path)
                size = 80
                mask_size = (size * 4, size * 4)
                mask = Image.new('L', mask_size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse([(0, 0), (mask_size[0] - 1, mask_size[1] - 1)], fill=255)
                mask = mask.resize((size, size), Image.Resampling.LANCZOS)

                last_frame = Image.new("RGBA", im.size)
                for frame in ImageSequence.Iterator(im):
                    curr = frame.convert("RGBA")
                    canvas = last_frame.copy()
                    canvas.paste(curr, (0, 0), curr)
                    sq = canvas.resize((size, size), Image.Resampling.LANCZOS)

                    circ = Image.new('RGBA', (size + 6, size + 6), (0, 0, 0, 0))
                    draw_circ = ImageDraw.Draw(circ)
                    draw_circ.ellipse([(0, 0), (size + 5, size + 5)], fill=COLOR_CARD_BG)
                    circ.paste(sq, (3, 3), mask=mask)

                    self.avatar_frames.append(ImageTk.PhotoImage(circ))
                    last_frame = canvas
            except Exception as e:
                print(f"Notice: Avatar load error: {e}")

    # ================= ANIMATION LOOPS =================

    def _animate_gear(self):
        """Rotates the vector settings gear."""
        if self.gear_photos:
            photos = self.gear_hover_photos if (self.is_gear_hovered and self.gear_hover_photos) else self.gear_photos
            self.gear_frame_index = (self.gear_frame_index + 1) % len(photos)
            if hasattr(self, 'lbl_gear_tk') and self.lbl_gear_tk.winfo_exists():
                self.lbl_gear_tk.configure(image=photos[self.gear_frame_index])
        self.after(55, self._animate_gear)

    def _animate_profile_gifs(self):
        """Drives the avatar & banner GIF playback inside the profile drawer."""
        if self.drawer_visible:
            if self.banner_frames and hasattr(self, 'lbl_drawer_banner_tk') and self.lbl_drawer_banner_tk.winfo_exists():
                self.banner_frame_index = (self.banner_frame_index + 1) % len(self.banner_frames)
                self.lbl_drawer_banner_tk.configure(image=self.banner_frames[self.banner_frame_index])

            if self.avatar_frames and hasattr(self, 'lbl_drawer_avatar_tk') and self.lbl_drawer_avatar_tk.winfo_exists():
                self.avatar_frame_index = (self.avatar_frame_index + 1) % len(self.avatar_frames)
                self.lbl_drawer_avatar_tk.configure(image=self.avatar_frames[self.avatar_frame_index])

        self.after(50, self._animate_profile_gifs)

    def _on_window_close(self):
        """Gracefully shuts down simulation and destroys the window."""
        try:
            if self.simulator and self.simulator.is_running():
                self.simulator.stop_simulation()
        except Exception:
            pass
        self.destroy()

    # ================= UI LAYOUT: HEADER =================

    def _build_header(self):
        """Top Header: Clean Transparent App Logo, Title, Admin Glow Pill, and User Pill."""
        self.header_frame = ctk.CTkFrame(
            self, fg_color=COLOR_BG_SIDEBAR, height=76, corner_radius=0,
            border_width=1, border_color=COLOR_CARD_BORDER
        )
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        # Left Branding Box
        brand_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        brand_box.pack(side="left", padx=20, pady=10)

        # In-App Cracked Discord PNG Logo
        icon_path = os.path.join(os.path.dirname(__file__), "..", "DQS.png")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.getcwd(), "DQS.png")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "app_icon.png")

        if os.path.exists(icon_path):
            try:
                raw_logo = Image.open(icon_path).convert("RGBA")
                self.header_logo_img = ctk.CTkImage(light_image=raw_logo, dark_image=raw_logo, size=(42, 42))
                lbl_icon = ctk.CTkLabel(brand_box, text="", image=self.header_logo_img)
                lbl_icon.pack(side="left", padx=(0, 12))
            except Exception:
                pass

        title_sub = ctk.CTkFrame(brand_box, fg_color="transparent")
        title_sub.pack(side="left")

        # Row 1: DQS Title + Admin Pill (Side by Side)
        top_row = ctk.CTkFrame(title_sub, fg_color="transparent")
        top_row.pack(anchor="w", pady=(0, 2))

        app_title = ctk.CTkLabel(
            top_row, text="DQS",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLOR_WHITE
        )
        app_title.pack(side="left", padx=(0, 10))

        admin_pill = ctk.CTkFrame(
            top_row, fg_color="#0c2314", border_width=1, border_color=COLOR_EMERALD, corner_radius=12
        )
        admin_pill.pack(side="left")

        ctk.CTkLabel(
            admin_pill, text="● ADMIN AKTIV",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=COLOR_EMERALD
        ).pack(padx=8, pady=2)

        # Row 2: Subtitle (NO 'Ultimate Edition')
        sub_badge = ctk.CTkLabel(
            title_sub, text="DISCORD QUEST SPOOFER",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        )
        sub_badge.pack(anchor="w")

        # Right User Profile Pill (Clickable to toggle profile drawer)
        self.account_bar = ctk.CTkFrame(
            self.header_frame, fg_color=COLOR_CARD_BG, corner_radius=20,
            border_width=1, border_color=COLOR_CARD_BORDER, cursor="hand2"
        )
        self.account_bar.pack(side="right", padx=20, pady=14)
        self.account_bar.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        # Mini Avatar preview
        mini_av_p = os.path.join(os.path.dirname(__file__), "..", "assets", "tentix_avatar.png")
        if not os.path.exists(mini_av_p):
            mini_av_p = os.path.join(os.getcwd(), "assets", "tentix_avatar.png")

        if os.path.exists(mini_av_p):
            try:
                raw_av = Image.open(mini_av_p).convert("RGBA").resize((30, 30), Image.Resampling.LANCZOS)
                m = Image.new('L', (30, 30), 0)
                ImageDraw.Draw(m).ellipse([(0, 0), (29, 29)], fill=255)
                circ_av = Image.new('RGBA', (30, 30), (0, 0, 0, 0))
                circ_av.paste(raw_av, (0, 0), mask=m)
                self.mini_av_img = ctk.CTkImage(light_image=circ_av, dark_image=circ_av, size=(30, 30))
                self.avatar_label = ctk.CTkLabel(self.account_bar, text="", image=self.mini_av_img)
            except Exception:
                self.avatar_label = ctk.CTkLabel(self.account_bar, text="👤", font=ctk.CTkFont(size=16))
        else:
            self.avatar_label = ctk.CTkLabel(self.account_bar, text="👤", font=ctk.CTkFont(size=16))

        self.avatar_label.pack(side="left", padx=(10, 8), pady=4)
        self.avatar_label.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        user_info = ctk.CTkFrame(self.account_bar, fg_color="transparent")
        user_info.pack(side="left", padx=(0, 10), pady=4)
        user_info.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        self.lbl_username = ctk.CTkLabel(
            user_info, text="TΞП†1Ж ツ",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
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

        # Vector Gear Icon inside user pill
        gear_container = tk.Frame(self.account_bar, bg=COLOR_CARD_BG)
        gear_container.pack(side="left", padx=(4, 12))
        gear_container.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        initial_gear = self.gear_photos[0] if self.gear_photos else None
        self.lbl_gear_tk = tk.Label(gear_container, image=initial_gear, bg=COLOR_CARD_BG, bd=0, cursor="hand2")
        self.lbl_gear_tk.pack()
        self.lbl_gear_tk.bind("<Button-1>", lambda e: self._toggle_profile_drawer())

        # Smooth Hover on Account Pill
        def _on_acc_enter(e):
            self.is_gear_hovered = True
            if self.account_bar.winfo_exists():
                self.account_bar.configure(border_color=COLOR_NEON_BLURPLE, fg_color="#18192a")
                gear_container.configure(bg="#18192a")
                self.lbl_gear_tk.configure(bg="#18192a")

        def _on_acc_leave(e):
            self.is_gear_hovered = False
            if self.account_bar.winfo_exists():
                self.account_bar.configure(border_color=COLOR_CARD_BORDER, fg_color=COLOR_CARD_BG)
                gear_container.configure(bg=COLOR_CARD_BG)
                self.lbl_gear_tk.configure(bg=COLOR_CARD_BG)

        self.account_bar.bind("<Enter>", _on_acc_enter)
        self.account_bar.bind("<Leave>", _on_acc_leave)

    # ================= UI LAYOUT: SLEEK DISCORD NAV BAR =================

    def _build_nav_bar(self):
        """Builds a custom Discord-styled horizontal navigation bar."""
        self.nav_frame = ctk.CTkFrame(
            self, fg_color="#090a10", height=48, corner_radius=0,
            border_width=1, border_color="#1a1b26"
        )
        self.nav_frame.pack(fill="x", side="top")
        self.nav_frame.pack_propagate(False)

        nav_inner = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        nav_inner.pack(side="left", padx=15, pady=6)

        self.nav_buttons = {}
        tabs = [
            ("quests", "⚡ QUESTS (6)"),
            ("videos", "🎬 VIDEOS & TRAILER"),
            ("simulator", "🎮 SPIELE-SIMULATOR"),
            ("console", "💻 DISCORD-CONSOLE"),
            ("logs", "📜 LIVE-LOGS")
        ]

        for tab_id, tab_label in tabs:
            btn = ctk.CTkButton(
                nav_inner, text=tab_label, height=34,
                fg_color=COLOR_NEON_BLURPLE if tab_id == "quests" else "transparent",
                hover_color="#1e2032",
                text_color=COLOR_WHITE if tab_id == "quests" else COLOR_TEXT_MUTED,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                corner_radius=8,
                command=lambda t=tab_id: self._switch_tab(t)
            )
            btn.pack(side="left", padx=4)
            self.nav_buttons[tab_id] = btn

    def _switch_tab(self, tab_id: str):
        """Switches the active tab frame and updates nav bar button highlights."""
        self.current_tab = tab_id
        for tid, btn in self.nav_buttons.items():
            if tid == tab_id:
                btn.configure(fg_color=COLOR_NEON_BLURPLE, text_color=COLOR_WHITE)
            else:
                btn.configure(fg_color="transparent", text_color=COLOR_TEXT_MUTED)

        # Show selected tab container
        for tid, frame in self.tab_pages.items():
            if tid == tab_id:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

    # ================= UI LAYOUT: MAIN CONTENT & PAGES =================

    def _build_main_layout(self):
        """Container holding the active page and the slide-out Discord profile drawer."""
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True, padx=14, pady=(6, 12))

        # Main Page Viewport
        self.page_viewport = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        self.page_viewport.pack(side="left", fill="both", expand=True)

        self.tab_pages = {}
        for tid in ["quests", "videos", "simulator", "console", "logs"]:
            page = ctk.CTkFrame(self.page_viewport, fg_color="transparent")
            self.tab_pages[tid] = page

        # Setup individual pages
        self._setup_quests_tab()
        self._setup_videos_tab()
        self._setup_simulator_tab()
        self._setup_console_tab()
        self._setup_logs_tab()

        # Show initial Quests page
        self.tab_pages["quests"].pack(fill="both", expand=True)

    # ================= DISCORD PROFILE DRAWER =================

    def _build_profile_drawer(self):
        """Authentic Discord User Profile popout matching real Discord UI."""
        self.drawer_frame = ctk.CTkFrame(
            self.body_frame, width=360, fg_color=COLOR_BG_SIDEBAR, corner_radius=10,
            border_width=1, border_color=COLOR_CARD_BORDER
        )

        self.drawer_scroll = ctk.CTkScrollableFrame(self.drawer_frame, fg_color="transparent")
        self.drawer_scroll.pack(fill="both", expand=True, padx=4, pady=6)

        card_wrapper = ctk.CTkFrame(self.drawer_scroll, fg_color=COLOR_CARD_BG, corner_radius=10, border_width=1, border_color="#202336")
        card_wrapper.pack(fill="x", padx=4, pady=(0, 10))

        # 1. Top Banner & Overlapping Avatar Area (160px height)
        header_canvas_frame = tk.Frame(card_wrapper, bg=COLOR_CARD_BG, width=340, height=160)
        header_canvas_frame.pack(fill="x")
        header_canvas_frame.pack_propagate(False)

        # Banner at top (125px)
        init_banner = self.banner_frames[0] if self.banner_frames else None
        self.lbl_drawer_banner_tk = tk.Label(header_canvas_frame, image=init_banner, bg="#1a1c29", bd=0)
        self.lbl_drawer_banner_tk.place(x=0, y=0, width=340, height=125)

        # Overlapping Circular Avatar placed at (18, 72)
        init_av = self.avatar_frames[0] if self.avatar_frames else None
        self.lbl_drawer_avatar_tk = tk.Label(header_canvas_frame, image=init_av, bg=COLOR_CARD_BG, bd=0)
        self.lbl_drawer_avatar_tk.place(x=18, y=72)

        # DND Status Badge (Red circle with white minus bar) at (74, 130)
        dnd_badge = tk.Frame(header_canvas_frame, bg="#f23f43", width=18, height=18, highlightbackground=COLOR_CARD_BG, highlightthickness=3)
        dnd_badge.place(x=74, y=130)
        minus_bar = tk.Frame(dnd_badge, bg="#ffffff", height=3, width=8)
        minus_bar.place(relx=0.5, rely=0.5, anchor="center")

        # 2. Content below header
        content_box = ctk.CTkFrame(card_wrapper, fg_color="transparent")
        content_box.pack(fill="x", padx=12, pady=(10, 12))

        # Status Speech Bubble (Fully visible, wrapping, zero cutoff!)
        bubble_box = ctk.CTkFrame(content_box, fg_color="#181926", border_width=1, border_color="#2c2e44", corner_radius=8)
        bubble_box.pack(fill="x", pady=(0, 10))

        lbl_b_text = ctk.CTkLabel(
            bubble_box, text="🩸 BEHIND EVERY KISS IS A CLAW THAT CAN BITE",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=COLOR_WHITE, justify="left", wraplength=280
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

        # 5. Activity Box
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
            activity_box, text="⏱ Zeit: 04:12 Min.",
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

        # Official GitHub Link
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
            info_box, text="DQS by Sandro (T3X / TNTIX)\n100% sauber wenn von GitHub geladen!\nWer es woanders her hat ist selber schuld.",
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
        self.after(2000, lambda: self.btn_copy_id.configure(text="🆔 NUTZER-ID KOPIEREN"))

    # ================= TAB 1: QUESTS =================

    def _setup_quests_tab(self):
        page = self.tab_pages["quests"]

        # Action Toolbar
        top_bar = ctk.CTkFrame(page, fg_color=COLOR_CARD_BG, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
        top_bar.pack(fill="x", padx=4, pady=(4, 8))

        ctk.CTkLabel(
            top_bar, text="⚡ AKTIVE QUESTS & BELOHNUNGEN",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(side="left", padx=15, pady=10)

        ctk.CTkButton(
            top_bar, text="🔄 AKTUALISIEREN", width=130, height=32,
            fg_color=COLOR_DARK_BTN, hover_color=COLOR_DARK_BTN_HOVER,
            border_width=1, border_color=COLOR_CARD_BORDER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            corner_radius=6, command=self.refresh_quests
        ).pack(side="right", padx=10, pady=8)

        ctk.CTkButton(
            top_bar, text="⚡ ALLE ANNEHMEN", width=140, height=32,
            fg_color=COLOR_NEON_BLURPLE, hover_color=COLOR_NEON_BLURPLE_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            corner_radius=6, command=self.enroll_all_quests
        ).pack(side="right", padx=(0, 6), pady=8)

        self.btn_autofarm = ctk.CTkButton(
            top_bar, text="🚀 AUTO-FARM", width=130, height=32,
            fg_color=COLOR_EMERALD, hover_color=COLOR_EMERALD_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            corner_radius=6, command=self.toggle_auto_farm
        )
        self.btn_autofarm.pack(side="right", padx=(0, 6), pady=8)

        self.quests_scroll = ctk.CTkScrollableFrame(
            page, fg_color="transparent",
            label_text="VERFÜGBARE QUESTS",
            label_font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            label_text_color=COLOR_TEXT_MUTED
        )
        self.quests_scroll.pack(fill="both", expand=True, padx=2, pady=2)

    def _render_quests(self, quests):
        for widget in self.quests_scroll.winfo_children():
            widget.destroy()

        self.quest_cards.clear()

        # Update Nav Bar Counter
        if "quests" in self.nav_buttons:
            self.nav_buttons["quests"].configure(text=f"⚡ QUESTS ({len(quests)})")

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

    def _create_quest_card(self, q: dict):
        qid = q.get("id")
        game_title = q.get("game_title", "Unbekanntes Spiel")
        quest_name = q.get("quest_name", "Quest")
        publisher = q.get("game_publisher", "")
        task_type = q.get("task_type", "PLAY_ON_DESKTOP")
        target_seconds = q.get("target_seconds", 900)
        current_seconds = q.get("current_seconds", 0)
        progress_percent = q.get("progress_percent", 0.0)
        enrolled = q.get("enrolled", False)
        completed = q.get("completed", False)
        claimed = q.get("claimed", False)
        rewards_text = q.get("rewards_text", "Belohnung")
        orb_count = q.get("orb_count", 0)
        app_id = q.get("app_id", "")
        video_url = q.get("video_url")

        card = ctk.CTkFrame(
            self.quests_scroll, fg_color=COLOR_CARD_BG,
            border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=10
        )
        card.pack(fill="x", padx=6, pady=6)

        # Smooth Hover on Quest Card
        def _on_card_enter(e, c=card):
            if c.winfo_exists():
                c.configure(border_color=COLOR_NEON_BLURPLE, fg_color=COLOR_CARD_BG_HOVER)
        def _on_card_leave(e, c=card):
            if c.winfo_exists():
                c.configure(border_color=COLOR_CARD_BORDER, fg_color=COLOR_CARD_BG)

        card.bind("<Enter>", _on_card_enter)
        card.bind("<Leave>", _on_card_leave)

        # Left: HD Rounded Cover Tile (84x84)
        tile_img = self._get_quest_tile(qid)
        if tile_img:
            lbl_tile = tk.Label(card, image=tile_img, bg=COLOR_CARD_BG, bd=0)
            lbl_tile.pack(side="left", padx=14, pady=12)
        else:
            ctk.CTkLabel(card, text="🎮", font=ctk.CTkFont(size=32)).pack(side="left", padx=18, pady=12)

        # Center: Detailed Quest Info
        center_box = ctk.CTkFrame(card, fg_color="transparent")
        center_box.pack(side="left", fill="both", expand=True, pady=10)

        # Row 1: Game Title + Badges
        r1 = ctk.CTkFrame(center_box, fg_color="transparent")
        r1.pack(fill="x", anchor="w", pady=(0, 2))

        ctk.CTkLabel(
            r1, text=game_title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(side="left", padx=(0, 10))

        # Task Pill
        task_label = "🎬 Video-Quest" if "VIDEO" in task_type else f"🎮 {target_seconds // 60} Min. Spielzeit"
        ctk.CTkLabel(
            r1, text=task_label,
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color="#93c5fd", fg_color="#172554", corner_radius=6, padx=8, pady=2
        ).pack(side="left", padx=(0, 6))

        # Orbs Reward Pill
        if orb_count > 0:
            ctk.CTkLabel(
                r1, text=f"🔮 {orb_count} ORBS",
                font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
                text_color=COLOR_GOLD, fg_color="#362d08", corner_radius=6, padx=8, pady=2
            ).pack(side="left")

        # Row 2: Quest Name
        ctk.CTkLabel(
            center_box, text=quest_name,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#9ca3af"
        ).pack(anchor="w", pady=(0, 6))

        # Row 3: Progress Bar & Detailed Min Counter
        prog_row = ctk.CTkFrame(center_box, fg_color="transparent")
        prog_row.pack(fill="x", anchor="w")

        p_bar = ctk.CTkProgressBar(prog_row, width=280, height=7, corner_radius=4)
        p_bar.set(progress_percent / 100.0)
        p_bar.pack(side="left", padx=(0, 12))

        cur_min = current_seconds // 60
        tgt_min = target_seconds // 60
        status_txt = f"{cur_min}/{tgt_min} MIN. ({int(progress_percent)}%)"
        if completed or claimed:
            status_txt += " - ERFÜLLT!"
            p_bar.configure(progress_color=COLOR_EMERALD)
        else:
            p_bar.configure(progress_color=COLOR_NEON_BLURPLE)

        lbl_progress_txt = ctk.CTkLabel(
            prog_row, text=status_txt,
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            text_color=COLOR_EMERALD if completed else COLOR_TEXT_MUTED
        )
        lbl_progress_txt.pack(side="left")

        # Right: Action Buttons
        btn_box = ctk.CTkFrame(card, fg_color="transparent")
        btn_box.pack(side="right", padx=16, pady=12)

        if claimed:
            btn_claimed = ctk.CTkButton(
                btn_box, text="✓ EINGELÖST", width=130, height=32,
                fg_color="#10281b", text_color=COLOR_EMERALD,
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                corner_radius=6, state="disabled"
            )
            btn_claimed.pack(side="right")
        elif completed:
            btn_claim = ctk.CTkButton(
                btn_box, text="🎁 BELOHNUNG", width=140, height=32,
                fg_color=COLOR_EMERALD, hover_color=COLOR_EMERALD_HOVER,
                text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                corner_radius=6
            )
            btn_claim.configure(command=lambda qid=qid, b=btn_claim: self._claim_quest(qid, b))
            btn_claim.pack(side="right")
        else:
            # 1. Simulate Button (Emerald, auto-presets and starts)
            btn_sim = ctk.CTkButton(
                btn_box, text="▶ SIMULIEREN", width=130, height=32,
                fg_color=COLOR_EMERALD, hover_color=COLOR_EMERALD_HOVER,
                text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                corner_radius=6, command=lambda aid=app_id, gt=game_title: self._sim_single_quest(aid, gt)
            )
            btn_sim.pack(side="right", padx=4)

            # 2. Video Button if applicable
            if video_url:
                btn_vid = ctk.CTkButton(
                    btn_box, text="🎬 VIDEO", width=100, height=32,
                    fg_color=COLOR_INDIGO, hover_color=COLOR_INDIGO_HOVER,
                    text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    corner_radius=6, command=lambda u=video_url: webbrowser.open(u)
                )
                btn_vid.pack(side="right", padx=4)

            # 3. Enroll if not enrolled
            if not enrolled:
                btn_enroll = ctk.CTkButton(
                    btn_box, text="ANNEHMEN", width=110, height=32,
                    fg_color=COLOR_NEON_BLURPLE, hover_color=COLOR_NEON_BLURPLE_HOVER,
                    text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    corner_radius=6
                )
                btn_enroll.configure(command=lambda qid=qid, b=btn_enroll: self._enroll_quest(qid, b))
                btn_enroll.pack(side="right", padx=4)

        self.quest_cards[qid] = {
            "p_bar": p_bar,
            "lbl_txt": lbl_progress_txt,
            "card_frame": card
        }

    def _get_quest_tile(self, qid: str):
        """Returns PhotoImage for official rounded quest cover tile."""
        if qid in self.quest_tiles:
            return self.quest_tiles[qid]

        tiles_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "quests", "tiles")
        if not os.path.exists(tiles_dir):
            tiles_dir = os.path.join(os.getcwd(), "assets", "quests", "tiles")

        tile_path = os.path.join(tiles_dir, f"{qid}.png")
        if os.path.exists(tile_path):
            try:
                im = Image.open(tile_path).convert("RGBA")
                tk_im = ImageTk.PhotoImage(im)
                self.quest_tiles[qid] = tk_im
                return tk_im
            except Exception:
                pass
        return None

    # ================= TAB 2: VIDEOS & TRAILER =================

    def _setup_videos_tab(self):
        page = self.tab_pages["videos"]

        top_bar = ctk.CTkFrame(page, fg_color=COLOR_CARD_BG, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
        top_bar.pack(fill="x", padx=4, pady=(4, 8))

        ctk.CTkLabel(
            top_bar, text="🎬 ALLE QUEST-VIDEOS & OFFIZIELLE TRAILER (720P HD)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(side="left", padx=15, pady=10)

        self.videos_scroll = ctk.CTkScrollableFrame(
            page, fg_color="transparent",
            label_text="VERFÜGBARE QUEST-VIDEOS",
            label_font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            label_text_color=COLOR_TEXT_MUTED
        )
        self.videos_scroll.pack(fill="both", expand=True, padx=2, pady=2)

    def _render_videos_tab(self, quests):
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
            card = ctk.CTkFrame(self.videos_scroll, fg_color=COLOR_CARD_BG, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=10)
            card.pack(fill="x", padx=6, pady=6)

            def _on_v_enter(e, c=card):
                if c.winfo_exists():
                    c.configure(border_color=COLOR_NEON_BLURPLE, fg_color=COLOR_CARD_BG_HOVER)
            def _on_v_leave(e, c=card):
                if c.winfo_exists():
                    c.configure(border_color=COLOR_CARD_BORDER, fg_color=COLOR_CARD_BG)

            card.bind("<Enter>", _on_v_enter)
            card.bind("<Leave>", _on_v_leave)

            # Left: Cover Tile
            tile_img = self._get_quest_tile(qid)
            if tile_img:
                tk.Label(card, image=tile_img, bg=COLOR_CARD_BG, bd=0).pack(side="left", padx=14, pady=12)
            else:
                ctk.CTkLabel(card, text="🎬", font=ctk.CTkFont(size=30)).pack(side="left", padx=18, pady=12)

            info_box = ctk.CTkFrame(card, fg_color="transparent")
            info_box.pack(side="left", fill="both", expand=True, pady=10)

            ctk.CTkLabel(
                info_box, text=f"{game_title} - {qname}",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLOR_WHITE
            ).pack(anchor="w")

            if vid_url:
                sub_txt = f"Publisher: {publisher or 'Discord'}  |  Format: 720p HD MP4 (Offizieller Stream)  |  Dauer: ~{target_sec} Sek."
            else:
                sub_txt = f"Publisher: {publisher or 'Discord'}  |  Format: Offizieller HD Trailer & Gameplay  |  Dauer: ~15 Min."

            ctk.CTkLabel(
                info_box, text=sub_txt,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=COLOR_TEXT_MUTED
            ).pack(anchor="w")

            btn_box = ctk.CTkFrame(card, fg_color="transparent")
            btn_box.pack(side="right", padx=16, pady=12)

            if vid_url:
                ctk.CTkButton(
                    btn_box, text="▶ 720P HD VIDEO ABSPIELEN", width=180, height=32,
                    fg_color=COLOR_INDIGO, hover_color=COLOR_INDIGO_HOVER,
                    text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    corner_radius=6, command=lambda u=vid_url: webbrowser.open(u)
                ).pack(side="left", padx=5)

                ctk.CTkButton(
                    btn_box, text="⚡ EXPRESS-ABSCHLUSS", width=160, height=32,
                    fg_color=COLOR_GOLD, hover_color=COLOR_GOLD_HOVER,
                    text_color="#000000", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    corner_radius=6, command=lambda qid=qid, t=target_sec: self._fast_video_quest(qid, t, None)
                ).pack(side="left", padx=5)
            else:
                yt_query = f"{game_title} official trailer".replace(' ', '+')
                trailer_url = f"https://www.youtube.com/results?search_query={yt_query}"
                ctk.CTkButton(
                    btn_box, text="▶ OFFIZIELLEN TRAILER ANSEHEN", width=190, height=32,
                    fg_color="#27273a", hover_color="#3b3b55",
                    border_width=1, border_color="#4f46e5",
                    text_color="#a5b4fc", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    corner_radius=6, command=lambda u=trailer_url: webbrowser.open(u)
                ).pack(side="left", padx=5)

                ctk.CTkButton(
                    btn_box, text="🎮 IM SIMULATOR STARTEN", width=170, height=32,
                    fg_color=COLOR_EMERALD, hover_color=COLOR_EMERALD_HOVER,
                    text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    corner_radius=6, command=lambda aid=app_id, gt=game_title: self._sim_single_quest(aid, gt)
                ).pack(side="left", padx=5)

    # ================= TAB 3: SIMULATOR (WITH AUTO-PRESET) =================

    def _setup_simulator_tab(self):
        page = self.tab_pages["simulator"]

        top_bar = ctk.CTkFrame(page, fg_color=COLOR_CARD_BG, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
        top_bar.pack(fill="x", padx=4, pady=(4, 8))

        ctk.CTkLabel(
            top_bar, text="🎮 NATIVE SPIELE-SIMULATION & DISCORD RPC INJEKTION",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(side="left", padx=15, pady=10)

        self.lbl_sim_indicator = ctk.CTkLabel(
            top_bar, text="● SIMULATOR BEREIT",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        )
        self.lbl_sim_indicator.pack(side="right", padx=15, pady=10)

        sim_card = ctk.CTkFrame(page, fg_color=COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=COLOR_CARD_BORDER)
        sim_card.pack(fill="both", expand=True, padx=4, pady=4)

        form_frame = ctk.CTkFrame(sim_card, fg_color="transparent")
        form_frame.pack(padx=30, pady=20, fill="both", expand=True)

        ctk.CTkLabel(
            form_frame, text="SPIELVORLAGE AUSWÄHLEN:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(0, 4))

        preset_names = [f"{info['name']} ({info['category']})" for _, info in QUEST_GAMES_DATABASE.items()]
        self.preset_menu = ctk.CTkOptionMenu(
            form_frame, values=preset_names, height=36,
            fg_color="#181926", button_color=COLOR_NEON_BLURPLE, button_hover_color=COLOR_NEON_BLURPLE_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=12),
            command=self._on_preset_selected
        )
        self.preset_menu.pack(fill="x", pady=(0, 16))

        # Title Entry
        ctk.CTkLabel(
            form_frame, text="SPIELNAME / FENSTERTITEL:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(0, 4))

        self.entry_sim_title = ctk.CTkEntry(
            form_frame, height=36, fg_color="#181926", border_color=COLOR_CARD_BORDER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.entry_sim_title.pack(fill="x", pady=(0, 16))

        # Exe Entry
        ctk.CTkLabel(
            form_frame, text="EXECUTABLE (DATEINAME):",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(0, 4))

        self.entry_sim_exe = ctk.CTkEntry(
            form_frame, height=36, fg_color="#181926", border_color=COLOR_CARD_BORDER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.entry_sim_exe.pack(fill="x", pady=(0, 16))

        # App-ID Entry
        ctk.CTkLabel(
            form_frame, text="DISCORD APPLICATION ID:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(0, 4))

        self.entry_sim_appid = ctk.CTkEntry(
            form_frame, height=36, fg_color="#181926", border_color=COLOR_CARD_BORDER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.entry_sim_appid.pack(fill="x", pady=(0, 20))

        # Button Row
        btn_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 10))

        self.btn_start_sim = ctk.CTkButton(
            btn_row, text="▶ SIMULATION STARTEN", height=40,
            fg_color=COLOR_EMERALD, hover_color=COLOR_EMERALD_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            corner_radius=6, command=self.start_manual_simulation
        )
        self.btn_start_sim.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.btn_stop_sim = ctk.CTkButton(
            btn_row, text="■ BEENDEN", height=40,
            fg_color=COLOR_CRIMSON, hover_color="#c9282c",
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            corner_radius=6, command=self.stop_manual_simulation
        )
        self.btn_stop_sim.pack(side="right", fill="x", expand=True, padx=(8, 0))

        self.lbl_sim_status = ctk.CTkLabel(
            form_frame, text="Status: Bereit.",
            font=ctk.CTkFont(family="Segoe UI", size=11), text_color=COLOR_TEXT_MUTED
        )
        self.lbl_sim_status.pack(pady=10)

        # Set Helldivers 2 as default
        self._on_preset_selected(preset_names[0])

    def _on_preset_selected(self, choice):
        for k, info in QUEST_GAMES_DATABASE.items():
            if f"{info['name']} ({info['category']})" == choice:
                self.entry_sim_title.delete(0, "end")
                self.entry_sim_title.insert(0, info["title"])
                self.entry_sim_exe.delete(0, "end")
                self.entry_sim_exe.insert(0, info["exe"])
                self.entry_sim_appid.delete(0, "end")
                self.entry_sim_appid.insert(0, str(k))
                break

    # ================= TAB 4: CONSOLE =================

    def _setup_console_tab(self):
        page = self.tab_pages["console"]

        top_bar = ctk.CTkFrame(page, fg_color=COLOR_CARD_BG, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
        top_bar.pack(fill="x", padx=4, pady=(4, 8))

        ctk.CTkLabel(
            top_bar, text="💻 DISCORD ENTWICKLER-KONSOLE (1-KLICK SKRIPT)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(side="left", padx=15, pady=10)

        box = ctk.CTkFrame(page, fg_color=COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=COLOR_CARD_BORDER)
        box.pack(fill="both", expand=True, padx=4, pady=4)

        warn_box = ctk.CTkFrame(box, fg_color="#2b1111", border_width=1, border_color="#f87171", corner_radius=6)
        warn_box.pack(fill="x", padx=20, pady=(16, 10))

        ctk.CTkLabel(
            warn_box, text="⚠️ WARNUNG: Führe NIEMALS fremde Skripte aus, deren Code du nicht kennst!\nDieser Spoofer von Sandro (T3X / TNTIX) ist 100% quelloffen, sicher und loggt keine Daten.",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#fca5a5", justify="center"
        ).pack(padx=10, pady=8)

        self.txt_console = ctk.CTkTextbox(
            box, fg_color="#090a10", text_color="#a5b4fc",
            font=ctk.CTkFont(family="Consolas", size=11), corner_radius=6
        )
        self.txt_console.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        # Fill script
        script_code = generate_discord_console_snippet()
        self.txt_console.insert("1.0", script_code)

        btn_row = ctk.CTkFrame(box, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 16))

        self.btn_copy_script = ctk.CTkButton(
            btn_row, text="📋 1-KLICK SKRIPT IN ZWISCHENABLAGE KOPIEREN", height=38,
            fg_color=COLOR_NEON_BLURPLE, hover_color=COLOR_NEON_BLURPLE_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=6, command=self._copy_console_script
        )
        self.btn_copy_script.pack(fill="x")

    def _copy_console_script(self):
        script_code = self.txt_console.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(script_code)
        self.btn_copy_script.configure(text="✓ IN ZWISCHENABLAGE KOPIERT! Jetzt in Discord Strg+Shift+I -> Console -> Enter")
        self.after(3000, lambda: self.btn_copy_script.configure(text="📋 1-KLICK SKRIPT IN ZWISCHENABLAGE KOPIEREN"))

    # ================= TAB 5: LOGS =================

    def _setup_logs_tab(self):
        page = self.tab_pages["logs"]

        top_bar = ctk.CTkFrame(page, fg_color=COLOR_CARD_BG, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
        top_bar.pack(fill="x", padx=4, pady=(4, 8))

        ctk.CTkLabel(
            top_bar, text="📜 SYSTEM-LOGS & EVENT-MONITOR",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(side="left", padx=15, pady=10)

        ctk.CTkButton(
            top_bar, text="LEEREN", width=80, height=30,
            fg_color=COLOR_DARK_BTN, hover_color=COLOR_DARK_BTN_HOVER,
            text_color=COLOR_TEXT_MUTED, font=ctk.CTkFont(family="Segoe UI", size=10),
            corner_radius=4, command=self.clear_logs
        ).pack(side="right", padx=15, pady=8)

        self.txt_logs = ctk.CTkTextbox(
            page, fg_color="#090a10", text_color="#10b981",
            font=ctk.CTkFont(family="Consolas", size=10), corner_radius=6
        )
        self.txt_logs.pack(fill="both", expand=True, padx=4, pady=4)

    def log(self, message: str, level: str = "INFO"):
        t_str = time.strftime("%H:%M:%S")
        prefix = f"[{t_str}] [{level}] "
        if hasattr(self, 'txt_logs') and self.txt_logs.winfo_exists():
            self.txt_logs.insert("end", f"{prefix}{message}\n")
            self.txt_logs.see("end")

    def clear_logs(self):
        if hasattr(self, 'txt_logs') and self.txt_logs.winfo_exists():
            self.txt_logs.delete("1.0", "end")

    # ================= BACKEND & ACTIONS =================

    def _initial_load(self):
        self.log("Starte automatische Discord-Account-Erkennung...", "INFO")
        self.accounts = find_all_valid_accounts()
        if self.accounts:
            self.log(f"{len(self.accounts)} aktive Discord Accounts gefunden!", "SUCCESS")
            self._set_active_account(self.accounts[0])
        else:
            self.log("Keine aktiven Accounts im lokalen Cache gefunden.", "WARNING")
            self._open_account_modal()

    def _set_active_account(self, acc_info: dict):
        self.current_user = acc_info
        username = acc_info.get("username", "Unbekannt")
        token = acc_info.get("token", "")

        disp_name = acc_info.get("global_name") or username
        self.lbl_username.configure(text=disp_name)

        self.api = DiscordQuestsAPI(token)
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
            try:
                if self.winfo_exists():
                    self.after(0, lambda: self._render_quests(quests))
                    self.after(0, lambda: self._render_videos_tab(quests))
                    self.after(0, lambda: self.log(f"{len(quests)} Quests erfolgreich synchronisiert.", "SUCCESS"))
            except Exception:
                pass
        except Exception as e:
            err_msg = str(e)
            try:
                if self.winfo_exists():
                    self.after(0, lambda m=err_msg: self.log(f"Fehler beim Laden der Quests: {m}", "ERROR"))
            except Exception:
                pass

    def _enroll_quest(self, qid: str, btn):
        if not self.api:
            return
        btn.configure(state="disabled", text="Nimmt an...")
        def _bg():
            ok = self.api.enroll_quest(qid)
            if ok:
                self.after(0, lambda: btn.configure(text="✓ ANGENOMMEN", fg_color="#10281b", text_color=COLOR_EMERALD))
                self.refresh_quests()
            else:
                self.after(0, lambda: btn.configure(state="normal", text="FEHLER"))
        threading.Thread(target=_bg, daemon=True).start()

    def _claim_quest(self, qid: str, btn):
        if not self.api:
            return
        btn.configure(state="disabled", text="Löst ein...")
        def _bg():
            res = self.api.claim_reward(qid)
            if res:
                self.after(0, lambda: btn.configure(text="✓ EINGELÖST", fg_color="#10281b", text_color=COLOR_EMERALD))
                self.refresh_quests()
            else:
                self.after(0, lambda: btn.configure(state="normal", text="FEHLER"))
        threading.Thread(target=_bg, daemon=True).start()

    def _fast_video_quest(self, qid: str, target_sec: int, btn):
        if not self.api:
            return
        if btn:
            btn.configure(state="disabled", text="⚡ EXPRESS...")
        self.log(f"Starte Express-Abschluss für Quest {qid}...", "INFO")
        def _bg():
            ok = self.api.complete_video_quest(qid, target_seconds=target_sec)
            if ok:
                self.log(f"Video-Quest {qid} erfolgreich in 5 Sekunden abgeschlossen!", "SUCCESS")
                self.refresh_quests()
            else:
                self.log(f"Express-Abschluss für {qid} fehlgeschlagen.", "ERROR")
                if btn:
                    self.after(0, lambda: btn.configure(state="normal", text="⚡ EXPRESS"))
        threading.Thread(target=_bg, daemon=True).start()

    def _sim_single_quest(self, app_id: str, game_title: str):
        """Switches to Simulator Tab and AUTOMATICALLY UPDATES THE PRESET & VALUES as requested!"""
        self._switch_tab("simulator")

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
                if not q.get("enrolled") and not q.get("completed"):
                    self.api.enroll_quest(q.get("id"))
                    count += 1
                    time.sleep(0.5)
            self.log(f"{count} Quests automatisch angenommen.", "SUCCESS")
            self.refresh_quests()
        threading.Thread(target=_bg, daemon=True).start()

    def toggle_auto_farm(self):
        if not self.farmer:
            return
        if self.auto_farm_running:
            self.farmer.stop()
            self.auto_farm_running = False
            self.btn_autofarm.configure(text="🚀 AUTO-FARM", fg_color=COLOR_EMERALD)
            self.log("Auto-Farm gestoppt.", "INFO")
        else:
            self.auto_farm_running = True
            self.btn_autofarm.configure(text="■ STOPPEN", fg_color=COLOR_CRIMSON)
            self.log("Auto-Farm gestartet! Alle Quests werden nacheinander erledigt.", "SUCCESS")
            self.farmer.start()

    def _on_farm_quest_progress(self, p_info):
        qid = p_info.get("quest_id")
        current_sec = p_info.get("current_seconds", 0)
        target_sec = p_info.get("target_seconds", 900)
        percent = min(100.0, (current_sec / target_sec * 100.0)) if target_sec > 0 else 0.0

        if qid in self.quest_cards:
            p_bar = self.quest_cards[qid]["p_bar"]
            lbl_txt = self.quest_cards[qid]["lbl_txt"]
            self.after(0, lambda: p_bar.set(percent / 100.0))
            self.after(0, lambda: lbl_txt.configure(
                text=f"{current_sec // 60}/{target_sec // 60} MIN. ({int(percent)}%)"
            ))

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

    def _open_account_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Discord Account Auswählen")
        modal.geometry("460x420")
        modal.resizable(False, False)
        modal.configure(fg_color=COLOR_BG_DARK)
        modal.transient(self)
        modal.grab_set()

        ctk.CTkLabel(
            modal, text="DISCORD ACCOUNT VERWALTUNG",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(pady=(16, 8))

        scroll = ctk.CTkScrollableFrame(modal, width=410, height=210, fg_color=COLOR_CARD_BG)
        scroll.pack(padx=20, pady=8, fill="both", expand=True)

        if not self.accounts:
            self.accounts = find_all_valid_accounts()

        for acc in self.accounts:
            row = ctk.CTkFrame(scroll, fg_color="#181926", corner_radius=6)
            row.pack(fill="x", padx=4, pady=4)

            uname = acc.get("username", "Unknown")
            disc = acc.get("discriminator", "0")
            lbl_name = f"{uname}#{disc}" if disc != "0" else uname

            ctk.CTkLabel(row, text=f"👤 {lbl_name}", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=COLOR_WHITE).pack(side="left", padx=10, pady=8)

            ctk.CTkButton(
                row, text="AUSWÄHLEN", width=90, height=28,
                fg_color=COLOR_NEON_BLURPLE, hover_color=COLOR_NEON_BLURPLE_HOVER,
                command=lambda a=acc: [self._set_active_account(a), modal.destroy()]
            ).pack(side="right", padx=10, pady=8)

        # Manual token input
        bottom_frame = ctk.CTkFrame(modal, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=(8, 16))

        token_entry = ctk.CTkEntry(bottom_frame, placeholder_text="Oder Discord User-Token manuell eingeben...", height=34)
        token_entry.pack(fill="x", pady=(0, 8))

        def _use_token():
            tok = token_entry.get().strip()
            if tok:
                prof = get_user_profile(tok)
                if prof:
                    self._set_active_account(prof)
                    modal.destroy()
                else:
                    messagebox.showerror("Fehler", "Ungültiger Token.")

        ctk.CTkButton(bottom_frame, text="MANUELLEN TOKEN LADEN", height=34, fg_color=COLOR_DARK_BTN, hover_color=COLOR_DARK_BTN_HOVER, command=_use_token).pack(fill="x")


if __name__ == '__main__':
    app = AutoQuestApp()
    app.mainloop()
