# agentik/cli.py
import os
from pathlib import Path
from typing import Optional

import typer
import yaml

import agentik.tools  # ensures registry is populated
from agentik.config import load_agent_config
from agentik.tools import Tool, tool_registry

app = typer.Typer(help="Agentik – Modular Agent Framework CLI")


# --------------------- Utilities ---------------------

def _assert_config_exists(path: str) -> Path:
    p = Path(path)
    if not p.exists():
        typer.echo(f"[Error] Config not found: {path}")
        raise typer.Exit(code=1)
    return p


# --------------------- Commands ----------------------

@app.command()
def run(config: str, prompt: Optional[str] = typer.Option(None, help="Initial prompt to run"),
        verbose: bool = False, dry_run: bool = False):
    """
    Run an agent from a config file. If --prompt is not provided, you'll be asked.
    """
    _assert_config_exists(config)
    agent = load_agent_config(config)
    if verbose:
        typer.echo(f"[Verbose] Agent '{agent.name}' ready. Goal: {agent.goal}")
    if dry_run:
        typer.echo("[Dry Run] Not executing agent loop.")
        raise typer.Exit()

    user_prompt = prompt or typer.prompt("Enter your prompt")
    agent.run(user_prompt)


@app.command("chat")
def chat(config: str):
    """
    Simple REPL chat with the agent (type 'exit' to quit).
    """
    _assert_config_exists(config)
    agent = load_agent_config(config)
    typer.echo(f"Interactive chat with '{agent.name}'. Type 'exit' to quit.")
    while True:
        msg = typer.prompt("You")
        if msg.strip().lower() in {"exit", "quit"}:
            break
        agent.run(msg)


@app.command("list-tools")
def list_tools():
    """
    List all discovered tools.
    """
    typer.echo("Available Tools:")
    if not tool_registry:
        typer.echo("  (none found)")
        return
    for name, cls in tool_registry.items():
        typer.echo(f"- {cls.name}: {cls.description}")


@app.command("list-models")
def list_models():
    """
    Show handy OpenRouter model slugs you can paste into configs.
    """
    models = [
        "openai/gpt-4o-mini",
        "openai/gpt-4o",
        "anthropic/claude-3.5-sonnet",
        "mistralai/mistral-nemo",
        "deepseek/deepseek-chat",
        "qwen/qwen-2.5-7b-instruct",
    ]
    typer.echo("Common OpenRouter models:")
    for m in models:
        typer.echo(f"- {m}")


@app.command("set-key")
def set_key(key: Optional[str] = typer.Argument(None)):
    """
    Set OPENROUTER_API_KEY in the current shell session (prints export command).
    """
    if not key:
        key = typer.prompt("Enter your OpenRouter API key", hide_input=True)
    typer.echo("# Run this in your shell to persist for the session:")
    typer.echo(f'export OPENROUTER_API_KEY="{key}"')


@app.command("validate-config")
def validate_config(config: str):
    """
    Validate that a config file is loadable.
    """
    try:
        _ = load_agent_config(config)
        typer.echo("✅ Config is valid.")
    except Exception as e:
        typer.echo(f"❌ Invalid config: {e}")
        raise typer.Exit(code=1)


@app.command("memory-show")
def memory_show(config: str, query: str = typer.Option("", help="Filter memories containing text")):
    """
    Print memories for the given agent.
    """
    agent = load_agent_config(config)
    if not agent.memory:
        typer.echo("No memory backend configured.")
        return
    items = agent.memory.recall(query=query)
    if not items:
        typer.echo("(no memories)")
        return
    for i, it in enumerate(items, 1):
        typer.echo(f"{i}. {it}")


@app.command("memory-clear")
def memory_clear(config: str, confirm: bool = typer.Option(False, help="Skip confirmation")):
    """
    Clear JSON memory file (if JSON backend).
    """
    agent = load_agent_config(config)
    mem = getattr(agent, "memory", None)
    path = getattr(mem, "path", None)
    if not path:
        typer.echo("This agent does not use JSON memory; nothing to clear.")
        return
    if not confirm and not typer.confirm(f"Delete {path}?"):
        typer.echo("Cancelled.")
        return
    try:
        Path(path).write_text("[]", encoding="utf-8")
        typer.echo("Memory cleared.")
    except Exception as e:
        typer.echo(f"Failed to clear memory: {e}")


def main():
    app()


if __name__ == "__main__":
    main()
