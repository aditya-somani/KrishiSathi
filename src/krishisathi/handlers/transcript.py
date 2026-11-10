"""LiveKit session event listener for capturing spoken conversation turns."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("krishisathi.handlers.transcript")


def attach_conversation_tracker(session: Any, conversation_log: list[str]) -> None:
    """Attach a listener to record non-empty user and assistant messages."""

    @session.on("conversation_item_added")
    def on_item_added(event: Any) -> None:
        try:
            item = event.item
            if getattr(item, "type", None) != "message":
                return

            role = getattr(item, "role", "unknown")
            content = (getattr(item, "text_content", None) or "").strip()
            if content:
                conversation_log.append(f"{role}: {content}")
                logger.debug("Captured [%s]: %s", role, content[:60])
        except Exception as exc:
            logger.warning("Transcript tracker skipped event: %s", exc)
