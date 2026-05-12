from __future__ import annotations

import argparse
import csv
import json
import os
import random
import signal
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from path_utils import get_experiment_run_id, raw_dir
from version_info import build_metadata, load_version_info


SCRIPT_NAME = "python/ha_zigbee_trigger.py"
DEFAULT_HA_URL = "http://<private-ip>:8123"
DEFAULT_ENTITY_ID = "light.benchmark_device"
DEFAULT_EVENTS = 100
DEFAULT_BASE_INTERVAL_MS = 3000
DEFAULT_JITTER_MS = 250

VERSION_INFO = load_version_info()

stop_requested = False


@dataclass(frozen=True)
class TriggerConfig:
    ha_url: str
    token: str
    run_id: str
    entity_id: str
    event_count: int
    base_interval_ms: int
    jitter_ms: int
    seed: int
    setup_helpers: bool
    disable_on_exit: bool
    dry_run: bool
    output_path: Path


def install_signal_handlers() -> None:
    def request_stop(_signum, _frame) -> None:
        global stop_requested
        stop_requested = True

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, request_stop)


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be > 0")
    return parsed


def non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return parsed


def default_seed(run_id: str) -> int:
    # Stable enough for reproducible schedules without relying on Python hash().
    return sum((idx + 1) * ord(ch) for idx, ch in enumerate(run_id)) % (2**31)


def parse_args() -> TriggerConfig:
    env_ha_url = os.getenv("HA_URL") or os.getenv("HOME_ASSISTANT_URL") or DEFAULT_HA_URL
    env_token = os.getenv("HA_TOKEN") or os.getenv("HOME_ASSISTANT_TOKEN") or ""
    env_run_id = os.getenv("RUN_ID", "").strip()

    parser = argparse.ArgumentParser(
        description="Drive W3 Zigbee state-change triggers through the Home Assistant REST API."
    )
    parser.add_argument("--ha-url", default=env_ha_url)
    parser.add_argument("--token", default=env_token)
    parser.add_argument("--run-id", default=env_run_id)
    parser.add_argument("--entity-id", default=os.getenv("ZIGBEE_ENTITY_ID", DEFAULT_ENTITY_ID))
    parser.add_argument("--events", type=positive_int, default=int(os.getenv("ZIGBEE_EVENT_COUNT", DEFAULT_EVENTS)))
    parser.add_argument(
        "--base-interval-ms",
        type=positive_int,
        default=int(os.getenv("ZIGBEE_BASE_INTERVAL_MS", DEFAULT_BASE_INTERVAL_MS)),
    )
    parser.add_argument(
        "--jitter-ms",
        type=non_negative_int,
        default=int(os.getenv("ZIGBEE_JITTER_MS", DEFAULT_JITTER_MS)),
    )
    parser.add_argument("--seed", type=non_negative_int)
    parser.add_argument("--no-setup-helpers", action="store_true")
    parser.add_argument("--leave-enabled", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output")

    args = parser.parse_args()

    if not args.run_id:
        raise SystemExit("RUN_ID is required; pass --run-id or set RUN_ID.")

    if not args.token and not args.dry_run:
        raise SystemExit(
            "Home Assistant token is required. Set HA_TOKEN or HOME_ASSISTANT_TOKEN, "
            "or pass --token."
        )

    exp_run_id = get_experiment_run_id(required=False)
    if args.output:
        output_path = Path(args.output)
    elif exp_run_id:
        output_path = raw_dir(exp_run_id) / f"{args.run_id}_zigbee_trigger_schedule.csv"
    else:
        output_path = Path(f"{args.run_id}_zigbee_trigger_schedule.csv")

    seed = args.seed if args.seed is not None else default_seed(args.run_id)

    return TriggerConfig(
        ha_url=args.ha_url.rstrip("/"),
        token=args.token,
        run_id=args.run_id,
        entity_id=args.entity_id,
        event_count=args.events,
        base_interval_ms=args.base_interval_ms,
        jitter_ms=args.jitter_ms,
        seed=seed,
        setup_helpers=not args.no_setup_helpers,
        disable_on_exit=not args.leave_enabled,
        dry_run=args.dry_run,
        output_path=output_path,
    )


class HomeAssistantClient:
    def __init__(self, ha_url: str, token: str, dry_run: bool = False):
        self.ha_url = ha_url
        self.token = token
        self.dry_run = dry_run

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, Any]:
        if self.dry_run:
            print(f"[DRY-RUN] {method} {path} {payload or {}}")
            return 200, {}

        body = None
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            f"{self.ha_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                raw = response.read().decode("utf-8")
                if not raw:
                    return response.status, None
                try:
                    return response.status, json.loads(raw)
                except json.JSONDecodeError:
                    return response.status, raw
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Home Assistant HTTP {exc.code} for {path}: {raw}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach Home Assistant at {self.ha_url}: {exc}") from exc

    def call_service(self, domain: str, service: str, payload: dict[str, Any]) -> tuple[int, Any]:
        return self.request("POST", f"/api/services/{domain}/{service}", payload)

    def get_state(self, entity_id: str) -> str | None:
        status, payload = self.request("GET", f"/api/states/{entity_id}")
        if status >= 400 or not isinstance(payload, dict):
            return None
        state = payload.get("state")
        return str(state) if state is not None else None


def write_header(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "command_index",
                "target_state",
                "planned_offset_ms",
                "sent_time_ns",
                "sent_at_local",
                "status_code",
                "error",
                "pipeline_version",
            ],
        )
        writer.writeheader()


def append_row(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "command_index",
                "target_state",
                "planned_offset_ms",
                "sent_time_ns",
                "sent_at_local",
                "status_code",
                "error",
                "pipeline_version",
            ],
        )
        writer.writerow(row)


def configure_helpers(client: HomeAssistantClient, run_id: str, enabled: bool) -> None:
    if enabled:
        client.call_service(
            "input_text",
            "set_value",
            {"entity_id": "input_text.current_experiment_id", "value": run_id},
        )
        client.call_service(
            "input_boolean",
            "turn_on",
            {"entity_id": "input_boolean.benchmark_run_enabled"},
        )
    else:
        client.call_service(
            "input_boolean",
            "turn_off",
            {"entity_id": "input_boolean.benchmark_run_enabled"},
        )


def opposite_state(state: str | None) -> str:
    if state == "on":
        return "off"
    return "on"


def service_for_state(state: str) -> str:
    if state == "on":
        return "turn_on"
    if state == "off":
        return "turn_off"
    raise ValueError(f"Unsupported target state: {state}")


def run_schedule(config: TriggerConfig) -> int:
    install_signal_handlers()
    client = HomeAssistantClient(config.ha_url, config.token, config.dry_run)
    rng = random.Random(config.seed)
    domain = config.entity_id.split(".", 1)[0]

    print(f"[INFO] Pipeline version: {VERSION_INFO.pipeline_version}")
    print(f"[INFO] Zigbee trigger schedule seed: {config.seed}")
    print(f"[INFO] Writing trigger schedule to: {config.output_path}")

    write_header(config.output_path)
    metadata_path = config.output_path.with_suffix(f"{config.output_path.suffix}.meta.json")
    metadata_path.write_text(
        json.dumps(
            {
                "metadata": build_metadata(
                    SCRIPT_NAME,
                    outputs=[config.output_path, metadata_path],
                    extra={
                        "run_id": config.run_id,
                        "entity_id": config.entity_id,
                        "events": config.event_count,
                        "base_interval_ms": config.base_interval_ms,
                        "jitter_ms": config.jitter_ms,
                        "seed": config.seed,
                    },
                )
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    configured_helpers = False
    exit_code = 0

    try:
        if config.setup_helpers:
            configure_helpers(client, config.run_id, True)
            configured_helpers = True

        current_state = client.get_state(config.entity_id)
        target_state = opposite_state(current_state)
        start_ns = time.monotonic_ns()
        next_offset_ms = 0

        for command_index in range(1, config.event_count + 1):
            if stop_requested:
                exit_code = 130
                break

            planned_time_ns = start_ns + int(next_offset_ms * 1_000_000)
            while True:
                remaining_ns = planned_time_ns - time.monotonic_ns()
                if remaining_ns <= 0 or stop_requested:
                    break
                time.sleep(min(remaining_ns / 1_000_000_000, 0.25))

            sent_time_ns = time.time_ns()
            error = ""
            status_code = ""

            try:
                status_code, _payload = client.call_service(
                    domain,
                    service_for_state(target_state),
                    {"entity_id": config.entity_id},
                )
            except Exception as exc:  # noqa: BLE001 - record and continue to cleanup.
                error = str(exc)
                exit_code = 1

            append_row(
                config.output_path,
                {
                    "command_index": command_index,
                    "target_state": target_state,
                    "planned_offset_ms": next_offset_ms,
                    "sent_time_ns": sent_time_ns,
                    "sent_at_local": datetime.now().astimezone().isoformat(timespec="milliseconds"),
                    "status_code": status_code,
                    "error": error,
                    "pipeline_version": VERSION_INFO.pipeline_version,
                },
            )

            if error:
                print(f"[ERROR] command {command_index}: {error}", file=sys.stderr)
                break

            print(f"ZIGBEE_TRIGGER command={command_index} target={target_state}")

            target_state = "off" if target_state == "on" else "on"
            if command_index < config.event_count:
                jitter = rng.randint(-config.jitter_ms, config.jitter_ms)
                next_offset_ms += config.base_interval_ms + jitter

    finally:
        if configured_helpers and config.disable_on_exit:
            try:
                configure_helpers(client, config.run_id, False)
            except Exception as exc:  # noqa: BLE001
                print(f"[WARN] Could not disable benchmark helper: {exc}", file=sys.stderr)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(run_schedule(parse_args()))
