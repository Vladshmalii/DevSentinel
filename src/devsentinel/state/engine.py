"""Central coordinator for DevSentinel."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from ..states import AudioState, BreakTimer, Command, CommandType, EngineState, FocusTimer, VisionState


@dataclass(slots=True)
class EngineConfig:
    focus_default_minutes: int = 40
    break_default_minutes: int = 10
    fatigue_threshold: float = 0.7


@dataclass
class StateEngine:
    config: EngineConfig
    state: EngineState = field(
        default_factory=lambda: EngineState(
            mode="idle", focus_level=0.0, fatigue_level=0.0, stress_level=0.0
        )
    )

    def update(self, vision: VisionState | None = None, audio: AudioState | None = None) -> EngineState:
        if vision:
            self.state.focus_level = 0.7 * self.state.focus_level + 0.3 * vision.attention
            self.state.fatigue_level = 0.8 * self.state.fatigue_level + 0.2 * vision.fatigue
            self.state.stress_level = 0.8 * self.state.stress_level + 0.2 * vision.stress
        if audio:
            self.state.stress_level = min(1.0, self.state.stress_level + audio.angry * 0.1)
        self._tick_timers()
        return self.state

    def handle_command(self, command: Command) -> EngineState:
        if command.type is CommandType.FOCUS:
            self._start_focus(command.duration_minutes or self.config.focus_default_minutes)
        elif command.type is CommandType.BREAK:
            self._start_break(command.duration_minutes or self.config.break_default_minutes)
        elif command.type is CommandType.NOTE and command.content:
            self.state.notes_saved += 1
            self.state.events.append(f"note_saved:{command.content[:30]}")
        return self.state

    def _start_focus(self, minutes: int) -> None:
        self.state.mode = "focus_session"
        duration = timedelta(minutes=minutes)
        self.state.current_focus_timer = FocusTimer(duration=duration, started_at=datetime.utcnow())
        self.state.current_break_timer = None
        self.state.events.append(f"focus_started:{minutes}")

    def _start_break(self, minutes: int) -> None:
        self.state.mode = "break"
        duration = timedelta(minutes=minutes)
        self.state.current_break_timer = BreakTimer(duration=duration, started_at=datetime.utcnow())
        self.state.current_focus_timer = None
        self.state.last_break_started = datetime.utcnow()
        self.state.events.append(f"break_started:{minutes}")

    def _tick_timers(self) -> None:
        timer = self.state.current_focus_timer or self.state.current_break_timer
        if timer and timer.remaining.total_seconds() <= 0:
            self.state.events.append("timer_completed")
            self.state.current_focus_timer = None
            self.state.current_break_timer = None
            self.state.mode = "idle"
