import tkinter as tk
from tkinter import ttk


def starte_gui(on_closing_callback):
    """Erstellt das Live-Fenster des Netzwerkmonitors."""
    root = tk.Tk()
    root.title("Netzwerk Monitor")
    root.geometry("480x340")
    root.resizable(False, False)

    ttk.Label(
        root,
        text="Netzwerk Monitor aktiv",
        font=("Arial", 14, "bold"),
    ).pack(pady=15)

    frame = ttk.LabelFrame(root, text=" Live-Werte ", padding=12)
    frame.pack(fill="x", padx=20, pady=5)

    labels = {}
    for key, text in (
        ("connection", "Verbindung: --"),
        ("latency", "Latenz: -- ms"),
        ("upload", "Upload: --"),
        ("download", "Download: --"),
        ("interfaces", "Aktive Interfaces: --"),
    ):
        labels[key] = ttk.Label(frame, text=text, font=("Arial", 10))
        labels[key].pack(anchor="w", pady=3)

    ttk.Button(
        root,
        text="Programm beenden",
        command=lambda: on_closing_callback(root),
    ).pack(pady=15)
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing_callback(root))
    return root, labels
