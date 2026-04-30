"""
tests/test_config_validator.py

Unit tests for configuration validation.
"""

import pytest
from agent.config_validator import ConfigValidator, ConfigValidationError


class TestConfigValidator:
    """Test cases for ConfigValidator."""
    
    def test_valid_config_passes(self):
        """Test that a valid configuration passes validation."""
        config = {
            "preferred_causes": ["climate", "education"],
            "decision_frequency": "daily",
            "max_repeat_skip": 3,
            "pitch_tone": "auto"
        }
        validator = ConfigValidator(config)
        assert validator.validate() is True
    
    def test_missing_required_field(self):
        """Test that missing required fields raise error."""
        config = {
            "preferred_causes": ["climate"],
            "max_repeat_skip": 3,
            "pitch_tone": "auto"
        }
        validator = ConfigValidator(config)
        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate()
        assert "decision_frequency" in str(exc_info.value)
    
    def test_invalid_cause(self):
        """Test that invalid causes are rejected."""
        config = {
            "preferred_causes": ["invalid_cause"],
            "decision_frequency": "daily",
            "max_repeat_skip": 3,
            "pitch_tone": "auto"
        }
        validator = ConfigValidator(config)
        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate()
        assert "invalid_cause" in str(exc_info.value)
    
    def test_empty_preferred_causes(self):
        """Test that empty preferred_causes list is rejected."""
        config = {
            "preferred_causes": [],
            "decision_frequency": "daily",
            "max_repeat_skip": 3,
            "pitch_tone": "auto"
        }
        validator = ConfigValidator(config)
        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate()
        assert "cannot be empty" in str(exc_info.value)
    
    def test_invalid_decision_frequency(self):
        """Test that invalid decision_frequency is rejected."""
        config = {
            "preferred_causes": ["climate"],
            "decision_frequency": "monthly",
            "max_repeat_skip": 3,
            "pitch_tone": "auto"
        }
        validator = ConfigValidator(config)
        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate()
        assert "monthly" in str(exc_info.value)
    
    def test_invalid_pitch_tone(self):
        """Test that invalid pitch_tone is rejected."""
        config = {
            "preferred_causes": ["climate"],
            "decision_frequency": "daily",
            "max_repeat_skip": 3,
            "pitch_tone": "excited"
        }
        validator = ConfigValidator(config)
        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate()
        assert "excited" in str(exc_info.value)
    
    def test_negative_max_repeat_skip(self):
        """Test that negative max_repeat_skip is rejected."""
        config = {
            "preferred_causes": ["climate"],
            "decision_frequency": "daily",
            "max_repeat_skip": -1,
            "pitch_tone": "auto"
        }
        validator = ConfigValidator(config)
        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate()
        assert "non-negative" in str(exc_info.value)
    
    def test_max_repeat_skip_too_high(self):
        """Test that very high max_repeat_skip warns."""
        config = {
            "preferred_causes": ["climate"],
            "decision_frequency": "daily",
            "max_repeat_skip": 15,
            "pitch_tone": "auto"
        }
        validator = ConfigValidator(config)
        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate()
        assert "10 or less" in str(exc_info.value)
    
    def test_wrong_type_for_causes(self):
        """Test that wrong type for preferred_causes is rejected."""
        config = {
            "preferred_causes": "climate",  # Should be list
            "decision_frequency": "daily",
            "max_repeat_skip": 3,
            "pitch_tone": "auto"
        }
        validator = ConfigValidator(config)
        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate()
        assert "list" in str(exc_info.value)