"""
Unit test for core agent loop behavior.
"""

from agentik.agent import Agent

# Mock LLM simulating tool command generation
class MockLLM:
    def generate(self, prompt: str) -> str:
        if "math" in prompt.lower():
            return "CalculatorTool 2 + 2"
        return "done"

# Mock calculator tool
class MockTool:
    name = "CalculatorTool"
    def run(self, input_text: str) -> str:
        return "Result: 4"

# Mock in-memory store
class MockMemory:
    def __init__(self):
        self.data = []
    def remember(self, context: str):
        self.data.append(context)
    def recall(self, query: str = ""):
        return self.data
    def summarize(self):
        return "\n".join(self.data)

# Core test for agent loop
def test_agent_run_loop(monkeypatch):
    llm = MockLLM()
    tool = MockTool()
    memory = MockMemory()

    agent = Agent(name="TestAgent", goal="Do math", llm=llm, tools=[tool], memory=memory)
    agent.run("math test")

    # Validate that memory has captured the tool result
    assert any("Result" in m for m in memory.data)
