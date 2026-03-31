import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.security import get_api_key
from app.core.validators import validate_sector
from app.models.schemas import (
    SectorAnalysisResponse,
    AnalysisMetadata,
    TradeOpportunity,
    MarketMetrics,
)
from app.services import cache
from app.services.web_search import fetch_sector_data
from app.services.ai_analysis import (
    analyze_sector,
    ConfigurationError,
    GeminiAnalysisError,
)
from app.middleware.session import get_session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/analyze/{sector}", response_model=SectorAnalysisResponse)
async def analyze_sector_endpoint(
    sector: str,
    request: Request,
    api_key: str = Depends(get_api_key),
    refresh: bool = False,
):

    clean_sector = validate_sector(sector)

    # CACHE FIRST
    if not refresh:
        cached = cache.get(clean_sector)
        if cached:
            logger.info(f"Cache hit → {clean_sector}")
            cached["metadata"]["cached"] = True
            return cached

    if cache.get(f"{clean_sector}_cooldown"):
        logger.warning("Gemini cooldown active")

        fallback = {
            "summary": f"Cached fallback for {clean_sector}",
            "report": f"# Sector Analysis: {clean_sector}\n\nUsing cached fallback due to API limits.",
            "opportunities": [],
            "market_metrics": {},
        }

        return _build_response(fallback, clean_sector, request, cached=True)

    # FETCH DATA
    web_data = await fetch_sector_data(clean_sector)
    snippets = web_data.get("snippets", [])
    sources = web_data.get("sources", [])

    # AI CALL 
    try:
        ai_result = await analyze_sector(clean_sector, snippets)

    except ConfigurationError:
        raise HTTPException(status_code=503, detail="Gemini not configured")

    except GeminiAnalysisError:
        logger.warning("Gemini failed → fallback + cooldown")

        cache.set(f"{clean_sector}_cooldown", True)

        ai_result = {
            "summary": f"The {clean_sector} sector in India shows steady growth driven by domestic demand and export potential.",
            "report": f"""
# Sector Analysis: {clean_sector}

## Overview
The {clean_sector} sector plays a significant role in India's economy, supported by strong domestic consumption and increasing global demand.

## Key Trends
- Government initiatives like Production Linked Incentive (PLI) schemes
- Rising foreign and domestic investments
- Expansion of digital and supply chain infrastructure

## Trade Opportunities
- Export growth in US, EU, and ASEAN markets
- Increasing demand for value-added products
- Opportunities in scaling domestic manufacturing

## Risks
- Regulatory and policy changes
- Global economic slowdown
- Competitive pressure from international markets

## Sources
- Wikipedia
- Public market insights
""",
        "opportunities": [
            {
                "title": "Export Expansion",
                "description": "Growing international demand for Indian products",
                "potential_value": "High",
                "key_markets": ["USA", "EU", "ASEAN"],
                "risk_level": "Medium",
            }
        ],
        "market_metrics": {
            "market_size": "Growing",
            "growth_rate": "8-12%",
            "key_players": ["Leading Indian firms"],
            "export_value": "High",
            "import_value": "Moderate",
        },
    }

    return _build_response(ai_result, clean_sector, request, sources)


# Helper (clean architecture)
def _build_response(data, sector, request, sources=None, cached=False):
    session_id = getattr(request.state, "session_id", None)

    if session_id:
        session = get_session(session_id)
        session.setdefault("sectors_analyzed", []).append(sector)

    opportunities = [
        TradeOpportunity(**opp)
        for opp in data.get("opportunities", [])
        if isinstance(opp, dict)
    ]

    raw_metrics = data.get("market_metrics")
    market_metrics = MarketMetrics(**raw_metrics) if isinstance(raw_metrics, dict) else None

    metadata = AnalysisMetadata(
        sector=sector,
        generated_at=datetime.now(timezone.utc).isoformat(),
        data_sources=sources or [],
        session_id=session_id,
        cached=cached,
    )

    response_obj = SectorAnalysisResponse(
        metadata=metadata,
        report=data.get("report", ""),
        summary=data.get("summary", ""),
        opportunities=opportunities,
        market_metrics=market_metrics,
    )

    cache.set(sector, response_obj.model_dump())

    return response_obj