"""
agent/config_validator.py

Configuration validation module for Saint Claw Bot.
Ensures all required config fields are present and valid before execution.

Author: Saint Claw Bot
"""

from typing import Dict, Any, List
from pathlib import Path


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigValidator:
    """
    Validates Saint Claw Bot configuration.
    
    Checks for required fields, valid values, and proper structure
    before the bot attempts to run. Provides clear error messages
    for configuration issues.
    """
    
    # Valid cause areas that exist in foundations_list.json
    VALID_CAUSES = [
        "climate", "education", "global_health", "hunger",
        "clean_water", "animal_welfare", "mental_health", "disaster_relief"
    ]
    
    # Valid configuration options
    VALID_DECISION_FREQUENCIES = ["daily", "weekly"]
    VALID_PITCH_TONES = ["auto", "urgent", "hopeful"]
    
    # Required fields with their expected types
    REQUIRED_FIELDS = {
        "preferred_causes": list,
        "decision_frequency": str,
        "max_repeat_skip": int,
        "pitch_tone": str
    }
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the validator with configuration.
        
        Args:
            config: Configuration dictionary to validate
        """
        self.config = config
        self.errors: List[str] = []
    
    def validate(self) -> bool:
        """
        Run all validation checks.
        
        Returns:
            True if config is valid
            
        Raises:
            ConfigValidationError: If validation fails with detailed error message
        """
        self.errors = []
        
        self._validate_required_fields()
        self._validate_preferred_causes()
        self._validate_decision_frequency()
        self._validate_max_repeat_skip()
        self._validate_pitch_tone()
        
        if self.errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in self.errors)
            raise ConfigValidationError(error_msg)
        
        return True
    
    def _validate_required_fields(self) -> None:
        """Check that all required fields exist with correct types."""
        for field, expected_type in self.REQUIRED_FIELDS.items():
            if field not in self.config:
                self.errors.append(f"Missing required field: '{field}'")
                continue
            
            value = self.config[field]
            if not isinstance(value, expected_type):
                self.errors.append(
                    f"Field '{field}' must be {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
    
    def _validate_preferred_causes(self) -> None:
        """Validate preferred_causes list."""
        if "preferred_causes" not in self.config:
            return
        
        causes = self.config["preferred_causes"]
        
        if not causes:
            self.errors.append("preferred_causes cannot be empty")
            return
        
        if not isinstance(causes, list):
            return  # Type error already caught above
        
        invalid_causes = []
        for cause in causes:
            if not isinstance(cause, str):
                self.errors.append(f"All items in preferred_causes must be strings, found: {type(cause).__name__}")
                continue
            if cause.lower() not in self.VALID_CAUSES:
                invalid_causes.append(cause)
        
        if invalid_causes:
            valid_list = ", ".join(self.VALID_CAUSES)
            self.errors.append(
                f"Invalid cause(s) in preferred_causes: {', '.join(invalid_causes)}. "
                f"Valid options: {valid_list}"
            )
    
    def _validate_decision_frequency(self) -> None:
        """Validate decision_frequency value."""
        if "decision_frequency" not in self.config:
            return
        
        freq = self.config["decision_frequency"]
        if not isinstance(freq, str):
            return  # Type error already caught
        
        if freq not in self.VALID_DECISION_FREQUENCIES:
            valid_list = ", ".join(self.VALID_DECISION_FREQUENCIES)
            self.errors.append(
                f"Invalid decision_frequency: '{freq}'. Must be one of: {valid_list}"
            )
    
    def _validate_max_repeat_skip(self) -> None:
        """Validate max_repeat_skip value."""
        if "max_repeat_skip" not in self.config:
            return
        
        skip = self.config["max_repeat_skip"]
        if not isinstance(skip, int):
            return  # Type error already caught
        
        if skip < 0:
            self.errors.append("max_repeat_skip must be non-negative")
        elif skip > 10:
            self.errors.append("max_repeat_skip should be 10 or less (recommend 1-5)")
    
    def _validate_pitch_tone(self) -> None:
        """Validate pitch_tone value."""
        if "pitch_tone" not in self.config:
            return
        
        tone = self.config["pitch_tone"]
        if not isinstance(tone, str):
            return  # Type error already caught
        
        if tone not in self.VALID_PITCH_TONES:
            valid_list = ", ".join(self.VALID_PITCH_TONES)
            self.errors.append(
                f"Invalid pitch_tone: '{tone}'. Must be one of: {valid_list}"
            )
    
    @staticmethod
    def validate_foundations_file(path: str = "foundations/foundations_list.json") -> bool:
        """
        Validate that foundations file exists and is readable.
        
        Args:
            path: Path to foundations JSON file
            
        Returns:
            True if file exists
            
        Raises:
            ConfigValidationError: If file doesn't exist
        """
        if not Path(path).exists():
            raise ConfigValidationError(
                f"Foundations file not found: {path}\n"
                "Run the bot from the project root directory."
            )
        return True