"""
Tool-level unit tests with dummy input and monkeypatched outputs.
"""

import os
from agentik.tools.calculator import CalculatorTool
from agentik.tools.filereader import FileReaderTool
from agentik.tools.websearch import WebSearchTool
from agentik.tools.template import TemplateTool

# Calculator Tests
def test_calculator_tool_valid():
    tool = CalculatorTool()
    result = tool.run("calculator 2 + 3 * 5")
    assert "17" in result

def test_calculator_tool_invalid():
    tool = CalculatorTool()
    result = tool.run("calculator 2 /")
    assert "[CalculatorTool Error]" in result

# File Reader Tests
def test_file_reader_tool_success(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("Hello Agentik")

    tool = FileReaderTool()
    result = tool.run(f"filereader {file_path}")
    assert "Hello Agentik" in result

def test_file_reader_tool_missing_file():
    tool = FileReaderTool()
    result = tool.run("filereader non_existing_file.txt")
    assert "File not found" in result

def test_file_reader_tool_no_input():
    tool = FileReaderTool()
    result = tool.run("filereader")
    assert "No file path provided" in result

# Web Search Tool
def test_web_search_tool_valid(monkeypatch):
    mock_data = {"AbstractText": "Simulated summary"}
    class MockResponse:
        def json(self): return mock_data
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: MockResponse())

    tool = WebSearchTool()
    result = tool.run("websearch GPT-4")
    assert "Simulated summary" in result

def test_web_search_tool_no_query():
    tool = WebSearchTool()
    result = tool.run("websearch")
    assert "No query provided" in result

# Template Tool
def test_template_tool_with_input():
    tool = TemplateTool()
    result = tool.run("template Hello Test")
    assert "Processed: Hello Test" in result

def test_template_tool_no_input():
    tool = TemplateTool()
    result = tool.run("template")
    assert "No input provided" in result
