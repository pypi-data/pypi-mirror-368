# Agentik Framework

**Agentik** is a CLI‑first, modular agent framework that runs LLMs via **OpenRouter**. It focuses on developer ergonomics: clean configs, a batteries‑included CLI, safe tool execution, rich transcripts with run metadata, and a `dev` profile with auto‑rerun watching for fast iteration.

---

## Highlights

* **CLI‑first workflow**: `agentik run`, `agentik dev watch`, `agentik tools ...`
* **OpenRouter integration**: one key → many models
* **Agent loop**: *plan → (optional tool) → reflect → finalize*
* **Pluggable tooling** (via entry points) with built‑ins:

  * `http_fetch` — GET with caching + limits
  * `html_to_text` — HTML → text
  * `write_file` — safe file writer
* **Policies** enforced per tool call: `allow_network`, `allow_filesystem`
* **Transcripts**: JSONL with `meta_start`/`meta_end` (tokens, cost estimate, timings, tags)
* **Run profiles**: `fast`, `thorough`, `deterministic`, `creative`, `cheap`, `dev`
* **Dev watcher**: polling file watcher, auto‑rerun on save (no extra deps)
* **Memory**: file‑backed minimal memory (`json` or in‑memory `dict`)

---

## Installation

Requires **Python 3.10+**.

```bash
pip install agentik-framework

# for local development
pip install -e .[dev]
```

### OpenRouter API key

Set your key once (recommended):

**PowerShell (Windows):**

```powershell
setx OPENROUTER_API_KEY "sk-or-..."
# then restart your shell
```

Or via Agentik RC:

```powershell
agentik keys set openrouter sk-or-... --global
```

Verify your setup:

```powershell
agentik self-test
```

---

## End‑User Guide (PyPI + CLI)

Once you’ve installed the package from PyPI, you can use **Agentik** entirely from the **CLI**. Here’s a concise, step‑by‑step guide for end users.

### 1) Install

```bash
pip install agentik-framework
```

> Python **3.10+** required.

### 2) Set your OpenRouter API key (one time)

**Windows (PowerShell):**

```powershell
setx OPENROUTER_API_KEY "sk-or-XXXXXXXXXXXXXXXX"
# Open a new PowerShell window afterwards
```

**macOS/Linux (bash/zsh):**

```bash
echo 'export OPENROUTER_API_KEY="sk-or-XXXXXXXXXXXXXXXX"' >> ~/.bashrc
source ~/.bashrc
```

**Verify:**

```powershell
agentik self-test
agentik models list --filter gpt --refresh   # optional network check
```

### 3) Create a project folder

```powershell
mkdir my-agent && cd my-agent
```

Initialize a basic layout (templates are bundled with the package):

```powershell
agentik init . --template basic --name "My Agent Project"
```

Generate a ready‑to‑run agent config (adds a file under `agents/`):

```powershell
agentik new agent research --template basic --tools http_fetch,html_to_text,write_file --with-tests --to .
```

Want to see available templates and tools?

```powershell
agentik template list
agentik tools list
```

### 4) Minimal config (if you prefer to paste one)

Create `agents/agent.yaml` with:

```yaml
agent:
  name: ResearchBot
  goal: "Research and summarize information."
  loop:
    max_steps: 3
    reflect: true

llm:
  model: openai/gpt-4o-mini
  temperature: 0.3

memory:
  type: json
  path: ./memory/research.json

policies:
  allow_network: true
  allow_filesystem: true

tools:
  - http_fetch
  - html_to_text
  - write_file
```

### 5) Run your agent

**Windows (PowerShell):**

```powershell
agentik run .\agents\agent.yaml `
  -p "Summarize the main differences between GPT-4o and small LLMs in 5 bullets." `
  --profile fast `
  --stream `
  --save-transcript .\runs\first-run.jsonl
```

**macOS/Linux:**

```bash
agentik run ./agents/agent.yaml \
  -p "Summarize the main differences between GPT-4o and small LLMs in 5 bullets." \
  --profile fast \
  --stream \
  --save-transcript ./runs/first-run.jsonl
```

**Handy flags:**

* `--profile fast|thorough|deterministic|creative|cheap|dev|none`
* `--model <openrouter-model-id>`
* `--temperature <float>`
* `--save-transcript <path>` — JSONL with metadata, tokens, timings, cost est.
* `--tag`, `--note`, `--run-id` — stored in transcript metadata

### 6) Use the dev watcher (auto re‑run on file changes)

> PowerShell tip: **quote your globs** to avoid expansion.

**Windows (PowerShell):**

```powershell
agentik dev watch .\agents\agent.yaml `
  --prompt "Summarize this project in 3 bullets." `
  --path . `
  --include '**/*.py' --include '**/*.yaml' --include 'templates/**' `
  --exclude '.venv/**' --exclude 'runs/**' `
  --save-transcripts .\runs `
  --profile dev `
  --stream
```

**macOS/Linux:**

```bash
agentik dev watch ./agents/agent.yaml \
  --prompt "Summarize this project in 3 bullets." \
  --path . \
  --include '**/*.py' --include '**/*.yaml' --include 'templates/**' \
  --exclude '.venv/**' --exclude 'runs/**' \
  --save-transcripts ./runs \
  --profile dev \
  --stream
```

### 7) Run tools directly (no agent loop)

```powershell
agentik tools run http_fetch --arg url=https://example.com --arg ttl=3600 --arg allow_network=true --json
agentik tools run html_to_text --arg "html=<p>Hello</p>" --arg keep_newlines=true --json
agentik tools run write_file --arg path=out\hello.txt --arg "content=Hello" --arg allow_filesystem=true --json
```

### 8) Memory helpers

```powershell
agentik memory init --type json --path .\memory\agentik.json
agentik memory recall --n 10 --config .\agents\agent.yaml
agentik memory summarize --n 20 --max-chars 1200 --config .\agents\agent.yaml
```

### 9) Batch prompts from a file

```powershell
agentik batch run .\prompts.jsonl --column prompt --out .\results.jsonl --model openai/gpt-4o-mini
```

`prompts.jsonl` example:

```json
{"prompt": "Write a haiku about summer."}
{"prompt": "One sentence on the solar eclipse."}
```

### 10) Common issues & fixes

**“Network error talking to OpenRouter.”**
Check your key in the same shell:
`echo $env:OPENROUTER_API_KEY` (PowerShell) / `echo $OPENROUTER_API_KEY` (bash).
Try: `agentik models list --refresh`. If you’re behind a proxy, set `HTTP_PROXY`/`HTTPS_PROXY`.

**Dev watcher says “unexpected extra arguments …”**
Quote your globs in PowerShell: `--include '**/*.py'` (with single quotes).

**Not seeing new CLI features after edits?**
Reinstall in editable mode from your project root: `pip install -e .[dev]`.

That’s it. After `pip install agentik-framework` you mainly interact through the `agentik` command. If you want examples or a minimal starter project scaffolded for you, just run `agentik init` and `agentik new agent …` and you’ll be up and running in minutes.

---

## Quick Start

Initialize a project:

```powershell
agentik init . --template basic --name "My Agent Project"
```

Scaffold an agent:

```powershell
agentik new agent research \
  --template basic \
  --tools http_fetch,html_to_text,write_file \
  --with-tests
```

Create a minimal config (save as `agents/agent.yaml`):

```yaml
agent:
  name: research
  goal: "Research and summarize web sources"
  loop:
    max_steps: 4
    reflect: true

llm:
  model: openai/gpt-4o-mini
  temperature: 0.2

memory:
  type: json
  path: ./memory/agent.json

policies:
  allow_network: true
  allow_filesystem: true

tools:
  - http_fetch
  - html_to_text
  - write_file
```

Run it:

```powershell
agentik run .\agents\agent.yaml -p "Summarize the latest about OpenRouter rate limits"
```

---

## CLI Reference

### `agentik version`

Print the current version.

### `agentik self-test`

Environment sanity checks (Python, OS, OpenRouter key, RC path).

### `agentik init`

Initialize a project folder.

```bash
agentik init [PATH] --template basic --force --name "Project Name"
```

### `agentik run`

Run an agent loop with profiles and run metadata. (CONFIG is typically a YAML under `agents/`, e.g., `agents/research.yaml`.)

```bash
agentik run CONFIG \
  -p "Prompt text" \
  --model TEXT \
  --temperature FLOAT \
  --stream \
  --dry-run \
  --save-transcript PATH \
  --profile [fast|thorough|deterministic|creative|cheap|dev|none] \
  --tag TAG \
  --note TEXT \
  --run-id TEXT \
  --obs-max-chars INT
```

### Keys

```bash
agentik keys set openrouter sk-or-... [--global|--local]
agentik keys show
```

### Models

```bash
agentik models list [--filter TEXT] [--refresh]
```

### New (scaffolding)

```bash
agentik new agent NAME \
  --template basic \
  --tools "t1,t2" \
  --memory json \
  --memory-path ./memory/agent.json \
  --to . \
  --with-tests \
  --force

agentik new tool NAME \
  --template python \
  --to . \
  --with-tests \
  --force
```

### Templates

```bash
agentik template list
agentik template apply kind/name --to . --force --name MyArtifact
agentik template pull <git-or-zip-url> --to .
```

### Tools

```bash
agentik tools list
agentik tools info NAME
agentik tools run NAME --arg key=value --arg key2=value2 [--json]
```

### Validate

```bash
agentik validate file CONFIG.yaml \
  --show-effective \
  --model TEXT \
  --temperature FLOAT \
  --max-steps INT
```

### Batch

Process prompts from CSV or JSONL.

```bash
agentik batch run FILE \
  --column prompt \
  --out results.jsonl \
  --model TEXT \
  --temperature FLOAT
```

### Memory

```bash
agentik memory init --type json --path ./memory/agentik.json
agentik memory recall --n 10 [--config CONFIG.yaml]
agentik memory summarize --n 20 --max-chars 1200 [--config CONFIG.yaml]
agentik memory clear [--config CONFIG.yaml]
agentik memory path [--config CONFIG.yaml]
```

### Eval

Tiny harness to check expected substrings/regex.

```bash
agentik eval run FILE.jsonl --config CONFIG.yaml --out eval_results.jsonl
```

### Dev Watch (auto‑rerun)

Watches files and re‑runs on change — great during development.

```bash
agentik dev watch CONFIG \
  -p "Prompt text" \
  --prompt-file PATH \
  --path PATH \            # repeatable (default .)
  --include GLOB \         # repeatable (default python/yaml/md/templates/tools)
  --exclude GLOB \         # repeatable
  --interval 0.6 \
  --debounce 0.5 \
  --clear/--no-clear \
  --stream/--no-stream \
  --profile dev \
  --save-transcripts DIR \
  --obs-max-chars 800 \
  --no-initial-run \
  --tag TAG \              # repeatable (default "dev")
  --note TEXT
```

Example (PowerShell):

```powershell
agentik dev watch .\agents\agent.yaml `
  --prompt-file .\prompt.txt `
  --path . `
  --include **/*.py --include **/*.yaml --include templates/** `
  --exclude .venv/** --exclude runs/** `
  --save-transcripts .\runs `
  --stream
```

---

## Tools & Policies

**Built‑in tools (selected):**

* `http_fetch(url, ttl, timeout, max_bytes, headers, allow_network)`
  Returns `{ok, data, error, meta}` with `data.text`, `data.status`, and cache hints.

* `html_to_text(html, keep_newlines, drop_links, max_chars)`
  Lightweight HTML → text (dependency‑free).

* `write_file(path, content, encoding, overwrite, allow_abs, allow_filesystem)`
  Safe writer with sandboxing and system‑path guards.

**Policies (YAML):**

```yaml
policies:
  allow_network: true
  allow_filesystem: false
```

If a tool requires a disabled capability, Agentik blocks it and records an observation.

---

## Transcripts & Cost

Each run can append JSONL records via `--save-transcript`. Files include:

* `meta_start`: run id, profile, tags, agent, model, policies, memory path
* Tool calls and assistant responses
* `meta_end`: timings (planner/tools/reflect), tokens (prompt/completion/total), **estimated cost**

Cost is derived from OpenRouter pricing when available. You can override with env vars:

```powershell
# USD per 1K tokens
$env:AGENTIK_PRICE_PROMPT_PER_1K = "0.50"
$env:AGENTIK_PRICE_COMPLETION_PER_1K = "1.50"
```

---

## Configuration Reference (YAML)

```yaml
agent:
  name: my-agent
  goal: "Help with tasks."
  loop:
    max_steps: 4
    reflect: true

llm:
  model: openai/gpt-4o-mini
  temperature: 0.2

memory:
  type: json         # json | dict
  path: ./memory/agent.json

policies:
  allow_network: true
  allow_filesystem: false

tools:
  - http_fetch
  - html_to_text
```

---

---

# Agentik CLI — All Command Reference

A clean, practical guide to the `agentik` command‑line interface. Use this to initialize projects, scaffold agents/tools, run and iterate, manage config, and evaluate.

**Typical workflow:** `init → new → run → dev`

---

## Table of Contents

1. [Basic Information](#basic-information)
2. [Project Setup](#project-setup)
3. [Core Functionality](#core-functionality)
4. [Configuration & Management](#configuration--management)
5. [Data & Evaluation](#data--evaluation)

---

## Basic Information

Commands that show tool and environment details.

### `version`

Shows the installed version of the Agentik CLI.

```bash
agentik version
```

### `self-test`

Checks whether your environment (Python/OS/API keys) is set up correctly.

```bash
agentik self-test
```

---

## Project Setup

Create projects, agents, and tools from templates.

### `init`

Initialize a new project directory with the standard structure (`agents/`, `tools/`, etc.).

**Example: Create a project in a folder named `my-first-project`.**

```bash
agentik init my-first-project
```

### `new`

Scaffold new files from templates.

#### `new agent`

Create a new agent YAML configuration.

**Example: Inside your project, create an agent named `researcher` that uses the `web_search` tool.**

```bash
cd my-first-project
agentik new agent researcher --tools "web_search" --to ./agents
```

#### `new tool`

Create a new custom tool (Python file).

**Example: Create a tool named `calculator` in `./tools`.**

```bash
agentik new tool calculator --to ./tools
```

### `template`

Manage built-in and third‑party templates.

#### `template list`

Show all available templates for projects, agents, and tools.

```bash
agentik template list
```

#### `template apply`

Apply a specific template to a directory.

```bash
agentik template apply agent/basic --to ./agents --name "my-basic-agent"
```

---

## Core Functionality

Run and iterate on your agents.

### `run`

Run an agent using a specific configuration file to complete a task.

**Example: Run the `researcher` agent with a prompt and save the transcript.**

```bash
agentik run .\agents\researcher.yaml \
  -p "What is the current time in India?" \
  --save-transcript .\runs\research-run.jsonl
```

### `dev`

Watch project files for changes and automatically re-run your agent for rapid iteration.

**Example: Re-run the `researcher` agent whenever a `.py` or `.yaml` file is saved.**

```bash
agentik dev watch .\agents\researcher.yaml --prompt "Summarize the agentik framework in 5 bullets."
```

> **Note:** If you encounter a `generator` error while streaming, add `--no-stream`.

---

## Configuration & Management

Manage API keys, models, tools, validation, and configuration paths.

### `keys`

Store and view API keys (e.g., OpenRouter) used by Agentik.

**Set a key:**

```bash
# Replace with your actual key
agentik keys set sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Show the active key (from env and `.agentikrc`):**

```bash
agentik keys show
```

### `models`

List available models (via OpenRouter) with optional filtering.

**Example: List models containing "claude".**

```bash
agentik models list --filter "claude"
```

### `tools`

Discover and test tools locally.

**List discovered tools:**

```bash
agentik tools list
```

**Run a specific tool with arguments (useful for testing):**

```bash
agentik tools run file_reader --arg "path=./README.md"
```

### `validate`

Validate an agent YAML configuration file.

```bash
agentik validate file .\agents\researcher.yaml
```

### `config`

Locate configuration file paths used by Agentik (`.agentikrc`).

**Global config path:**

```bash
agentik config path --global
```

**Local project config path:**

```bash
agentik config path --local
```

---

## Data & Evaluation

Work with agent memory, batch processing, and test evaluations.

### `memory`

Interact with an agent’s memory (requires a config file to target the correct memory store).

**Recall the last N items:**

```bash
agentik memory recall --config .\agents\researcher.yaml --n 5
```

**Clear memory:**

```bash
agentik memory clear --config .\agents\researcher.yaml
```

### `batch`

Run a set of prompts from a CSV or JSONL file through a specified model.

**Example: Prepare `prompts.csv`**

```text
id,question
1,"What is 2+2?"
2,"What is the capital of France?"
```

**Run the batch (using the `question` column):**

```bash
agentik batch run prompts.csv --column "question" --out results.jsonl --model "openai/gpt-4o-mini"
```

### `eval`

Evaluate an agent against test cases.

**Example: Create `tests.jsonl`**

```json
{"prompt": "What is the capital of Germany?", "expect_contains": ["Berlin"]}
{"prompt": "Calculate 5*5.", "expect_regex": "25"}
```

**Run the evaluation:**

```bash
agentik eval run tests.jsonl --config .\agents\researcher.yaml --out eval-results.jsonl
```

---

### Quick Tips

* Use `--no-stream` if your terminal shows streaming-related generator errors.
* Keep agent configs small and composable; prefer separate YAMLs for different roles.
* Commit `.agentikrc` cautiously; consider environment variables for secrets in CI/CD.

---

## Development

* **Lint/format:** `ruff check .` and `black .`
* **Tests:** `pytest -q`
* **Build:** `python -m build`
* **Publish:** `twine upload dist/*`

---

## Authors

* Vinay Joshi — [joshivinay822@gmail.com](mailto:joshivinay822@gmail.com)
* Avinash Raghuvanshi — [avi95461@gmail.com](mailto:avi95461@gmail.com)

## License

[MIT](LICENSE)

---

**Happy building with Agentik!**

---
