"""Tests for environment configuration and validation."""

import pytest

from krishisathi.config import Settings


def test_validate_raises_when_required_keys_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GNANI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("WEB_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY_2", raising=False)

    cfg = Settings.from_env()
    with pytest.raises(ValueError, match="GNANI_API_KEY"):
        cfg.validate()


def test_validate_succeeds_with_gnani_and_google_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GNANI_API_KEY", "gnani-test-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "google-test-key")
    monkeypatch.delenv("WEB_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY_2", raising=False)

    cfg = Settings.from_env()
    cfg.validate()
    assert cfg.search_api_keys() == ["google-test-key"]


def test_search_api_keys_deduplicates_preserving_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WEB_API_KEY", "key-a")
    monkeypatch.setenv("GOOGLE_API_KEY_2", "key-b")
    monkeypatch.setenv("GOOGLE_API_KEY", "key-a")

    cfg = Settings.from_env()
    assert cfg.search_api_keys() == ["key-a", "key-b"]
