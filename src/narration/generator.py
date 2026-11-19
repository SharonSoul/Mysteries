"""
ElevenLabs Documentary Narration Module.
Generates voiceovers, handles word-level timestamps, and verifies API credentials.
"""

import logging
from pathlib import Path
from typing import Any, Optional

from config.settings import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, MEDIA_LIBRARY_DIR

logger = logging.getLogger(__name__)


class ElevenLabsNarrationEngine:
    """Manages text-to-speech generation using ElevenLabs."""

    def __init__(self, api_key: str = None, default_voice_id: str = None):
        self.api_key = api_key or ELEVENLABS_API_KEY
        self.voice_id = default_voice_id or ELEVENLABS_VOICE_ID
        self._client = None

    def _get_client(self):
        if not self._client:
            if not self.api_key or self.api_key.startswith("your_"):
                raise ValueError("ELEVENLABS_API_KEY is not configured in .env.")
            from elevenlabs.client import ElevenLabs
            self._client = ElevenLabs(api_key=self.api_key)
        return self._client

    def verify_connection(self) -> dict[str, Any]:
        """Tests ElevenLabs API reachability and key validity."""
        if not self.api_key or self.api_key.startswith("your_"):
            return {
                "service": "ElevenLabs",
                "status": "missing_credentials",
                "authenticated": False,
                "message": "ELEVENLABS_API_KEY is not configured in .env."
            }

        try:
            client = self._get_client()
            # Test speech generation with configured voice
            stream = client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=".",
                model_id="eleven_multilingual_v2"
            )
            next(iter(stream))
            return {
                "service": "ElevenLabs",
                "status": "connected",
                "authenticated": True,
                "voice_id_configured": self.voice_id,
                "message": "ElevenLabs API connection and voice synthesis verified successfully."
            }
        except Exception as e:
            return {
                "service": "ElevenLabs",
                "status": "auth_failed_or_error",
                "authenticated": False,
                "message": str(e)
            }

    def generate_narration(
        self,
        text: str,
        output_file: Path,
        voice_id: Optional[str] = None,
        model_id: str = "eleven_multilingual_v2"
    ) -> Path:
        """
        Synthesizes speech audio for a scene narration text.
        """
        client = self._get_client()
        target_voice = voice_id or self.voice_id

        output_file.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Synthesizing narration for %d characters with voice %s", len(text), target_voice)

        audio_generator = client.text_to_speech.convert(
            voice_id=target_voice,
            text=text,
            model_id=model_id,
            voice_settings={
                "stability": 0.50,
                "similarity_boost": 0.80,
                "style": 0.15,
                "use_speaker_boost": True
            }
        )

        with open(output_file, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)

        logger.info("Saved narration audio to %s", output_file)
        return output_file

    def generate_narration_with_timestamps(
        self,
        text: str,
        output_file: Path,
        voice_id: Optional[str] = None,
        model_id: str = "eleven_multilingual_v2"
    ) -> dict[str, Any]:
        """
        Synthesizes speech and returns word-level timing alignment for subtitles.
        """
        client = self._get_client()
        target_voice = voice_id or self.voice_id

        output_file.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Synthesizing timestamped narration for %d characters", len(text))

        response = client.text_to_speech.convert_with_timestamps(
            voice_id=target_voice,
            text=text,
            model_id=model_id
        )

        with open(output_file, "wb") as f:
            f.write(response.audio_base64_decoded)

        # alignment dict contains characters and start/end timecodes
        alignment = getattr(response, "alignment", {})
        return {
            "audio_file": str(output_file),
            "alignment": alignment
        }
