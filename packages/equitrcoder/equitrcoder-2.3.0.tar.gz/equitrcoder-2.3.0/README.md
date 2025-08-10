# EQUITR Coder

Modular AI coding assistant supporting single and multi-agent workflows and an ML-focused researcher mode. Includes an advanced TUI.

## Quick Start

- Install (latest from PyPI):
  ```bash
pip install equitrcoder
  ```
- Optional extras:
  - API server: `pip install "equitrcoder[api]"`
  - TUI (Textual+Rich): `pip install textual rich`

## Configure API keys (env vars)

Set whatever providers you plan to use:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENROUTER_API_KEY`
- `MOONSHOT_API_KEY`
- `GROQ_API_KEY`

You can also set `CLAUDE_AGENT_MODEL`, `CLAUDE_AGENT_BUDGET`, and `CLAUDE_AGENT_PROFILE` to override defaults.

Export examples (macOS/Linux):
```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=...
export OPENROUTER_API_KEY=...
```

## TUI (Interactive)

- Launch TUI:
  ```bash
equitrcoder tui --mode single   # or multi, research
  ```
- Keys:
  - Enter: execute task in current mode (requires task in input field)
  - m: open model selector
  - Ctrl+C: exit
- Research mode fields:
  - Datasets: comma-separated paths
  - Experiments: `name:command; name:command; ...`

Troubleshooting:
- If you see a Textual widget error, ensure `textual` and `rich` are installed.
- If you have no API keys, you can still launch the TUI, but model listings will be minimal and execution may fail when contacting providers.

## CLI

- Single:
  ```bash
equitrcoder single "Build a small API" --model moonshot/kimi-k2-0711-preview
  ```
- Multi:
  ```bash
equitrcoder multi "Ship a feature" --supervisor-model moonshot/kimi-k2-0711-preview \
  --worker-model moonshot/kimi-k2-0711-preview --workers 3 --max-cost 15
  ```
- Research (ML only):
  ```bash
equitrcoder research "Evaluate model X on dataset Y" \
  --supervisor-model moonshot/kimi-k2-0711-preview --worker-model moonshot/kimi-k2-0711-preview \
  --workers 3 --max-cost 12
  ```

## Programmatic Usage

```python
from equitrcoder import EquitrCoder, TaskConfiguration

coder = EquitrCoder(mode="single", repo_path=".")
config = TaskConfiguration(description="Refactor module X", max_cost=2.0, max_iterations=20)
result = await coder.execute_task("Refactor module X", config)
print(result.success, result.cost, result.iterations)
```

- Multi-agent and researcher programmatic configs are available via `MultiAgentTaskConfiguration` and `ResearchTaskConfiguration`.

## API Server

- Start server (requires extras):
  ```bash
equitrcoder api --host 0.0.0.0 --port 8000
  ```
- Endpoints:
  - `GET /` root
  - `GET /health`
  - `GET /tools`
  - `POST /single/execute`
  - `POST /multi/create`
  - `POST /multi/{id}/execute`
  - `GET /multi/{id}/status`
  - `DELETE /multi/{id}`

## Configuration

- Default config lives in `equitrcoder/config/default.yaml`.
- User overrides: `~/.EQUITR-coder/config.yaml`.
- Env overrides supported for selected keys (see code and docs).
- `session.max_context: "auto"` is supported and normalized automatically.

## Examples

See `examples/` for patterns:
- `create_react_website.py`
- `mario_parallel_example.py`
- `research_programmatic_example.py`

## Troubleshooting

- Missing models or keys: ensure relevant env vars are set. The TUI will still load, but execution may fail when contacting providers.
- Textual errors: install TUI deps: `pip install textual rich`.
- Git integration issues: run inside a git repo or disable with `git_enabled=False` in programmatic usage. 