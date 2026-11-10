"""Telephony utilities for ending active LiveKit call rooms."""

from __future__ import annotations

import logging

from livekit import api

from krishisathi.config import settings

logger = logging.getLogger("krishisathi.utils.telephony")


async def hangup_call(room_name: str) -> None:
    """Terminate all participants in a room by deleting the LiveKit room."""
    lkapi = api.LiveKitAPI(
        settings.livekit_url,
        settings.livekit_api_key,
        settings.livekit_api_secret,
    )
    try:
        logger.info("Closing LiveKit room %s", room_name)
        await lkapi.room.delete_room(api.DeleteRoomRequest(room=room_name))
        logger.info("Room %s closed successfully", room_name)
    except Exception as exc:
        logger.error("Failed to close room %s: %s", room_name, exc)
    finally:
        await lkapi.aclose()

