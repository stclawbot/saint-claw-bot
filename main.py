"""
main.py

Entry point for Saint Claw Bot.
Runs the complete donation decision pipeline with rich terminal output.

Author: Saint Claw Bot
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from agent.config_validator import ConfigValidator, ConfigValidationError
from agent.data_fetcher import DataFetcher
from agent.decision_engine import DecisionEngine
from agent.logger import DecisionLogger
from agent.pitcher import PitchGenerator

# Load environment variables from .env file
load_dotenv()

console = Console()


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration values
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config contains invalid YAML
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if config is None:
                console.print("[red]Error: Config file is empty[/red]")
                return {}
            return config
    except FileNotFoundError:
        console.print(f"[red]Error: Config file not found: {config_path}[/red]")
        raise
    except yaml.YAMLError as e:
        console.print(f"[red]Error: Invalid YAML in config: {e}[/red]")
        raise


def print_banner() -> None:
    """Print the Saint Claw Bot startup banner with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    banner_text = Text()
    banner_text.append("╔══════════════════════════════════════════════════════════════════╗\n", style="bold cyan")
    banner_text.append("║                 🙏 SAINT CLAW BOT 🙏                             ║\n", style="bold cyan")
    banner_text.append("║                                                                  ║\n", style="bold cyan")
    banner_text.append("║     An AI that decides where to give, and tells you exactly why  ║\n", style="cyan")
    banner_text.append("╚══════════════════════════════════════════════════════════════════╝", style="bold cyan")
    
    console.print(banner_text)
    console.print(f"\n⚡ [bold]Saint Claw Bot is thinking...[/bold] {timestamp}\n")


def print_decision_result(
    foundation: Dict[str, Any],
    confidence: float,
    reasoning: Dict[str, Any],
    pitch: str
) -> None:
    """
    Print a beautifully formatted decision result.
    
    Args:
        foundation: Selected foundation data
        confidence: Confidence score (0.0-1.0)
        reasoning: Decision reasoning breakdown
        pitch: Generated pitch text
    """
    # Main decision panel
    decision_table = Table(show_header=False, box=None, padding=(0, 2))
    decision_table.add_column("Label", style="bold cyan", width=15)
    decision_table.add_column("Value", style="white")
    
    decision_table.add_row("Foundation:", foundation.get("name", "Unknown"))
    decision_table.add_row("Cause:", foundation.get("cause_area", "Unknown").replace("_", " ").title())
    decision_table.add_row("Confidence:", f"{confidence:.1%}")
    
    console.print(Panel(
        decision_table,
        title="🎯 DECISION",
        border_style="green",
        padding=(1, 2)
    ))
    
    # Reasoning panel
    weights = reasoning.get("weights_applied", {})
    reasoning_table = Table(show_header=False, box=None, padding=(0, 2))
    reasoning_table.add_column("Factor", style="dim", width=25)
    reasoning_table.add_column("Score", style="white")
    
    cause_pct = weights.get("cause_alignment", 0.30) * 100
    impact_pct = weights.get("impact_score", 0.40) * 100
    news_pct = weights.get("news_relevance", 0.30) * 100
    
    reasoning_table.add_row(
        f"Cause Alignment ({cause_pct:.0f}%):",
        f"{reasoning.get('cause_alignment', 0):.0%} — aligned with preferences"
    )
    reasoning_table.add_row(
        f"Impact Score ({impact_pct:.0f}%):",
        f"{reasoning.get('impact_score', 0):.0%} — exceptional effectiveness"
    )
    reasoning_table.add_row(
        f"News Relevance ({news_pct:.0f}%):",
        f"{reasoning.get('news_relevance', 0):.0%} — current event relevance"
    )
    reasoning_table.add_row("", "")
    reasoning_table.add_row("Final Score:", f"[bold green]{reasoning.get('final_score', 0):.1%}[/bold green]")
    
    console.print(Panel(
        reasoning_table,
        title="🧠 REASONING",
        border_style="blue",
        padding=(1, 2)
    ))
    
    # Pitch panel
    console.print(Panel(
        pitch,
        title="💬 PITCH",
        border_style="yellow",
        padding=(1, 2)
    ))
    
    # Details panel
    details_table = Table(show_header=False, box=None, padding=(0, 2))
    details_table.add_column("Label", style="dim", width=15)
    details_table.add_column("Value", style="white")
    
    details_table.add_row("Website:", foundation.get("website", "N/A"))
    details_table.add_row("Impact Score:", f"{foundation.get('impact_score', 0)}/10.0")
    details_table.add_row("Founded:", str(foundation.get("founded_year", "N/A")))
    
    console.print(Panel(
        details_table,
        title="📊 DETAILS",
        border_style="magenta",
        padding=(1, 2)
    ))


def main() -> None:
    """
    Main entry point for Saint Claw Bot.
    
    Runs the complete pipeline: load config → fetch data → make decision →
    generate pitch → log result → display output.
    """
    try:
        # Print startup banner
        print_banner()
        
        # Step 1: Load and validate configuration
        console.print("[dim]Loading configuration from config.yaml...[/dim]")
        config = load_config()
        
        # Validate config before proceeding
        console.print("[dim]Validating configuration...[/dim]")
        validator = ConfigValidator(config)
        validator.validate()
        ConfigValidator.validate_foundations_file()
        
        # Step 2: Initialize components
        logger = DecisionLogger()
        data_fetcher = DataFetcher()
        decision_engine = DecisionEngine(config, logger=logger)
        pitcher = PitchGenerator(config)
        
        # Step 3: Fetch live data
        preferred_causes = config.get("preferred_causes", [])
        console.print(f"[dim]Fetching current news for: {', '.join(preferred_causes)}...[/dim]")
        news_data = data_fetcher.fetch_news(preferred_causes)
        
        console.print("[dim]Fetching charity ratings...[/dim]")
        charity_ratings = data_fetcher.fetch_charity_ratings()
        
        # Step 4: Run decision engine
        foundation, confidence, reasoning = decision_engine.make_decision(news_data, charity_ratings)
        
        # Step 5: Generate pitch
        pitch = pitcher.generate_pitch(foundation, news_data, reasoning)
        
        # Step 6: Log the decision
        data_sources = data_fetcher.get_demo_mode_sources()
        if not data_sources:
            data_sources = ["newsapi", "charity_navigator"]
        
        logger.log_decision(
            chosen_foundation=foundation.get("name", "Unknown"),
            cause_area=foundation.get("cause_area", "unknown"),
            confidence_score=confidence,
            reasoning=reasoning,
            pitch=pitch,
            data_sources_used=data_sources
        )
        
        # Step 7: Display rich output
        console.print()  # Spacer
        print_decision_result(foundation, confidence, reasoning, pitch)
        
    except ConfigValidationError as e:
        console.print(f"[red]Configuration Error:[/red]")
        console.print(f"[yellow]{e}[/yellow]")
        raise SystemExit(1)
    except FileNotFoundError as e:
        console.print(f"[red]Setup Error: {e}[/red]")
        console.print("[yellow]Make sure config.yaml and foundations/foundations_list.json exist.[/yellow]")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()