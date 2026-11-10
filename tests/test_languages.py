"""Tests for Indian language normalization and Gnani BCP-47 mapping."""

from krishisathi.languages import (
    normalize_language,
    to_gnani_stt_language,
    to_gnani_tts_language,
)


def test_normalize_language_handles_aliases_and_codes() -> None:
    assert normalize_language("Hindi") == "hindi"
    assert normalize_language("hi-IN") == "hindi"
    assert normalize_language("bangla") == "bengali"
    assert normalize_language("mr") == "marathi"
    assert normalize_language("en-IN,hi-IN") == "hinglish"
    assert normalize_language(None) == "english"


def test_gnani_stt_and_tts_locale_mappings() -> None:
    assert to_gnani_stt_language("kannada") == "kn-IN"
    assert to_gnani_tts_language("kannada") == "kn-IN"
    assert to_gnani_stt_language("hinglish") == "en-IN,hi-IN"
    assert to_gnani_tts_language("hinglish") == "auto"
    assert to_gnani_stt_language("tamil") == "ta-IN"
    assert to_gnani_tts_language("marathi") == "mr-IN"

