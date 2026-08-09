"""Pure core functions: scenario loading, validation, manifest assembly.

No network, no LLM — all unit-testable.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml


def load_scenario(path: Path) -> dict:
    """Load a single YAML scenario file.

    Args:
        path: Path to scenario YAML file

    Returns:
        Scenario dict

    Raises:
        ValueError: If file is not valid YAML or missing required fields
    """
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"scenario must be a YAML object, got {type(data).__name__}")
    return data


def load_scenarios(scenario_dir: Path) -> list[dict]:
    """Load all scenario YAML files from a directory.

    Args:
        scenario_dir: Directory containing .yaml/.yml files

    Returns:
        List of scenario dicts
    """
    scenarios = []
    for path in sorted(scenario_dir.glob("*.y*ml")):
        if path.suffix not in {".yaml", ".yml"}:
            continue
        scenarios.append(load_scenario(path))
    return scenarios


def validate_scenario(scenario: dict, schema_path: Path) -> None:
    """Validate a scenario against the JSON schema.

    Args:
        scenario: Scenario dict to validate
        schema_path: Path to schema.json

    Raises:
        jsonschema.ValidationError: If scenario is invalid
    """
    schema = json.loads(schema_path.read_text())
    jsonschema.validate(scenario, schema)


def load_tools(tools_path: Path) -> list[dict]:
    """Load tool definitions from JSON file.

    Args:
        tools_path: Path to tools JSON file

    Returns:
        List of tool definition dicts
    """
    return json.loads(tools_path.read_text())


def assemble_manifest(
    *,
    run_id: str,
    model: str,
    corpus_git_sha: str,
    started: str,
    finished: str,
    results: list[dict],
) -> dict:
    """Build a run manifest from scenario results.

    Args:
        run_id: Unique run identifier
        model: Model name/identifier
        corpus_git_sha: Git SHA of the scenario corpus
        started: ISO 8601 timestamp of run start
        finished: ISO 8601 timestamp of run finish
        results: List of per-scenario result dicts with keys:
                 id, pass, reason, started, finished, transcript

    Returns:
        Manifest dict
    """
    return {
        "schema_version": 1,
        "run_id": run_id,
        "model": model,
        "corpus_git_sha": corpus_git_sha,
        "started": started,
        "finished": finished,
        "results": [
            {
                "id": r["id"],
                "pass": r["pass"],
                "reason": r["reason"],
                "started": r["started"],
                "finished": r["finished"],
                "transcript": r["transcript"],
            }
            for r in results
        ],
    }
