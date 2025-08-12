from __future__ import annotations
from importlib.metadata import entry_points
from typing import Dict, Type, Any

from .calculator import Calculator
from .filereader import FileReader
from .websearch import WebSearch
from .base import Tool

def builtin_tools() -> Dict[str, Type]:
    return {
        "calculator": Calculator,
        "filereader": FileReader,
        "websearch": WebSearch,
    }

def discover_tools() -> Dict[str, Type]:
    found: Dict[str, Type] = dict(builtin_tools())
    try:
        eps = entry_points(group="agentik.tools")  # Python 3.10+
    except TypeError:
        eps = entry_points().get("agentik.tools", [])  # fallback older API
    for ep in eps:
        try:
            cls = ep.load()
            name = getattr(cls, "name", ep.name)
            found[name] = cls
        except Exception:
            continue
    return found

def instantiate(name: str, **kwargs: Any) -> Tool:
    tools = discover_tools()
    if name not in tools:
        raise KeyError(f"Unknown tool: {name}")
    return tools[name](**kwargs)
