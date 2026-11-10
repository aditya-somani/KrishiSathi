"""Agent tool registry for KrishiSathi."""

from krishisathi.tools.farmer import (
    register_farmer,
    update_farmer_profile,
    update_language_preference,
)
from krishisathi.tools.language import detect_language
from krishisathi.tools.search import web_search

ALL_TOOLS = [
    register_farmer,
    update_language_preference,
    update_farmer_profile,
    web_search,
    detect_language,
]

__all__ = [
    "ALL_TOOLS",
    "detect_language",
    "register_farmer",
    "update_farmer_profile",
    "update_language_preference",
    "web_search",
]

