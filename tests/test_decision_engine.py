"""
tests/test_decision_engine.py

Unit tests for the decision engine.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path

from agent.decision_engine import DecisionEngine
from agent.logger import DecisionLogger


class TestDecisionEngine:
    """Test cases for DecisionEngine."""
    
    @pytest.fixture
    def sample_foundations(self, tmp_path):
        """Create a sample foundations file for testing."""
        foundations = [
            {
                "id": "test_climate",
                "name": "Test Climate Org",
                "cause_area": "climate",
                "impact_score": 9.0,
                "description": "Test description.",
                "website": "https://test.org",
                "founded_year": 2000
            },
            {
                "id": "test_education",
                "name": "Test Education Org",
                "cause_area": "education",
                "impact_score": 8.5,
                "description": "Test description.",
                "website": "https://test2.org",
                "founded_year": 2005
            }
        ]
        file_path = tmp_path / "foundations_list.json"
        with open(file_path, 'w') as f:
            json.dump(foundations, f)
        return str(file_path)
    
    @pytest.fixture
    def sample_config(self):
        """Create a sample config for testing."""
        return {
            "preferred_causes": ["climate"],
            "max_repeat_skip": 3,
            "pitch_tone": "auto"
        }
    
    def test_load_foundations(self, sample_config, sample_foundations):
        """Test that foundations are loaded correctly."""
        engine = DecisionEngine(sample_config, foundations_path=sample_foundations)
        assert len(engine.foundations) == 2
        assert engine.foundations[0]["name"] == "Test Climate Org"
    
    def test_cause_alignment_preferred(self, sample_config, sample_foundations):
        """Test that preferred causes get high alignment."""
        engine = DecisionEngine(sample_config, foundations_path=sample_foundations)
        foundation = {"cause_area": "climate"}
        score = engine._calculate_cause_alignment(foundation)
        assert score >= 0.95  # Should be near 1.0
    
    def test_cause_alignment_non_preferred(self, sample_config, sample_foundations):
        """Test that non-preferred causes get lower alignment."""
        engine = DecisionEngine(sample_config, foundations_path=sample_foundations)
        foundation = {"cause_area": "animal_welfare"}
        score = engine._calculate_cause_alignment(foundation)
        assert score < 0.5  # Should be lower
    
    def test_news_relevance_with_matching_articles(self, sample_config, sample_foundations):
        """Test news relevance calculation with matching articles."""
        engine = DecisionEngine(sample_config, foundations_path=sample_foundations)
        foundation = {"cause_area": "climate"}
        news_data = {
            "articles": [
                {"title": "Climate Summit", "description": "Major climate news"},
                {"title": "Other News", "description": "Something else"}
            ]
        }
        score = engine._calculate_news_relevance(foundation, news_data)
        assert score > 0.5  # Should have some relevance
        assert score <= 0.95  # Should be capped
    
    def test_news_relevance_no_articles(self, sample_config, sample_foundations):
        """Test news relevance with no articles."""
        engine = DecisionEngine(sample_config, foundations_path=sample_foundations)
        foundation = {"cause_area": "climate"}
        news_data = {"articles": []}
        score = engine._calculate_news_relevance(foundation, news_data)
        assert score == 0.5  # Neutral baseline
    
    def test_evaluate_foundations_returns_ranked_list(self, sample_config, sample_foundations):
        """Test that foundation evaluation returns sorted list."""
        engine = DecisionEngine(sample_config, foundations_path=sample_foundations)
        news_data = {"articles": []}
        charity_ratings = {"ratings": {}}
        
        ranked = engine.evaluate_foundations(news_data, charity_ratings)
        assert len(ranked) == 2
        # Climate should rank higher due to preferred cause
        assert ranked[0]["foundation"]["cause_area"] == "climate"
    
    def test_make_decision_returns_tuple(self, sample_config, sample_foundations):
        """Test that make_decision returns correct tuple structure."""
        engine = DecisionEngine(sample_config, foundations_path=sample_foundations)
        news_data = {"articles": []}
        charity_ratings = {"ratings": {}}
        
        foundation, confidence, reasoning = engine.make_decision(news_data, charity_ratings)
        assert isinstance(foundation, dict)
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1
        assert isinstance(reasoning, dict)
        assert "cause_alignment" in reasoning
        assert "impact_score" in reasoning
        assert "final_score" in reasoning