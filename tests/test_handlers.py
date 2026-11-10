"""Tests for conversation transcript tracking and post-call summarization."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from krishisathi.handlers import summarizer
from krishisathi.handlers.transcript import attach_conversation_tracker
from krishisathi.storage import FarmerRepository


class FakeSession:
    def __init__(self) -> None:
        self._handlers = {}

    def on(self, event_name: str):
        def decorator(fn):
            self._handlers[event_name] = fn
            return fn

        return decorator

    def emit(self, event_name: str, payload) -> None:
        self._handlers[event_name](payload)


def test_conversation_tracker_records_only_non_empty_messages() -> None:
    session = FakeSession()
    log: list[str] = []
    attach_conversation_tracker(session, log)

    session.emit(
        "conversation_item_added",
        SimpleNamespace(item=SimpleNamespace(type="function_call", role="assistant", text_content="ignored")),
    )
    session.emit(
        "conversation_item_added",
        SimpleNamespace(item=SimpleNamespace(type="message", role="user", text_content="  Gehu ke rate kya hain?  ")),
    )
    session.emit(
        "conversation_item_added",
        SimpleNamespace(item=SimpleNamespace(type="message", role="assistant", text_content="   ")),
    )

    assert log == ["user: Gehu ke rate kya hain?"]


async def test_save_session_summary_short_call_saves_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = FarmerRepository(tmp_path / "summary.db")
    repo.register_farmer("+919000000001", "Asha", "Jaipur", "Rajasthan", "mustard", "hindi")
    monkeypatch.setattr(summarizer, "repository", repo)

    result = await summarizer.save_session_summary("+919000000001", ["user: Namaste"])
    assert "Brief call" in result
    assert repo.get_farmer("+919000000001")["history"][0] == result
