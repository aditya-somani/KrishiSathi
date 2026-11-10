"""Tests for agent tools and Gnani STT/TTS session construction."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from krishisathi import agent as agent_module
from krishisathi.storage import FarmerRepository
from krishisathi.tools import farmer as farmer_tools
from krishisathi.tools import language as language_tools


@pytest.fixture()
def temp_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> FarmerRepository:
    repo = FarmerRepository(tmp_path / "tools.db")
    monkeypatch.setattr(language_tools, "repository", repo)
    monkeypatch.setattr(farmer_tools, "repository", repo)
    return repo


async def test_detect_language_syncs_session_db_and_gnani_tts(temp_repo: FarmerRepository) -> None:
    phone = "+919876543210"
    temp_repo.register_farmer(phone, "Kiran", "Pune", "Maharashtra", "sugarcane", "english")

    mock_tts = MagicMock()
    session = SimpleNamespace(userdata={"phone": phone, "language": "english"}, tts=mock_tts)
    ctx = SimpleNamespace(session=session)

    reply = await language_tools.detect_language(ctx, "Marathi")

    assert "marathi" in reply.lower()
    assert session.userdata["language"] == "marathi"
    mock_tts.update_options.assert_called_once_with(language="mr-IN")
    assert temp_repo.get_farmer(phone)["preferred_language"] == "marathi"


async def test_register_and_update_farmer_tools(temp_repo: FarmerRepository) -> None:
    phone = "+919111122222"
    mock_tts = MagicMock()
    session = SimpleNamespace(userdata={"phone": phone, "language": "english"}, tts=mock_tts)
    ctx = SimpleNamespace(session=session)

    res = await farmer_tools.register_farmer(
        ctx,
        name="Mahesh",
        place="Mysuru",
        state="Karnataka",
        crops="ragi",
        language="kannada",
    )
    assert "Mahesh" in res
    assert session.userdata["language"] == "kannada"
    mock_tts.update_options.assert_called_once_with(language="kn-IN")

    update_res = await farmer_tools.update_farmer_profile(ctx, crops="ragi, paddy")
    assert "updated successfully" in update_res.lower()
    assert temp_repo.get_farmer(phone)["crops"] == "ragi, paddy"


def test_build_agent_session_wires_gnani_stt_and_tts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(agent_module.settings, "gnani_api_key", "gnani-key")
    monkeypatch.setattr(agent_module.settings, "google_api_key", "google-key")

    mock_stt = MagicMock()
    mock_tts = MagicMock()
    mock_llm = MagicMock()
    mock_vad = MagicMock()
    mock_turn = MagicMock()
    mock_session_cls = MagicMock()

    monkeypatch.setattr(agent_module.gnani, "STT", mock_stt)
    monkeypatch.setattr(agent_module.gnani, "TTS", mock_tts)
    monkeypatch.setattr(agent_module.google, "LLM", mock_llm)
    monkeypatch.setattr(agent_module.silero.VAD, "load", MagicMock(return_value=mock_vad))
    monkeypatch.setattr(agent_module, "MultilingualModel", MagicMock(return_value=mock_turn))
    monkeypatch.setattr(agent_module, "AgentSession", mock_session_cls)

    agent_module.build_agent_session(stt_language="hi-IN", tts_language="hi-IN")

    mock_stt.assert_called_once()
    assert mock_stt.call_args.kwargs["language"] == "hi-IN"
    assert mock_stt.call_args.kwargs["use_streaming"] is True

    mock_tts.assert_called_once()
    assert mock_tts.call_args.kwargs["language"] == "hi-IN"
    assert mock_tts.call_args.kwargs["model"] == "timbre-v2.5"
    assert mock_tts.call_args.kwargs["synthesize_method"] == "websocket"
