# agentik/config.py
import json
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel, ValidationError

from agentik.agent import Agent
from agentik.llms import (
    OpenRouterModel,
    OpenAIModel,
    ClaudeModel,
    MistralModel,
    DeepSeekModel,
    LocalLLM,
)
from agentik.memory import DictMemory, JSONMemoryStore
from agentik.tools import tool_registry


# ---------- Pydantic Schemas ----------

class LLMConfig(BaseModel):
    type: str
    api_key: Optional[str] = None
    model: Optional[str] = None
    url: Optional[str] = None
    site_url: Optional[str] = None
    site_name: Optional[str] = None
    prompt_prefix: Optional[str] = None


class MemoryConfig(BaseModel):
    type: str
    path: Optional[str] = "memory.json"


class AgentConfig(BaseModel):
    name: str
    goal: str
    llm: LLMConfig
    tools: List[str]
    memory: Optional[MemoryConfig] = None
    prompt_prefix: Optional[str] = None  # allow top-level prefix too


# ---------- Loader ----------

def _read_config(path: Path):
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    raise ValueError("Unsupported config format. Use .yaml/.yml or .json")


def load_agent_config(path: str) -> Agent:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    raw = _read_config(file_path)
    try:
        cfg = AgentConfig(**raw)
    except ValidationError as e:
        raise ValueError(f"Invalid config: {e}")

    llm_type = (cfg.llm.type or "").lower()

    # Choose LLM (prefer the generic OpenRouter)
    if llm_type == "openrouter":
        llm = OpenRouterModel(
            api_key=cfg.llm.api_key or None,
            model=cfg.llm.model or "openai/gpt-4o-mini",
            site_url=cfg.llm.site_url or "",
            site_name=cfg.llm.site_name or "Agentik",
        )
    elif llm_type == "openai":
        llm = OpenAIModel(api_key=cfg.llm.api_key, model=cfg.llm.model or "openai/gpt-4o-mini")
    elif llm_type == "claude":
        llm = ClaudeModel(api_key=cfg.llm.api_key, model=cfg.llm.model or "anthropic/claude-3.5-sonnet")
    elif llm_type == "mistral":
        llm = MistralModel(api_key=cfg.llm.api_key, model=cfg.llm.model or "mistralai/mistral-nemo")
    elif llm_type == "deepseek":
        llm = DeepSeekModel(api_key=cfg.llm.api_key, model=cfg.llm.model or "deepseek/deepseek-chat")
    elif llm_type == "local":
        if not cfg.llm.url:
            raise ValueError("For type=local, 'url' is required.")
        llm = LocalLLM(api_url=cfg.llm.url)
    elif llm_type == "test_input":
        # trivial dummy for tests
        class _Dummy:
            def generate(self, prompt: str) -> str: return "done"
        llm = _Dummy()
    else:
        raise ValueError(f"Unsupported LLM type: {cfg.llm.type}")

    # Memory
    memory = None
    if cfg.memory:
        mtype = cfg.memory.type.lower()
        if mtype == "dict":
            memory = DictMemory()
        elif mtype == "json":
            memory = JSONMemoryStore(filepath=cfg.memory.path or "memory.json")
        elif mtype == "test_input":
            class _DummyMem:
                def remember(self, c): ...
                def recall(self, q=""): return []
                def summarize(self): return ""
            memory = _DummyMem()
        else:
            raise ValueError(f"Unsupported memory type: {cfg.memory.type}")

    # Tools
    tools = []
    for name in cfg.tools:
        cls = tool_registry.get(name.lower())
        if not cls:
            print(f"[Warning] Tool '{name}' not found; skipping.")
            continue
        tools.append(cls())

    # System/prefix prompt
    sys_prefix = cfg.prompt_prefix or cfg.llm.prompt_prefix

    return Agent(
        name=cfg.name,
        goal=cfg.goal,
        llm=llm,
        tools=tools,
        memory=memory,
        system_prefix=sys_prefix,
    )
