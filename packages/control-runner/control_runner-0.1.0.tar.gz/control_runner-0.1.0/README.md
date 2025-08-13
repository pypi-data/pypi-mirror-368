### Control Runner

Run control_arena experiments from YAML. Define settings, protocols, policies, monitors, and scorers as reusable components or inline specs. Then execute them from a single CLI.

### Why use it
- **Simple YAML**: Reference reusable components or define them inline
- **Dynamic variables**: `${var}` substitution and file-content expansion
- **Safe dry-runs**: Validate configs without importing heavy deps
- **Batteries included**: Rich built‑in registry mapped to control_arena

## Quick start (PyPI)

Prereqs: Python >= 3.13, `uv` installed.

```bash
# 1) Add to your project
uv add control-runner

# 2) Run with uv
uv run control_runner run path/to/config.yaml --dry-run  # validate
uv run control_runner run path/to/config.yaml            # execute

# Optional: include a custom module
uv run control_runner run path/to/config.yaml custom_ext.py --dry-run

# Alternative: one-off run without adding to your project
uvx control-runner run path/to/config.yaml --dry-run
```

## CLI

```text
control_runner run CONFIG [CUSTOM_PY] [--dry-run]
```

- `CONFIG` (required): Path to a YAML file
- `CUSTOM_PY` (optional): Path to a Python module for extensions (see below)
- `--dry-run`: Load and print tasks without running evaluation

Behavior:
- Sets `UNTRUSTED_MODEL` and `TRUSTED_MODEL` env vars if present in `vars`
- Groups tasks by their `limit` and runs each group via `inspect_ai.eval(tasks=..., limit=...)`

## YAML configuration

Top-level keys:
- `vars` (optional): Simple key/value variables
- `settings`: Named settings objects
- `components` (optional): Reusable components (policies, monitors, protocols, scorers, …)
- `tasks`: List of tasks to run

### Referencing values
You can reference values in two ways:
- `${name}`: explicit reference
- `name`: bare string; if it exactly matches a key in `vars`, `settings`, or `components`, it resolves to that value

String substitutions are supported for primitives inside larger strings, e.g. `"Model: ${untrusted_model}"`.

### Variables and file loading
Within `vars`, any string that looks like a path (`./`, `../`, or `/` and has an extension) is read as file content. This makes prompts easy to manage:

```yaml
vars:
  untrusted_model: google/gemini-2.5-flash
  trusted_model: google/gemini-2.5-flash-lite
  attack_monitor_prompt: ./prompts/attack_monitor_simple.txt  # contents will be in this var
```

Use these variables anywhere (including inside inline specs) via `${...}`.

### Inline specs and the registry
Components can be defined inline using either `type` (lookup in the registry) or `import` (direct Python import path):

```yaml
policy_builder:
  type: untrusted_policy
  params:
    honest: ${honest_policy_builder}
    attack: ${attack_policy_builder}

protocol:
  import: control_arena.protocol.dtt_protocol:dtt_protocol
  params:
    untrusted_policy_builder: ${policy_builder}
    monitor_builder: ${monitor_builder}
```

The registry contains keys for settings, policies, monitors, protocols, scorers, and tools. See `src/control_runner/registry.py` for the full list of supported names.

### Tasks

```yaml
tasks:
  - id: attack_task
    setting: ${apps_setting}          # reference or inline spec
    protocol: ${monitored_protocol}   # reference or inline spec
    mode: ATTACK                      # string or EvalMode name (case‑insensitive)
    monitoring_scorers:               # list of names or inline spec(s)
      - max_suspicion_scorer
    limit: 1                          # per‑group limit for inspect_ai.eval
```

`monitoring_scorers` accepts either a list or a single inline spec object.

### Settings and components
Reusable blocks defined under `settings` and `components` can be referenced from tasks or other components:

```yaml
settings:
  apps_setting:
    type: apps
    params:
      dataset_name: simple

components:
  monitored_protocol:
    type: tm_protocol
    params:
      policy_builder: ${untrusted_policy_builder}
      monitor_builder: ${untrusted_monitor_builder}
```

## Using a custom Python module
Pass a path to a Python file as the second CLI argument. If it defines `register(resolver)`, it will be called at load time so you can extend behavior (e.g., pre‑register objects, mutate vars):

```python
# custom_ext.py
def register(resolver):
    # Example: inject a computed variable
    resolver.vars["run_id"] = "local-dev"
```

Run with:

```bash
uv run python -m control_runner.cli run example_configs/components.yaml custom_ext.py --dry-run
```

## Examples

The `example_configs` directory shows common patterns:
- `components.yaml`: Reusable components and reference-based tasks
- `inline.yaml`: Fully inline protocol and nested inline components
- `inline_with_components.yaml`: Mix of inline protocol with referenced components
- `inline_strings.yaml`: Minimal config using bare string references

Run any example with `--dry-run` to validate it, then without to execute.

## Troubleshooting
- **Unknown reference**: Ensure the name exists in `vars`, `settings`, or `components`
- **Unknown type**: Check that the `type` exists in the registry (`src/control_runner/registry.py`)
- **File var not loaded**: File expansion only applies to values in `vars`

## Development

```text
control_runner/
├─ example_configs/
├─ prompts/
├─ src/control_runner/
│  ├─ cli.py         # Click CLI (recommended entrypoint)
│  ├─ loader.py      # YAML loading and resolution
│  └─ registry.py    # control_arena registry mapping
├─ tests/
└─ main.py           # Argparse legacy entrypoint
```

From source (repo checkout):

```bash
uv sync
uv run control_runner run example_configs/components.yaml --dry-run
```

## Testing

```bash
uv run pytest -q
```
