"""Vision module placeholder that wires OpenCV + PyTorch once models are available."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

try:  # pragma: no cover - optional dependency during early scaffolding
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore

from ..states import Mood, VisionState


@dataclass(slots=True)
class VisionConfig:
    camera_index: int = 0
    frame_width: int = 640
    frame_height: int = 480
    inference_interval_s: float = 0.5


class VisionAnalyzer:
    """Continuously grabs frames and estimates basic attention metrics."""

    def __init__(self, config: VisionConfig):
        self.config = config
        self._capture: Optional["cv2.VideoCapture"] = None

    def start(self) -> None:
        if cv2 is None:
            raise RuntimeError("OpenCV is not available in this environment")
        self._capture = cv2.VideoCapture(self.config.camera_index)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.frame_width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.frame_height)

    def stop(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def read_state(self) -> VisionState:
        if self._capture is None:
            raise RuntimeError("VisionAnalyzer must be started before reading state")
        ok, frame = self._capture.read()
        if not ok or frame is None:
            raise RuntimeError("Failed to grab frame from camera")

        metrics = self._dummy_model(frame)
        return VisionState(
            present=True,
            attention=metrics["attention"],
            fatigue=metrics["fatigue"],
            stress=metrics["stress"],
            mood=metrics["mood"],
        )

    def _dummy_model(self, frame: np.ndarray) -> dict[str, float | Mood]:
        """Temporary heuristic until the real model is wired in."""

        brightness = float(np.mean(frame) / 255.0)
        attention = min(max(brightness, 0.0), 1.0)
        fatigue = 1.0 - attention
        stress = abs(0.5 - attention)
        mood = Mood.FOCUSED if attention > 0.6 else Mood.TIRED
        return {
            "attention": attention,
            "fatigue": fatigue,
            "stress": stress,
            "mood": mood,
        }
