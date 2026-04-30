"""
agent/data_fetcher.py

External data fetching module for Saint Claw Bot.
Handles API calls to NewsAPI and charity rating services with
graceful fallback to mock data when APIs are unavailable.

Author: Saint Claw Bot
"""

import os
from typing import Dict, List, Any, Optional

import requests
import yaml
from dotenv import load_dotenv
from rich.console import Console

# Load environment variables from .env file
load_dotenv()

console = Console()


class DataFetcher:
    """
    Fetches live data from external APIs with mock data fallback.
    
    This class handles all external data sources for the bot,
    including current news events and charity impact ratings.
    When API keys are missing or calls fail, it falls back to
    realistic mock data and clearly indicates demo mode.
    """
    
    def __init__(self, config_path: str = "config.yaml") -> None:
        """
        Initialize the DataFetcher with configuration.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        # Track which data sources are in demo mode
        self.demo_mode_sources: List[str] = []
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Returns:
            Dictionary containing configuration values
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            console.print(f"[red]Error: Config file not found: {self.config_path}[/red]")
            return {}
        except yaml.YAMLError as e:
            console.print(f"[red]Error: Invalid YAML in config: {e}[/red]")
            return {}
    
    def _print_demo_warning(self, source: str) -> None:
        """
        Print a demo mode warning if not already shown for this source.
        
        Args:
            source: Name of the data source in demo mode
        """
        if source not in self.demo_mode_sources:
            console.print(
                f"[yellow][DEMO MODE] Using mock data for {source}. "
                f"Set API key in .env for live data.[/yellow]"
            )
            self.demo_mode_sources.append(source)
    
    def fetch_news(self, keywords: List[str]) -> Dict[str, Any]:
        """
        Fetch current news related to the given keywords.
        
        Attempts to call NewsAPI if NEWS_API_KEY is set. Falls back
        to realistic mock news data if the key is missing or the
        API call fails.
        
        Args:
            keywords: List of cause-related keywords to search for
            
        Returns:
            Dictionary containing news articles and metadata
        """
        api_key = os.getenv("NEWS_API_KEY")
        
        if not api_key or api_key == "your_newsapi_key_here"::
            self._print_demo_warning("NewsAPI")
            return self._get_mock_news(keywords)
        
        try:
            # Build query string from keywords
            query = " OR ".join(keywords)
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "sortBy": "relevancy",
                "language": "en",
                "pageSize": 10,
                "apiKey": api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                return {
                    "source": "newsapi",
                    "articles": data.get("articles", []),
                    "total_results": data.get("totalResults", 0)
                }
            else:
                console.print(f"[yellow]NewsAPI error: {data.get('message')}[/yellow]")
                self._print_demo_warning("NewsAPI")
                return self._get_mock_news(keywords)
                
        except requests.RequestException as e:
            console.print(f"[yellow]NewsAPI request failed: {e}[/yellow]")
            self._print_demo_warning("NewsAPI")
            return self._get_mock_news(keywords)
    
    def _get_mock_news(self, keywords: List[str]) -> Dict[str, Any]:
        """
        Generate realistic mock news data for demo mode.
        
        Creates contextually relevant mock articles based on
        the keywords provided, simulating real news content.
        
        Args:
            keywords: List of cause-related keywords
            
        Returns:
            Dictionary with mock news articles
        """
        # Contextually relevant mock articles based on keywords
        mock_articles = []
        
        if "climate" in keywords:
            mock_articles.append({
                "title": "Global Climate Summit Reaches Historic Agreement on Emissions",
                "description": "World leaders commit to accelerated carbon reduction targets amid rising global temperatures.",
                "publishedAt": "2025-01-14T10:00:00Z",
                "source": {"name": "Environmental News Network"}
            })
        
        if "education" in keywords:
            mock_articles.append({
                "title": "UN Report: 244 Million Children Out of School Worldwide",
                "description": "New data reveals urgent need for education funding in low-income regions.",
                "publishedAt": "2025-01-13T14:30:00Z",
                "source": {"name": "Global Education Watch"}
            })
        
        if "global_health" in keywords or "healthcare" in keywords:
            mock_articles.append({
                "title": "Malaria Vaccine Rollout Shows 75% Efficacy in African Trials",
                "description": "Breakthrough vaccination program could save hundreds of thousands of lives annually.",
                "publishedAt": "2025-01-12T09:15:00Z",
                "source": {"name": "Health Affairs Today"}
            })
        
        if "hunger" in keywords:
            mock_articles.append({
                "title": "WFP Warns of Catastrophic Hunger Crisis in Multiple Regions",
                "description": "Conflict and climate change drive food insecurity to unprecedented levels.",
                "publishedAt": "2025-01-11T16:45:00Z",
                "source": {"name": "Food Security Monitor"}
            })
        
        if "clean_water" in keywords:
            mock_articles.append({
                "title": "New Water Purification Technology Deployed in Rural Communities",
                "description": "Innovative solar-powered systems provide clean drinking water to 50,000 people.",
                "publishedAt": "2025-01-10T11:20:00Z",
                "source": {"name": "Water & Sanitation Weekly"}
            })
        
        # Default article if no specific keywords match
        if not mock_articles:
            mock_articles.append({
                "title": "Philanthropic Giving Reaches Record Highs in 2024",
                "description": "Donors increasingly focused on data-driven impact and measurable outcomes.",
                "publishedAt": "2025-01-09T08:00:00Z",
                "source": {"name": "Philanthropy Today"}
            })
        
        return {
            "source": "mock_news",
            "articles": mock_articles,
            "total_results": len(mock_articles)
        }
    
    def fetch_charity_ratings(self) -> Dict[str, Dict[str, Any]]:
        """
        Fetch charity impact ratings and financial data.
        
        Attempts to call Charity Navigator API if CHARITY_API_KEY is set.
        Falls back to the foundation list's built-in impact scores if
        the API is unavailable.
        
        Returns:
            Dictionary mapping foundation IDs to their ratings data
        """
        api_key = os.getenv("CHARITY_API_KEY")
        
        if not api_key or api_key == "your_charity_navigator_key_here":
            self._print_demo_warning("Charity Ratings")
            return self._get_mock_charity_ratings()
        
        try:
            # Charity Navigator API endpoint (v2)
            # Note: This is a simplified example; real implementation
            # would query specific organizations from foundations_list.json
            url = "https://api.data.charitynavigator.org/v2/Organizations"
            params = {
                "app_id": "saint_claw_bot",
                "app_key": api_key,
                "pageSize": 20
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            organizations = response.json()
            
            ratings = {}
            for org in organizations:
                org_id = org.get("ein", org.get("charityName", "unknown"))
                ratings[org_id] = {
                    "name": org.get("charityName"),
                    "rating": org.get("currentRating", {}).get("rating"),
                    "financial_score": org.get("currentRating", {}).get("financialRating", {}).get("score"),
                    "accountability_score": org.get("currentRating", {}).get("accountabilityRating", {}).get("score")
                }
            
            return {"source": "charity_navigator", "ratings": ratings}
            
        except requests.RequestException as e:
            console.print(f"[yellow]Charity API request failed: {e}[/yellow]")
            self._print_demo_warning("Charity Ratings")
            return self._get_mock_charity_ratings()
    
    def _get_mock_charity_ratings(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate mock charity ratings for demo mode.
        
        In demo mode, we rely on the impact scores already defined
        in foundations_list.json, returning a structure that matches
        what the decision engine expects.
        
        Returns:
            Dictionary indicating mock source and empty ratings
            (decision engine will use foundation list scores)
        """
        return {
            "source": "mock_charity_ratings",
            "ratings": {}
        }
    
    def get_demo_mode_sources(self) -> List[str]:
        """
        Get list of data sources currently in demo mode.
        
        Returns:
            List of source names using mock data
        """
        return self.demo_mode_sources.copy()