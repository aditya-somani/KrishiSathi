"""Farmer profile registration and preference management tools."""

from __future__ import annotations

import logging

from livekit.agents import RunContext, function_tool

from krishisathi.storage import repository
from krishisathi.tools.language import sync_session_language

logger = logging.getLogger("krishisathi.tools.farmer")


@function_tool()
async def register_farmer(
    context: RunContext,
    name: str,
    place: str,
    state: str,
    crops: str,
    language: str = "hindi",
) -> str:
    """Register a farmer profile in persistent storage for personalized calls.

    Args:
        name: Full name of the farmer (e.g., "Ramesh Kumar").
        place: Village or town name (e.g., "Nashik").
        state: Indian state name (e.g., "Maharashtra").
        crops: Comma-separated main crops grown (e.g., "onion, grapes").
        language: Preferred language (e.g., "hindi", "marathi", "english").
    """
    phone = context.session.userdata["phone"]
    canonical_lang = sync_session_language(context.session, language, persist=False)
    repository.register_farmer(phone, name, place, state, crops, canonical_lang)
    logger.info("Registered farmer %s (%s) in %s, %s", name, phone, place, state)
    return (
        f"Registration saved for {name} ji from {place}, {state}. "
        f"Preferred language is set to {canonical_lang}."
    )


@function_tool()
async def update_language_preference(
    context: RunContext,
    language: str,
) -> str:
    """Update the farmer's preferred language mid-call when requested.

    Args:
        language: Requested language (e.g., "hindi", "kannada", "english").
    """
    canonical_lang = sync_session_language(context.session, language, persist=True)
    return f"Understood. Switched active language to {canonical_lang}."


@function_tool()
async def update_farmer_profile(
    context: RunContext,
    name: str | None = None,
    place: str | None = None,
    state: str | None = None,
    crops: str | None = None,
) -> str:
    """Update specific fields of an existing farmer's profile.

    Args:
        name: Updated farmer name, if provided.
        place: Updated village or city, if provided.
        state: Updated state, if provided.
        crops: Updated comma-separated crops list, if provided.
    """
    phone = context.session.userdata["phone"]
    updated = repository.update_farmer_details(
        phone,
        name=name,
        place=place,
        state=state,
        crops=crops,
    )
    if not updated:
        return "No existing profile found to update, or no new details were provided."
    return "Farmer profile details updated successfully."

