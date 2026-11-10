"""Session language detection and Gnani TTS synchronization tool."""

from __future__ import annotations

import logging
from typing import Any

from livekit.agents import RunContext, function_tool

from krishisathi.languages import normalize_language, to_gnani_tts_language
from krishisathi.storage import repository

logger = logging.getLogger("krishisathi.tools.language")


def sync_session_language(
    session: Any,
    language: str,
    *,
    persist: bool = True,
) -> str:
    """Sync active session language, DB preference, and Gnani TTS locale."""
    canonical = normalize_language(language)
    userdata = getattr(session, "userdata", None)
    if isinstance(userdata, dict):
        userdata["language"] = canonical
        phone = userdata.get("phone")
    else:
        phone = None

    if persist and phone:
        try:
            repository.update_language(phone, canonical)
        except Exception as exc:
            logger.error("Failed to persist language %s for %s: %s", canonical, phone, exc)

    tts_engine = getattr(session, "tts", None)
    if tts_engine is not None and hasattr(tts_engine, "update_options"):
        tts_locale = to_gnani_tts_language(canonical)
        try:
            tts_engine.update_options(language=tts_locale)
            logger.info("Updated Gnani TTS language option to %s", tts_locale)
        except Exception as exc:
            logger.warning("Could not update TTS language to %s: %s", tts_locale, exc)

    return canonical


@function_tool()
async def detect_language(
    context: RunContext,
    detected_language: str,
) -> str:
    """Set the active conversation language ONLY when the farmer explicitly speaks another regional language or asks to switch.
    Do NOT call this for mixed English loan words like 'rate', 'price', 'mandi', 'spray', 'weather'.

    Args:
        detected_language: Language spoken by the farmer (e.g., "hindi", "marathi", "tamil", "kannada").
    """
    requested = normalize_language(detected_language)
    current = "hindi"
    if hasattr(context, "session") and hasattr(context.session, "userdata"):
        current = context.session.userdata.get("language", "hindi")

    # Guard: prevent accidental flip to English when farmer speaks Hindi with English loanwords
    if current == "hindi" and requested == "english":
        logger.info("Retaining Hindi mode despite English loanword detection")
        return "Continuing conversation in Hindi."

    canonical = sync_session_language(context.session, requested, persist=True)
    logger.info("Detected language set to %s", canonical)
    return f"Language set to {canonical}. Continue responding in {canonical}."

