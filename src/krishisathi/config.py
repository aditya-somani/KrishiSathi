"""Application settings and startup validation for KrishiSathi."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Centralized runtime configuration loaded from environment variables."""

    # LiveKit (injected automatically in LiveKit Cloud deployments)
    livekit_url: str | None = os.getenv("LIVEKIT_URL")
    livekit_api_key: str | None = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret: str | None = os.getenv("LIVEKIT_API_SECRET")

    # Gnani.ai Vachana Speech AI (STT + TTS)
    gnani_api_key: str | None = os.getenv("GNANI_API_KEY")
    gnani_stt_language: str = os.getenv("GNANI_STT_LANGUAGE", "en-IN,hi-IN")
    gnani_stt_sample_rate: int = int(os.getenv("GNANI_STT_SAMPLE_RATE", "16000"))
    gnani_stt_format: str = os.getenv("GNANI_STT_FORMAT", "transcribe")
    gnani_tts_model: str = os.getenv("GNANI_TTS_MODEL", "timbre-v2.5")
    gnani_tts_voice: str = os.getenv("GNANI_TTS_VOICE", "Nalini")
    gnani_tts_language: str = os.getenv("GNANI_TTS_LANGUAGE", "auto")
    gnani_tts_method: str = os.getenv("GNANI_TTS_METHOD", "websocket")
    gnani_tts_sample_rate: int = int(os.getenv("GNANI_TTS_SAMPLE_RATE", "16000"))

    # LLM & Search Grounding
    google_api_key: str | None = os.getenv("GOOGLE_API_KEY")
    google_api_key_2: str | None = os.getenv("GOOGLE_API_KEY_2")
    web_api_key: str | None = os.getenv("WEB_API_KEY")
    gemini_llm_model: str = os.getenv("GEMINI_LLM_MODEL", "gemini-2.5-flash")

    # Optional Groq fast summarizer
    groq_api_key: str | None = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY_2")

    # Persistence & Session Guardrails
    db_path: str = os.getenv("KRISHISATHI_DB_PATH", "data/krishisathi.db")
    max_call_duration_seconds: int = int(os.getenv("MAX_CALL_DURATION_SECONDS", "240"))

    @classmethod
    def from_env(cls) -> Settings:
        """Build a fresh Settings snapshot from the current process environment."""
        return cls(
            livekit_url=os.getenv("LIVEKIT_URL"),
            livekit_api_key=os.getenv("LIVEKIT_API_KEY"),
            livekit_api_secret=os.getenv("LIVEKIT_API_SECRET"),
            gnani_api_key=os.getenv("GNANI_API_KEY"),
            gnani_stt_language=os.getenv("GNANI_STT_LANGUAGE", "en-IN,hi-IN"),
            gnani_stt_sample_rate=int(os.getenv("GNANI_STT_SAMPLE_RATE", "16000")),
            gnani_stt_format=os.getenv("GNANI_STT_FORMAT", "transcribe"),
            gnani_tts_model=os.getenv("GNANI_TTS_MODEL", "timbre-v2.5"),
            gnani_tts_voice=os.getenv("GNANI_TTS_VOICE", "Nalini"),
            gnani_tts_language=os.getenv("GNANI_TTS_LANGUAGE", "auto"),
            gnani_tts_method=os.getenv("GNANI_TTS_METHOD", "websocket"),
            gnani_tts_sample_rate=int(os.getenv("GNANI_TTS_SAMPLE_RATE", "16000")),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            google_api_key_2=os.getenv("GOOGLE_API_KEY_2"),
            web_api_key=os.getenv("WEB_API_KEY"),
            gemini_llm_model=os.getenv("GEMINI_LLM_MODEL", "gemini-2.5-flash"),
            groq_api_key=os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY_2"),
            db_path=os.getenv("KRISHISATHI_DB_PATH", "data/krishisathi.db"),
            max_call_duration_seconds=int(os.getenv("MAX_CALL_DURATION_SECONDS", "240")),
        )

    def search_api_keys(self) -> list[str]:
        """Return available Gemini API keys usable for Google Search grounding."""
        candidates = [self.web_api_key, self.google_api_key_2, self.google_api_key]
        # Preserve order while deduplicating non-empty keys
        seen: set[str] = set()
        keys: list[str] = []
        for key in candidates:
            if key and key not in seen:
                seen.add(key)
                keys.append(key)
        return keys

    def validate(self) -> None:
        """Fail fast at worker startup if mandatory credentials are missing."""
        missing: list[str] = []
        if not self.gnani_api_key:
            missing.append("GNANI_API_KEY")
        if not self.google_api_key:
            missing.append("GOOGLE_API_KEY")
        if not self.search_api_keys():
            missing.append("WEB_API_KEY (or GOOGLE_API_KEY)")

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )


settings = Settings()
