# agentik/llms.py
"""
Unified LLM adapters.
Primary path: OpenRouterModel (generic). Others remain for compatibility.
"""
from __future__ import annotations

import abc
from typing import Optional
import requests
from openai import OpenAI


# ---------- Base ----------

class LLMBase(abc.ABC):
    @abc.abstractmethod
    def generate(self, prompt: str) -> str: ...


# ---------- Generic OpenRouter ----------

class OpenRouterModel(LLMBase):
    """
    Use OpenRouter with the OpenAI python client.
    Set API key via arg or env OPENROUTER_API_KEY.
    """
    def __init__(self, api_key: Optional[str], model: str, site_url: str = "", site_name: str = "Agentik"):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,  # None => env var
        )
        self.model = model
        self.headers = {
            "HTTP-Referer": site_url,
            "X-Title": site_name,
        }

    def generate(self, prompt: str) -> str:
        try:
            comp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                extra_headers=self.headers or None,
            )
            return comp.choices[0].message.content
        except Exception as e:
            return f"[OpenRouter Error] {e}"


# ---------- Provider-Flavored (compat) ----------

class OpenAIModel(OpenRouterModel):
    def __init__(self, api_key: Optional[str], model: str = "openai/gpt-4o-mini", site_url: str = "", site_name: str = "Agentik"):
        super().__init__(api_key=api_key, model=model, site_url=site_url, site_name=site_name)


class ClaudeModel(OpenRouterModel):
    def __init__(self, api_key: Optional[str], model: str = "anthropic/claude-3.5-sonnet", site_url: str = "", site_name: str = "Agentik"):
        super().__init__(api_key=api_key, model=model, site_url=site_url, site_name=site_name)


class MistralModel(OpenRouterModel):
    def __init__(self, api_key: Optional[str], model: str = "mistralai/mistral-nemo", site_url: str = "", site_name: str = "Agentik"):
        super().__init__(api_key=api_key, model=model, site_url=site_url, site_name=site_name)


class DeepSeekModel(OpenRouterModel):
    def __init__(self, api_key: Optional[str], model: str = "deepseek/deepseek-chat", site_url: str = "", site_name: str = "Agentik"):
        super().__init__(api_key=api_key, model=model, site_url=site_url, site_name=site_name)


# ---------- Local HTTP Adapter ----------

class LocalLLM(LLMBase):
    def __init__(self, api_url: str):
        self.api_url = api_url

    def generate(self, prompt: str) -> str:
        try:
            r = requests.post(self.api_url, json={"prompt": prompt}, timeout=30)
            r.raise_for_status()
            return r.json().get("output", "")
        except Exception as e:
            return f"[LocalLLM Error] {e}"
