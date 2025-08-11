# agentik/tools/template.py
from agentik.tools.base import Tool

class TemplateTool(Tool):
    name = "template"
    description = "Demo tool that echoes. Usage: template <text>"

    def run(self, input_text: str) -> str:
        arg = input_text[len(self.name):].strip().lstrip(":").strip()
        if not arg:
            return "[template] No input provided."
        return f"[template] Processed: {arg}"
