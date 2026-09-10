"""
Lightweight Game Window Runner (DQS)
Provides a genuine Win32 GUI window with process name and title matching target games,
and shows the cracked lock icon so the user sees it is actively running and clean.
"""

import os
import sys
import argparse
import tkinter as tk
import ctypes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", default="Game Simulation")
    args, _ = parser.parse_known_args()

    title = args.title
    ctypes.windll.kernel32.SetConsoleTitleW(title)

    root = tk.Tk()
    root.title(title)
    root.geometry("400x170")
    root.configure(bg="#090a0f")
    root.resizable(False, False)

    # Set Window Icon if present
    icon_candidates = [
        os.path.join(os.path.dirname(__file__), "..", "assets", "app_icon.ico"),
        os.path.join(os.path.dirname(__file__), "app_icon.ico"),
        os.path.join(os.getcwd(), "assets", "app_icon.ico"),
        os.path.join(os.getcwd(), "app_icon.ico"),
    ]
    for ic in icon_candidates:
        if os.path.exists(ic):
            try:
                root.iconbitmap(ic)
                break
            except Exception:
                pass

    # Card container
    card = tk.Frame(root, bg="#11131a", highlightbackground="#252736", highlightthickness=1)
    card.pack(fill="both", expand=True, padx=10, pady=10)

    # Top header with open lock
    header_box = tk.Frame(card, bg="#11131a")
    header_box.pack(pady=(12, 4))

    lbl_lock = tk.Label(
        header_box, text="🔓", font=("Segoe UI Emoji", 16),
        fg="#00A8FC", bg="#11131a"
    )
    lbl_lock.pack(side="left", padx=(0, 6))

    lbl_title = tk.Label(
        header_box, text=title,
        font=("Segoe UI", 12, "bold"), fg="#ffffff", bg="#11131a"
    )
    lbl_title.pack(side="left")

    # Status Pill
    status_box = tk.Frame(card, bg="#0d2818", highlightbackground="#23A55A", highlightthickness=1)
    status_box.pack(pady=4)

    lbl_status = tk.Label(
        status_box, text=" ● DISCORD QUEST SIMULATION AKTIV ",
        font=("Segoe UI", 9, "bold"), fg="#23A55A", bg="#0d2818"
    )
    lbl_status.pack(padx=6, pady=2)

    lbl_tip = tk.Label(
        card, text="Discord erkennt dieses Spiel als laufend.\nDu kannst dieses Fenster minimieren.",
        font=("Segoe UI", 9), fg="#86899c", bg="#11131a", justify="center"
    )
    lbl_tip.pack(pady=(6, 10))

    # Position cleanly at bottom right of screen
    try:
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"360x150+{sw - 380}+{sh - 220}")
    except Exception:
        pass

    root.mainloop()

if __name__ == '__main__':
    main()

