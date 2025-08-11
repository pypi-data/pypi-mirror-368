"""
Research Bot
Searches and summarizes recent AI tool news.
"""
import os
from agentik.config import load_agent_config

if __name__ == "__main__":
    os.environ.setdefault("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))
    agent = load_agent_config("configs/research_bot.yaml")
    agent.run("websearch latest AI agent frameworks and toolkits\nSummarize top 5 with 1-line reason each.")
