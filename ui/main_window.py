from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from app.controller.runner import HookRuntime
from tkinter import Listbox
from core.hooks.events import AnomalyEvent

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Anti-Paste Guard — Exam Mode: OFF")
        self.geometry("900x600")
        self.minsize(700, 420)

        self._content = ttk.Frame(self, padding=12)
        self._content.pack(fill="both", expand=True)
        # see anomaly log
        self.anom_list = Listbox(self._content, height=6)
        self.anom_list.pack(fill="x", pady=(4,0))

        # top bar with a start/stop toggle & event count
        topbar = ttk.Frame(self._content)
        topbar.pack(side="top", fill="x", pady=(0,8))

        self.event_count_var = tk.StringVar(value="Events: 0")
        ttk.Label(topbar, textvariable=self.event_count_var).pack(side="left")

        self.toggle_btn_var = tk.StringVar(value="Start Capture")
        self.toggle_btn = ttk.Button(topbar, textvariable=self.toggle_btn_var, command=self._toggle_capture)
        self.toggle_btn.pack(side="right")

        # status bar
        self.status_var = tk.StringVar(value="Ready")
        self._status = ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(8, 4))
        self._status.pack(side="bottom", fill="x")

        # hook runtime (Stage 2)
        self._runtime = HookRuntime(on_event=self._on_event)
        self._capturing = False

        # ensure graceful stop on window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # (optional) demo status changes
        self.after(600, self._demo_state_progress)

    def _toggle_capture(self):
        if not self._capturing:
            self._runtime.start()
            self._capturing = True
            self.toggle_btn_var.set("Stop Capture")
            self.set_status("Capture: ON")
        else:
            self._runtime.stop()
            self._capturing = False
            self.toggle_btn_var.set("Start Capture")
            self.set_status("Capture: OFF")

    def _on_event(self, ev, count: int):
        self.event_count_var.set(f"Events: {count}")
        if isinstance(ev, AnomalyEvent):
            line = f"[{ev.severity.value.upper()}] {ev.rule_id} — {ev.rationale}"
            self.anom_list.insert(0, line)
            # keep it short
            if self.anom_list.size() > 50:
                self.anom_list.delete(50, 'end')

    def set_status(self, text: str) -> None:
        self.status_var.set(text)
        self._status.update_idletasks()

    def _demo_state_progress(self) -> None:
        # (unchanged demo) remove whenever
        steps = ["Initializing…","Configuring logging…","Loading modules…","Ready"]
        def stepper(i=0):
            if i < len(steps):
                self.set_status(steps[i])
                self.after(300, lambda: stepper(i + 1))
        stepper()

    def _on_close(self):
        # stop hooks if running, then close
        try:
            if self._capturing:
                self._runtime.stop()
        finally:
            self.destroy()
