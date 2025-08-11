# agentik/tools/filereader.py
from pathlib import Path
from agentik.tools.base import Tool

class FileReaderTool(Tool):
    name = "filereader"
    description = "Read a text/markdown file. Usage: filereader <path>"

    def run(self, input_text: str) -> str:
        arg = input_text[len(self.name):].strip().lstrip(":").strip()
        if not arg:
            return "[FileReaderTool] No file path provided."
        path = Path(arg)
        if not path.exists():
            return f"[FileReaderTool] File not found: {arg}"
        # try common encodings
        for enc in ("utf-8", "utf-8-sig", "latin-1"):
            try:
                text = path.read_text(encoding=enc)
                return text
            except UnicodeDecodeError:
                continue
            except Exception as e:
                return f"[FileReaderTool Error] {e}"
        return "[FileReaderTool Error] Could not decode file."
