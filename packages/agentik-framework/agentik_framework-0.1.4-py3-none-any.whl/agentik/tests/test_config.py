"""
Test for configuration file loader using DeepSeekModel.
"""

from agentik.config import load_agent_config

CONFIG_YAML = """
name: "TestBot"
goal: "Testing"
llm:
  type: deepseek
  api_key: "fake_key"
  model: deepseek/deepseek-chat-v3-0324:free
tools:
  - calculator
memory:
  type: dict
"""

def test_load_agent_config(tmp_path, monkeypatch):
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(CONFIG_YAML)

    # Patch the DeepSeekModel to avoid real API call
    monkeypatch.setattr(
        "agentik.llms.DeepSeekModel",
        lambda api_key, model: type("MockLLM", (), {"generate": lambda self, prompt: "done"})()
    )

    agent = load_agent_config(str(config_file))
    assert agent.name == "TestBot"
    assert agent.goal == "Testing"
    assert agent.tools
