"""
DQS - Discord Quest Spoofer Setup / Installer
Official Installer by Sandro (T3X / TNTIX)
Allows 1-click seamless installation, desktop shortcut creation,
start menu integration, and uninstaller creation.
"""

import os
import sys
import shutil
import subprocess
import threading
import time
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import webbrowser

# Appearance setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR_BG_DARK = "#090a0f"
COLOR_BG_SIDEBAR = "#111218"
COLOR_CARD_BG = "#13141e"
COLOR_CARD_BORDER = "#232536"
COLOR_WHITE = "#ffffff"
COLOR_TEXT_PRIMARY = "#f3f4f6"
COLOR_TEXT_MUTED = "#86899c"
COLOR_NEON_BLURPLE = "#5865F2"
COLOR_NEON_BLURPLE_HOVER = "#4752C4"
COLOR_EMERALD = "#23A55A"
COLOR_CRIMSON = "#F23F43"

def get_bundle_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def create_windows_shortcut(target_exe, shortcut_path, icon_path=None, description=""):
    try:
        ps_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target_exe}"
$Shortcut.WorkingDirectory = "{os.path.dirname(target_exe)}"
'''
        if icon_path and os.path.exists(icon_path):
            ps_script += f'$Shortcut.IconLocation = "{icon_path}, 0"\n'
        if description:
            ps_script += f'$Shortcut.Description = "{description}"\n'
        ps_script += '$Shortcut.Save()'

        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                       creationflags=subprocess.CREATE_NO_WINDOW, check=False)
        return True
    except Exception as e:
        print(f"Failed to create shortcut: {e}")
        return False

class DQSInstaller(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DQS Setup // Installer")
        self.geometry("640x580")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG_DARK)

        # Set Window Icon
        self._set_window_icon()

        # Default Install Path
        local_app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        self.default_install_dir = os.path.join(local_app_data, "Programs", "Discord Quest Spoofer")

        self._build_ui()

    def _set_window_icon(self):
        """Sets the installer window icon natively using DQS.png / app_icon.png."""
        bundle = get_bundle_dir()
        candidates = [
            os.path.join(bundle, "DQS.png"),
            os.path.join(bundle, "assets", "app_icon.png"),
            os.path.join(os.getcwd(), "DQS.png"),
            os.path.join(os.getcwd(), "assets", "app_icon.png"),
        ]
        for c in candidates:
            if os.path.exists(c):
                try:
                    temp_ico = os.path.join(tempfile.gettempdir(), "dqs_inst_icon.ico")
                    im = Image.open(c)
                    im.save(temp_ico, format='ICO', sizes=[(16,16), (24,24), (32,32), (48,48), (64,64), (128,128)])
                    self.iconbitmap(temp_ico)
                    self._inst_icon_photo = ImageTk.PhotoImage(im.resize((32, 32)))
                    self.iconphoto(True, self._inst_icon_photo)
                    break
                except Exception:
                    pass

    def _build_ui(self):
        # Header Box
        header = ctk.CTkFrame(self, fg_color=COLOR_BG_SIDEBAR, height=80, corner_radius=0,
                              border_width=1, border_color=COLOR_CARD_BORDER)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        brand_box = ctk.CTkFrame(header, fg_color="transparent")
        brand_box.pack(side="left", padx=20, pady=12)

        bundle = get_bundle_dir()
        logo_path = os.path.join(bundle, "assets", "app_icon.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(bundle, "DQS.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.getcwd(), "DQS.png")

        if os.path.exists(logo_path):
            try:
                raw_logo = Image.open(logo_path).convert("RGBA")
                self.logo_img = ctk.CTkImage(light_image=raw_logo, dark_image=raw_logo, size=(44, 44))
                lbl_icon = ctk.CTkLabel(brand_box, text="", image=self.logo_img)
                lbl_icon.pack(side="left", padx=(0, 12))
            except Exception:
                pass

        title_sub = ctk.CTkFrame(brand_box, fg_color="transparent")
        title_sub.pack(side="left")

        lbl_title = ctk.CTkLabel(
            title_sub, text="DQS SETUP // INSTALLER",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLOR_WHITE
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_sub, text="DISCORD QUEST SPOOFER • RELEASE V3",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        )
        lbl_sub.pack(anchor="w")

        # Creator / GitHub Badge on right
        btn_git = ctk.CTkButton(
            header, text="⭐ GITHUB", width=90, height=28,
            fg_color="#2b1a38", hover_color="#3e2552",
            border_width=1, border_color="#9333ea",
            text_color="#c084fc", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            corner_radius=4, command=lambda: webbrowser.open("https://github.com/TentixTV/Discord-Quest-Spoofer")
        )
        btn_git.pack(side="right", padx=20, pady=25)

        # Body Container
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=25, pady=15)

        # Safety & Creator Card
        safety_card = ctk.CTkFrame(body, fg_color=COLOR_CARD_BG, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        safety_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            safety_card, text="🛡️ OFFZIELLER INSTALLER VON SANDRO (T3X / TNTIX)",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLOR_EMERALD
        ).pack(anchor="w", padx=15, pady=(10, 2))

        ctk.CTkLabel(
            safety_card,
            text="Dieser Installer richtet DQS mit allen Abhängigkeiten, Verknüpfungen und Schutzmechanismen\n"
                 "auf deinem PC ein. 100% sauber und frei von Viren, wenn von TentixTV geladen!",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLOR_TEXT_MUTED, justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # Path Selector Card
        path_card = ctk.CTkFrame(body, fg_color=COLOR_CARD_BG, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        path_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            path_card, text="INSTALLATIONSVERZEICHNIS:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_WHITE
        ).pack(anchor="w", padx=15, pady=(12, 6))

        path_row = ctk.CTkFrame(path_card, fg_color="transparent")
        path_row.pack(fill="x", padx=15, pady=(0, 12))

        self.entry_path = ctk.CTkEntry(
            path_row, fg_color=COLOR_BG_DARK, border_color=COLOR_CARD_BORDER,
            font=ctk.CTkFont(family="Segoe UI", size=11), text_color=COLOR_TEXT_PRIMARY
        )
        self.entry_path.insert(0, self.default_install_dir)
        self.entry_path.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_browse = ctk.CTkButton(
            path_row, text="DURCHSUCHEN...", width=120, height=32,
            fg_color="#1a1b24", hover_color="#262836",
            border_width=1, border_color=COLOR_CARD_BORDER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            command=self._browse_dir
        )
        btn_browse.pack(side="right")

        # Checkboxes Card
        opts_card = ctk.CTkFrame(body, fg_color=COLOR_CARD_BG, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        opts_card.pack(fill="x", pady=(0, 12))

        self.chk_desktop = ctk.CTkCheckBox(
            opts_card, text="Desktop-Verknüpfung erstellen",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=COLOR_NEON_BLURPLE, hover_color=COLOR_NEON_BLURPLE_HOVER
        )
        self.chk_desktop.select()
        self.chk_desktop.pack(anchor="w", padx=15, pady=(10, 5))

        self.chk_startmenu = ctk.CTkCheckBox(
            opts_card, text="Startmenü-Eintrag erstellen",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=COLOR_NEON_BLURPLE, hover_color=COLOR_NEON_BLURPLE_HOVER
        )
        self.chk_startmenu.select()
        self.chk_startmenu.pack(anchor="w", padx=15, pady=5)

        self.chk_autostart = ctk.CTkCheckBox(
            opts_card, text="DQS nach Abschluss direkt starten",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=COLOR_NEON_BLURPLE, hover_color=COLOR_NEON_BLURPLE_HOVER
        )
        self.chk_autostart.select()
        self.chk_autostart.pack(anchor="w", padx=15, pady=(5, 10))

        # Status & Progress
        self.lbl_status = ctk.CTkLabel(
            body, text="Bereit zur Installation.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_TEXT_MUTED
        )
        self.lbl_status.pack(anchor="w", pady=(0, 4))

        self.prog_bar = ctk.CTkProgressBar(body, fg_color="#181924", progress_color=COLOR_NEON_BLURPLE)
        self.prog_bar.set(0.0)
        self.prog_bar.pack(fill="x", pady=(0, 15))

        # Bottom Action Buttons
        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x")

        self.btn_install = ctk.CTkButton(
            btn_row, text="⚡ DQS JETZT INSTALLIEREN", height=42,
            fg_color=COLOR_NEON_BLURPLE, hover_color=COLOR_NEON_BLURPLE_HOVER,
            text_color=COLOR_WHITE, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            corner_radius=4, command=self._start_install
        )
        self.btn_install.pack(side="right", fill="x", expand=True)

    def _browse_dir(self):
        chosen = filedialog.askdirectory(initialdir=self.entry_path.get(), title="Zielverzeichnis auswählen")
        if chosen:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, os.path.normpath(chosen))

    def _start_install(self):
        self.btn_install.configure(state="disabled", text="INSTALLIERE...")
        threading.Thread(target=self._run_installation, daemon=True).start()

    def _run_installation(self):
        try:
            target_dir = self.entry_path.get().strip()
            if not target_dir:
                target_dir = self.default_install_dir

            self._update_progress(0.1, f"Erstelle Verzeichnis {target_dir}...")
            os.makedirs(target_dir, exist_ok=True)
            time.sleep(0.3)

            bundle = get_bundle_dir()
            current = os.getcwd()

            # Files to deploy
            payloads = [
                ("DQS.exe", "DQS.exe"),
                ("DQS.png", "DQS.png"),
                ("Start.bat", "Start.bat"),
                ("README.md", "README.md"),
                ("LICENSE", "LICENSE")
            ]

            total = len(payloads)
            for idx, (src_name, dst_name) in enumerate(payloads):
                p_val = 0.2 + (0.5 * (idx / total))
                self._update_progress(p_val, f"Kopiere {dst_name}...")

                src_found = None
                # Search in bundle dir, current dir, or script dir
                for search_base in [bundle, current, os.path.dirname(os.path.abspath(__file__))]:
                    candidate = os.path.join(search_base, src_name)
                    if os.path.exists(candidate):
                        src_found = candidate
                        break

                if src_found:
                    shutil.copy2(src_found, os.path.join(target_dir, dst_name))
                time.sleep(0.1)

            # Copy assets folder recursively if present
            assets_src = None
            for search_base in [bundle, current, os.path.dirname(os.path.abspath(__file__))]:
                cand = os.path.join(search_base, "assets")
                if os.path.exists(cand) and os.path.isdir(cand):
                    assets_src = cand
                    break
            if assets_src:
                dest_assets = os.path.join(target_dir, "assets")
                shutil.copytree(assets_src, dest_assets, dirs_exist_ok=True)

            # Copy bin folder recursively if present
            bin_src = None
            for search_base in [bundle, current, os.path.dirname(os.path.abspath(__file__))]:
                cand = os.path.join(search_base, "bin")
                if os.path.exists(cand) and os.path.isdir(cand):
                    bin_src = cand
                    break
            if bin_src:
                dest_bin = os.path.join(target_dir, "bin")
                shutil.copytree(bin_src, dest_bin, dirs_exist_ok=True)

            # Copy ui folder recursively if present
            ui_src = None
            for search_base in [bundle, current, os.path.dirname(os.path.abspath(__file__))]:
                cand = os.path.join(search_base, "ui")
                if os.path.exists(cand) and os.path.isdir(cand):
                    ui_src = cand
                    break
            if ui_src:
                dest_ui = os.path.join(target_dir, "ui")
                shutil.copytree(ui_src, dest_ui, dirs_exist_ok=True)

            self._update_progress(0.75, "Erstelle Uninstaller...")
            uninstaller_path = os.path.join(target_dir, "Uninstall.bat")
            desktop_link = os.path.join(os.environ.get("USERPROFILE", "C:\\"), "Desktop", "DQS - Discord Quest Spoofer.lnk")
            startmenu_folder = os.path.join(os.environ.get("APPDATA", "C:\\"), "Microsoft", "Windows", "Start Menu", "Programs", "Discord Quest Spoofer")

            uninstall_script = f"""@echo off
title DQS Uninstaller
echo ===================================================
echo     DQS // Discord Quest Spoofer Deinstallation
echo ===================================================
echo.
taskkill /F /IM DQS.exe 2>nul
taskkill /F /IM dummy_runner.exe 2>nul
del /F /Q "{desktop_link}" 2>nul
rmdir /S /Q "{startmenu_folder}" 2>nul
echo Entferne Programmdateien...
cd ..
timeout /t 2 /nobreak >nul
rmdir /S /Q "{target_dir}" 2>nul
echo.
echo DQS wurde vollstaendig von deinem System entfernt.
pause
exit
"""
            with open(uninstaller_path, "w", encoding="utf-8") as uf:
                uf.write(uninstall_script)

            installed_exe = os.path.join(target_dir, "DQS.exe")
            installed_ico = installed_exe

            # Shortcuts
            self._update_progress(0.85, "Registriere Desktop- und Startmenü-Verknüpfungen...")
            if self.chk_desktop.get() == 1:
                create_windows_shortcut(installed_exe, desktop_link, installed_ico, "DQS - Discord Quest Spoofer by Sandro (T3X / TNTIX)")

            if self.chk_startmenu.get() == 1:
                os.makedirs(startmenu_folder, exist_ok=True)
                startmenu_link = os.path.join(startmenu_folder, "DQS - Discord Quest Spoofer.lnk")
                create_windows_shortcut(installed_exe, startmenu_link, installed_ico, "DQS - Discord Quest Spoofer")
                uninst_link = os.path.join(startmenu_folder, "DQS Deinstallieren.lnk")
                create_windows_shortcut(uninstaller_path, uninst_link, None, "DQS Deinstallieren")

            self._update_progress(1.0, "✓ Installation erfolgreich abgeschlossen!")
            time.sleep(0.5)

            if self.chk_autostart.get() == 1 and os.path.exists(installed_exe):
                subprocess.Popen([installed_exe], cwd=target_dir)

            self.after(0, self._show_success)

        except Exception as e:
            self._update_progress(0.0, f"Fehler: {e}")
            self.after(0, lambda: messagebox.showerror("Installationsfehler", f"Fehler bei der Installation:\n{e}"))
            self.after(0, lambda: self.btn_install.configure(state="normal", text="ERNEUT VERSUCHEN"))

    def _update_progress(self, val, msg):
        self.after(0, lambda: self.prog_bar.set(val))
        self.after(0, lambda: self.lbl_status.configure(text=msg))

    def _show_success(self):
        messagebox.showinfo("DQS Installation", "✓ DQS - Discord Quest Spoofer wurde erfolgreich installiert!\n\nDu kannst die App jetzt über die Desktop-Verknüpfung starten.")
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = DQSInstaller()
    app.mainloop()
