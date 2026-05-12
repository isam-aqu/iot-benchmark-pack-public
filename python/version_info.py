from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class VersionInfo:
    firmware_version: str = "unknown"
    ha_config_version: str = "unknown"
    analysis_version: str = "unknown"
    logger_version: str = "unknown"
    ha_automation_version: str = "unknown"
    experiment_protocol_version: str = "unknown"
    pipeline_version: str = "unknown"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def display_path(path: str | Path) -> str:
    p = Path(path)
    root = repo_root()

    try:
        resolved = p.resolve() if p.is_absolute() else (root / p).resolve()
        return str(resolved.relative_to(root))
    except (OSError, ValueError):
        return str(p)


def load_version_info() -> VersionInfo:
    path = repo_root() / "experiments" / "version_info.yaml"

    if not path.exists():
        return VersionInfo()

    with path.open("r", encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}

    return VersionInfo(
        firmware_version=str(raw.get("firmware_version", "unknown")),
        ha_config_version=str(raw.get("ha_config_version", "unknown")),
        analysis_version=str(raw.get("analysis_version", "unknown")),
        logger_version=str(raw.get("logger_version", "unknown")),
        ha_automation_version=str(raw.get("ha_automation_version", "unknown")),
        experiment_protocol_version=str(raw.get("experiment_protocol_version", "unknown")),
        pipeline_version=str(raw.get("pipeline_version", "unknown")),
    )


def _git_text(args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root(),
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None

    return result.stdout.strip()


def git_info() -> dict[str, Any]:
    status = _git_text(["status", "--porcelain"])
    return {
        "commit": _git_text(["rev-parse", "--short", "HEAD"]),
        "branch": _git_text(["rev-parse", "--abbrev-ref", "HEAD"]),
        "dirty": bool(status),
    }


def build_metadata(
    script_name: str,
    *,
    inputs: list[str | Path] | None = None,
    outputs: list[str | Path] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    versions = load_version_info()
    generated_at_utc = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    local_now = datetime.now().astimezone()

    metadata: dict[str, Any] = {
        "script": script_name,
        "generated_at_utc": generated_at_utc,
        "generated_at_local": local_now.isoformat(timespec="seconds"),
        "timezone": local_now.tzname(),
        "versions": {
            "pipeline": versions.pipeline_version,
            "firmware": versions.firmware_version,
            "ha_config": versions.ha_config_version,
            "analysis": versions.analysis_version,
            "logger": versions.logger_version,
            "ha_automation": versions.ha_automation_version,
            "experiment_protocol": versions.experiment_protocol_version,
        },
        "git": git_info(),
        "python": sys.version.split()[0],
    }

    run_instance_id = os.getenv("RUN_INSTANCE_ID", "").strip()
    if run_instance_id:
        metadata["run_instance_id"] = run_instance_id

    if inputs is not None:
        metadata["inputs"] = [display_path(path) for path in inputs]

    if outputs is not None:
        metadata["outputs"] = [display_path(path) for path in outputs]

    if extra:
        metadata["extra"] = extra

    return metadata


def write_metadata(
    path: str | Path,
    script_name: str,
    *,
    inputs: list[str | Path] | None = None,
    outputs: list[str | Path] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": build_metadata(
            script_name,
            inputs=inputs,
            outputs=outputs if outputs is not None else [out],
            extra=extra,
        )
    }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload["metadata"]
