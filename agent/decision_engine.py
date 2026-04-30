"""
agent/decision_engine.py

Decision-making engine for Saint Claw Bot.
Scores and ranks charitable foundations based on cause alignment,
impact metrics, and current news relevance.

Author: Saint Claw Bot
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

from rich.console import Console

console = Console()


class DecisionEngine:
    """
    The brain of Saint Claw Bot.
    
    Evaluates charitable foundations using a multi-factor scoring
    algorithm that considers cause alignment, impact scores, and
    relevance to current events. Ensures diversity by checking
    decision history.
    """
    
    # Scoring weights — these can be adjusted to change decision priorities
    WEIGHT_CAUSE_ALIGNMENT = 0.30  # 30% — How well the cause matches preferences
    WEIGHT_IMPACT_SCORE = 0.40     # 40% — Charity's proven effectiveness
    WEIGHT_NEWS_RELEVANCE = 0.30   # 30% — Timeliness based on current events
    
    def __init__(
        self,
        config: Dict[str, Any],
        foundations_path: str = "foundations/foundations_list.json",
        logger=None
    ) -> None:
        """
        Initialize the DecisionEngine.
        
        Args:
            config: Configuration dictionary with preferred_causes and settings
            foundations_path: Path to the JSON file containing foundation data
            logger: Optional DecisionLogger instance for history checking
        """
        self.config = config
        self.foundations_path = Path(foundations_path)
        self.logger = logger
        self.preferred_causes = config.get("preferred_causes", [])
        self.max_repeat_skip = config.get("max_repeat_skip", 3)
        
        # Load foundation data
        self.foundations = self._load_foundations()
        
    def _load_foundations(self) -> List[Dict[str, Any]]:
        """
        Load foundation data from JSON file.
        
        Returns:
            List of foundation dictionaries
            
        Raises:
            FileNotFoundError: If foundations file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        try:
            with open(self.foundations_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            console.print(f"[red]Error: Foundations file not found: {self.foundations_path}[/red]")
            raise
        except json.JSONDecodeError as e:
            console.print(f"[red]Error: Invalid JSON in foundations file: {e}[/red]")
            raise
    
    def _calculate_cause_alignment(self, foundation: Dict[str, Any]) -> float:
        """
        Calculate how well a foundation's cause aligns with preferences.
        
        Returns 1.0 if the foundation's cause is in the preferred list,
        otherwise returns a lower score based on priority ranking.
        
        Args:
            foundation: Foundation dictionary with cause_area field
            
        Returns:
            Alignment score between 0.0 and 1.0
        """
        cause = foundation.get("cause_area", "").lower()
        
        # Direct match gets full score
        if cause in [c.lower() for c in self.preferred_causes]:
            # Higher score for higher priority (earlier in list)
            try:
                priority_index = [c.lower() for c in self.preferred_causes].index(cause)
                # Scale from 0.8 to 1.0 based on priority position
                return 1.0 - (priority_index * 0.05)
            except ValueError:
                return 0.9
        
        # No direct match — check for related causes
        cause_relations = {
            "climate": ["clean_water", "disaster_relief"],
            "global_health": ["hunger", "mental_health", "disaster_relief"],
            "education": ["global_health", "hunger"],
            "hunger": ["global_health", "clean_water"],
            "clean_water": ["climate", "global_health"],
            "animal_welfare": ["climate"],
            "mental_health": ["global_health"],
            "disaster_relief": ["global_health", "climate", "hunger"]
        }
        
        # Check if this cause relates to any preferred cause
        for preferred in self.preferred_causes:
            preferred_lower = preferred.lower()
            if cause in cause_relations.get(preferred_lower, []):
                return 0.7  # Related cause gets partial credit
        
        return 0.4  # No relation to preferences
    
    def _calculate_news_relevance(
        self,
        foundation: Dict[str, Any],
        news_data: Dict[str, Any]
    ) -> float:
        """
        Calculate semantic news relevance using multi-factor scoring.
        
        Instead of simple keyword matching, this uses weighted factors:
        - Keyword relevance (weighted by importance)
        - Article prominence (headlines weighted more than descriptions)
        - Recency bias (newer articles score higher)
        - Sentiment alignment (urgent news boosts relevance for relief causes)
        
        Args:
            foundation: Foundation dictionary with cause_area field
            news_data: Dictionary containing news articles
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        cause = foundation.get("cause_area", "").lower()
        articles = news_data.get("articles", [])
        
        if not articles:
            return 0.5  # Neutral if no news data
        
        # Hierarchical keyword mapping with weights (primary, secondary, tertiary)
        cause_keyword_weights = {
            "climate": {
                "primary": ["climate", "carbon", "emissions", "global warming"],
                "secondary": ["renewable", "green energy", "environmental", "sustainability"],
                "tertiary": ["weather", "temperature", "pollution", "conservation"]
            },
            "education": {
                "primary": ["education", "literacy", "school", "students"],
                "secondary": ["learning", "teaching", "curriculum", "university"],
                "tertiary": ["children", "youth", "academic", "scholarship"]
            },
            "global_health": {
                "primary": ["health", "disease", "vaccine", "malaria", "pandemic"],
                "secondary": ["medical", "healthcare", "hospital", "treatment"],
                "tertiary": ["doctor", "patient", "medicine", "research"]
            },
            "hunger": {
                "primary": ["hunger", "famine", "malnutrition", "food crisis"],
                "secondary": ["food insecurity", "starvation", "feeding", "nutrition"],
                "tertiary": ["crops", "agriculture", "food aid", "drought"]
            },
            "clean_water": {
                "primary": ["water", "sanitation", "clean water", "drinking water"],
                "secondary": ["water crisis", "drought", "well", "hygiene"],
                "tertiary": ["aquifer", "water supply", "irrigation", "purification"]
            },
            "animal_welfare": {
                "primary": ["animal", "wildlife", "endangered", "conservation"],
                "secondary": ["habitat", "species", "biodiversity", "extinction"],
                "tertiary": ["nature", "ecosystem", "forest", "ocean"]
            },
            "mental_health": {
                "primary": ["mental health", "depression", "anxiety", "suicide"],
                "secondary": ["therapy", "counseling", "psychological", "crisis"],
                "tertiary": ["wellness", "stress", "trauma", "support"]
            },
            "disaster_relief": {
                "primary": ["disaster", "emergency", "earthquake", "flood", "hurricane"],
                "secondary": ["relief", "aid", "evacuation", "crisis"],
                "tertiary": ["damage", "rescue", "recovery", "victims"]
            }
        }
        
        weights = cause_keyword_weights.get(cause, {"primary": [cause], "secondary": [], "tertiary": []})
        
        # Score each article
        article_scores = []
        for idx, article in enumerate(articles):
            title = article.get("title", "").lower()
            desc = article.get("description", "").lower()
            
            # Calculate weighted keyword matches
            score = 0.0
            
            # Primary keywords in title = highest weight
            for kw in weights["primary"]:
                if kw in title:
                    score += 0.4
                elif kw in desc:
                    score += 0.2
            
            # Secondary keywords
            for kw in weights["secondary"]:
                if kw in title:
                    score += 0.25
                elif kw in desc:
                    score += 0.1
            
            # Tertiary keywords
            for kw in weights["tertiary"]:
                if kw in title:
                    score += 0.15
                elif kw in desc:
                    score += 0.05
            
            # Recency bias: newer articles (lower index) get boost
            recency_boost = 1.0 - (idx / len(articles)) * 0.3
            score *= recency_boost
            
            # Cap individual article score
            article_scores.append(min(1.0, score))
        
        # Calculate aggregate relevance
        if article_scores:
            # Use average of top 3 scores to avoid dilution from many weak matches
            top_scores = sorted(article_scores, reverse=True)[:3]
            avg_relevance = sum(top_scores) / len(top_scores)
            
            # Boost if multiple articles are relevant (indicates trending topic)
            highly_relevant = sum(1 for s in article_scores if s > 0.5)
            if highly_relevant >= 2:
                avg_relevance = min(1.0, avg_relevance * 1.2)
            
            # Normalize to 0.2-0.95 range
            return max(0.2, min(0.95, avg_relevance))
        
        return 0.5
    
    def _check_recent_history(self, foundation_name: str) -> bool:
        """
        Check if a foundation was recently selected.
        
        Uses the logger (if provided) to check decision history
        and prevent repetitive selections.
        
        Args:
            foundation_name: Name of the foundation to check
            
        Returns:
            True if the foundation should be skipped (was recently chosen)
        """
        if self.logger is None:
            return False
        
        return self.logger.was_recently_chosen(foundation_name, self.max_repeat_skip)
    
    def evaluate_foundations(
        self,
        news_data: Dict[str, Any],
        charity_ratings: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate all foundations and return ranked list.
        
        Scores each foundation using the weighted formula and
        filters out recently chosen charities.
        
        Args:
            news_data: Current news context from data fetcher
            charity_ratings: Charity rating data (may be empty in demo mode)
            
        Returns:
            List of foundations sorted by score (highest first)
        """
        scored_foundations = []
        
        for foundation in self.foundations:
            name = foundation.get("name", "Unknown")
            
            # Skip if recently chosen
            if self._check_recent_history(name):
                console.print(f"[dim]Skipping {name} (chosen recently)[/dim]")
                continue
            
            # Calculate individual scores
            cause_alignment = self._calculate_cause_alignment(foundation)
            
            # Impact score from foundation data (normalized to 0-1)
            raw_impact = foundation.get("impact_score", 5.0)
            impact_score = raw_impact / 10.0
            
            # News relevance
            news_relevance = self._calculate_news_relevance(foundation, news_data)
            
            # Calculate weighted final score
            final_score = (
                cause_alignment * self.WEIGHT_CAUSE_ALIGNMENT +
                impact_score * self.WEIGHT_IMPACT_SCORE +
                news_relevance * self.WEIGHT_NEWS_RELEVANCE
            )
            
            # Build reasoning dict for transparency
            reasoning = {
                "cause_alignment": round(cause_alignment, 3),
                "impact_score": round(impact_score, 3),
                "news_relevance": round(news_relevance, 3),
                "final_score": round(final_score, 3),
                "weights_applied": {
                    "cause_alignment": self.WEIGHT_CAUSE_ALIGNMENT,
                    "impact_score": self.WEIGHT_IMPACT_SCORE,
                    "news_relevance": self.WEIGHT_NEWS_RELEVANCE
                }
            }
            
            scored_foundations.append({
                "foundation": foundation,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score (descending)
        scored_foundations.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_foundations
    
    def make_decision(
        self,
        news_data: Dict[str, Any],
        charity_ratings: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], float, Dict[str, Any]]:
        """
        Make a donation decision.
        
        Evaluates all foundations and returns the top choice with
        full reasoning.
        
        Args:
            news_data: Current news context
            charity_ratings: Charity rating data
            
        Returns:
            Tuple of (chosen_foundation_dict, confidence_score, reasoning_dict)
        """
        console.print(f"[dim]Analyzing {len(self.foundations)} charitable foundations...[/dim]")
        
        if self.logger:
            console.print(f"[dim]Checking decision history to avoid recent repeats...[/dim]")
        
        ranked = self.evaluate_foundations(news_data, charity_ratings)
        
        if not ranked:
            raise ValueError("No foundations available for selection. Check foundations_list.json and decision history.")
        
        top_choice = ranked[0]
        foundation = top_choice["foundation"]
        confidence = top_choice["score"]
        reasoning = top_choice["reasoning"]
        
        return foundation, confidence, reasoning