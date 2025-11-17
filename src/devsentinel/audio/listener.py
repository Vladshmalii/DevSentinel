"""Audio capture + basic sentiment stub."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

try:  # pragma: no cover
    import sounddevice as sd  # type: ignore
except Exception:  # pragma: no cover
    sd = None  # type: ignore

from ..states import AudioState, Command, CommandType, SpeechSegment


@dataclass(slots=True)
class AudioConfig:
    sample_rate: int = 16000
    block_size: int = 2048


class AudioListener:
    """Streams microphone audio and emits transcripts via an injected STT backend."""

    def __init__(self, config: AudioConfig, stt_backend: "SpeechToText"):
        self.config = config
        self._stt = stt_backend

    def listen(self) -> Iterable[SpeechSegment]:
        """Generator that yields speech segments as soon as they are decoded."""

        for text in self._stt.stream_transcripts():
            yield SpeechSegment(text=text, timestamp=datetime.utcnow())

    def audio_state(self) -> AudioState:
        """Placeholder heuristics based on backend confidence."""

        confidence = self._stt.last_confidence
        return AudioState(
            angry=max(0.0, 1.0 - confidence),
            tired=0.2,
            calm=confidence,
            excited=max(0.0, confidence - 0.5),
        )


class SpeechToText:
    """Minimal protocol for Whisper/Vosk wrappers."""

    last_confidence: float = 0.5

    def stream_transcripts(self) -> Iterable[str]:  # pragma: no cover - interface only
        raise NotImplementedError


class DummySTT(SpeechToText):
    """Development stub that yields canned phrases from the spec."""

    def __init__(self, phrases: Iterable[str]):
        self._phrases = list(phrases)

    def stream_transcripts(self) -> Iterable[str]:
        for phrase in self._phrases:
            self.last_confidence = 0.9
            yield phrase


class CommandParser:
    """Simple keyword driven parser for MVP commands."""

    def parse(self, segment: SpeechSegment) -> Command | None:
        text = segment.text.lower().strip()
        if text.startswith("фокус"):
            duration = self._extract_minutes(text)
            return Command(type=CommandType.FOCUS, duration_minutes=duration)
        if text.startswith("перер") or text.startswith("break"):
            duration = self._extract_minutes(text)
            return Command(type=CommandType.BREAK, duration_minutes=duration)
        if text.startswith("запиши заметку"):
            content = text.split(":", 1)[-1].strip()
            return Command(type=CommandType.NOTE, content=content)
        return None

    def _extract_minutes(self, text: str) -> int:
        for token in text.split():
            if token.isdigit():
                return int(token)
        return 25
