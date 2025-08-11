"""
Tests for CLI commands using Typer.
"""

from typer.testing import CliRunner
from agentik.cli import app

runner = CliRunner()

def test_list_tools():
    result = runner.invoke(app, ["list-tools"])
    # Check lowercase tool names (not class names)
    assert "calculator" in result.output
    assert "filereader" in result.output

def test_explain_memory():
    result = runner.invoke(app, ["explain-memory"])
    assert "Memory Backends in Agentik" in result.output

def test_create_agent(monkeypatch):
    monkeypatch.setattr("typer.prompt", lambda *args, **kwargs: "test_input")
    result = runner.invoke(app, ["create-agent"])
    assert "Created new agent config" in result.output
