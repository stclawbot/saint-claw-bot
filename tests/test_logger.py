"""
tests/test_logger.py

Unit tests for the decision logger.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path

from agent.logger import DecisionLogger


class TestDecisionLogger:
    """Test cases for DecisionLogger."""
    
    @pytest.fixture
    def temp_log_file(self, tmp_path):
        """Create a temporary log file path."""
        return str(tmp_path / "test_decisions.json")
    
    def test_log_decision_creates_file(self, temp_log_file):
        """Test that logging creates the file if it doesn't exist."""
        logger = DecisionLogger(log_file_path=temp_log_file)
        logger.log_decision(
            chosen_foundation="Test Foundation",
            cause_area="climate",
            confidence_score=0.85,
            reasoning={"test": "data"},
            pitch="Test pitch",
            data_sources_used=["test"]
        )
        assert os.path.exists(temp_log_file)
    
    def test_log_decision_appends(self, temp_log_file):
        """Test that logging appends rather than overwrites."""
        logger = DecisionLogger(log_file_path=temp_log_file)
        
        # Log first decision
        logger.log_decision(
            chosen_foundation="Foundation 1",
            cause_area="climate",
            confidence_score=0.85,
            reasoning={},
            pitch="Pitch 1",
            data_sources_used=[]
        )
        
        # Log second decision
        logger.log_decision(
            chosen_foundation="Foundation 2",
            cause_area="education",
            confidence_score=0.90,
            reasoning={},
            pitch="Pitch 2",
            data_sources_used=[]
        )
        
        # Check both are in file
        with open(temp_log_file, 'r') as f:
            logs = json.load(f)
        assert len(logs) == 2
        assert logs[0]["chosen_foundation"] == "Foundation 1"
        assert logs[1]["chosen_foundation"] == "Foundation 2"
    
    def test_get_recent_decisions(self, temp_log_file):
        """Test retrieving recent decisions."""
        logger = DecisionLogger(log_file_path=temp_log_file)
        
        # Log multiple decisions
        for i in range(5):
            logger.log_decision(
                chosen_foundation=f"Foundation {i}",
                cause_area="climate",
                confidence_score=0.8,
                reasoning={},
                pitch=f"Pitch {i}",
                data_sources_used=[]
            )
        
        recent = logger.get_recent_decisions(count=3)
        assert len(recent) == 3
        # Most recent first (by array order)
        assert recent[0]["chosen_foundation"] == "Foundation 4"
        assert recent[2]["chosen_foundation"] == "Foundation 2"
    
    def test_was_recently_chosen_true(self, temp_log_file):
        """Test that was_recently_chosen returns True for recent foundations."""
        logger = DecisionLogger(log_file_path=temp_log_file)
        
        logger.log_decision(
            chosen_foundation="Recent Foundation",
            cause_area="climate",
            confidence_score=0.8,
            reasoning={},
            pitch="Test",
            data_sources_used=[]
        )
        
        assert logger.was_recently_chosen("Recent Foundation", skip_count=3) is True
    
    def test_was_recently_chosen_false(self, temp_log_file):
        """Test that was_recently_chosen returns False for older foundations."""
        logger = DecisionLogger(log_file_path=temp_log_file)
        
        # Log some decisions
        for i in range(5):
            logger.log_decision(
                chosen_foundation=f"Foundation {i}",
                cause_area="climate",
                confidence_score=0.8,
                reasoning={},
                pitch="Test",
                data_sources_used=[]
            )
        
        # Foundation 0 is 5 decisions back, outside skip_count=3
        assert logger.was_recently_chosen("Foundation 0", skip_count=3) is False
    
    def test_log_entry_structure(self, temp_log_file):
        """Test that log entries have all required fields."""
        logger = DecisionLogger(log_file_path=temp_log_file)
        
        logger.log_decision(
            chosen_foundation="Test Foundation",
            cause_area="climate",
            confidence_score=0.85,
            reasoning={"cause_alignment": 0.9},
            pitch="Test pitch content",
            data_sources_used=["newsapi", "charity_navigator"]
        )
        
        with open(temp_log_file, 'r') as f:
            logs = json.load(f)
        
        entry = logs[0]
        assert "timestamp" in entry
        assert entry["chosen_foundation"] == "Test Foundation"
        assert entry["cause_area"] == "climate"
        assert entry["confidence_score"] == 0.85
        assert "reasoning" in entry
        assert entry["pitch"] == "Test pitch content"
        assert "data_sources_used" in entry