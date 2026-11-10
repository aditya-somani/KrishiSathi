"""Post-call conversation summarizer with Groq primary and Gemini fallback."""

from __future__ import annotations

import logging
from datetime import datetime

from livekit.agents import llm
from livekit.plugins import google
from livekit.plugins import openai as lk_openai

from krishisathi.config import settings
from krishisathi.storage import repository

logger = logging.getLogger("krishisathi.handlers.summarizer")


def _build_summarizer_llm():
    """Choose the lightest configured LLM client for post-call summarization."""
    if settings.groq_api_key:
        return lk_openai.LLM(
            model="llama-3.1-8b-instant",
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
            temperature=0.2,
        )
    if settings.google_api_key:
        return google.LLM(
            model=settings.gemini_llm_model,
            api_key=settings.google_api_key,
            temperature=0.2,
        )
    return None


def _format_summary_prompt(conversation_log: list[str]) -> str:
    transcript = "\n".join(conversation_log[-20:])
    return (
        "Summarize this farmer phone call in 10 words or fewer, strictly based on "
        "what was actually said. Do not invent requests or topics.\n"
        'If the caller only greeted and hung up, reply: "Brief greeting only".\n'
        "Output ONLY the short summary.\n\n"
        f"Conversation:\n{transcript}\n\n"
        "Summary:"
    )


async def save_session_summary(phone: str, conversation_log: list[str]) -> str:
    """Generate and persist a concise summary for the completed call."""
    if not conversation_log or len(conversation_log) < 2:
        summary = "Brief call, no significant interaction"
        repository.add_summary(phone, summary)
        return summary

    llm_client = _build_summarizer_llm()
    if llm_client is None:
        fallback = f"Call on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        repository.add_summary(phone, fallback)
        return fallback

    try:
        chat_ctx = llm.ChatContext()
        chat_ctx.add_message(role="user", content=_format_summary_prompt(conversation_log))

        parts: list[str] = []
        async with llm_client.chat(chat_ctx=chat_ctx) as stream:
            async for chunk in stream:
                if chunk.delta and chunk.delta.content:
                    parts.append(chunk.delta.content)

        summary = "".join(parts).strip().strip('"').strip("'").rstrip(".")
        if not summary:
            summary = f"Call on {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        repository.add_summary(phone, summary)
        logger.info("Saved call summary for %s: %s", phone, summary)
        return summary
    except Exception as exc:
        logger.error("Call summarization failed for %s: %s", phone, exc)
        fallback = f"Call on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        repository.add_summary(phone, fallback)
        return fallback
