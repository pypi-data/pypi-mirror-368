"""
File Summarizer Agent
Reads a file and summarizes its content using an LLM via OpenRouter.
"""
import os
from agentik.config import load_agent_config

if __name__ == "__main__":
    # Ensure API key is available
    os.environ.setdefault("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))

    agent = load_agent_config("configs/file_summarizer.yaml")
    # You can change the initial prompt here:
    agent.run("filereader examples/sample.txt\nPlease summarize it in bullet points.")
