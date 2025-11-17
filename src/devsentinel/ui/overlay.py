"""PySide6 overlay skeleton."""
from __future__ import annotations

from dataclasses import dataclass

try:  # pragma: no cover
    from PySide6 import QtCore, QtGui, QtWidgets
except Exception:  # pragma: no cover
    QtCore = QtGui = QtWidgets = None  # type: ignore

from ..states import EngineState


@dataclass(slots=True)
class OverlayConfig:
    always_on_top: bool = True
    width: int = 260
    height: int = 160


class OverlayWidget:
    """Minimal always-on-top transparent window for MVP."""

    def __init__(self, config: OverlayConfig):
        if QtWidgets is None:
            raise RuntimeError("PySide6 is not available in this environment")
        self.config = config
        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        self.window = QtWidgets.QWidget()
        self.window.setWindowFlags(
            QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
        )
        self.window.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.window.setFixedSize(config.width, config.height)
        self.label = QtWidgets.QLabel("DevSentinel", self.window)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont("Segoe UI", 12)
        self.label.setFont(font)
        layout = QtWidgets.QVBoxLayout(self.window)
        layout.addWidget(self.label)

    def update(self, state: EngineState) -> None:
        message = f"Mode: {state.mode}\nFocus: {state.focus_level:.2f}\nFatigue: {state.fatigue_level:.2f}"
        if state.current_focus_timer:
            remaining = int(state.current_focus_timer.remaining.total_seconds() // 60)
            message += f"\nFocus timer: {remaining}m"
        if state.current_break_timer:
            remaining = int(state.current_break_timer.remaining.total_seconds() // 60)
            message += f"\nBreak timer: {remaining}m"
        self.label.setText(message)
        self.window.show()

    def run(self) -> None:
        self.window.show()
        self.app.exec()
