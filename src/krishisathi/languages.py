"""Indian language registry and BCP-47 mapping for Gnani Vachana STT/TTS."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageSpec:
    """Normalized language specification for Gnani STT and Timbre TTS."""

    canonical_name: str
    display_name: str
    stt_code: str
    tts_code: str


SUPPORTED_LANGUAGES: dict[str, LanguageSpec] = {
    "hindi": LanguageSpec("hindi", "Hindi", "hi-IN", "hi-IN"),
    "english": LanguageSpec("english", "English", "en-IN", "en-IN"),
    "hinglish": LanguageSpec("hinglish", "Hinglish", "en-IN,hi-IN", "auto"),
    "bengali": LanguageSpec("bengali", "Bengali", "bn-IN", "bn-IN"),
    "gujarati": LanguageSpec("gujarati", "Gujarati", "gu-IN", "gu-IN"),
    "kannada": LanguageSpec("kannada", "Kannada", "kn-IN", "kn-IN"),
    "malayalam": LanguageSpec("malayalam", "Malayalam", "ml-IN", "ml-IN"),
    "marathi": LanguageSpec("marathi", "Marathi", "mr-IN", "mr-IN"),
    "punjabi": LanguageSpec("punjabi", "Punjabi", "pa-IN", "pa-IN"),
    "tamil": LanguageSpec("tamil", "Tamil", "ta-IN", "ta-IN"),
    "telugu": LanguageSpec("telugu", "Telugu", "te-IN", "te-IN"),
}

_ALIASES: dict[str, str] = {
    "hi": "hindi",
    "hi-in": "hindi",
    "en": "english",
    "en-in": "english",
    "en-us": "english",
    "en-in,hi-in": "hinglish",
    "bn": "bengali",
    "bn-in": "bengali",
    "bangla": "bengali",
    "gu": "gujarati",
    "gu-in": "gujarati",
    "kn": "kannada",
    "kn-in": "kannada",
    "ml": "malayalam",
    "ml-in": "malayalam",
    "mr": "marathi",
    "mr-in": "marathi",
    "pa": "punjabi",
    "pa-in": "punjabi",
    "panjabi": "punjabi",
    "ta": "tamil",
    "ta-in": "tamil",
    "te": "telugu",
    "te-in": "telugu",
}


def normalize_language(language: str | None) -> str:
    """Normalize any user/LLM language label or locale code to a canonical key."""
    if not language:
        return "english"
    cleaned = language.strip().lower()
    if cleaned in SUPPORTED_LANGUAGES:
        return cleaned
    return _ALIASES.get(cleaned, cleaned)


def resolve_language_spec(language: str | None) -> LanguageSpec:
    """Resolve a language name or locale code into a Gnani LanguageSpec."""
    canonical = normalize_language(language)
    return SUPPORTED_LANGUAGES.get(
        canonical,
        LanguageSpec(canonical, canonical.title(), "en-IN,hi-IN", "auto"),
    )


def to_gnani_tts_language(language: str | None) -> str:
    """Return the Gnani Timbre v2.5 language code for a given language."""
    return resolve_language_spec(language).tts_code


def to_gnani_stt_language(language: str | None) -> str:
    """Return the Gnani Prisma STT language code for a given language."""
    return resolve_language_spec(language).stt_code

