"""External data source integrations for market analysis."""

import datetime
import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import requests
import spacy
import wbdata
from dotenv import load_dotenv

from ..utils.caching import cache_result

# Load environment variables from .env file
load_dotenv(override=True)  # This will load .env and override existing env vars


# Configure logging
logger = logging.getLogger(__name__)


class MarketRelationType(Enum):
    """Type of relationship between markets."""

    INDEPENDENT = "independent"  # Markets are separate (use sum)
    OVERLAPPING = "overlapping"  # Markets overlap (use weighted average)
    SUBSET = "subset"  # One market is subset of another (use larger)


@dataclass
class IndustryMatch:
    """Matched industry with confidence score."""

    code: str  # Industry code (e.g., NAICS code)
    score: float  # Raw match score
    confidence: float  # Normalized confidence (0-1)
    keywords_matched: List[str]  # Keywords that contributed to the match

    @property
    def industry_code(self) -> str:
        """Alias for code to maintain compatibility."""
        return self.code


@dataclass
class MarketRelationship:
    """Relationship between two markets."""

    industry1: str
    industry2: str
    relationship: MarketRelationType
    overlap_factor: float  # 0-1, how much markets overlap


@dataclass
class IndustryMetrics:
    """Industry metrics from external sources."""

    industry_code: str
    gdp_contribution: float
    employment: int
    growth_rate: float
    market_size: float
    confidence_score: float
    year: int
    sources: List[str]


@dataclass
class MultiMarketInsights:
    """Analysis for multiple related markets."""

    primary_market: IndustryMetrics
    related_markets: List[IndustryMetrics]
    relationships: List[MarketRelationship]
    combined_market_size: float
    combined_growth_rate: float
    confidence_score: float
    year: int
    sources: List[str]


class WorldBankData:
    """World Bank data integration."""

    def __init__(self):
        """Initialize World Bank data client."""
        self.indicators = {
            "NY.GDP.MKTP.CD": "GDP (current US$)",
            "NV.IND.TOTL.ZS": "Industry (% of GDP)",
            "NY.GDP.MKTP.KD.ZG": "GDP growth (annual %)",
        }

    @cache_result("worldbank", ttl=24 * 60 * 60)  # Cache for 24 hours
    def get_industry_metrics(
        self, country: str = "USA", year: Optional[int] = None
    ) -> Dict[str, float]:
        """Get industry metrics from World Bank.

        Args:
            country: Country code (default: USA)
            year: Year for data (default: latest available)

        Returns:
            Dictionary of industry metrics
        """
        try:
            if year is None:
                year = datetime.datetime.now().year - 1  # Previous year

            # Get data for each indicator separately and combine
            data = {}
            for indicator in self.indicators:
                try:
                    # World Bank API expects dates in format "YYYY"
                    result = wbdata.get_data(indicator, country=country, date=str(year))
                    if result and len(result) > 0:
                        # Get the most recent value
                        value = result[0].get("value")
                        # Convert value to float if it exists
                        if value is not None:
                            try:
                                data[indicator] = float(value)
                            except (ValueError, TypeError):
                                logger.warning(
                                    f"Could not convert value {value} to float for indicator {indicator}"
                                )
                                data[indicator] = None
                        else:
                            data[indicator] = None
                except Exception as e:
                    logger.warning(f"Failed to fetch indicator {indicator}: {e}")
                    data[indicator] = None

            # Use default values if data is missing or None
            gdp = data.get("NY.GDP.MKTP.CD")
            if gdp is None or gdp <= 0:
                gdp = 20000000000000.0  # $20T default GDP

            industry_pct = data.get("NV.IND.TOTL.ZS")
            if industry_pct is None or industry_pct <= 0:
                industry_pct = 20.0  # 20% default

            growth_rate = data.get("NY.GDP.MKTP.KD.ZG")
            if growth_rate is None:
                growth_rate = 2.5  # 2.5% default

            # Always return a dictionary with all required keys and valid values
            return {
                "gdp": gdp,
                "industry_percentage": industry_pct,
                "growth_rate": growth_rate,
            }
        except Exception as e:
            logger.error(f"Error fetching World Bank data: {e}", exc_info=True)
            # Return dictionary with default values
            return {
                "gdp": 20000000000000.0,  # $20T
                "industry_percentage": 20.0,  # 20%
                "growth_rate": 2.5,  # 2.5%
            }


class BLSData:
    """Bureau of Labor Statistics data integration."""

    def __init__(self):
        """Initialize BLS client with API key."""
        self.api_key = os.getenv("BLS_API_KEY")
        if self.api_key:
            logger.debug("BLS API key found in environment")
        else:
            logger.warning("BLS API key not found in environment")

        self.base_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

        # Expanded NAICS to BLS series mapping
        self.series_mapping = {
            # Technology and Software
            "5112": "CEU5051200001",  # Software Publishers
            "5415": "CEU6054150001",  # Computer Systems Design
            "5182": "CEU5051820001",  # Data Processing and Hosting
            "5191": "CEU5051910001",  # Internet Publishing and Broadcasting
            # Retail and E-commerce
            "4510": "CEU4245100001",  # Electronic Shopping and Mail-Order Houses
            "4529": "CEU4245290001",  # Other General Merchandise Stores
            # Healthcare and Biotech
            "6211": "CEU6562110001",  # Offices of Physicians
            "6215": "CEU6562150001",  # Medical and Diagnostic Laboratories
            "3254": "CEU3232540001",  # Pharmaceutical and Medicine Manufacturing
            # Financial Services
            "5221": "CEU5552110001",  # Depository Credit Intermediation
            "5239": "CEU5552390001",  # Other Financial Investment Activities
            "5242": "CEU5552420001",  # Insurance Agencies and Brokerages
            # Manufacturing and Hardware
            "3341": "CEU3133410001",  # Computer and Peripheral Equipment
            "3344": "CEU3133440001",  # Semiconductor and Electronic Components
            "3345": "CEU3133450001",  # Electronic Instruments
            # Entertainment and Media
            "5121": "CEU5051210001",  # Motion Picture and Video Industries
            "5122": "CEU5051220001",  # Sound Recording Industries
            # Transportation and Logistics
            "4921": "CEU4349210001",  # Couriers and Express Delivery
            "4931": "CEU4349310001",  # Warehousing and Storage
        }

        # Industry keywords for classification
        self.industry_keywords = {
            # Technology and Software
            "5112": {
                "software",
                "saas",
                "application",
                "platform software",
                "development",
                "enterprise software",
                "developer tools",
                "platform",
                "online platform",
                "digital platform",
                "marketplace platform",
            },
            "5415": {
                "technology",
                "consulting",
                "it",
                "service",
                "solution",
                "system",
                "integration",
                "tech",
            },
            "5182": {
                "cloud",
                "hosting",
                "datacenter",
                "data center",
                "processing",
                "infrastructure",
            },
            # E-commerce and Digital
            "4510": {
                "ecommerce",
                "e-commerce",
                "marketplace",
                "online marketplace",
                "online retail",
                "online store",
                "online shopping",
                "digital retail",
                "online commerce",
                "digital marketplace",
            },
            "4529": {
                "retail",
                "merchandise",
                "store",
                "shopping",
                "retailer",
                "retail technology",
                "retail platform",
                "retail solution",
            },
            "5191": {
                "internet",
                "digital",
                "web",
                "content",
                "media",
                "publishing",
                "portal",
            },
            # Healthcare and Life Sciences
            "6211": {
                "health",
                "medical",
                "healthcare",
                "clinical",
                "patient",
                "doctor",
                "hospital",
                "telemedicine",
                "telehealth",
            },
            "6215": {
                "laboratory",
                "diagnostic",
                "testing",
                "lab",
                "medical lab",
                "clinical",
            },
            "3254": {"biotech", "pharmaceutical", "therapeutic", "drug", "medicine"},
            # Financial Services
            "5221": {
                "banking",
                "financial",
                "payment",
                "payments",
                "loan",
                "lending",
                "finance",
                "fintech",
                "bank",
                "transaction",
                "money",
            },
            "5242": {
                "insurance",
                "insurtech",
                "risk",
                "policy",
                "coverage",
                "underwriting",
                "claim",
                "insurer",
            },
            "5239": {"investment", "wealth", "portfolio", "asset", "trading", "invest"},
            # Hardware and Manufacturing
            "3341": {
                "hardware",
                "device",
                "electronics",
                "computer",
                "smart device",
                "iot",
            },
            "3344": {"semiconductor", "chip", "processor", "circuit"},
            # Media and Entertainment
            "5121": {
                "video",
                "streaming",
                "motion picture",
                "film",
                "movie",
                "content",
                "video platform",
                "video streaming",
            },
            "5122": {
                "audio",
                "podcast",
                "music",
                "sound",
                "recording",
                "radio",
                "audio platform",
                "podcast platform",
                "podcast hosting",
            },
            # Logistics
            "4921": {
                "delivery",
                "courier",
                "shipping",
                "last mile",
                "logistics",
                "delivery platform",
                "last-mile delivery",
                "delivery automation",
            },
            "4931": {
                "warehouse",
                "fulfillment",
                "storage",
                "supply chain",
                "inventory",
                "warehousing platform",
                "fulfillment platform",
            },
        }

        # Priority weights for industries
        self.industry_priorities = {
            # Core tech and digital
            "5112": 1.2,  # Software is common in modern businesses
            "5182": 1.2,  # Cloud infrastructure is fundamental
            # Financial and Healthcare
            "5221": 1.4,  # Banking/Fintech (highest priority)
            "5242": 1.4,  # Insurance (highest priority)
            "6211": 1.3,  # Healthcare
            # E-commerce and Digital
            "4510": 1.3,  # E-commerce
            "4529": 1.2,  # Retail tech
            "5191": 1.1,  # Digital content
            # Default priority for others
            "5415": 1.1,  # IT consulting
            "6215": 1.0,
            "3254": 1.0,
            "5239": 1.0,
            "3341": 1.0,
            "3344": 1.0,
            "5121": 1.0,
            "5122": 1.0,
            "4921": 1.0,
            "4931": 1.0,
        }

        # Load spaCy model for text analysis
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.debug("Loaded spaCy model successfully")
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
            self.nlp = None

        # Define known market relationships
        self.market_relationships = {
            ("5221", "6211"): MarketRelationship(
                industry1="5221",
                industry2="6211",
                relationship=MarketRelationType.INDEPENDENT,
                overlap_factor=0.2,  # 20% overlap in healthcare fintech
            ),
            ("5242", "6211"): MarketRelationship(
                industry1="5242",
                industry2="6211",
                relationship=MarketRelationType.INDEPENDENT,
                overlap_factor=0.3,  # 30% overlap in insurtech
            ),
            ("5112", "5182"): MarketRelationship(
                industry1="5112",
                industry2="5182",
                relationship=MarketRelationType.OVERLAPPING,
                overlap_factor=0.6,  # 60% overlap in software/cloud
            ),
        }

    def register_api_key(self) -> str:
        """Get instructions for BLS API key registration."""
        return """
        To get a free BLS API key:
        1. Visit https://data.bls.gov/registrationEngine/
        2. Fill out the registration form
        3. Save the API key in your .env file as BLS_API_KEY=your_key_here
        """

    def get_employment_data(self, series_id: str) -> Dict[str, Any]:
        """Get employment data for a specific industry series.

        Args:
            series_id: BLS series ID for the industry

        Returns:
            Dictionary containing employment data
        """
        if not series_id:
            logger.warning("No series ID provided for employment data")
            return {}

        try:
            response = self._make_request(series_id)
            if not response or "Results" not in response:
                logger.warning(f"No results found for series {series_id}")
                return {}

            series_data = response["Results"].get("series", [])
            if not series_data or not series_data[0].get("data"):
                logger.warning(f"No data found in series {series_id}")
                return {}

            # Get the latest data point
            latest_data = series_data[0]["data"][0]

            # BLS values are in thousands, multiply by 1000
            employment = float(latest_data["value"]) * 1000

            return {
                "employment": employment,
                "year": int(latest_data["year"]),
                "period": latest_data["period"],
                "period_name": latest_data.get("periodName", ""),
            }

        except Exception as e:
            logger.error(f"Error getting employment data for series {series_id}: {e}")
            return {}

    def _make_request(self, series_id: str) -> Dict:
        """Make request to BLS API."""
        if not self.api_key:
            logger.warning(
                "BLS API key not found. Use register_api_key() for instructions."
            )
            return {}

        headers = {"Content-type": "application/json"}
        data = {
            "seriesid": [series_id],
            "startyear": str(datetime.datetime.now().year - 1),
            "endyear": str(datetime.datetime.now().year),
            "registrationkey": self.api_key,
        }

        response = requests.post(self.base_url, json=data, headers=headers)
        response.raise_for_status()

        return response.json()

    @cache_result("bls", ttl=12 * 60 * 60)  # Cache for 12 hours
    def get_industry_employment_data(
        self,
        industry_code: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> Dict:
        """Get employment data from BLS.

        Args:
            industry_code: Industry code (NAICS)
            start_year: Start year for data (default: previous year)
            end_year: End year for data (default: current year)

        Returns:
            Dictionary with employment data
        """
        try:
            if not self.api_key:
                logger.warning(
                    "BLS API key not found. Use register_api_key() for instructions."
                )
                # Return default data structure even without API key
                return {
                    "employment": 100000,  # Default value for testing
                    "year": datetime.datetime.now().year,
                    "period": "M01",
                }

            # Set default years if not provided
            if not end_year:
                end_year = datetime.datetime.now().year
            if not start_year:
                start_year = end_year - 1

            # Get series ID from mapping
            series_id = self.series_mapping.get(industry_code)
            if not series_id:
                logger.warning(
                    f"No BLS series mapping found for industry code {industry_code}"
                )
                return {
                    "employment": 100000,  # Default value for testing
                    "year": end_year,
                    "period": "M01",
                }

            logger.debug(f"Using BLS series ID: {series_id}")

            employment_data = self.get_employment_data(series_id)

            return {
                "employment": employment_data["employment"],
                "year": employment_data["year"],
                "period": employment_data["period"],
            }
        except Exception as e:
            logger.error(f"Error fetching BLS data: {e}")
            return {
                "employment": 100000,  # Default value for testing
                "year": end_year if end_year else datetime.datetime.now().year,
                "period": "M01",
            }

    def get_industry_metrics(
        self, industry_code: str, year: Optional[int] = None
    ) -> Optional[IndustryMetrics]:
        """Get comprehensive metrics for an industry.

        Args:
            industry_code: Industry code (NAICS)
            year: Target year for metrics (default: current year)

        Returns:
            IndustryMetrics object with combined data from BLS and World Bank
        """
        if not year:
            year = datetime.datetime.now().year - 1

        try:
            logger.debug(f"Getting metrics for industry {industry_code}, year {year}")

            # Get employment data from BLS
            series_id = self.series_mapping.get(industry_code, "")
            logger.debug(f"Using BLS series ID: {series_id}")

            employment_data = self.get_employment_data(series_id)
            logger.debug(f"Employment data: {employment_data}")

            employment_data = employment_data or {}
            employment = int(employment_data.get("employment", 100000))
            logger.debug(f"Calculated employment: {employment}")

            # Get World Bank data
            wb = WorldBankData()
            wb_metrics = wb.get_industry_metrics()
            logger.debug(f"World Bank metrics: {wb_metrics}")

            wb_metrics = wb_metrics or {}
            gdp = wb_metrics.get("gdp", 20000000000000)
            industry_pct = wb_metrics.get("industry_percentage", 20) / 100
            growth_rate = wb_metrics.get("growth_rate", 2.5)
            logger.debug(
                f"GDP: {gdp}, Industry %: {industry_pct}, Growth: {growth_rate}"
            )

            # Calculate market size
            total_industry_gdp = gdp * industry_pct
            logger.debug(f"Total industry GDP: {total_industry_gdp}")

            total_industry_employment = 150000000
            industry_share = max(0.001, (employment / total_industry_employment))
            logger.debug(f"Industry share before priority: {industry_share}")

            priority_factor = self.industry_priorities.get(industry_code, 1.0)
            industry_share *= priority_factor
            logger.debug(
                f"Industry share after priority ({priority_factor}): {industry_share}"
            )

            market_size = max((total_industry_gdp * industry_share) / 1e9, 0.1)
            logger.debug(f"Calculated market size: {market_size}")

            confidence_score = min(
                1.0,
                max(
                    0.1,
                    0.4 + (0.3 if employment > 0 else 0) + (0.3 if wb_metrics else 0),
                ),
            )
            logger.debug(f"Calculated confidence score: {confidence_score}")

            metrics = IndustryMetrics(
                industry_code=industry_code,
                gdp_contribution=market_size,
                employment=employment,
                growth_rate=growth_rate,
                market_size=market_size,
                confidence_score=confidence_score,
                year=year,
                sources=["World Bank", "BLS"] if wb_metrics else ["BLS"],
            )
            logger.debug(f"Created metrics object: {metrics}")
            return metrics

        except Exception as e:
            logger.error(
                f"Error getting industry metrics for {industry_code}: {e}",
                exc_info=True,
            )
            metrics = IndustryMetrics(
                industry_code=industry_code,
                gdp_contribution=0.1,
                employment=100000,
                growth_rate=2.5,
                market_size=0.1,
                confidence_score=0.1,
                year=year,
                sources=["Default"],
            )
            logger.debug(f"Created default metrics object: {metrics}")
            return metrics

    def _calculate_combined_metrics(
        self, markets: List[IndustryMetrics], relationships: List[MarketRelationship]
    ) -> Dict[str, float]:
        """Calculate combined market size and growth rate."""
        if not markets:
            logger.debug("No markets provided, returning defaults")
            return {"market_size": 0, "growth_rate": 0, "confidence": 0.1}

        logger.debug(f"Calculating combined metrics for {len(markets)} markets")
        logger.debug(f"First market: {markets[0]}")

        # Start with the primary market
        combined_size = markets[0].market_size or 0.1
        total_weight = markets[0].confidence_score or 0.1
        weighted_growth = (markets[0].growth_rate or 0) * (
            markets[0].confidence_score or 0.1
        )
        logger.debug(
            f"Initial values - Size: {combined_size}, Weight: {total_weight}, Growth: {weighted_growth}"
        )

        # Process each additional market
        for i, market in enumerate(markets[1:], 1):
            logger.debug(f"Processing market {i}: {market}")
            # Find relationship with previous markets
            rel = None
            for r in relationships:
                if (
                    r.industry1 == market.industry_code
                    or r.industry2 == market.industry_code
                ):
                    for prev_market in markets[:i]:
                        if (
                            r.industry1 == prev_market.industry_code
                            or r.industry2 == prev_market.industry_code
                        ):
                            rel = r
                            break
                    if rel:
                        break

            if not rel:
                # Default to independent with 10% overlap
                rel = MarketRelationship(
                    industry1=markets[0].industry_code,
                    industry2=market.industry_code,
                    relationship=MarketRelationType.INDEPENDENT,
                    overlap_factor=0.1,
                )

            # Calculate contribution based on relationship type
            market_size = market.market_size or 0.1
            if rel.relationship == MarketRelationType.INDEPENDENT:
                # Add market size minus overlap
                overlap = min(combined_size, market_size) * rel.overlap_factor
                combined_size += market_size - overlap
            elif rel.relationship == MarketRelationType.OVERLAPPING:
                # Use weighted average for overlapping portion
                overlap = min(combined_size, market_size) * rel.overlap_factor
                non_overlap = market_size - overlap
                combined_size += non_overlap
            else:  # SUBSET
                # Take larger market size
                combined_size = max(combined_size, market_size)

            # Update weighted growth rate
            market_confidence = market.confidence_score or 0.1
            total_weight += market_confidence
            weighted_growth += (market.growth_rate or 0) * market_confidence
            logger.debug(
                f"Updated values - Size: {combined_size}, Weight: {total_weight}, Growth: {weighted_growth}"
            )

        # Calculate final metrics
        avg_growth = weighted_growth / total_weight if total_weight > 0 else 0
        avg_confidence = total_weight / len(markets)
        logger.debug(
            f"Final values - Growth: {avg_growth}, Confidence: {avg_confidence}"
        )

        return {
            "market_size": max(combined_size, 0.1),  # Minimum $100M
            "growth_rate": avg_growth,
            "confidence": avg_confidence,
        }

    def _detect_industry_codes(
        self, target_market: str, threshold: float = 0.10
    ) -> List[IndustryMatch]:
        """Map target market description to relevant industry codes using NLP.

        Args:
            target_market: Description of the target market
            threshold: Minimum confidence threshold for including an industry (default: 0.10)

        Returns:
            List of industry matches ordered by relevance score
        """
        if not self.nlp:
            logger.error("spaCy model not loaded")
            return []

        # Preprocess target market description
        doc = self.nlp(target_market.lower())
        tokens = [token.text for token in doc]

        matches = []
        for code, keywords in self.industry_keywords.items():
            score = 0.0
            matched_keywords = []

            # Check for exact matches (4.0x weight)
            exact_matches = keywords.intersection(set(tokens))
            if exact_matches:
                score += len(exact_matches) * 4.0
                matched_keywords.extend(exact_matches)

            # Check for partial matches (1.5x weight)
            for keyword in keywords:
                if any(keyword in token for token in tokens):
                    score += 1.5
                    matched_keywords.append(keyword)

            # Check for exact phrase matches (6.0x weight)
            for keyword in keywords:
                if " " in keyword and keyword in target_market.lower():
                    score += 6.0
                    matched_keywords.append(keyword)

            # Apply industry priority weight
            priority = self.industry_priorities.get(code, 1.0)
            score *= priority

            # Context bonuses
            if code in ["5221", "5242"] and any(
                kw in target_market.lower()
                for kw in ["health", "medical", "healthcare"]
            ):
                score *= 1.5  # 50% bonus for fintech-healthcare combinations

            if code == "4529" and any(
                kw in target_market.lower() for kw in ["tech", "platform", "digital"]
            ):
                score *= 2.0  # 100% bonus for retail-tech combinations

            # Calculate confidence score (normalized)
            confidence = min(score / 10.0, 1.0)  # Normalize to 0-1 range

            if confidence >= threshold:
                matches.append(
                    IndustryMatch(
                        code=code,
                        score=score,
                        confidence=confidence,
                        keywords_matched=list(set(matched_keywords)),
                    )
                )

        # Sort by score descending
        matches.sort(key=lambda x: x.score, reverse=True)
        return matches

    def get_industry_analysis(
        self, target_market: str, country: str = "USA", year: Optional[int] = None
    ) -> MultiMarketInsights:
        """Get comprehensive industry analysis for multiple related markets.

        Args:
            target_market: Description of target market
            country: Country code (default: USA)
            year: Target year for metrics

        Returns:
            MultiMarketInsights object with combined metrics
        """
        try:
            # Detect relevant industry codes
            matches = self._detect_industry_codes(target_market)
            if not matches:
                logger.warning(f"No industry matches found for: {target_market}")
                return MultiMarketInsights(
                    primary_market=IndustryMetrics(
                        industry_code="0000",
                        gdp_contribution=0,
                        employment=0,
                        growth_rate=0,
                        market_size=0,
                        confidence_score=0.1,
                        year=year or datetime.datetime.now().year,
                        sources=["Default"],
                    ),
                    related_markets=[],
                    relationships=[],
                    combined_market_size=0,
                    combined_growth_rate=0,
                    confidence_score=0.1,
                    year=year or datetime.datetime.now().year,
                    sources=["Default"],
                )

            # Get metrics for each industry
            markets = []
            for match in matches:
                try:
                    metrics = self.get_industry_metrics(match.code, year)
                    if metrics:  # Only add valid metrics
                        metrics.confidence_score *= (
                            match.confidence
                        )  # Adjust confidence based on match quality
                        markets.append(metrics)
                except Exception as e:
                    logger.error(f"Error getting metrics for {match.code}: {e}")
                    # Create default metrics for this industry
                    markets.append(
                        IndustryMetrics(
                            industry_code=match.code,
                            gdp_contribution=0.1,  # Minimum $100M
                            employment=100000,  # Default 100k employees
                            growth_rate=2.5,  # Default 2.5% growth
                            market_size=0.1,  # Minimum $100M
                            confidence_score=0.1
                            * match.confidence,  # Low confidence adjusted by match quality
                            year=year or datetime.datetime.now().year,
                            sources=["Default"],
                        )
                    )

            if not markets:
                logger.warning("No market metrics found")
                return MultiMarketInsights(
                    primary_market=IndustryMetrics(
                        industry_code=matches[0].code,
                        gdp_contribution=0,
                        employment=0,
                        growth_rate=0,
                        market_size=0,
                        confidence_score=0.1,
                        year=year or datetime.datetime.now().year,
                        sources=["Default"],
                    ),
                    related_markets=[],
                    relationships=[],
                    combined_market_size=0,
                    combined_growth_rate=0,
                    confidence_score=0.1,
                    year=year or datetime.datetime.now().year,
                    sources=["Default"],
                )

            # Sort markets by confidence score and market size
            markets.sort(
                key=lambda x: (x.confidence_score, x.market_size), reverse=True
            )

            # Get relationships between markets
            relationships = []
            for i, m1 in enumerate(markets):
                for m2 in markets[i + 1 :]:
                    key = tuple(sorted([m1.industry_code, m2.industry_code]))
                    if key in self.market_relationships:
                        relationships.append(self.market_relationships[key])

            # Calculate combined metrics
            combined_metrics = self._calculate_combined_metrics(markets, relationships)

            return MultiMarketInsights(
                primary_market=markets[0],
                related_markets=markets[1:],
                relationships=relationships,
                combined_market_size=combined_metrics["market_size"],
                combined_growth_rate=combined_metrics["growth_rate"],
                confidence_score=combined_metrics["confidence"],
                year=year or datetime.datetime.now().year,
                sources=list(set(sum([m.sources for m in markets], []))),
            )

        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            return MultiMarketInsights(
                primary_market=IndustryMetrics(
                    industry_code="5112",  # Default to software
                    gdp_contribution=0,
                    employment=0,
                    growth_rate=0,
                    market_size=0,
                    confidence_score=0.1,
                    year=year or datetime.datetime.now().year,
                    sources=["Default"],
                ),
                related_markets=[],
                relationships=[],
                combined_market_size=0,
                combined_growth_rate=0,
                confidence_score=0.1,
                year=year or datetime.datetime.now().year,
                sources=["Default"],
            )


def get_industry_analysis(
    target_market: str, country: str = "USA", year: Optional[int] = None
) -> MultiMarketInsights:
    """Get comprehensive industry analysis for multiple related markets.

    Args:
        target_market: Description of target market
        country: Country code (default: USA)
        year: Target year for metrics

    Returns:
        MultiMarketInsights object with combined metrics
    """
    try:
        bls = BLSData()

        # Detect relevant industry codes
        matches = bls._detect_industry_codes(target_market)
        if not matches:
            logger.warning(f"No industry matches found for: {target_market}")
            return MultiMarketInsights(
                primary_market=IndustryMetrics(
                    industry_code="0000",
                    gdp_contribution=0,
                    employment=0,
                    growth_rate=0,
                    market_size=0,
                    confidence_score=0.1,
                    year=year or datetime.datetime.now().year,
                    sources=["Default"],
                ),
                related_markets=[],
                relationships=[],
                combined_market_size=0,
                combined_growth_rate=0,
                confidence_score=0.1,
                year=year or datetime.datetime.now().year,
                sources=["Default"],
            )

        # Get metrics for each industry
        markets = []
        for match in matches:
            try:
                metrics = bls.get_industry_metrics(match.code, year)
                if metrics:  # Only add valid metrics
                    metrics.confidence_score *= (
                        match.confidence
                    )  # Adjust confidence based on match quality
                    markets.append(metrics)
            except Exception as e:
                logger.error(f"Error getting metrics for {match.code}: {e}")
                # Create default metrics for this industry
                markets.append(
                    IndustryMetrics(
                        industry_code=match.code,
                        gdp_contribution=0.1,  # Minimum $100M
                        employment=100000,  # Default 100k employees
                        growth_rate=2.5,  # Default 2.5% growth
                        market_size=0.1,  # Minimum $100M
                        confidence_score=0.1
                        * match.confidence,  # Low confidence adjusted by match quality
                        year=year or datetime.datetime.now().year,
                        sources=["Default"],
                    )
                )

        if not markets:
            logger.warning("No market metrics found")
            return MultiMarketInsights(
                primary_market=IndustryMetrics(
                    industry_code=matches[0].code,
                    gdp_contribution=0,
                    employment=0,
                    growth_rate=0,
                    market_size=0,
                    confidence_score=0.1,
                    year=year or datetime.datetime.now().year,
                    sources=["Default"],
                ),
                related_markets=[],
                relationships=[],
                combined_market_size=0,
                combined_growth_rate=0,
                confidence_score=0.1,
                year=year or datetime.datetime.now().year,
                sources=["Default"],
            )

        # Sort markets by confidence score and market size
        markets.sort(key=lambda x: (x.confidence_score, x.market_size), reverse=True)

        # Get relationships between markets
        relationships = []
        for i, m1 in enumerate(markets):
            for m2 in markets[i + 1 :]:
                key = tuple(sorted([m1.industry_code, m2.industry_code]))
                if key in bls.market_relationships:
                    relationships.append(bls.market_relationships[key])

        # Calculate combined metrics
        combined_metrics = bls._calculate_combined_metrics(markets, relationships)

        return MultiMarketInsights(
            primary_market=markets[0],
            related_markets=markets[1:],
            relationships=relationships,
            combined_market_size=combined_metrics["market_size"],
            combined_growth_rate=combined_metrics["growth_rate"],
            confidence_score=combined_metrics["confidence"],
            year=year or datetime.datetime.now().year,
            sources=list(set(sum([m.sources for m in markets], []))),
        )

    except Exception as e:
        logger.error(f"Error in market analysis: {e}")
        return MultiMarketInsights(
            primary_market=IndustryMetrics(
                industry_code="5112",  # Default to software
                gdp_contribution=0,
                employment=0,
                growth_rate=0,
                market_size=0,
                confidence_score=0.1,
                year=year or datetime.datetime.now().year,
                sources=["Default"],
            ),
            related_markets=[],
            relationships=[],
            combined_market_size=0,
            combined_growth_rate=0,
            confidence_score=0.1,
            year=year or datetime.datetime.now().year,
            sources=["Default"],
        )
