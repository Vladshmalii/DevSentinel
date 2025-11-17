"""Glue code that stitches modules together for manual experiments."""
from __future__ import annotations

from datetime import datetime
from time import sleep

from .audio.listener import AudioConfig, AudioListener, CommandParser, DummySTT
from .speech.tts import VoiceAssistant
from .state.engine import EngineConfig, StateEngine
from .states import SpeechSegment
from .storage.database import Storage, StorageConfig
from .vision.analyzer import VisionAnalyzer, VisionConfig


class DevSentinelApp:
    def __init__(self) -> None:
        self.engine = StateEngine(config=EngineConfig())
        self.storage = Storage(StorageConfig())
        self.voice = VoiceAssistant()
        self.vision = VisionAnalyzer(VisionConfig())
        self.audio = AudioListener(AudioConfig(), DummySTT([]))
        self.parser = CommandParser()

    def run_once(self) -> None:
        vision_state = None
        audio_state = None
        try:
            vision_state = self.vision.read_state()
        except Exception:
            pass
        try:
            audio_state = self.audio.audio_state()
        except Exception:
            pass
        state = self.engine.update(vision_state, audio_state)
        print(state)

    def handle_segment(self, text: str) -> None:
        segment = SpeechSegment(text=text, timestamp=datetime.utcnow())
        command = self.parser.parse(segment)
        if command:
            self.engine.handle_command(command)
            if command.type.name.endswith("NOTE") and command.content:
                self.storage.save_note(command.content)
            elif command.duration_minutes:
                self.storage.save_session(command.type.value, command.duration_minutes)
            self.voice.speak(f"Команда {command.type.value} принята.")


def main() -> None:  # pragma: no cover
    app = DevSentinelApp()
    app.vision.start()
    try:
        while True:
            app.run_once()
            sleep(1.0)
    finally:
        app.vision.stop()


if __name__ == "__main__":  # pragma: no cover
    main()
