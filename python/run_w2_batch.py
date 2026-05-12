#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
import re
import select
import subprocess
import sys
import termios
import time
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

BAUD_RATES = {
    value: getattr(termios, f"B{value}")
    for value in (9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600)
    if hasattr(termios, f"B{value}")
}


@dataclass(frozen=True)
class W2Run:
    exp_run_id: str
    raw_run_id: str
    interval_ms: int
    run_type: str
    telemetry_enabled: bool
    replicate_id: str


class PosixSerial:
    def __init__(self, port: str, baud: int) -> None:
        if baud not in BAUD_RATES:
            supported = ", ".join(str(value) for value in sorted(BAUD_RATES))
            raise ValueError(f"Unsupported baud {baud}; supported values: {supported}")

        self.port = port
        self.baud = baud
        self.fd: int | None = None
        self._buffer = ""

    def __enter__(self) -> "PosixSerial":
        self.fd = os.open(self.port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        attrs = termios.tcgetattr(self.fd)
        attrs[0] = 0
        attrs[1] = 0
        attrs[2] = BAUD_RATES[self.baud] | termios.CS8 | termios.CLOCAL | termios.CREAD
        attrs[3] = 0
        attrs[4] = BAUD_RATES[self.baud]
        attrs[5] = BAUD_RATES[self.baud]
        attrs[6][termios.VMIN] = 0
        attrs[6][termios.VTIME] = 0
        termios.tcsetattr(self.fd, termios.TCSANOW, attrs)
        termios.tcflush(self.fd, termios.TCIOFLUSH)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def write_line(self, line: str) -> None:
        if self.fd is None:
            raise RuntimeError("serial port is not open")
        payload = (line.rstrip("\r\n") + "\n").encode("utf-8")
        os.write(self.fd, payload)

    def read_lines(self, timeout_sec: float) -> list[str]:
        if self.fd is None:
            raise RuntimeError("serial port is not open")

        ready, _, _ = select.select([self.fd], [], [], timeout_sec)
        if not ready:
            return []

        try:
            chunk = os.read(self.fd, 4096)
        except BlockingIOError:
            return []

        if not chunk:
            return []

        self._buffer += chunk.decode("utf-8", errors="replace")
        lines: list[str] = []

        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            line = line.strip("\r\n")
            if line:
                lines.append(line)

        return lines


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def run_number(run_id: str) -> int:
    match = re.fullmatch(r"R(\d+)", run_id.strip())
    if not match:
        raise ValueError(f"Run id must look like R698, got {run_id!r}")
    return int(match.group(1))


def load_run_sheet(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def interval_token(interval_ms: int) -> str:
    if interval_ms > 0 and interval_ms % 1000 == 0:
        return f"{interval_ms // 1000}s"
    return f"{interval_ms}ms"


def parse_interval_ms(value: str) -> int:
    cleaned = value.strip()
    if not re.fullmatch(r"\d+", cleaned):
        raise ValueError(f"W2 interval_ms must be an integer, got {value!r}")
    return int(cleaned)


def raw_run_id_for(row: dict[str, str]) -> str:
    interval_ms = parse_interval_ms(row["interval_ms"])
    run_type = row["run_type"].strip().lower()

    if run_type == "telemetry":
        mode_token = "telemetry"
    elif run_type in {"control", "ctrl"}:
        mode_token = "ctrl"
    else:
        raise ValueError(f"{row['run_id']}: unsupported W2 run_type {run_type!r}")

    replicate_id = row.get("replicate_id", "").strip()
    suffix = "" if replicate_id in {"", "primary"} else f"_{replicate_id}"
    return f"W2_wifi_periodic_{interval_token(interval_ms)}_quiet_{mode_token}_v2{suffix}"


def selected_rows(
    rows: list[dict[str, str]],
    *,
    run_ids: list[str] | None,
    from_run: str | None,
    to_run: str | None,
) -> list[dict[str, str]]:
    by_id = {row["run_id"]: row for row in rows}

    if run_ids:
        missing = [run_id for run_id in run_ids if run_id not in by_id]
        if missing:
            raise SystemExit(f"Run id(s) not found in run sheet: {', '.join(missing)}")
        return [by_id[run_id] for run_id in run_ids]

    if from_run and to_run:
        start = run_number(from_run)
        end = run_number(to_run)
        if end < start:
            raise SystemExit("--to-run must be greater than or equal to --from-run")
        return [
            row for row in rows
            if re.fullmatch(r"R\d+", row["run_id"])
            and start <= run_number(row["run_id"]) <= end
        ]

    raise SystemExit("Select runs with --run-id R698 [R699 ...] or --from-run/--to-run.")


def row_to_w2_run(row: dict[str, str]) -> W2Run:
    exp_run_id = row["run_id"].strip()
    workload = row.get("workload", "").strip()
    protocol = row.get("protocol", "").strip()
    run_type = row.get("run_type", "").strip().lower()

    if workload != "W2" or protocol != "wifi":
        raise ValueError(f"{exp_run_id}: expected W2/wifi row, got {workload}/{protocol}")

    if run_type not in {"control", "telemetry"}:
        raise ValueError(f"{exp_run_id}: expected control or telemetry, got {run_type!r}")

    interval_ms = parse_interval_ms(row["interval_ms"])
    return W2Run(
        exp_run_id=exp_run_id,
        raw_run_id=raw_run_id_for(row),
        interval_ms=interval_ms,
        run_type=run_type,
        telemetry_enabled=run_type == "telemetry",
        replicate_id=row.get("replicate_id", "").strip() or "primary",
    )


def shell_join(cmd: list[str]) -> str:
    import shlex

    return " ".join(shlex.quote(part) for part in cmd)


def run_subprocess(
    cmd: list[str],
    *,
    env: dict[str, str] | None = None,
    dry_run: bool = False,
) -> None:
    prefix = "$ " if env is None else f"$ EXP_RUN_ID={env.get('EXP_RUN_ID', '')} "
    if env is not None and "EXP_RUN_ID" in env:
        display_cmd = shell_join(cmd)
    else:
        display_cmd = shell_join(cmd)

    print(f"{prefix}{display_cmd}")
    if dry_run:
        return

    subprocess.run(cmd, cwd=REPO_ROOT, env=env, check=True)


def upload_firmware(args: argparse.Namespace) -> None:
    sketch = str(repo_path(args.sketch))
    config_args = []
    if args.arduino_config_file:
        config_args = ["--config-file", str(repo_path(args.arduino_config_file))]

    compile_cmd = [
        args.arduino_cli,
        "compile",
        *config_args,
        "--fqbn",
        args.fqbn,
        sketch,
    ]
    upload_cmd = [
        args.arduino_cli,
        "upload",
        *config_args,
        "-p",
        args.serial_port,
        "--fqbn",
        args.fqbn,
        sketch,
    ]

    run_subprocess(compile_cmd, dry_run=args.dry_run)
    run_subprocess(upload_cmd, dry_run=args.dry_run)

    if not args.dry_run and args.post_upload_wait_sec > 0:
        time.sleep(args.post_upload_wait_sec)


def configure_device(args: argparse.Namespace, run: W2Run) -> None:
    duration_ms = args.firmware_duration_sec * 1000
    command = (
        f"CONFIG exp={run.raw_run_id} "
        f"interval_ms={run.interval_ms} "
        f"telemetry={1 if run.telemetry_enabled else 0} "
        f"duration_ms={duration_ms} "
        f"power_ms={args.power_sample_ms}"
    )

    print(f"[W2] Configure {run.exp_run_id}: {command}")
    if args.dry_run:
        return

    deadline = time.monotonic() + args.config_timeout_sec
    next_send = 0.0
    seen_lines: list[str] = []
    ignored_unknown_config_errors = 0

    with PosixSerial(args.serial_port, args.serial_baud) as serial:
        for _ in range(max(args.config_sync_newlines, 0)):
            serial.write_line("")
            time.sleep(0.05)

        while time.monotonic() < deadline:
            now = time.monotonic()
            if now >= next_send:
                serial.write_line(command)
                next_send = now + args.config_retry_sec

            for line in serial.read_lines(0.25):
                seen_lines.append(line)
                seen_lines = seen_lines[-8:]
                if args.verbose_serial:
                    print(f"[SERIAL] {line}")
                if line.startswith("CONFIG_ERROR"):
                    if "reason=unknown_command" in line:
                        ignored_unknown_config_errors += 1
                        continue
                    raise RuntimeError(f"{run.exp_run_id}: firmware rejected config: {line}")
                if line.startswith("CONFIG_OK"):
                    serial.write_line("SHOW_CONFIG")
                    config_deadline = time.monotonic() + 2.0
                    while time.monotonic() < config_deadline:
                        for verify_line in serial.read_lines(0.25):
                            if args.verbose_serial:
                                print(f"[SERIAL] {verify_line}")
                            if verify_line.startswith("CONFIG_STATE"):
                                print(f"[W2] {verify_line}")
                                return
                    return

    detail = ""
    if ignored_unknown_config_errors:
        detail = (
            " Saw CONFIG_ERROR/unknown_command responses, which usually means "
            "the ESP32 is still running the pre-0.5.0 firmware parser or the "
            "serial RX line is receiving garbage before CONFIG."
        )
    elif not seen_lines:
        detail = (
            " Saw no serial response at all. Check TX/RX crossover, shared GND, "
            "baud rate, and that the uploaded firmware is the INA231 power-node "
            "runtime-config firmware."
        )

    if seen_lines:
        recent = " Recent serial lines: " + " | ".join(seen_lines[-4:])
    else:
        recent = ""

    raise TimeoutError(
        f"{run.exp_run_id}: timed out waiting for CONFIG_OK on "
        f"{args.serial_port}.{detail}{recent}"
    )


def run_experiment(args: argparse.Namespace, run: W2Run) -> None:
    env = os.environ.copy()
    env["EXP_RUN_ID"] = run.exp_run_id
    runner_duration = args.runner_duration_sec or (
        args.firmware_duration_sec + args.runner_padding_sec
    )
    cmd = [
        str(repo_path(args.run_all)),
        "--run-id",
        run.raw_run_id,
        "--disable-ble",
        "--disable-ack",
        "--duration-sec",
        str(runner_duration),
        "--serial-port",
        args.serial_port,
        "--serial-baud",
        str(args.serial_baud),
    ]

    if args.start_over_serial:
        cmd.extend([
            "--no-reset-esp32",
            "--serial-start-command",
            "START",
            "--serial-start-delay-sec",
            str(args.serial_start_delay_sec),
        ])
    elif args.no_reset:
        cmd.append("--no-reset-esp32")
    else:
        cmd.extend([
            "--reset-esp32",
            "--reset-settle-sec",
            str(args.reset_settle_sec),
        ])

    run_subprocess(cmd, env=env, dry_run=args.dry_run)


def analyze_run(args: argparse.Namespace, run: W2Run) -> None:
    raw_dir = REPO_ROOT / "experiments" / "runs" / run.exp_run_id / "raw"
    serial_log = raw_dir / f"{run.raw_run_id}_serial.log"

    commands = [
        [
            sys.executable,
            "scripts/parse_w2_control_serial.py",
            str(serial_log),
            "--run-id",
            run.raw_run_id,
        ],
        [
            sys.executable,
            "python/summarize_w2_run.py",
            str(raw_dir),
            "--run-id",
            run.raw_run_id,
        ],
        [
            sys.executable,
            "python/analyze_w2_run.py",
            str(raw_dir),
            "--run-id",
            run.raw_run_id,
            "--run-sheet",
            str(repo_path(args.run_sheet)),
        ],
    ]

    for cmd in commands:
        run_subprocess(cmd, dry_run=args.dry_run)


def analyze_groups(args: argparse.Namespace) -> None:
    cmd = [
        sys.executable,
        "python/analyze_w2_groups.py",
        "--run-sheet",
        str(repo_path(args.run_sheet)),
    ]
    run_subprocess(cmd, dry_run=args.dry_run)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Configure the W2 ESP32 power node over serial, run selected "
            "run-sheet rows, and regenerate per-run W2 analysis."
        )
    )
    parser.add_argument("--run-sheet", default="docs/run_sheet.csv")
    parser.add_argument("--run-id", nargs="+", help="Run-sheet id(s), e.g. R698 R699.")
    parser.add_argument("--from-run", help="Inclusive first run id, e.g. R698.")
    parser.add_argument("--to-run", help="Inclusive final run id, e.g. R733.")
    parser.add_argument("--serial-port", required=True)
    parser.add_argument("--serial-baud", type=int, default=115200)
    parser.add_argument("--firmware-duration-sec", type=int, default=300)
    parser.add_argument("--runner-duration-sec", type=int, default=None)
    parser.add_argument("--runner-padding-sec", type=int, default=20)
    parser.add_argument("--power-sample-ms", type=int, default=100)
    parser.add_argument("--reset-settle-sec", type=float, default=2)
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="Do not request ESP32 reset from run_all.sh.",
    )
    parser.add_argument(
        "--start-over-serial",
        action="store_true",
        help=(
            "Use run_all.sh serial capture to send START after loggers are ready; "
            "implies --no-reset."
        ),
    )
    parser.add_argument("--serial-start-delay-sec", type=float, default=0.0)
    parser.add_argument("--config-timeout-sec", type=float, default=30)
    parser.add_argument("--config-retry-sec", type=float, default=1)
    parser.add_argument("--config-sync-newlines", type=int, default=3)
    parser.add_argument("--upload", action="store_true", help="Compile/upload once before the batch.")
    parser.add_argument("--upload-each-run", action="store_true", help="Compile/upload before every run.")
    parser.add_argument("--arduino-cli", default="arduino-cli")
    parser.add_argument("--arduino-config-file", default=None)
    parser.add_argument("--fqbn", default="esp32:esp32:esp32")
    parser.add_argument("--sketch", default="firmware/power_node_ina231")
    parser.add_argument("--post-upload-wait-sec", type=float, default=5)
    parser.add_argument("--skip-analysis", action="store_true")
    parser.add_argument("--skip-group-analysis", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose-serial", action="store_true")
    parser.add_argument("--run-all", default="./run_all.sh")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.no_reset and not args.start_over_serial:
        args.start_over_serial = True
        print("[W2] --no-reset selected; enabling --start-over-serial so the firmware starts after loggers are ready.")

    rows = load_run_sheet(repo_path(args.run_sheet))
    selected = selected_rows(
        rows,
        run_ids=args.run_id,
        from_run=args.from_run,
        to_run=args.to_run,
    )
    runs = [row_to_w2_run(row) for row in selected]

    print("[W2] Planned run order:")
    for run in runs:
        mode = "telemetry" if run.telemetry_enabled else "control"
        print(f"  {run.exp_run_id}: {run.raw_run_id} ({run.interval_ms} ms, {mode})")

    if args.upload and not args.upload_each_run:
        upload_firmware(args)

    failures: list[tuple[str, str]] = []

    for run in runs:
        print(f"\n[W2] === {run.exp_run_id} ===")
        try:
            if args.upload_each_run:
                upload_firmware(args)
            configure_device(args, run)
            run_experiment(args, run)
            if not args.skip_analysis:
                analyze_run(args, run)
        except Exception as exc:
            failures.append((run.exp_run_id, str(exc)))
            print(f"[W2][ERROR] {run.exp_run_id}: {exc}", file=sys.stderr)
            if not args.continue_on_error:
                raise

    if not args.skip_analysis and not args.skip_group_analysis:
        analyze_groups(args)

    if failures:
        print("\n[W2] Failures:")
        for run_id, message in failures:
            print(f"  {run_id}: {message}")
        raise SystemExit(1)

    print("\n[W2] Batch complete.")


if __name__ == "__main__":
    main()
