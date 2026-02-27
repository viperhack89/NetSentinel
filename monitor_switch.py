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

PING_INTERVAL_SECONDS = 2
TIMEOUT_MS = 1000
MIN_TABLE_ROWS = 6
MAX_TABLE_ROWS = 24
MAX_DESCRIPTION_LENGTH = 40
LOGO_CANDIDATES = ("logo.png", "viper_logo.png", "viper.png")


class PingMonitorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Monitor Switch IP")
        self.root.geometry("980x620")

        self.worker_thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.result_queue: queue.Queue[tuple[str, bool, str]] = queue.Queue()

        self.ip_items: list[str] = []
        self.ip_descriptions: dict[str, str] = {}

        self._build_ui()
        self._poll_results()

    def _build_ui(self) -> None:
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        title = ttk.Label(
            self.main_frame,
            text="Monitoraggio Switch - Inserimento IP",
            font=("Segoe UI", 14, "bold"),
        )
        title.pack(anchor="w", pady=(0, 8))

        subtitle = ttk.Label(
            self.main_frame,
            text="Aggiungi/rimuovi IP, inserisci una descrizione breve, poi premi GO.",
        )
        subtitle.pack(anchor="w", pady=(0, 10))

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

        self.footer_frame = ttk.Frame(self.main_frame)
        self.footer_frame.pack(fill="x", pady=(8, 0))

        self.logo_label: ttk.Label | None = None
        self.logo_photo: tk.PhotoImage | None = None
        self._load_footer_logo()

        self.signature_label = ttk.Label(
            self.footer_frame,
            text="Viperhack89 Grd.Capo Giovanni PIROZZI",
            font=("Segoe UI", 10, "italic"),
        )
        self.signature_label.pack(side="right", anchor="e")

        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        self.ip_entry.focus_set()
        self._update_monitor_size()

    def _load_footer_logo(self) -> None:
        logo_path = None
        for candidate in LOGO_CANDIDATES:
            candidate_path = Path(candidate)
            if candidate_path.exists():
                logo_path = candidate_path
                break

        if logo_path is None:
            return

        try:
            self.logo_photo = tk.PhotoImage(file=str(logo_path))
            self.logo_label = ttk.Label(self.footer_frame, image=self.logo_photo)
            self.logo_label.pack(side="right", padx=(0, 10))
        except tk.TclError:
            self.logo_photo = None
            self.logo_label = None

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
            self.tree.insert(
                "",
                "end",
                iid=ip,
                values=(ip, description, "⚪ In attesa", "-"),
                tags=("wait",),
            )

        self._update_monitor_size()

        self.worker_thread = threading.Thread(
            target=self._monitor_ips,
            args=(self.ip_items.copy(),),
            daemon=True,
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

    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def main() -> None:
    root = tk.Tk()
    app = PingMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_monitoring)
    root.mainloop()


if __name__ == "__main__":
    main()
