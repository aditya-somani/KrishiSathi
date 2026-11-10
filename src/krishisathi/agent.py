"""KrishiSathi LiveKit voice agent orchestrating Gnani STT/TTS and Gemini LLM."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from livekit.agents import Agent, AgentSession, AutoSubscribe, JobContext
from livekit.plugins import gnani, google, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from krishisathi.config import settings
from krishisathi.handlers import attach_conversation_tracker, save_session_summary
from krishisathi.languages import (
    normalize_language,
    to_gnani_stt_language,
    to_gnani_tts_language,
)
from krishisathi.prompts import build_system_instructions
from krishisathi.storage import repository
from krishisathi.tools import ALL_TOOLS
from krishisathi.utils.telephony import hangup_call

logger = logging.getLogger("krishisathi.agent")
logger.setLevel(logging.INFO)


class KrishiSathiAgent(Agent):
    """Voice assistant persona and tool definitions for Indian farmers."""

    def __init__(self, instructions: str) -> None:
        super().__init__(
            instructions=instructions,
            tools=ALL_TOOLS,
        )


def _resolve_session_languages(
    farmer_profile: dict[str, Any] | None,
) -> tuple[str, str, str]:
    """Determine canonical, Gnani STT, and Gnani TTS language codes for a caller."""
    if farmer_profile:
        preferred = normalize_language(farmer_profile.get("preferred_language"))
        return (
            preferred,
            to_gnani_stt_language(preferred),
            to_gnani_tts_language(preferred),
        )
    return (
        "english",
        settings.gnani_stt_language,
        settings.gnani_tts_language,
    )


def build_agent_session(*, stt_language: str, tts_language: str) -> AgentSession:
    """Construct an AgentSession wired with Gnani Vachana STT/TTS and Gemini LLM."""
    return AgentSession(
        stt=gnani.STT(
            language=stt_language,
            api_key=settings.gnani_api_key,
            sample_rate=settings.gnani_stt_sample_rate,
            format=settings.gnani_stt_format,
            use_streaming=True,
        ),
        llm=google.LLM(
            model=settings.gemini_llm_model,
            api_key=settings.google_api_key,
        ),
        tts=gnani.TTS(
            voice=settings.gnani_tts_voice,
            model=settings.gnani_tts_model,
            language=tts_language,
            sample_rate=settings.gnani_tts_sample_rate,
            api_key=settings.gnani_api_key,
            synthesize_method=settings.gnani_tts_method,
        ),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
        preemptive_generation=True,
    )


async def entrypoint(ctx: JobContext) -> None:
    """Handle an incoming LiveKit farmer call lifecycle."""
    logger.info("Incoming call in room: %s", ctx.room.name)
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()
    phone = participant.identity

    farmer_profile = repository.get_farmer(phone)
    session_language, stt_language, tts_language = _resolve_session_languages(farmer_profile)
    instructions = build_system_instructions(farmer_profile)

    session = build_agent_session(
        stt_language=stt_language,
        tts_language=tts_language,
    )
    session.userdata = {"phone": phone, "language": session_language}

    conversation_log: list[str] = []
    attach_conversation_tracker(session, conversation_log)

    await session.start(
        room=ctx.room,
        agent=KrishiSathiAgent(instructions=instructions),
    )
    logger.info(
        "KrishiSathi session started for %s (stt=%s, tts=%s)",
        phone,
        stt_language,
        tts_language,
    )

    await session.generate_reply(
        instructions="Greet the caller warmly according to your Greeting Behavior instructions."
    )

    async def _enforce_call_limit() -> None:
        try:
            await asyncio.sleep(settings.max_call_duration_seconds)
            logger.warning(
                "Call limit (%ss) reached for %s; closing room",
                settings.max_call_duration_seconds,
                phone,
            )
            await hangup_call(ctx.room.name)
        except asyncio.CancelledError:
            pass

    watchdog_task = asyncio.create_task(_enforce_call_limit())

    async def _on_shutdown() -> None:
        watchdog_task.cancel()
        await save_session_summary(phone, conversation_log)
        logger.info("Session cleaned up for %s", phone)

    ctx.add_shutdown_callback(_on_shutdown)
