#!/usr/bin/env python3
"""Offline IP monitor with editable list, descriptions, and auto-sized monitor view."""

from __future__ import annotations

import platform
import queue
import subprocess
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

# -- Pillow opzionale: usato per caricare loghi PNG/JPG in modo affidabile --
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

PING_INTERVAL_SECONDS = 2
TIMEOUT_MS = 1000
MIN_TABLE_ROWS = 6
MAX_TABLE_ROWS = 24
MAX_DESCRIPTION_LENGTH = 40
# Cartella dove si trova lo script (funziona anche se lanciato da altra directory)
SCRIPT_DIR = Path(__file__).parent

TOP_LOGO_PREFERRED = "netsentinel_logo.png"
TOP_LOGO_CANDIDATES = (
    "netsentinel_logo.png",
    "netsentinel.png",
    "netsentinel_logo.jpg",
    "netsentinel.jpg",
    "logo_top.png",
)
FOOTER_LOGO_CANDIDATES = ("viper_logo.png", "viper.png", "logo.png")
APP_ICON_CANDIDATES = (
    "netsentinel_icon.ico",
    "netsentinel_logo.png",
    "netsentinel.png",
    "logo_top.png",
)


class PingMonitorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("NetSentinel")
        self.root.geometry("980x620")

        self.worker_thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.result_queue: queue.Queue[tuple[str, bool, str]] = queue.Queue()

        self.ip_items: list[str] = []
        self.ip_descriptions: dict[str, str] = {}

        self.app_icon_photo = None
        self.fallback_icon_photo: tk.PhotoImage | None = None

        self._build_ui()
        self._poll_results()

    def _build_ui(self) -> None:
        self._load_window_icon()

        self.footer_frame = ttk.Frame(self.root, padding=(10, 0, 10, 8))
        self.footer_frame.pack(side="bottom", fill="x")

        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(side="top", fill="both", expand=True)

        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 10))

        title_block = ttk.Frame(header_frame)
        title_block.pack(side="left", fill="x", expand=True)

        title = ttk.Label(
            title_block,
            text="Monitoraggio Switch - Inserimento IP",
            font=("Segoe UI", 14, "bold"),
        )
        title.pack(anchor="w", pady=(0, 4))

        subtitle = ttk.Label(
            title_block,
            text="Aggiungi/rimuovi IP, inserisci una descrizione breve, poi premi GO.",
        )
        subtitle.pack(anchor="w")

        self.top_logo_label: ttk.Label | None = None
        self.top_logo_photo = None
        self._load_logo(parent=header_frame, attr_prefix="top", candidates=TOP_LOGO_CANDIDATES)

        input_row = ttk.Frame(self.main_frame)
        input_row.pack(fill="x", pady=(0, 8))

        ttk.Label(input_row, text="IP switch:").pack(side="left")
        self.ip_var = tk.StringVar()
        self.ip_entry = ttk.Entry(input_row, textvariable=self.ip_var, width=20)
        self.ip_entry.pack(side="left", padx=(8, 12))

        ttk.Label(input_row, text=f"Descrizione breve (max {MAX_DESCRIPTION_LENGTH}):").pack(side="left")
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(input_row, textvariable=self.desc_var)
        self.desc_entry.pack(side="left", fill="x", expand=True, padx=8)

        self.ip_entry.bind("<Return>", lambda _event: self.add_ip())
        self.desc_entry.bind("<Return>", lambda _event: self.add_ip())

        ttk.Button(input_row, text="Aggiungi", command=self.add_ip).pack(side="left")

        small_desc_hint = ttk.Label(
            self.main_frame,
            text="La descrizione è facoltativa e serve come nota rapida per identificare lo switch.",
        )
        small_desc_hint.pack(anchor="w", pady=(0, 8))

        list_frame = ttk.LabelFrame(self.main_frame, text="Lista IP")
        list_frame.pack(fill="both", expand=False)

        self.ip_listbox = tk.Listbox(list_frame, height=8)
        self.ip_listbox.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)

        list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.ip_listbox.yview)
        list_scroll.pack(side="left", fill="y", padx=(4, 8), pady=8)
        self.ip_listbox.configure(yscrollcommand=list_scroll.set)

        list_buttons = ttk.Frame(list_frame)
        list_buttons.pack(side="left", fill="y", padx=(0, 8), pady=8)

        ttk.Button(list_buttons, text="Rimuovi selezionato", command=self.remove_selected_ip).pack(
            fill="x", pady=(0, 6)
        )
        ttk.Button(list_buttons, text="Svuota lista", command=self.clear_ip_list).pack(fill="x")

        actions = ttk.Frame(self.main_frame)
        actions.pack(fill="x", pady=12)

        self.go_button = ttk.Button(actions, text="GO", command=self.start_monitoring)
        self.go_button.pack(side="left")

        self.stop_button = ttk.Button(actions, text="STOP", command=self.stop_monitoring, state="disabled")
        self.stop_button.pack(side="left", padx=8)

        self.interval_label = ttk.Label(
            actions,
            text=f"Intervallo: {PING_INTERVAL_SECONDS}s | Timeout: {TIMEOUT_MS}ms",
        )
        self.interval_label.pack(side="right")

        self.monitor_frame = ttk.LabelFrame(self.main_frame, text="Stato monitoraggio")
        self.monitor_frame.pack(fill="both", expand=True)

        monitor_hint = ttk.Label(
            self.monitor_frame,
            text="La tabella si adatta automaticamente alla lunghezza della lista IP.",
        )
        monitor_hint.pack(anchor="w", padx=8, pady=(8, 0))

        self.tree = ttk.Treeview(
            self.monitor_frame,
            columns=("ip", "description", "status", "last_check"),
            show="headings",
            height=MIN_TABLE_ROWS,
        )
        self.tree.heading("ip", text="IP")
        self.tree.heading("description", text="Descrizione")
        self.tree.heading("status", text="Stato")
        self.tree.heading("last_check", text="Ultimo controllo")
        self.tree.column("ip", width=190, anchor="center")
        self.tree.column("description", width=260, anchor="w")
        self.tree.column("status", width=220, anchor="center")
        self.tree.column("last_check", width=180, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        self.tree.tag_configure("up", foreground="#0A8A0A")
        self.tree.tag_configure("down", foreground="#B22222")
        self.tree.tag_configure("wait", foreground="#6B7280")

        self.footer_logo_label: ttk.Label | None = None
        self.footer_logo_photo = None
        self._load_logo(parent=self.footer_frame, attr_prefix="footer", candidates=FOOTER_LOGO_CANDIDATES)

        self.signature_label = ttk.Label(
            self.footer_frame,
            text="Viperhack89 Grd.Capo Giovanni PIROZZI",
            font=("Segoe UI", 10, "italic"),
        )
        self.signature_label.pack(side="right")

        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        self.ip_entry.focus_set()
        self._update_monitor_size()

    def _load_window_icon(self) -> None:
        for candidate in APP_ICON_CANDIDATES:
            path = SCRIPT_DIR / candidate
            if not path.exists():
                continue
            try:
                if path.suffix.lower() == ".ico":
                    self.root.iconbitmap(default=str(path))
                    return
                # Usa Pillow se disponibile, altrimenti tk nativo
                if PIL_AVAILABLE:
                    img = Image.open(str(path))
                    img = img.resize((32, 32), Image.LANCZOS)
                    self.app_icon_photo = ImageTk.PhotoImage(img)
                else:
                    self.app_icon_photo = tk.PhotoImage(file=str(path))
                self.root.iconphoto(True, self.app_icon_photo)
                return
            except Exception:
                continue

        # Fallback: cerchio verde minimale
        self.fallback_icon_photo = tk.PhotoImage(width=16, height=16)
        circle_points = [
            (6,1),(7,1),(8,1),(9,1),
            (4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(11,2),
            (3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,3),(11,3),(12,3),
            (2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),(11,4),(12,4),(13,4),
            (2,5),(3,5),(4,5),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(11,5),(12,5),(13,5),
            (1,6),(2,6),(3,6),(4,6),(5,6),(6,6),(7,6),(8,6),(9,6),(10,6),(11,6),(12,6),(13,6),(14,6),
            (1,7),(2,7),(3,7),(4,7),(5,7),(6,7),(7,7),(8,7),(9,7),(10,7),(11,7),(12,7),(13,7),(14,7),
            (1,8),(2,8),(3,8),(4,8),(5,8),(6,8),(7,8),(8,8),(9,8),(10,8),(11,8),(12,8),(13,8),(14,8),
            (1,9),(2,9),(3,9),(4,9),(5,9),(6,9),(7,9),(8,9),(9,9),(10,9),(11,9),(12,9),(13,9),(14,9),
            (2,10),(3,10),(4,10),(5,10),(6,10),(7,10),(8,10),(9,10),(10,10),(11,10),(12,10),(13,10),
            (2,11),(3,11),(4,11),(5,11),(6,11),(7,11),(8,11),(9,11),(10,11),(11,11),(12,11),(13,11),
            (3,12),(4,12),(5,12),(6,12),(7,12),(8,12),(9,12),(10,12),(11,12),(12,12),
            (4,13),(5,13),(6,13),(7,13),(8,13),(9,13),(10,13),(11,13),
            (6,14),(7,14),(8,14),(9,14),
        ]
        for x, y in circle_points:
            self.fallback_icon_photo.put("#0A8A0A", to=(x, y))
        self.root.iconphoto(True, self.fallback_icon_photo)

    def _load_logo(self, parent: ttk.Frame, attr_prefix: str, candidates: tuple[str, ...]) -> None:
        logo_path = None
        if attr_prefix == "top":
            preferred = SCRIPT_DIR / TOP_LOGO_PREFERRED
            if preferred.exists():
                logo_path = preferred

        if logo_path is None:
            for candidate in candidates:
                p = SCRIPT_DIR / candidate
                if p.exists():
                    logo_path = p
                    break

        if logo_path is None:
            return

        max_w, max_h = (320, 120) if attr_prefix == "top" else (120, 120)

        try:
            if PIL_AVAILABLE:
                # Pillow: supporta PNG, JPG, e sfondo trasparente
                img = Image.open(str(logo_path)).convert("RGBA")
                img.thumbnail((max_w, max_h), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
            else:
                # Fallback tk nativo
                photo = tk.PhotoImage(file=str(logo_path))
                w_ratio = max(1, (photo.width() + max_w - 1) // max_w)
                h_ratio = max(1, (photo.height() + max_h - 1) // max_h)
                ratio = max(w_ratio, h_ratio)
                if ratio > 1:
                    photo = photo.subsample(ratio, ratio)

            label = ttk.Label(parent, image=photo)
            label.pack(side="right", padx=(0, 10), anchor="ne")
            setattr(self, f"{attr_prefix}_logo_photo", photo)
            setattr(self, f"{attr_prefix}_logo_label", label)

        except Exception as e:
            print(f"[logo] Errore caricamento {logo_path}: {e}")
            setattr(self, f"{attr_prefix}_logo_photo", None)
            setattr(self, f"{attr_prefix}_logo_label", None)

    def _update_monitor_size(self) -> None:
        target_rows = max(MIN_TABLE_ROWS, min(MAX_TABLE_ROWS, len(self.ip_items) + 2))
        self.tree.configure(height=target_rows)

    def add_ip(self) -> None:
        ip = self.ip_var.get().strip()
        description = self.desc_var.get().strip()[:MAX_DESCRIPTION_LENGTH]
        if not ip:
            return
        if ip in self.ip_items:
            messagebox.showinfo("IP già presente", f"L'IP {ip} è già nella lista.")
            return
        self.ip_items.append(ip)
        self.ip_descriptions[ip] = description
        display_text = f"{ip} | {description}" if description else ip
        self.ip_listbox.insert("end", display_text)
        self.ip_var.set("")
        self.desc_var.set("")
        self.ip_entry.focus_set()
        self._update_monitor_size()

    def remove_selected_ip(self) -> None:
        selection = self.ip_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        self.ip_listbox.delete(index)
        if 0 <= index < len(self.ip_items):
            ip = self.ip_items.pop(index)
            self.ip_descriptions.pop(ip, None)
        self._update_monitor_size()

    def clear_ip_list(self) -> None:
        self.ip_items.clear()
        self.ip_descriptions.clear()
        self.ip_listbox.delete(0, "end")
        self._update_monitor_size()

    def start_monitoring(self) -> None:
        if not self.ip_items:
            messagebox.showwarning("Nessun IP", "Aggiungi almeno un IP prima di premere GO.")
            return
        self.stop_event.clear()
        self.go_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        for row in self.tree.get_children():
            self.tree.delete(row)
        for ip in self.ip_items:
            description = self.ip_descriptions.get(ip, "")
            self.tree.insert("", "end", iid=ip, values=(ip, description, "⚪ In attesa", "-"), tags=("wait",))
        self._update_monitor_size()
        self.worker_thread = threading.Thread(
            target=self._monitor_ips, args=(self.ip_items.copy(),), daemon=True
        )
        self.worker_thread.start()

    def stop_monitoring(self) -> None:
        self.stop_event.set()
        self.go_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def _monitor_ips(self, ip_list: list[str]) -> None:
        while not self.stop_event.is_set():
            timestamp = time.strftime("%H:%M:%S")
            for ip in ip_list:
                if self.stop_event.is_set():
                    break
                is_up = ping_host(ip)
                self.result_queue.put((ip, is_up, timestamp))
            self.stop_event.wait(PING_INTERVAL_SECONDS)

    def _poll_results(self) -> None:
        while True:
            try:
                ip, is_up, timestamp = self.result_queue.get_nowait()
            except queue.Empty:
                break
            icon = "🟢" if is_up else "🔴"
            text = f"{icon} {'ATTIVO' if is_up else 'NON ATTIVO'}"
            if self.tree.exists(ip):
                row_tag = "up" if is_up else "down"
                description = self.ip_descriptions.get(ip, "")
                self.tree.item(ip, values=(ip, description, text, timestamp), tags=(row_tag,))
        self.root.after(200, self._poll_results)


def ping_host(ip: str) -> bool:
    system = platform.system().lower()
    if "windows" in system:
        cmd = ["ping", "-n", "1", "-w", str(TIMEOUT_MS), ip]
    else:
        timeout_seconds = max(1, TIMEOUT_MS // 1000)
        cmd = ["ping", "-c", "1", "-W", str(timeout_seconds), ip]
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    return result.returncode == 0


def main() -> None:
    root = tk.Tk()
    app = PingMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_monitoring)
    root.mainloop()


if __name__ == "__main__":
    main()
