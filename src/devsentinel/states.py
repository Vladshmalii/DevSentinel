"""Core dataclasses that describe the state flowing between DevSentinel modules."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class Mood(str, Enum):
    """Discrete mood labels reported by the vision pipeline."""

    NEUTRAL = "neutral"
    FOCUSED = "focused"
    TIRED = "tired"
    STRESSED = "stressed"
    HAPPY = "happy"
    BORED = "bored"


@dataclass(slots=True)
class VisionState:
    """Snapshot produced by the vision module every ~500–1000 ms."""

    present: bool
    attention: float
    fatigue: float
    stress: float
    mood: Mood


@dataclass(slots=True)
class AudioState:
    """Light‑weight emotional distribution inferred from the microphone."""

    angry: float
    tired: float
    calm: float
    excited: float


@dataclass(slots=True)
class SpeechSegment:
    """Transcript emitted by the speech recognizer/command parser."""

    text: str
    timestamp: datetime


class CommandType(str, Enum):
    FOCUS = "focus"
    BREAK = "break"
    NOTE = "note"


@dataclass(slots=True)
class Command:
    """Structured representation of an understood user request."""

    type: CommandType
    duration_minutes: Optional[int] = None
    content: Optional[str] = None


@dataclass(slots=True)
class FocusTimer:
    duration: timedelta
    started_at: datetime

    @property
    def remaining(self) -> timedelta:
        elapsed = datetime.utcnow() - self.started_at
        remaining = self.duration - elapsed
        return max(remaining, timedelta())


@dataclass(slots=True)
class BreakTimer(FocusTimer):
    """Alias for semantic clarity."""


@dataclass(slots=True)
class EngineState:
    """Aggregated view maintained by the state engine."""

    mode: str
    focus_level: float
    fatigue_level: float
    stress_level: float
    current_focus_timer: Optional[FocusTimer] = None
    current_break_timer: Optional[BreakTimer] = None
    last_break_started: Optional[datetime] = None
    notes_saved: int = 0
    events: list[str] = field(default_factory=list)
