"""Market analysis functionality for startup ideas."""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from .external_data import BLSData, WorldBankData

logger = logging.getLogger(__name__)


@dataclass
class MarketInsights:
    """Structured market analysis results."""

    market_size: float
    growth_rate: float
    competition_level: str
    barriers_to_entry: List[str]
    key_trends: List[str]
    risk_factors: List[str]
    opportunity_score: float  # 0-1 score
    confidence_score: float  # 0-1 score indicating confidence in the analysis
    year: int
    sources: List[str]


class MarketAnalyzer:
    """Analyzes market potential for startup ideas."""

    def __init__(self):
        """Initialize market analysis components."""
        self.world_bank = WorldBankData()
        self.bls = BLSData()

    def analyze_startup_idea(
        self, idea: Dict, country: str = "USA", year: Optional[int] = None
    ) -> MarketInsights:
        """
        Analyze market potential for a startup idea.

        Args:
            idea: Dictionary containing startup idea details
            country: Country code for market analysis
            year: Year for market data (default: latest available)

        Returns:
            MarketInsights object containing analysis results
        """
        try:
            # Get market data
            target_market = idea.get("target_market", "")
            if not target_market:
                logger.warning("No target market specified in idea")
                return None

            market_data = self.bls.get_industry_analysis(target_market, country, year)
            if not market_data:
                logger.warning(f"No market data found for {target_market}")
                return None

            # Convert MultiMarketInsights to MarketInsights
            return MarketInsights(
                market_size=market_data.combined_market_size,
                growth_rate=market_data.combined_growth_rate,
                competition_level=self._assess_competition(market_data),
                barriers_to_entry=self._identify_barriers(market_data),
                key_trends=self._identify_trends(market_data),
                risk_factors=self._identify_risks(market_data),
                opportunity_score=self._calculate_opportunity_score(market_data),
                confidence_score=market_data.confidence_score,
                year=market_data.year,
                sources=market_data.sources,
            )

        except Exception as e:
            logger.error(f"Failed to analyze idea {idea.get('name', '')}: {str(e)}")
            raise

    def _detect_industry_code(self, target_market: str) -> str:
        """Map target market description to industry code."""
        # TODO: Implement proper industry code detection
        # For now, return a default code
        return "5112"  # Software Publishers

    def _assess_competition(self, market_data) -> str:
        """Assess competition level based on market data."""
        if market_data.combined_market_size > 100:  # Large market
            return "High"
        elif market_data.combined_market_size > 50:  # Medium market
            return "Medium"
        else:
            return "Low"

    def _identify_barriers(self, market_data) -> List[str]:
        """Identify barriers to entry."""
        barriers = []
        if market_data.combined_market_size > 100:
            barriers.append("High capital requirements")
        if len(market_data.related_markets) > 2:
            barriers.append("Complex market relationships")
        if market_data.confidence_score < 0.5:
            barriers.append("Market uncertainty")
        return barriers

    def _identify_trends(self, market_data) -> List[str]:
        """Identify key market trends."""
        trends = []
        if market_data.combined_growth_rate > 10:
            trends.append("High growth market")
        if market_data.combined_growth_rate < 0:
            trends.append("Market contraction")
        if len(market_data.related_markets) > 2:
            trends.append("Market consolidation")
        return trends

    def _identify_risks(self, market_data) -> List[str]:
        """Identify risk factors."""
        risks = []
        if market_data.combined_growth_rate < 0:
            risks.append("Declining market")
        if market_data.confidence_score < 0.5:
            risks.append("Limited market data")
        if len(market_data.related_markets) > 3:
            risks.append("Complex competitive landscape")
        return risks

    def _calculate_opportunity_score(self, market_data) -> float:
        """Calculate opportunity score (0-1)."""
        # Base score from market size and growth
        base_score = min(market_data.combined_market_size / 200, 0.5) + min(
            max(market_data.combined_growth_rate / 20, 0), 0.5
        )

        # Adjust for confidence
        base_score *= market_data.confidence_score

        # Ensure score is between 0 and 1
        return max(min(base_score, 1.0), 0.0)
