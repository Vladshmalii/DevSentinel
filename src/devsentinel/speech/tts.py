"""Local TTS wrapper."""
from __future__ import annotations

try:  # pragma: no cover
    import pyttsx3
except Exception:  # pragma: no cover
    pyttsx3 = None  # type: ignore


class VoiceAssistant:
    def __init__(self):
        if pyttsx3 is None:
            raise RuntimeError("pyttsx3 is not installed")
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 185)

    def speak(self, text: str) -> None:
        self.engine.say(text)
        self.engine.runAndWait()
