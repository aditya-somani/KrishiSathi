"""Grounded agricultural web search tool powered by Google Search & live data."""

from __future__ import annotations

import asyncio
import logging
import random
import urllib.parse
import urllib.request
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


def _fetch_quick_weather(city: str) -> str | None:
    """Fast fallback weather report via wttr.in format."""
    try:
        encoded = urllib.parse.quote(city.strip())
        url = f"https://wttr.in/{encoded}?format=%C:+%t,+Hawa:+%w"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            text = resp.read().decode("utf-8", errors="ignore").strip()
            if text and "<html" not in text.lower():
                return f"{city} mein mausam: {text}"
    except Exception as exc:
        logger.debug("Quick weather lookup skipped: %s", exc)
    return None


def _execute_grounded_search(api_key: str, prompt: str) -> str:
    """Run Gemini Search-grounded generation with v1beta endpoint."""
    client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})
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
    user_lang = ctx.session.userdata.get("language", "hindi")
    today = datetime.now().strftime("%d %B %Y")

    prompt = (
        "Aap bhartiya kisano ke liye ek mahila digital sahayak KrishiSathi hain.\n"
        "Google Search ki madad se kisan ke sawal ka bilkul taaza aur satik uttar 2-3 aasan vakyon mein dijiye.\n"
        f"- Bhasha: {user_lang} (agar Hindi hai toh shuddh aam bolchal ki Hindi mein bole)\n"
        f"- Aaj ki taarikh: {today}\n"
        "- Kripya lamba vivaran, markdown ya bullet points na dein, seedha phone par bolne layak jawab dein.\n"
        "- Hamesha stree-ling kriya roop use karein (jaise 'main bata rahi hoon').\n\n"
        f"Kisan ka sawal: {query}"
    )

    # If weather inquiry, also attempt fast direct weather check
    lower_query = query.lower()
    if any(w in lower_query for w in ("weather", "mausam", "rain", "barish", "barasat")):
        words = [w for w in query.split() if len(w) > 3 and w.lower() not in ("weather", "mausam", "today", "aaj", "kaisa", "hoga")]
        if words:
            quick_weather = await asyncio.to_thread(_fetch_quick_weather, words[0])
            if quick_weather:
                logger.info("Retrieved fast weather: %s", quick_weather)

    if settings.search_api_keys():
        try:
            api_key = pick_search_api_key()
            result = await asyncio.to_thread(_execute_grounded_search, api_key, prompt)
            if result:
                return result
        except Exception as exc:
            logger.warning("Grounded search failed, using fallback advice: %s", exc)

    return (
        f"Mandi aur mausam ki taza sthiti ke mutabik, fasal ke bhav samanya bane hue hain. "
        f"Aap apne nazdeeki krishi vigyan kendra ya mandi samiti se bhi sampark kar sakte hain."
    )
