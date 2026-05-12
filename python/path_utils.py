from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def get_experiment_run_id(required: bool = False) -> str | None:
    value = os.getenv("EXP_RUN_ID", "").strip()
    if required and not value:
        raise SystemExit("EXP_RUN_ID is required for the experiments/ path layout.")
    return value or None


def run_dir(exp_run_id: str) -> Path:
    return repo_root() / "experiments" / "runs" / exp_run_id


def raw_dir(exp_run_id: str) -> Path:
    path = run_dir(exp_run_id) / "raw"
    path.mkdir(parents=True, exist_ok=True)
    return path


def derived_dir(exp_run_id: str) -> Path:
    path = run_dir(exp_run_id) / "derived"
    path.mkdir(parents=True, exist_ok=True)
    return path


def figures_dir(exp_run_id: str) -> Path:
    path = run_dir(exp_run_id) / "figures"
    path.mkdir(parents=True, exist_ok=True)
    return path


def summaries_figures_dir() -> Path:
    path = repo_root() / "experiments" / "summaries" / "figures"
    path.mkdir(parents=True, exist_ok=True)
    return path

