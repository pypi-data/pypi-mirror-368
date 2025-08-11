# agentik/tools/websearch.py
"""
DuckDuckGo Instant Answer API (no API key).
"""
import urllib.parse
import requests

from agentik.tools.base import Tool

class WebSearchTool(Tool):
    name = "websearch"
    description = "Quick web search. Usage: websearch <query>"

    def run(self, input_text: str) -> str:
        q = input_text[len(self.name):].strip().lstrip(":").strip()
        if not q:
            return "[WebSearchTool] No query provided."
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote_plus(q)}&format=json&no_html=1&skip_disambig=1"
        try:
            r = requests.get(url, headers={"User-Agent": "Agentik/1.0"}, timeout=10)
            data = r.json()
            return data.get("AbstractText") or "No summary available."
        except Exception as e:
            return f"[WebSearchTool Error] {e}"
