"""
Math Agent
Performs complex mathematical calculations with safe evaluation.
"""
import os
from agentik.config import load_agent_config

if __name__ == "__main__":
    os.environ.setdefault("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))
    agent = load_agent_config("configs/math_agent.yaml")
    agent.run("calculator 150 * (32 / 8) + sin(3.1415926535 / 2)")
