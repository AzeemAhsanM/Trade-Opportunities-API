"""
Input validation for sector names.
"""

import re
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# Allowed characters in a sector name
_SECTOR_RE = re.compile(r"^[a-zA-Z0-9\s\-&/]{2,60}$")

# Curated list of well-known Indian sectors (informational — not a whitelist)
KNOWN_SECTORS = [
    "agriculture",
    "automobiles",
    "aviation",
    "chemicals",
    "construction",
    "defence",
    "education",
    "electronics",
    "energy",
    "fintech",
    "food processing",
    "gems and jewellery",
    "healthcare",
    "information technology",
    "infrastructure",
    "logistics",
    "manufacturing",
    "media",
    "mining",
    "pharmaceuticals",
    "real estate",
    "renewable energy",
    "retail",
    "shipping",
    "steel",
    "telecommunications",
    "textiles",
    "tourism",
    "water",
]


def validate_sector(sector: str) -> str:

    cleaned = sector.strip().lower()

    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Invalid sector",
                "message": "Sector name cannot be empty.",
            },
        )

    if not _SECTOR_RE.match(sector.strip()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Invalid sector name",
                "message": (
                    "Sector names may only contain letters, numbers, spaces, hyphens, "
                    "ampersands, and forward slashes (2-60 characters)."
                ),
                "examples": ["pharmaceuticals", "information technology", "food processing"],
            },
        )

    logger.debug(f"Sector validated: '{cleaned}'")
    return cleaned
