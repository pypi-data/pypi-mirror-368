# agentik/tools/__init__.py
"""
Dynamic tool loader and registry.
"""
import importlib
import inspect
import os
from pathlib import Path

from agentik.tools.base import Tool

tool_registry = {}

def import_all_tools():
    tools_dir = Path(__file__).parent
    for file in os.listdir(tools_dir):
        if not file.endswith(".py"):
            continue
        if file in {"__init__.py", "base.py"}:
            continue
        module_name = f"agentik.tools.{file[:-3]}"
        try:
            module = importlib.import_module(module_name)
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Tool) and obj is not Tool:
                    tool_registry[obj.name.lower()] = obj
        except Exception as e:
            print(f"[Warning] Failed to import {module_name}: {e}")

import_all_tools()

__all__ = ["Tool", "tool_registry"]
