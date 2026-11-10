"""Tests for environment configuration and validation."""

import pytest

from krishisathi.config import Settings


def test_validate_raises_when_required_keys_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GNANI_API_KEY", raising=False)
    monkeypatch.delenv("GNANI_API_KEYS", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY_2", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    cfg = Settings.from_env()
    with pytest.raises(ValueError, match="GNANI_API_KEY"):
        cfg.validate()


def test_validate_succeeds_with_gnani_api_keys_plural(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GNANI_API_KEY", raising=False)
    monkeypatch.setenv("GNANI_API_KEYS", "key-1, key-2")
    monkeypatch.setenv("GROQ_API_KEY", "groq-test-key")
    monkeypatch.setenv("GNANI_TTS_URL", "https://api.vachana.ai/api/v1/tts/inference")

    cfg = Settings.from_env()
    cfg.validate()
    assert cfg.gnani_api_key == "key-1"
    assert cfg.gnani_base_url == "https://api.vachana.ai"


def test_validate_succeeds_with_gnani_and_groq_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GNANI_API_KEY", "gnani-test-key")
    monkeypatch.setenv("GROQ_API_KEY", "groq-test-key")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    cfg = Settings.from_env()
    cfg.validate()


def test_search_api_keys_deduplicates_preserving_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WEB_API_KEY", "key-a")
    monkeypatch.setenv("GOOGLE_API_KEY_2", "key-b")
    monkeypatch.setenv("GOOGLE_API_KEY", "key-a")

    cfg = Settings.from_env()
    assert cfg.search_api_keys() == ["key-a", "key-b"]
