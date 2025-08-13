from pathlib import Path

from click.testing import CliRunner

from control_runner.cli import cli


def _example_yaml_paths() -> list[Path]:
    project_root = Path(__file__).resolve().parents[1]
    examples_dir = project_root / "example_configs"
    return sorted(examples_dir.glob("*.yaml"))


def test_cli_dry_run_all_example_configs() -> None:
    runner = CliRunner()
    yaml_paths = _example_yaml_paths()
    assert yaml_paths, "No example YAML files found in example_configs/"

    for yaml_path in yaml_paths:
        # Dry-run should not import heavy deps or execute eval
        result = runner.invoke(cli, ["run", str(yaml_path), "--dry-run"])  # type: ignore[list-item]
        assert result.exit_code == 0, (
            f"CLI failed for {yaml_path.name} with exit_code={result.exit_code}\n"
            f"Output:\n{result.output}\nException: {result.exception}"
        )
