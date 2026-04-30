# Saint Claw Bot

> "An AI that decides where to give, and tells you exactly why."

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What It Does

Saint Claw Bot is an autonomous donation decision engine that intelligently selects charitable foundations based on live data, current events, and a configurable value system. It doesn't just pick a charity — it explains exactly why, generates a compelling pitch, and maintains a transparent decision history. Perfect for donors who want their giving to be data-driven, timely, and impactful.

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        SAINT CLAW BOT                           │
│                                                                 │
│  ┌──────────────┐     ┌──────────────────┐                     │
│  │  Live Data   │────▶│ Decision Engine  │                     │
│  │  Fetcher     │     │                  │                     │
│  └──────────────┘     │ • Score causes   │                     │
│         │             │ • Check history  │                     │
│         │             │ • Rank options   │                     │
│         ▼             └────────┬─────────┘                     │
│  ┌──────────────┐              │                               │
│  │  NewsAPI     │              ▼                               │
│  │  Charity API │     ┌──────────────────┐                     │
│  └──────────────┘     │ Pitch Generator  │                     │
│                       │                  │                     │
│                       │ • Tone-aware     │                     │
│                       │ • Context-aware  │                     │
│                       └────────┬─────────┘                     │
│                                │                               │
│                                ▼                               │
│                       ┌──────────────────┐                     │
│                       │  Decision Log    │                     │
│                       │                  │                     │
│                       │ • Timestamp      │                     │
│                       │ • Reasoning      │                     │
│                       │ • Full audit     │                     │
│                       └──────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/stclawbot/saint-claw-bot.git
   cd saint-claw-bot
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

5. **Customize config.yaml** (optional):
   ```yaml
   preferred_causes:
     - climate
     - education
     - mental_health
   decision_frequency: daily
   pitch_tone: auto
   ```

6. **Run the bot**:
   ```bash
   python main.py
   ```

## Example Output

```
╔══════════════════════════════════════════════════════════════════╗
║                 🙏 SAINT CLAW BOT 🙏                             ║
║                                                                  ║
║     An AI that decides where to give, and tells you exactly why  ║
╚══════════════════════════════════════════════════════════════════╝

⚡ Saint Claw Bot is thinking... 2025-01-15 09:30:42

[DEMO MODE] Using mock data. Set NEWS_API_KEY in .env for live data.
[DEMO MODE] Using mock data. Set CHARITY_API_KEY in .env for live data.

Fetching current news for: climate, education, global_health...
Analyzing 15 charitable foundations...
Checking decision history to avoid recent repeats...

┌─ 🎯 DECISION ─────────────────────────────────────────────────────┐
│                                                                   │
│  Foundation: Doctors Without Borders                              │
│  Cause: Global Health                                             │
│  Confidence: 94.2%                                                │
│                                                                   │
├─ 🧠 REASONING ────────────────────────────────────────────────────┤
│                                                                   │
│  • Cause Alignment (30%): 95/100 — global_health is top priority  │
│  • Impact Score (40%): 93/100 — Exceptional cost-effectiveness    │
│  • News Relevance (30%): 95/100 — Active health crisis coverage   │
│                                                                   │
│  Final Score: 94.2/100                                            │
│                                                                   │
├─ 💬 PITCH ────────────────────────────────────────────────────────┤
│                                                                   │
│  Right now, Doctors Without Borders is on the front lines of      │
│  multiple global health crises. Every dollar you give directly    │
│  funds medical care for people caught in conflicts and            │
│  epidemics — no bureaucracy, no delays, just healing where it's   │
│  needed most. This isn't charity for someday. This is life-saving │
│  action for today.                                                │
│                                                                   │
├─ 📊 DETAILS ──────────────────────────────────────────────────────┤
│                                                                   │
│  Website: https://www.doctorswithoutborders.org                   │
│  Impact Score: 9.3/10.0                                           │
│  Founded: 1971                                                    │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘

✅ Decision logged to data/decision_log.json
```

## Configuration

| Field | Type | Description |
|-------|------|-------------|
| `preferred_causes` | List[str] | Priority causes to consider. Options: climate, education, global_health, hunger, clean_water, animal_welfare, mental_health, disaster_relief |
| `decision_frequency` | String | How often decisions are made: `daily` or `weekly` |
| `max_repeat_skip` | Integer | How many consecutive decisions to skip the same foundation |
| `pitch_tone` | String | Tone of generated pitch: `auto`, `urgent`, or `hopeful` |
| `api_keys` | Section | Environment variable placeholders for NewsAPI, Charity API, and OpenAI |

## Decision Log

Each decision is logged as a structured JSON entry:

```json
{
  "timestamp": "2025-01-15T09:30:42.123456",
  "chosen_foundation": "Doctors Without Borders",
  "cause_area": "global_health",
  "confidence_score": 0.942,
  "reasoning": {
    "cause_alignment": 0.95,
    "impact_score": 0.93,
    "news_relevance": 0.95,
    "final_score": 0.942
  },
  "pitch": "Right now, Doctors Without Borders is on the front lines...",
  "data_sources_used": ["mock_news", "mock_charity_ratings"]
}
```

## Roadmap

- **Portfolio Mode**: Split donations across multiple causes based on percentage weights
- **Community Voting**: Integration with GitHub Discussions for community input on priorities
- **Social Integration**: Auto-post pitches to X/Twitter with donation links
- **Web Dashboard**: Visualize decision history, trends, and impact metrics
- **Recurring Donations**: Integration with payment platforms for automated giving
- **Multi-Currency Support**: Handle donations in various currencies with real-time conversion

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with transparency, data, and a genuine belief that giving should be smarter.*