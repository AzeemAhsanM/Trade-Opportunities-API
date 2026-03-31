from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

class TradeOpportunity(BaseModel):
    title: str = Field(..., description="Short title of the opportunity")
    description: str = Field(..., description="Detailed description")
    potential_value: Optional[str] = Field(None, description="Estimated market value")
    key_markets: Optional[List[str]] = Field(default_factory=list, description="Target export/import markets")
    risk_level: Optional[str] = Field(None, description="Low / Medium / High")


class MarketMetrics(BaseModel):
    market_size: Optional[str] = None
    growth_rate: Optional[str] = None
    key_players: Optional[List[str]] = Field(default_factory=list)
    export_value: Optional[str] = None
    import_value: Optional[str] = None


class AnalysisMetadata(BaseModel):
    sector: str
    generated_at: str
    data_sources: List[str] = Field(default_factory=list)
    session_id: Optional[str] = None
    cached: bool = False


class SectorAnalysisResponse(BaseModel):
    metadata: AnalysisMetadata
    report: str = Field(..., description="Full markdown-formatted analysis report")
    summary: str = Field(..., description="One-paragraph executive summary")
    opportunities: List[TradeOpportunity] = Field(
        default_factory=list,
        description="Top trade opportunities identified"
    )
    market_metrics: Optional[MarketMetrics] = None


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[str] = None
