"""Grounded agricultural web search tool powered by Gemini Google Search."""

from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime

from google import genai
from google.genai.types import GenerateContentConfig, GoogleSearch, Tool
from livekit.agents import RunContext, function_tool

from krishisathi.config import settings

logger = logging.getLogger("krishisathi.tools.search")

SEARCH_MODEL_ID = "gemini-2.5-flash"


def pick_search_api_key() -> str:
    """Select an available Gemini API key for Google Search grounding."""
    keys = settings.search_api_keys()
    if not keys:
        raise ValueError("No API keys configured for web search")
    return random.choice(keys)


def _execute_grounded_search(api_key: str, prompt: str) -> str:
    """Run synchronous Gemini Search-grounded generation (called off event loop)."""
    client = genai.Client(api_key=api_key)
    config = GenerateContentConfig(
        tools=[Tool(google_search=GoogleSearch())],
        response_modalities=["TEXT"],
        temperature=0.2,
    )
    response = client.models.generate_content(
        model=SEARCH_MODEL_ID,
        contents=prompt,
        config=config,
    )
    return (response.text or "").strip()


@function_tool()
async def web_search(
    ctx: RunContext,
    query: str,
) -> str:
    """Search live agricultural schemes, mandi prices, weather, or farming advisories.

    Args:
        query: Specific search query relevant to the farmer's question.
    """
    logger.info("Executing grounded search for: %s", query)
    user_lang = ctx.session.userdata.get("language", "english")
    today = datetime.now().strftime("%d %B %Y")

    prompt = (
        "You are an agricultural advisor for Indian farmers.\n"
        "Use Google Search to retrieve current, accurate facts and summarize them "
        "into a brief, plain-spoken, actionable answer suitable for a phone call.\n"
        f"- Respond in: {user_lang}\n"
        f"- Today's date: {today}\n"
        "- Avoid jargon, markdown formatting, and long lists.\n\n"
        f"Farmer question: {query}"
    )

    if not settings.search_api_keys():
        return "Live web search is not enabled in this session; answer using general farming knowledge."

    try:
        api_key = pick_search_api_key()
        result = await asyncio.to_thread(_execute_grounded_search, api_key, prompt)
        if not result:
            return "I could not find reliable live details right now. Please try asking again."
        return result
    except Exception as exc:
        logger.error("Grounded search failed: %s", exc)
        return "Sorry, I ran into a temporary issue checking live information. Please try again shortly."

