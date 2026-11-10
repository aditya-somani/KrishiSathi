"""Tests for KrishiSathi prompt construction and persona rules."""

from krishisathi.prompts import BASE_SYSTEM_PROMPT, build_system_instructions


def test_base_prompt_contains_no_cartesia_emotion_tags() -> None:
    assert "<emotion" not in BASE_SYSTEM_PROMPT
    assert "KrishiSathi" in BASE_SYSTEM_PROMPT


def test_build_system_instructions_for_new_caller() -> None:
    instructions = build_system_instructions(None)
    assert "New caller" in instructions
    assert "Returning Farmer Context" not in instructions


def test_build_system_instructions_for_returning_farmer() -> None:
    profile = {
        "name": "Suresh",
        "place": "Satara",
        "state": "Maharashtra",
        "crops": "soybean, jowar",
        "preferred_language": "marathi",
        "history": ["Asked about soybean rust", "Checked Satara rain forecast"],
    }

    instructions = build_system_instructions(profile)
    assert "Returning Farmer Context" in instructions
    assert "Suresh" in instructions
    assert "Satara" in instructions
    assert "soybean, jowar" in instructions
    assert "marathi" in instructions
    assert "Asked about soybean rust" in instructions
