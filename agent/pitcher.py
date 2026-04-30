"""
agent/pitcher.py

Pitch generation module for Saint Claw Bot.
Creates compelling, emotionally resonant donation pitches
with adjustable tone based on context.

Author: Saint Claw Bot
"""

import os
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from rich.console import Console

# Load environment variables
load_dotenv()

console = Console()


class PitchGenerator:
    """
    Generates human-readable donation pitches.
    
    Creates emotionally compelling, shareable text that explains
    why the chosen foundation matters right now. Adapts tone
    based on configuration and current events.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the PitchGenerator.
        
        Args:
            config: Configuration dictionary containing pitch_tone setting
        """
        self.config = config
        self.pitch_tone = config.get("pitch_tone", "auto")
        
    def _determine_tone(self, news_data: Dict[str, Any]) -> str:
        """
        Determine the appropriate tone for the pitch.
        
        If pitch_tone is set to "auto", analyzes news data to
        determine if the context calls for urgent or hopeful tone.
        
        Args:
            news_data: Current news context
            
        Returns:
            Tone string: "urgent" or "hopeful"
        """
        if self.pitch_tone != "auto":
            return self.pitch_tone
        
        # Analyze news for urgency indicators
        articles = news_data.get("articles", [])
        urgent_keywords = [
            "crisis", "emergency", "disaster", "urgent", "catastrophic",
            "breaking", "critical", "severe", "devastating", "famine",
            "epidemic", "outbreak", "war", "conflict", "urgent need"
        ]
        
        urgency_count = 0
        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}".lower()
            if any(keyword in text for keyword in urgent_keywords):
                urgency_count += 1
        
        # If more than half the articles indicate urgency, use urgent tone
        if articles and urgency_count / len(articles) > 0.5:
            return "urgent"
        
        return "hopeful"
    
    def _generate_urgent_pitch(
        self,
        foundation: Dict[str, Any],
        news_data: Dict[str, Any]
    ) -> str:
        """
        Generate an urgent, call-to-action style pitch.
        
        Use this tone when current events indicate crisis or
        immediate need. Creates a sense of timeliness and
        moral obligation.
        
        Args:
            foundation: Selected foundation dictionary
            news_data: Current news context
            
        Returns:
            Urgent-style pitch string
        """
        name = foundation.get("name", "This organization")
        cause = foundation.get("cause_area", "this cause")
        description = foundation.get("description", "")
        
        # Extract first sentence of description for context
        first_sentence = description.split('.')[0] + '.' if description else ""
        
        urgent_templates = [
            f"Right now, {name} is responding to urgent needs on the ground. {first_sentence} "
            f"The situation is critical, and every moment matters. Your donation doesn't just help — "
            f"it directly saves lives. This is the moment to act.",
            
            f"{name} needs support today. {first_sentence} "
            f"While the headlines capture attention for a moment, the need continues long after. "
            f"Your contribution ensures sustained, immediate impact where it matters most.",
            
            f"There's no time to wait. {name} is on the front lines of {cause}, and the need has never been greater. "
            f"{first_sentence} When you give now, you're part of the solution happening today — not someday."
        ]
        
        # Select template based on foundation characteristics
        if "disaster" in cause.lower() or "relief" in cause.lower():
            return urgent_templates[0]
        elif "health" in cause.lower():
            return urgent_templates[2]
        else:
            return urgent_templates[1]
    
    def _generate_hopeful_pitch(
        self,
        foundation: Dict[str, Any],
        news_data: Dict[str, Any]
    ) -> str:
        """
        Generate a hopeful, optimistic style pitch.
        
        Use this tone for forward-looking, positive messaging
        that emphasizes progress and possibility.
        
        Args:
            foundation: Selected foundation dictionary
            news_data: Current news context
            
        Returns:
            Hopeful-style pitch string
        """
        name = foundation.get("name", "This organization")
        cause = foundation.get("cause_area", "this cause")
        description = foundation.get("description", "")
        founded = foundation.get("founded_year", "")
        
        # Extract first sentence of description
        first_sentence = description.split('.')[0] + '.' if description else ""
        
        # Add historical context if available
        history_text = ""
        if founded:
            years_active = 2025 - founded
            history_text = f"For {years_active} years, they've been proving that lasting change is possible. "
        
        hopeful_templates = [
            f"{name} is building something that lasts. {first_sentence} "
            f"{history_text}Your donation isn't just a gift — it's an investment in a better future. "
            f"Together, we're creating the world we want to see.",
            
            f"Imagine a world where {cause.replace('_', ' ')} is no longer a crisis. "
            f"{name} is making that future real. {first_sentence} "
            f"When you support them, you're not just solving today's problems — you're building tomorrow's solutions.",
            
            f"Real change is happening, and {name} is leading the way. {first_sentence} "
            f"{history_text}Every dollar you give fuels proven solutions that multiply over time. "
            f"This is what progress looks like."
        ]
        
        # Select based on cause type
        if "education" in cause.lower():
            return hopeful_templates[1]
        elif "climate" in cause.lower():
            return hopeful_templates[2]
        else:
            return hopeful_templates[0]
    
    def generate_pitch(
        self,
        foundation: Dict[str, Any],
        news_data: Dict[str, Any],
        reasoning: Dict[str, Any]
    ) -> str:
        """
        Generate a donation pitch for the chosen foundation.
        
        Determines appropriate tone and generates a compelling,
        contextually relevant pitch.
        
        Args:
            foundation: Selected foundation dictionary
            news_data: Current news context
            reasoning: Decision reasoning for context
            
        Returns:
            Generated pitch string (3-5 sentences)
        """
        tone = self._determine_tone(news_data)
        
        console.print(f"[dim]Generating {tone}-tone pitch...[/dim]")
        
        if tone == "urgent":
            pitch = self._generate_urgent_pitch(foundation, news_data)
        else:
            pitch = self._generate_hopeful_pitch(foundation, news_data)
        
        return pitch