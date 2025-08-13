import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Optional

import click

from control_runner.loader import ConfigResolver, import_custom_module, load_yaml_config
from inspect_ai import Task


def _parse_mode(value: Any):
    # Lazy import to keep CLI lightweight for --help and parsing
    from control_arena.eval_mode import EvalMode  # noqa: WPS433

    if isinstance(value, EvalMode):
        return value
    if isinstance(value, str):
        name = value.split(".")[-1].upper()
        try:
            return EvalMode[name]
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"Unknown EvalMode: {value}") from exc
    raise TypeError(f"Mode must be a string or EvalMode, got {type(value)}")


def _group_by_limit(
    task_specs: Iterable[tuple[Task, dict[str, Any], Optional[int]]],
) -> dict[Optional[int], list[Task]]:
    by_limit: dict[Optional[int], list[Task]] = defaultdict(list)
    for task, task_params, limit in task_specs:
        by_limit[limit].append(task)
    return by_limit


def load_and_build_tasks_from_dict(
    raw_config: dict[str, Any], custom_py: Optional[str] = None
) -> list[tuple[Task, dict[str, Any], Optional[int]]]:
    # Lazy import to avoid heavy deps for non-run code paths
    from control_arena.eval.control_eval_def import get_control_task  # noqa: WPS433

    # Environment hints for downstream libraries
    vars_section = raw_config.get("vars", {})
    if "untrusted_model" in vars_section:
        os.environ["UNTRUSTED_MODEL"] = str(vars_section["untrusted_model"])
    if "trusted_model" in vars_section:
        os.environ["TRUSTED_MODEL"] = str(vars_section["trusted_model"])

    # Resolver uses cwd and (optionally) the YAML directory for relative files
    resolver = ConfigResolver(raw_config, base_dir=None)
    if custom_py:
        import_custom_module(custom_py, resolver)

    tasks_with_limits: list[tuple[Task, dict[str, Any], Optional[int]]] = []
    for task_def in raw_config.get("tasks", []):
        setting_obj = resolver.resolve_component(task_def["setting"])  # type: ignore[arg-type]
        protocol_obj = resolver.resolve_protocol(task_def["protocol"])  # type: ignore[arg-type]
        mode_value = _parse_mode(task_def.get("mode", "ATTACK"))
        scorers_list_spec = task_def.get("monitoring_scorers", [])
        monitoring_scorers = (
            resolver.resolve_component(scorers_list_spec)
            if isinstance(scorers_list_spec, dict)
            else [resolver.resolve_component(s) for s in scorers_list_spec]
        )

        task_params = dict(
            setting=setting_obj,
            protocol=protocol_obj,
            mode=mode_value,
            monitoring_scorers=monitoring_scorers,
        )
        tasks_with_limits.append(
            (get_control_task(**task_params), task_params, task_def.get("limit"))
        )

    return tasks_with_limits


def load_and_build_tasks(
    yaml_path: str, custom_py: Optional[str] = None
) -> list[tuple[Task, dict[str, Any], Optional[int]]]:
    raw_config = load_yaml_config(yaml_path)
    # Ensure base_dir used for file loading is the YAML file dir
    # ConfigResolver constructed inside load_and_build_tasks_from_dict uses cwd; set cwd to yaml dir temporarily
    yaml_dir = str(Path(yaml_path).resolve().parent)
    prev_cwd = os.getcwd()
    try:
        os.chdir(yaml_dir)
        return load_and_build_tasks_from_dict(raw_config, custom_py=custom_py)
    finally:
        os.chdir(prev_cwd)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Control Runner CLI."""


@cli.command("run")
@click.argument(
    "config", type=click.Path(exists=True, dir_okay=False, readable=True, path_type=str)
)
@click.argument(
    "custom_py",
    required=False,
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=str),
)
@click.option(
    "--dry-run", is_flag=True, help="Print tasks and exit without running eval"
)
def run_cmd(config: str, custom_py: Optional[str], dry_run: bool) -> None:
    """Run experiments from a YAML CONFIG file."""
    # Load raw YAML first so we can avoid importing heavy deps when doing a dry run

    tasks = load_and_build_tasks(config, custom_py)

    if dry_run:
        num_tasks = len(tasks)
        click.echo(f"Loaded {num_tasks} tasks (dry run). Nothing executed.")
        for i, (task, task_params, limit) in enumerate(tasks):
            click.echo(task_params)
        return

    # Lazy import of inspect_ai only when actually running
    from inspect_ai import eval as inspect_eval  # noqa: WPS433

    # Group tasks by desired limit and run eval per group
    grouped = _group_by_limit(tasks)

    for limit, group_tasks in grouped.items():
        inspect_eval(tasks=group_tasks, limit=limit)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
