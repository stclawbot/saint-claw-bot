"""
agent/logger.py

Decision logging module for Saint Claw Bot.
Handles persistent storage of all donation decisions in JSON format.

Author: Saint Claw Bot
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console

console = Console()


class DecisionLogger:
    """
    Handles logging of donation decisions to a JSON file.
    
    This class ensures every decision made by Saint Claw Bot is
    persistently stored with full context, enabling audit trails
    and historical analysis.
    """
    
    def __init__(self, log_file_path: str = "data/decision_log.json") -> None:
        """
        Initialize the DecisionLogger.
        
        Args:
            log_file_path: Path to the JSON log file. Creates parent
                directories if they don't exist.
        """
        self.log_file_path = Path(log_file_path)
        # Ensure the data directory exists
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
    def _load_existing_logs(self) -> List[Dict[str, Any]]:
        """
        Load existing decision logs from file.
        
        Returns:
            List of existing log entries, or empty list if file
            doesn't exist or is corrupted.
        """
        if not self.log_file_path.exists():
            return []
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            # Log the error but don't crash — return empty list
            console.print(f"[yellow]Warning: Could not read log file: {e}[/yellow]")
            return []
    
    def log_decision(
        self,
        chosen_foundation: str,
        cause_area: str,
        confidence_score: float,
        reasoning: Dict[str, Any],
        pitch: str,
        data_sources_used: List[str]
    ) -> None:
        """
        Log a donation decision to the JSON file.
        
        Creates a structured log entry with timestamp and all
        decision context, then appends it to the existing log.
        Never overwrites — always appends.
        
        Args:
            chosen_foundation: Name of the selected charity
            cause_area: Category of the cause (e.g., 'climate', 'education')
            confidence_score: Final confidence score (0.0–1.0)
            reasoning: Dictionary containing detailed scoring breakdown
            pitch: The generated pitch text
            data_sources_used: List of data sources referenced
        """
        # Create the log entry with ISO format timestamp
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "chosen_foundation": chosen_foundation,
            "cause_area": cause_area,
            "confidence_score": round(confidence_score, 3),
            "reasoning": reasoning,
            "pitch": pitch,
            "data_sources_used": data_sources_used
        }
        
        # Load existing logs (or start fresh)
        logs = self._load_existing_logs()
        
        # Append the new decision
        logs.append(log_entry)
        
        # Write back to file with pretty formatting for readability
        try:
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
            console.print(f"[green]✅ Decision logged to {self.log_file_path}[/green]")
        except IOError as e:
            console.print(f"[red]Error: Failed to write log file: {e}[/red]")
            raise
    
    def get_recent_decisions(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve the most recent decisions from the log.
        
        Useful for checking if a foundation was recently selected
        to avoid repetitive donations.
        
        Args:
            count: Number of recent decisions to retrieve
            
        Returns:
            List of the most recent log entries, most recent first
        """
        logs = self._load_existing_logs()
        # Return the last 'count' entries, reversed to show newest first
        return logs[-count:] if logs else []
    
    def was_recently_chosen(self, foundation_name: str, skip_count: int = 3) -> bool:
        """
        Check if a foundation was chosen in the last N decisions.
        
        This prevents the bot from selecting the same charity
        repeatedly, ensuring diverse giving.
        
        Args:
            foundation_name: Name of the foundation to check
            skip_count: How many recent decisions to look back
            
        Returns:
            True if the foundation was chosen in the last skip_count decisions
        """
        recent = self.get_recent_decisions(skip_count)
        # Check if this foundation appears in recent decisions
        for decision in recent:
            if decision.get("chosen_foundation") == foundation_name:
                return True
        return False