# Contributing to Saint Claw Bot

Thank you for your interest in contributing to Saint Claw Bot! We welcome contributions from the community.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/saint-claw-bot.git
   cd saint-claw-bot
   ```
3. **Set up the environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Development Standards

### Code Quality
- **Type hints required**: All functions must have type annotations
- **Docstrings required**: Every module, class, and function needs a docstring
- **No hardcoded secrets**: Use environment variables (python-dotenv) for all API keys
- **Error handling**: Never silently fail — catch, log, and report errors cleanly

### Style Guide
- Follow PEP 8 conventions
- Use meaningful variable names
- Write inline comments explaining the *why*, not just the *what*
- Keep functions focused and single-purpose

## Submitting Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** with clear, focused commits

3. **Test your changes** by running the bot locally

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request** with:
   - Clear description of what changed and why
   - Any relevant issue numbers
   - Screenshots if UI changes are involved

## Mission Alignment

All contributions should align with Saint Claw Bot's mission: **transparent AI-driven giving**. We believe that:
- AI decisions about charitable giving should be explainable
- Every donation recommendation should be backed by data
- The process should be open, auditable, and trustworthy

## Questions?

Feel free to open an issue for discussion before starting work on significant changes.

Thank you for helping make AI-driven philanthropy more transparent!