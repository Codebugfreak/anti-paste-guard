# core/hooks/events.py
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Set, Dict, Any
import time
from datetime import datetime, timezone

# --- timing helpers ---
def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

def mono_ts() -> float:
    # Monotonic high-res timestamp (immune to system clock changes)
    return time.perf_counter()

# --- core enums ---
class EventType(Enum):
    KEY = auto()
    MOUSE = auto()

class KeyAction(Enum):
    DOWN = "down"
    UP = "up"

class MouseAction(Enum):
    DOWN = "down"
    UP = "up"
    CLICK = "click"     # reserved for future double-click inference if needed
    SCROLL = "scroll"

# --- base event ---
@dataclass(frozen=True)
class BaseEvent:
    # etype is auto-set by subclasses in __post_init__
    etype: EventType = field(init=False)
    # Lazy UTC: keep None until serialization to avoid heavy ISO formatting per event
    t_utc: Optional[str] = None
    t_mono: float = field(default_factory=mono_ts)
    app: Optional[str] = None  # filled later by focus/process tracker (Stage 4)

    def to_record(self) -> Dict[str, Any]:
        # materialize UTC only if not already set
        t_utc_val = self.t_utc or utc_iso()
        return {
            "etype": self.etype.name,
            "t_utc": t_utc_val,
            "t_mono": self.t_mono,
            "app": self.app,
        }

# --- key event ---
@dataclass(frozen=True)
class KeyEvent(BaseEvent):
    key: str = ""
    action: KeyAction = KeyAction.DOWN
    mods: Set[str] = field(default_factory=set)  # {"ctrl","shift","alt","cmd"}
    scan_code: Optional[int] = None             # platform-specific; normalize later

    def __post_init__(self):
        object.__setattr__(self, "etype", EventType.KEY)

    def to_record(self) -> Dict[str, Any]:
        base = super().to_record()
        base.update({
            "key": self.key,
            "action": self.action.value,
            "mods": sorted(self.mods),
            "scan_code": self.scan_code,
        })
        return base

# --- mouse event ---
@dataclass(frozen=True)
class MouseEvent(BaseEvent):
    button: Optional[str] = None     # "left","right","middle" (normalized elsewhere)
    action: MouseAction = MouseAction.DOWN
    clicks: Optional[int] = None     # 1 / 2 for double, if inferred later
    x: Optional[int] = None
    y: Optional[int] = None

    def __post_init__(self):
        object.__setattr__(self, "etype", EventType.MOUSE)

    def to_record(self) -> Dict[str, Any]:
        base = super().to_record()
        base.update({
            "button": self.button,
            "action": self.action.value,
            "clicks": self.clicks,
            "x": self.x,
            "y": self.y,
        })
        return base
