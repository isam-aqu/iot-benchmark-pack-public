#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

POWER_FIELDS = [
    "type",
    "power_seq",
    "exp",
    "t_local_us",
    "bus_v",
    "shunt_mV",
    "current_mA",
    "power_mW",
    "wifi_rssi",
    "last_event_seq",
    "last_event_t_local_us",
    "dt_since_event_us",
]

EVENT_FIELDS = [
    "type",
    "seq",
    "exp",
    "trigger",
    "t_local_us",
    "wifi_rssi",
]


def sanitize_serial_line(line: str) -> str:
    # PTY wrappers can prepend a few control bytes before the first printable
    # characters. The log format itself is ASCII, so stripping control chars
    # keeps parsing robust without affecting payload fields.
    cleaned = "".join(ch for ch in line if ch == "\t" or ord(ch) >= 32)
    return cleaned.strip()


def parse_kv_line(line: str) -> Tuple[str, Dict[str, str]] | None:
    line = sanitize_serial_line(line)
    if not line:
        return None
    if not (
        line.startswith("POWER_SAMPLE")
        or line.startswith("EVENT")
        or line.startswith("EXPERIMENT_COMPLETE")
    ):
        return None

    parts = line.split(",")
    rec_type = parts[0].strip()
    data: Dict[str, str] = {"type": rec_type.lower()}

    for part in parts[1:]:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        data[key.strip()] = value.strip()

    # Backward compatibility with earlier power logs using seq instead of power_seq
    if rec_type == "POWER_SAMPLE" and "power_seq" not in data and "seq" in data:
        data["power_seq"] = data["seq"]

    return rec_type, data


def infer_run_id(log_path: Path) -> str:
    stem = log_path.stem
    if stem.endswith("_serial"):
        return stem[:-7]
    return stem


def write_csv(path: Path, fieldnames: List[str], rows: Iterable[Dict[str, str]]) -> int:
    count = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse W2 serial logs into CSV files."
    )
    parser.add_argument("logfile", type=Path, help="Serial log file captured with tee")
    parser.add_argument("--run-id", type=str, default=None, help="Override run id")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for parsed CSV outputs. Defaults to the logfile directory.",
    )
    args = parser.parse_args()

    log_path = args.logfile
    if not log_path.exists():
        raise SystemExit(f"Log file not found: {log_path}")

    run_id = args.run_id or infer_run_id(log_path)
    output_dir = args.output_dir or log_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    power_rows: List[Dict[str, str]] = []
    event_rows: List[Dict[str, str]] = []
    meta: Dict[str, str] = {
        "run_id": run_id,
        "source_log": str(log_path),
    }

    with log_path.open("r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            parsed = parse_kv_line(raw_line)
            if parsed is None:
                continue

            rec_type, data = parsed
            if rec_type == "POWER_SAMPLE":
                power_rows.append(data)
            elif rec_type == "EVENT":
                event_rows.append(data)
            elif rec_type == "EXPERIMENT_COMPLETE":
                meta.update(data)

    power_csv = output_dir / f"{run_id}_power_samples.csv"
    event_csv = output_dir / f"{run_id}_mqtt_events.csv"
    meta_json = output_dir / f"{run_id}_meta.json"

    power_count = write_csv(power_csv, POWER_FIELDS, power_rows)
    event_count = write_csv(event_csv, EVENT_FIELDS, event_rows)

    meta["power_sample_count"] = str(power_count)
    meta["event_count"] = str(event_count)

    with meta_json.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"[OK] Parsed log: {log_path}")
    print(f"[OK] Power CSV : {power_csv} ({power_count} rows)")
    print(f"[OK] Event CSV : {event_csv} ({event_count} rows)")
    print(f"[OK] Meta JSON : {meta_json}")


if __name__ == "__main__":
    main()
