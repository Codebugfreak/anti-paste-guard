# app/controller/runner.py
from __future__ import annotations
import threading
import time
from typing import Optional
import structlog

from core.hooks.keyboard_listener import KeyboardHook
from core.hooks.mouse_listener import MouseHook
from app.controller.event_bus import event_queue
from core.hooks.events import BaseEvent

log = structlog.get_logger()

class HookRuntime:
    """Starts/stops hooks; runs a consumer thread that you can later replace with the full analyzer."""
    def __init__(self, on_event=None):
        self.kbd = KeyboardHook(event_queue)
        self.mouse = MouseHook(event_queue)
        self._consumer_thr: Optional[threading.Thread] = None
        self._stop_evt = threading.Event()
        # simple callback so UI can reflect event counts
        self._on_event = on_event

    def start(self) -> None:
        self._stop_evt.clear()
        self.kbd.start()
        self.mouse.start()
        self._consumer_thr = threading.Thread(target=self._consume_loop, daemon=True)
        self._consumer_thr.start()
        log.info("hooks.runtime.start")

    def stop(self) -> None:
        self.kbd.stop()
        self.mouse.stop()
        self._stop_evt.set()
        if self._consumer_thr:
            self._consumer_thr.join(timeout=1.0)
        log.info("hooks.runtime.stop")

    def _consume_loop(self):
        # Minimal consumer: counts events and calls a callback.
        count = 0
        while not self._stop_evt.is_set():
            try:
                ev: BaseEvent = event_queue.get(timeout=0.5)
            except Exception:
                continue
            count += 1
            if self._on_event:
                try:
                    self._on_event(ev, count)
                except Exception as e:
                    log.warning("hooks.runtime.on_event.error", err=str(e))
