"""
agent/pitcher.py

Pitch generation module for Saint Claw Bot.
Creates compelling, emotionally resonant donation pitches using
OpenAI for dynamic generation with template fallback.

Author: Saint Claw Bot
"""

import os
from typing import Dict, Any, Optional, List

from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console

# Load environment variables
load_dotenv()

console = Console()


class PitchGenerator:
    """
    Generates human-readable donation pitches using AI.
    
    Uses OpenAI's GPT model to create dynamic, contextually-aware
    pitches when API key is available. Falls back to sophisticated
    templates when OpenAI is unavailable.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the PitchGenerator.
        
        Args:
            config: Configuration dictionary containing pitch_tone setting
        """
        self.config = config
        self.pitch_tone = config.get("pitch_tone", "auto")
        self.openai_client: Optional[OpenAI] = None
        
        # Initialize OpenAI client if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_key_here":
            try:
                self.openai_client = OpenAI(api_key=api_key)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not initialize OpenAI: {e}[/yellow]")
    
    def _determine_tone(self, news_data: Dict[str, Any]) -> str:
        """
        Determine the appropriate tone for the pitch.
        
        If pitch_tone is set to "auto", analyzes news data to
        determine if the context calls for urgent or hopeful tone.
        Uses semantic analysis instead of simple keyword matching.
        
        Args:
            news_data: Current news context
            
        Returns:
            Tone string: "urgent" or "hopeful"
        """
        if self.pitch_tone != "auto":
            return self.pitch_tone
        
        articles = news_data.get("articles", [])
        if not articles:
            return "hopeful"
        
        # Urgency indicators with weighted severity
        urgency_patterns = {
            "critical": 3, "emergency": 3, "crisis": 3, "catastrophic": 3,
            "famine": 3, "epidemic": 3, "pandemic": 3, "disaster": 2,
            "urgent": 2, "severe": 2, "devastating": 2, "outbreak": 2,
            "war": 2, "conflict": 2, "breaking": 1, "critical": 1
        }
        
        urgency_score = 0
        total_weight = 0
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}".lower()
            for pattern, weight in urgency_patterns.items():
                if pattern in text:
                    urgency_score += weight
                    total_weight += 3  # Max weight per article
        
        # Normalize and threshold
        if total_weight > 0:
            normalized = urgency_score / total_weight
            return "urgent" if normalized > 0.3 else "hopeful"
        
        return "hopeful"
    
    def _build_system_prompt(self, tone: str) -> str:
        """
        Build the system prompt for OpenAI based on tone.
        
        Args:
            tone: Either "urgent" or "hopeful"
            
        Returns:
            System prompt string
        """
        base_prompt = """You are Saint Claw Bot, an AI that creates compelling donation pitches.
Your pitches are:
- 3-5 sentences long
- Emotionally resonant and authentic
- Specific to the foundation and current context
- Written to inspire immediate action
- Shareable on social media
- Free of generic platitudes"""
        
        if tone == "urgent":
            return base_prompt + """

TONE: URGENT - Create a sense of immediacy and moral obligation. The situation needs attention NOW.
Emphasize: timeliness, critical need, direct impact, the cost of inaction."""
        else:
            return base_prompt + """

TONE: HOPEFUL - Emphasize progress, possibility, and building a better future.
Emphasize: proven solutions, lasting change, collective impact, optimism."""
    
    def _build_user_prompt(
        self,
        foundation: Dict[str, Any],
        news_data: Dict[str, Any],
        reasoning: Dict[str, Any]
    ) -> str:
        """
        Build the user prompt with foundation and context data.
        
        Args:
            foundation: Selected foundation data
            news_data: Current news context
            reasoning: Decision reasoning
            
        Returns:
            User prompt string
        """
        # Extract relevant news snippets
        news_snippets = []
        for article in news_data.get("articles", [])[:3]:
            title = article.get("title", "")
            desc = article.get("description", "")
            if title or desc:
                news_snippets.append(f"- {title}: {desc}")
        
        news_context = "\n".join(news_snippets) if news_snippets else "No specific current events."
        
        prompt = f"""Create a donation pitch for this foundation:

FOUNDATION: {foundation.get("name", "Unknown")}
CAUSE: {foundation.get("cause_area", "Unknown").replace("_", " ").title()}
IMPACT SCORE: {foundation.get("impact_score", "N/A")}/10
DESCRIPTION: {foundation.get("description", "No description")}
WEBSITE: {foundation.get("website", "N/A")}
FOUNDED: {foundation.get("founded_year", "Unknown")}

CURRENT NEWS CONTEXT:
{news_context}

SELECTION REASONING:
- Cause Alignment: {reasoning.get("cause_alignment", 0):.0%}
- Impact Score: {reasoning.get("impact_score", 0):.0%}
- News Relevance: {reasoning.get("news_relevance", 0):.0%}

Write a compelling 3-5 sentence pitch that explains WHY this foundation was chosen based on current events and their impact. Make it specific, authentic, and inspiring."""
        
        return prompt
    
    def _generate_openai_pitch(
        self,
        foundation: Dict[str, Any],
        news_data: Dict[str, Any],
        reasoning: Dict[str, Any],
        tone: str
    ) -> Optional[str]:
        """
        Generate pitch using OpenAI API.
        
        Args:
            foundation: Selected foundation data
            news_data: Current news context
            reasoning: Decision reasoning
            tone: Desired tone
            
        Returns:
            Generated pitch or None if API call fails
        """
        if not self.openai_client:
            return None
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self._build_system_prompt(tone)},
                    {"role": "user", "content": self._build_user_prompt(foundation, news_data, reasoning)}
                ],
                max_tokens=250,
                temperature=0.7
            )
            
            pitch = response.choices[0].message.content.strip()
            console.print(f"[dim][AI] Pitch generated via OpenAI ({tone} tone)[/dim]")
            return pitch
            
        except Exception as e:
            console.print(f"[yellow]OpenAI pitch generation failed: {e}[/yellow]")
            return None
    
    def _generate_template_pitch(
        self,
        foundation: Dict[str, Any],
        news_data: Dict[str, Any],
        tone: str
    ) -> str:
        """
        Generate pitch using sophisticated templates (fallback).
        
        Args:
            foundation: Selected foundation data
            news_data: Current news context
            tone: Desired tone
            
        Returns:
            Template-generated pitch
        """
        name = foundation.get("name", "This organization")
        cause = foundation.get("cause_area", "this cause")
        description = foundation.get("description", "")
        founded = foundation.get("founded_year", "")
        
        # Extract first sentence
        first_sentence = description.split('.')[0] + '.' if description else ""
        
        # Get relevant news hook if available
        news_hook = ""
        articles = news_data.get("articles", [])
        if articles:
            # Find most relevant article
            cause_keywords = {
                "climate": ["climate", "carbon", "emissions", "warming"],
                "education": ["education", "school", "literacy", "students"],
                "global_health": ["health", "medical", "disease", "vaccine"],
                "hunger": ["hunger", "food", "famine", "nutrition"],
                "clean_water": ["water", "sanitation", "drinking"],
                "animal_welfare": ["animal", "wildlife", "conservation"],
                "mental_health": ["mental health", "depression", "anxiety"],
                "disaster_relief": ["disaster", "emergency", "earthquake"]
            }
            
            keywords = cause_keywords.get(cause.lower(), [cause.lower()])
            
            for article in articles:
                text = f"{article.get('title', '')} {article.get('description', '')}".lower()
                if any(kw in text for kw in keywords):
                    news_hook = article.get("description", "")[:150]
                    if news_hook:
                        news_hook += "..." if len(news_hook) == 150 else ""
                    break
        
        # Historical context
        history_text = ""
        if founded:
            years_active = 2025 - founded
            history_text = f"For {years_active} years, they've proven that lasting change is possible. "
        
        if tone == "urgent":
            if news_hook:
                return f"{name} is responding to urgent needs right now. {first_sentence} With {news_hook} your immediate support can make a critical difference. This is the moment to act — every contribution goes directly where it's needed most."
            else:
                return f"Right now, {name} is on the front lines of {cause.replace('_', ' ')}. {first_sentence} The situation demands immediate action, and your donation doesn't just help — it saves lives. This is the moment to make your impact felt."
        else:  # hopeful
            if history_text:
                return f"{name} is building something extraordinary. {first_sentence} {history_text}When you support them, you're investing in proven solutions that multiply over time. This is what meaningful progress looks like."
            else:
                return f"Imagine a world where {cause.replace('_', ' ')} is no longer a crisis. {name} is making that future real. {first_sentence} Your donation fuels solutions that create lasting change for generations to come."
    
    def generate_pitch(
        self,
        foundation: Dict[str, Any],
        news_data: Dict[str, Any],
        reasoning: Dict[str, Any]
    ) -> str:
        """
        Generate a donation pitch for the chosen foundation.
        
        Attempts OpenAI generation first, falls back to templates
        if unavailable. Determines tone based on news context.
        
        Args:
            foundation: Selected foundation dictionary
            news_data: Current news context
            reasoning: Decision reasoning for context
            
        Returns:
            Generated pitch string (3-5 sentences)
        """
        tone = self._determine_tone(news_data)
        
        # Try OpenAI first
        pitch = self._generate_openai_pitch(foundation, news_data, reasoning, tone)
        
        # Fall back to templates if OpenAI fails
        if pitch is None:
            console.print(f"[dim][Template] Generating {tone}-tone pitch...[/dim]")
            pitch = self._generate_template_pitch(foundation, news_data, tone)
        
        return pitch