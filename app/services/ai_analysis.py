"""
AI analysis service — uses Google Gemini to generate structured trade reports
"""

import logging
from datetime import datetime
from typing import List

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/{model}:generateContent?key={key}"
)


class ConfigurationError(Exception):
    pass


class GeminiAnalysisError(Exception):
    pass


# Prompt builder

def _build_prompt(sector: str, snippets: List[str]) -> str:
    today = datetime.utcnow().strftime("%B %d, %Y")

    limited_snippets = snippets[:5]
    context_block = "\n".join(f"- {s[:200]}" for s in limited_snippets)

    return f"""
You are a financial analyst specializing in Indian markets.

Analyze the {sector} sector in India using the data below.

STRICT RULES:
- Output MUST be valid markdown
- Keep response under 300 words
- Be concise and actionable

FORMAT:

# Sector Analysis: {sector}

## Overview
...

## Key Trends
...

## Trade Opportunities
...

## Risks
...

## Sources
- Based on recent market data

DATA:
{context_block}
"""


# Gemini API call

async def analyze_sector(sector: str, snippets: List[str]) -> dict:
    if not settings.GEMINI_API_KEY:
        raise ConfigurationError(
            "GEMINI_API_KEY is not configured. "
            "Add it to your .env file and restart the server."
        )

    prompt = _build_prompt(sector, snippets)

    url = GEMINI_API_URL.format(
        model=settings.GEMINI_MODEL,
        key=settings.GEMINI_API_KEY,
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 800,
        },
    }

    logger.info(f"Calling Gemini ({settings.GEMINI_MODEL}) for sector '{sector}'...")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            raw = resp.json()

    except httpx.HTTPStatusError as exc:
        logger.error(
            f"Gemini HTTP error: {exc.response.status_code} — {exc.response.text[:200]}"
        )
        raise GeminiAnalysisError(
            f"Gemini API returned {exc.response.status_code}"
        )

    except httpx.RequestError as exc:
        logger.error(f"Gemini request error: {exc}")
        raise GeminiAnalysisError(f"Could not reach Gemini API: {exc}")

    # Extract markdown text
    try:
        text = raw["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as exc:
        logger.error(f"Unexpected Gemini response structure: {raw}")
        raise GeminiAnalysisError("Invalid Gemini response format")

    logger.info(f"Gemini analysis complete for sector '{sector}'")

    return {
        "summary": f"AI-generated analysis for {sector}",
        "report": text.strip(),
        "opportunities": [],  
        "market_metrics": {}, 
    }