"""
Unit tests for LLM integrations with mocking.
"""

import pytest
from agentik.llms import OpenAIModel, ClaudeModel, MistralModel, DeepSeekModel, LocalLLM

class DummyResponse:
    def __init__(self, output):
        self.status_code = 200
        self._output = output
    def json(self):
        return {"output": self._output}

def test_local_llm(monkeypatch):
    def mock_post(url, json):
        return DummyResponse("Mocked response")
    monkeypatch.setattr("requests.post", mock_post)

    model = LocalLLM(api_url="http://fake-url")
    response = model.generate("Hello")
    assert "Mocked" in response

def test_openai_model_error_handling(monkeypatch):
    class FakeClient:
        class Chat:
            class Completions:
                def create(self, **kwargs):
                    raise Exception("API error")
            completions = Completions()
        chat = Chat()
    monkeypatch.setattr("openai.OpenAI", lambda **kwargs: FakeClient())

    model = OpenAIModel(api_key="invalid", model="fake")
    result = model.generate("test")
    assert "[OpenAIModel Error]" in result
