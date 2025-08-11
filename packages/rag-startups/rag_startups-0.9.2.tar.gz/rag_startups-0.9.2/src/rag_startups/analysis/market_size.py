"""Market size estimation module for startup analysis."""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Tuple

from .external_data import (
    BLSData,
    IndustryMetrics,
    MarketRelationship,
    MarketRelationType,
    MultiMarketInsights,
)


class MarketSegment(Enum):
    """Market segment categories."""

    B2B = "b2b"
    B2C = "b2c"
    ENTERPRISE = "enterprise"
    SMB = "smb"
    UNKNOWN = "unknown"


class MarketStage(Enum):
    """Market maturity stages."""

    EMERGING = "emerging"
    GROWING = "growing"
    MATURE = "mature"
    DECLINING = "declining"
    UNKNOWN = "unknown"


@dataclass
class MarketSize:
    """Market size estimation results."""

    total_addressable_market: float  # in billions USD
    serviceable_addressable_market: float
    serviceable_obtainable_market: float
    segment: MarketSegment
    stage: MarketStage
    year: int
    confidence_score: float
    sources: List[str]


class MarketSizeEstimator:
    """Estimates market size for startup ideas."""

    def __init__(self, startup_data: List[Dict]):
        """Initialize with historical startup data.

        Args:
            startup_data: List of startup dictionaries containing metadata
        """
        self.startup_data = startup_data
        self._segment_patterns = self._compile_segment_patterns()

    def _compile_segment_patterns(self) -> Dict[MarketSegment, List[str]]:
        """Compile regex patterns for market segmentation."""
        return {
            MarketSegment.B2B: [
                r"b2b",
                r"business[\s-]to[\s-]business",
                r"enterprise\s+software",
                r"saas",
            ],
            MarketSegment.B2C: [
                r"b2c",
                r"business[\s-]to[\s-]consumer",
                r"consumer",
                r"retail",
                r"mobile\s+app",
                r"end[\s-]user",
            ],
            MarketSegment.ENTERPRISE: [
                r"enterprise",
                r"large\s+business",
                r"corporate",
            ],
            MarketSegment.SMB: [r"smb", r"small\s+business", r"medium\s+business"],
        }

    def estimate_market_size(
        self, description: str, similar_startups: List[Dict], year: int = 2024
    ) -> MarketSize:
        """Estimate market size for a startup idea.

        Args:
            description: Startup idea description
            similar_startups: List of similar startups from the database
            year: Target year for estimation (default: current year)

        Returns:
            MarketSize object containing the estimation results
        """
        # Determine market segment
        segment = self._determine_segment(description)

        # Calculate market sizes based on similar startups and patterns
        tam = self._estimate_total_addressable_market(description, similar_startups)
        sam = tam * 0.4  # Typically 30-50% of TAM
        som = sam * 0.1  # Typically 10-20% of SAM

        # Determine market stage
        stage = self._determine_market_stage(similar_startups)

        # Calculate confidence score based on data quality
        confidence = self._calculate_confidence_score(similar_startups)

        return MarketSize(
            total_addressable_market=tam,
            serviceable_addressable_market=sam,
            serviceable_obtainable_market=som,
            segment=segment,
            stage=stage,
            year=year,
            confidence_score=confidence,
            sources=["Historical startup data", "Pattern analysis"],
        )

    def _determine_segment(self, description: str) -> MarketSegment:
        """Determine market segment based on description patterns."""
        description = description.lower()

        for segment, patterns in self._segment_patterns.items():
            if any(re.search(pattern, description) for pattern in patterns):
                return segment

        return MarketSegment.UNKNOWN

    def _estimate_total_addressable_market(
        self, description: str, similar_startups: List[Dict]
    ) -> float:
        """Estimate total addressable market size in billions USD."""
        bls = BLSData()
        market_insights = bls.get_industry_analysis(description)
        if market_insights:
            return market_insights.combined_market_size
        else:
            # Base estimate from similar startups
            startup_based_estimate = (
                sum(s.get("valuation", 0) for s in similar_startups)
                / len(similar_startups)
                if similar_startups
                else 0
            )
            return startup_based_estimate

    def _get_industry_code(self, description: str) -> str:
        """Get BLS industry code from description."""
        # TODO: Implement more sophisticated industry code mapping
        # For now, return a default code for software industry
        return "5112"  # Software Publishers

    def _determine_market_stage(self, similar_startups: List[Dict]) -> MarketStage:
        """Determine market stage based on similar startups."""
        # TODO: Implement stage determination using:
        # 1. Growth rates
        # 2. Number of competitors
        # 3. Investment patterns
        return MarketStage.GROWING  # Default for now

    def _calculate_confidence_score(self, similar_startups: List[Dict]) -> float:
        """Calculate confidence score for the estimation."""
        # Factors affecting confidence:
        # 1. Number of similar startups
        # 2. Data completeness
        # 3. Market similarity
        base_score = min(len(similar_startups) / 10, 1.0)  # 0.0 to 1.0
        return base_score * 0.8  # Conservative adjustment


def calculate_market_relationship(industry1: str, industry2: str) -> MarketRelationship:
    """Calculate the relationship between two industries."""
    # For now, use a simple heuristic based on industry codes
    # In the future, this could use more sophisticated analysis

    # Convert to same length for comparison
    code1 = industry1[:2]
    code2 = industry2[:2]

    # Same major industry group - likely substitutes
    if code1 == code2:
        return MarketRelationship(
            industry1=industry1,
            industry2=industry2,
            relationship=MarketRelationType.SUBSTITUTE,
            overlap_factor=0.3,
        )

    # Known complementary pairs
    complementary_pairs = {
        frozenset({"52", "62"}),  # Finance + Healthcare
        frozenset({"51", "54"}),  # Information + Professional Services
        frozenset({"45", "49"}),  # Retail + Transportation
    }

    if frozenset({code1, code2}) in complementary_pairs:
        return MarketRelationship(
            industry1=industry1,
            industry2=industry2,
            relationship=MarketRelationType.COMPLEMENTARY,
            overlap_factor=0.2,
        )

    # Default to independent with small overlap
    return MarketRelationship(
        industry1=industry1,
        industry2=industry2,
        relationship=MarketRelationType.INDEPENDENT,
        overlap_factor=0.1,
    )


def calculate_combined_metrics(
    industries: List[IndustryMetrics], relationships: List[MarketRelationship]
) -> Tuple[float, float]:
    """Calculate combined market size and growth rate."""
    if not industries:
        return 0.0, 0.0

    # Start with primary market
    total_size = industries[0].market_size
    total_growth = industries[0].growth_rate

    # Track processed pairs to avoid double counting
    processed_pairs = set()

    # Add related markets considering relationships
    for rel in relationships:
        # Get corresponding market metrics
        market1 = next(
            (m for m in industries if m.industry_code == rel.industry1), None
        )
        market2 = next(
            (m for m in industries if m.industry_code == rel.industry2), None
        )

        if not market1 or not market2:
            continue

        # Create unique pair identifier
        pair = tuple(sorted([rel.industry1, rel.industry2]))
        if pair in processed_pairs:
            continue

        if rel.relationship == MarketRelationType.INDEPENDENT:
            # Add market sizes minus overlap
            overlap = min(market1.market_size, market2.market_size) * rel.overlap_factor
            total_size += market2.market_size - overlap
            total_growth = max(total_growth, market2.growth_rate)
        elif rel.relationship == MarketRelationType.COMPLEMENTARY:
            # Add full market sizes
            total_size += market2.market_size
            total_growth = max(total_growth, market2.growth_rate)
        else:  # SUBSTITUTE
            # Use larger market
            total_size = max(total_size, market2.market_size)
            total_growth = max(total_growth, market2.growth_rate)

        processed_pairs.add(pair)

    return total_size, total_growth


def get_industry_analysis(target_market: str) -> MultiMarketInsights:
    """Get comprehensive market analysis for a target market description."""
    bls = BLSData()
    matches = bls._detect_industry_codes(target_market)

    if not matches:
        return MultiMarketInsights(
            primary_market=None,
            related_markets=[],
            relationships=[],
            combined_market_size=0,
            combined_growth_rate=0,
            confidence_score=0,
            year=datetime.now().year,
            sources=[],
        )

    # Get metrics for each industry
    industries: List[IndustryMetrics] = []
    for match in matches:
        metrics = bls.get_industry_metrics(match.code)
        if metrics:
            # Use match confidence as metrics confidence
            metrics.confidence_score = match.confidence
            industries.append(metrics)

    if not industries:
        return MultiMarketInsights(
            primary_market=None,
            related_markets=[],
            relationships=[],
            combined_market_size=0,
            combined_growth_rate=0,
            confidence_score=0,
            year=datetime.now().year,
            sources=[],
        )

    # Sort by confidence score
    industries.sort(key=lambda x: x.confidence_score, reverse=True)

    # Calculate relationships between industries
    relationships = []
    for i, industry1 in enumerate(industries):
        for industry2 in industries[i + 1 :]:
            rel = calculate_market_relationship(
                industry1.industry_code, industry2.industry_code
            )
            relationships.append(rel)

    # Calculate combined metrics
    total_size, total_growth = calculate_combined_metrics(industries, relationships)

    # Average confidence across all industries
    avg_confidence = sum(i.confidence_score for i in industries) / len(industries)

    # Combine sources
    sources = list(set(sum((i.sources for i in industries), [])))

    return MultiMarketInsights(
        primary_market=industries[0],
        related_markets=industries[1:],
        relationships=relationships,
        combined_market_size=total_size,
        combined_growth_rate=total_growth,
        confidence_score=avg_confidence,
        year=industries[0].year,
        sources=sources,
    )
