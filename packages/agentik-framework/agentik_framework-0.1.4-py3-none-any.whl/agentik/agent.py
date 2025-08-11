# agentik/agent.py
from __future__ import annotations

from typing import List, Optional, Any
import re

from agentik.utils import get_logger

logger = get_logger(__name__)


class Agent:
    """
    Core Agent implementing a compact Plan -> Act -> Reflect loop.
    - plan(): ask LLM what to do next (may include a tool call)
    - act(): route to matching tool if present
    - reflect(): store results in memory
    The loop stops early if LLM says 'done' or 'exit'.
    """

    def __init__(self, name: str, goal: str, llm: Any, tools: List[Any], memory: Optional[Any] = None,
                 system_prefix: Optional[str] = None):
        self.name = name
        self.goal = goal
        self.llm = llm
        self.tools = tools or []
        self.memory = memory
        self.system_prefix = system_prefix or ""

    def _tool_for_action(self, action: str):
        # Tool command = first token equals tool.name (case-insensitive)
        head = action.strip().split(maxsplit=1)[0].lower() if action.strip() else ""
        for t in self.tools:
            if head == t.name.lower():
                return t
        # also allow "<tool>: args"
        m = re.match(r"^\s*([a-zA-Z0-9_\-]+)\s*:\s*(.*)$", action)
        if m:
            name = m.group(1).lower()
            for t in self.tools:
                if name == t.name.lower():
                    return t
        return None

    def plan(self, prompt: str) -> str:
        """Ask the LLM what to do next, passing memory summary and a system prefix if provided."""
        memory_context = ""
        if self.memory:
            summary = self.memory.summarize()
            if summary:
                memory_context = f"\n\n[Previous context]\n{summary}\n"

        composed = (
            (self.system_prefix + "\n") if self.system_prefix else ""
        ) + f"[Goal] {self.goal}\n{memory_context}\n[User]\n{prompt}\n\nRespond with either:\n" \
            "- a tool call like 'calculator 2+2' or 'filereader path.txt'\n" \
            "- or a final message containing 'done' when finished."
        logger.info(f"[Plan] Querying LLM...")
        return self.llm.generate(composed) or ""

    def act(self, action: str) -> str:
        """Route to a tool if it matches; otherwise return the LLM's raw text."""
        logger.info(f"[Act] {action}")
        tool = self._tool_for_action(action)
        if tool:
            return tool.run(action)
        return action

    def reflect(self, result: str):
        """Store the outcome in memory if available."""
        logger.info(f"[Reflect] {result[:300] + ('...' if len(result)>300 else '')}")
        if self.memory:
            self.memory.remember(result)

    def run(self, prompt: str):
        logger.info(f"\nAgent '{self.name}' starting. Goal: {self.goal}\n")
        context = prompt
        for step in range(5):  # allow a little more depth
            logger.info(f"[Cycle {step+1}]")
            action = self.plan(context).strip()
            if not action:
                logger.info("[Agent] LLM returned empty response. Stopping.")
                break
            if re.search(r"\b(done|exit|stop)\b", action.lower()):
                logger.info("[Agent] Received completion signal.")
                break
            result = self.act(action)
            self.reflect(result)
            context = result
        logger.info("\n[Agent] Finished.\n")
