"""Tests for SQLite FarmerRepository CRUD and summary retention."""

from pathlib import Path

from krishisathi.storage import FarmerRepository


def test_register_and_update_farmer(tmp_path: Path) -> None:
    repo = FarmerRepository(tmp_path / "test.db")
    repo.register_farmer(
        phone="+919999900000",
        name="Ramesh",
        place="Nashik",
        state="Maharashtra",
        crops="onion",
        language="mr-IN",
    )

    profile = repo.get_farmer("+919999900000")
    assert profile is not None
    assert profile["name"] == "Ramesh"
    assert profile["preferred_language"] == "marathi"

    assert repo.update_farmer_details("+919999900000", crops="onion, grapes") is True
    repo.update_language("+919999900000", "hindi")

    updated = repo.get_farmer("+919999900000")
    assert updated is not None
    assert updated["crops"] == "onion, grapes"
    assert updated["preferred_language"] == "hindi"


def test_summary_retention_keeps_only_five_most_recent(tmp_path: Path) -> None:
    repo = FarmerRepository(tmp_path / "test.db")
    phone = "+919999911111"
    repo.register_farmer(phone, "Sita", "Indore", "MP", "wheat", "hindi")

    for idx in range(7):
        repo.add_summary(phone, f"Summary {idx}")

    profile = repo.get_farmer(phone)
    assert profile is not None
    assert len(profile["history"]) == 5
    assert profile["history"][0] == "Summary 6"
    assert "Summary 0" not in profile["history"]
    assert "Summary 1" not in profile["history"]
