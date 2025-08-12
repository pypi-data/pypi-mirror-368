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

Create a minimal config (save as `configs/agent.yaml`):

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
agentik run .\configs\agent.yaml -p "Summarize the latest about OpenRouter rate limits"
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

Run an agent loop with profiles and run metadata.

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
agentik dev watch .\configs\agent.yaml `
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
