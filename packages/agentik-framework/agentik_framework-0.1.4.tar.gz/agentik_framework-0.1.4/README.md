Agentik – Modular Agentic AI Framework for Python
=================================================

A lightweight, extensible Python framework for building LLM-powered agents with a clear planning loop, safe tool execution, and optional persistent memory. Agentik emphasizes clarity, reliability, and business-ready configuration via YAML and a focused CLI.

Overview
--------

Agentik enables you to assemble agents that can plan → act → reflect using configurable LLM backends (via OpenRouter or local HTTP), safe tools, and memory stores. The framework stays small and auditable while remaining easy to extend.

Key Capabilities
----------------

- Pluggable LLMs via OpenRouter (OpenAI, Anthropic, Mistral, DeepSeek, Qwen, and more) or a local HTTP model.
- Safe tools out of the box: calculator (AST-based evaluation), file reader, and web search (DuckDuckGo Instant Answer).
- Memory backends: in-memory dictionary and JSON file store.
- Clean configuration with YAML or JSON; load and run via CLI or Python.
- Business-friendly CLI for running agents, validating configs, listing tools/models, and managing memory.

Architecture and Workflow
-------------------------

[User Prompt]
     ↓
[Agent.run()]
     ↓
Plan    → LLM decides the next action (tool call or final answer)
Act     → Matching tool executes securely with provided arguments
Reflect → Output is stored in memory (optional)
Repeat  → Up to a limited number of cycles, or stop on “done/exit”

Project Structure
-----------------

agentik/
├── agent.py          # Core plan/act/reflect loop and orchestration
├── config.py         # YAML/JSON parser → Agent instance (pydantic schemas)
├── llms.py           # LLM adapters (OpenRouter + provider-flavored wrappers)
├── memory.py         # DictMemory, JSONMemoryStore
├── tools/            # Built-in tools and dynamic registry
│   ├── base.py
│   ├── calculator.py
│   ├── filereader.py
│   ├── template.py
│   └── websearch.py
├── cli.py            # Typer-based CLI (run/chat/list/validate/memory ops)
├── utils.py          # Logging, retry/timing helpers, token counting
├── configs/          # Example YAML configs
└── examples/         # Example scripts

Requirements
------------

- Python 3.10 or newer
- An OpenRouter API key for hosted LLMs (set via environment or CLI “set-key” helper)

Installation
------------

Install from source or your internal package index:

pip install -U -r requirements.txt

If you distribute Agentik as a package:

pip install agentik-framework

OpenRouter Configuration
------------------------

Set the key in your shell (preferred):

export OPENROUTER_API_KEY="sk-or-..."

Or use the CLI helper to print a ready-to-paste export command:

python -m agentik.cli set-key

Selecting Models
----------------

Agentik uses OpenRouter model slugs. Common choices:

- openai/gpt-4o-mini
- anthropic/claude-3.5-sonnet
- mistralai/mistral-nemo
- deepseek/deepseek-chat
- qwen/qwen-2.5-7b-instruct

List a quick reference from the CLI:

python -m agentik.cli list-models

Defining an Agent (YAML)
------------------------

Example: configs/research_bot.yaml

name: "ResearchBot"
goal: "Summarize recent AI tools"

llm:
  type: openrouter
  model: openai/gpt-4o-mini
  # api_key: ""  # optional; prefer environment variable OPENROUTER_API_KEY

tools:
  - websearch
  - calculator

memory:
  type: json
  path: "memory.json"

Defining an Agent (Python)
--------------------------

from agentik.config import load_agent_config

agent = load_agent_config("configs/research_bot.yaml")
agent.run("websearch latest AI agent frameworks; summarize top 5.")

Built-in Tools
--------------

Tool Name       | Usage Example                                | Notes
calculator      | calculator sin(pi/2) + 3**2                  | Safe AST-based math; supports common operators and math.* functions
filereader      | filereader examples/sample.txt               | Reads .txt / .md with encoding fallbacks
websearch       | websearch retrieval augmented generation     | DuckDuckGo Instant Answer API
template        | template hello world                         | Minimal example tool for extension

Creating a Custom Tool
----------------------

1. Subclass agentik.tools.base.Tool.
2. Set a name and description.
3. Implement run(self, input_text: str) -> str to process "<name> <args>".

The dynamic registry auto-discovers tools inside agentik/tools/.

CLI Usage
---------

All commands are available via module execution:

python -m agentik.cli <command> [options]

Primary commands:

run
    Run an agent once with a prompt.
    python -m agentik.cli run configs/file_summarizer.yaml --prompt "filereader examples/sample.txt then summarize"

    Options:
    --prompt TEXT   Provide the initial prompt non-interactively.
    --verbose       Print additional progress details.
    --dry-run       Load and show agent details without execution.

chat
    Interactive loop (type exit to quit).
    python -m agentik.cli chat configs/research_bot.yaml

list-tools
    Show all discovered tools.
    python -m agentik.cli list-tools

list-models
    Display common OpenRouter model slugs for quick selection.
    python -m agentik.cli list-models

validate-config
    Verify that a YAML/JSON config is loadable.
    python -m agentik.cli validate-config configs/math_agent.yaml

memory-show
    Print memories for a configured agent. Filter with --query.
    python -m agentik.cli memory-show configs/file_summarizer.yaml --query summarize

memory-clear
    Clear JSON memory file for an agent (requires confirmation unless --confirm is supplied).
    python -m agentik.cli memory-clear configs/file_summarizer.yaml --confirm

set-key
    Prompt for your OpenRouter key and print an export command for the current shell.
    python -m agentik.cli set-key

Examples
--------

Run the included examples after setting your API key:

python examples/file_summarizer.py
python examples/math_agent.py
python examples/research_bot.py

Logging and Observability
-------------------------

- Human-readable logging is enabled by default and includes plan/act/reflect steps.
- For richer diagnostics, run with --verbose or add your own instrumentation around Agent.run().

Testing
-------

All components are designed for unit testing with mocked LLMs and HTTP calls.

pytest -q

Add tests for any new tools or memory providers you contribute.

Security and Reliability Notes
------------------------------

- The calculator tool uses AST-based evaluation to avoid arbitrary code execution.
- The file reader restricts itself to reading local text/markdown with encoding fallbacks.
- For hosted LLMs, keys are never embedded in the repository; use environment variables.
- Network timeouts and error messages in tools and LLM adapters are user-friendly and non-verbose.

Troubleshooting
---------------

- Missing API key: Ensure OPENROUTER_API_KEY is set, or run python -m agentik.cli set-key.
- Tool not found: Confirm the tool file is under agentik/tools/ and the class inherits Tool with a unique name.
- Invalid config: Run python -m agentik.cli validate-config <file> to see schema errors.
- No output or early stop: The agent stops when the LLM replies with “done/exit”. Provide a prompt that requests a specific tool call or output.

Contributing
------------

Contributions are welcome. Please include tests for new functionality.

1. Fork the repository.
2. Add or modify tools, memory backends, or adapters.
3. Add tests under tests/.
4. Open a pull request with a clear summary and rationale.

License
-------

MIT License © 2025. Use, modify, and distribute with attribution and without warranty.
[Avinash Raghuvanshi, Vinay Joshi]

Project Philosophy
------------------

Agentik focuses on clarity, stability, and composability. It provides pragmatic building blocks—planning loop, tools, memory, and LLM adapters—so you can assemble production-quality agents that are easy to reason about, test, and maintain.
