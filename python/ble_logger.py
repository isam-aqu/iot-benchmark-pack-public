import asyncio
import csv
import os
import signal
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Optional

from bleak import BleakScanner

from version_info import load_version_info
from path_utils import raw_dir, get_experiment_run_id

VERSION_INFO = load_version_info()
PIPELINE_VERSION = VERSION_INFO.pipeline_version
SCRIPT_VERSION = VERSION_INFO.logger_version

print(f"[INFO] Pipeline version: {PIPELINE_VERSION} | BLE logger version: {SCRIPT_VERSION}")

RUN_ID = os.getenv("RUN_ID", "").strip()
if not RUN_ID:
    RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

EXP_RUN_ID = get_experiment_run_id(required=True)
OUT_DIR = raw_dir(EXP_RUN_ID)
ble_file = OUT_DIR / f"{RUN_ID}_ble_events.csv"

FIELDS = [
    "pi_rx_time_ns", "address", "name", "rssi", "company_id",
    "version", "node_num", "exp_code", "seq", "t_local_us",
    "raw_hex", "pipeline_version",
]

def get_env_int(name: str, default: int, *, min_value: Optional[int] = None) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        value = default
    else:
        try:
            value = int(raw, 0)
        except ValueError as exc:
            raise SystemExit(
                f"Invalid value for {name}: {raw!r}. Expected an integer."
            ) from exc

    if min_value is not None and value < min_value:
        raise SystemExit(
            f"Invalid value for {name}: {value}. Must be >= {min_value}."
        )

    return value


def ensure_csv_header(path: Path, fields: list[str]) -> None:
    expected_header = ",".join(fields)

    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=fields).writeheader()
        return

    try:
        with path.open("r", newline="", encoding="utf-8") as f:
            first_line = f.readline().strip()
    except OSError:
        first_line = ""

    if first_line == expected_header:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rotated_target = path.with_name(f"{path.stem}_badheader_{timestamp}{path.suffix}")
    try:
        path.rename(rotated_target)
        rotation_notice = f" and was rotated to: {rotated_target}"
    except OSError as exc:
        rotation_notice = (
            f"; attempted to rotate to {rotated_target} but rename failed: {exc}. "
            "Continuing by overwriting existing file."
        )

    with path.open("w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=fields).writeheader()

    print(f"[WARN] Existing BLE file had missing/mismatched header{rotation_notice}")


EXPECTED_COMPANY_ID = get_env_int("BLE_EXPECTED_COMPANY_ID", 0x1234, min_value=0)
EXPECTED_VERSION = get_env_int("BLE_EXPECTED_VERSION", 2, min_value=0)
EXPECTED_EXP_CODE = os.getenv("BLE_EXPECTED_EXP_CODE", "W1BL").strip() or "W1BL"
EXPECTED_NODE_NUM = get_env_int("BLE_EXPECTED_NODE_NUM", 1, min_value=0)
DEDUP_WINDOW = get_env_int("BLE_DEDUP_WINDOW", 512, min_value=1)

ensure_csv_header(ble_file, FIELDS)

seen = set()
recent_keys = deque()
locked_address = None


def remember_sequence(address: str, seq: int) -> bool:
    key = (address, seq)
    if key in seen:
        return False

    seen.add(key)
    recent_keys.append(key)

    while len(recent_keys) > DEDUP_WINDOW:
        seen.discard(recent_keys.popleft())

    return True


def parse_mfg(company_id: int, payload: bytes):
    if len(payload) < 14:
        return None
    return {
        "company_id": company_id,
        "version": payload[0],
        "node_num": payload[1],
        "exp_code": payload[2:6].decode("ascii", errors="replace"),
        "seq": int.from_bytes(payload[6:10], "little"),
        "t_local_us": int.from_bytes(payload[10:14], "little"),
        "raw_hex": payload.hex(),
    }


def detection_callback(device, advertisement_data):
    global locked_address

    now_ns = time.time_ns()
    mfg = advertisement_data.manufacturer_data
    if not mfg:
        return

    for company_id, payload in mfg.items():
        parsed = parse_mfg(company_id, payload)
        if not parsed:
            continue

        if parsed["company_id"] != EXPECTED_COMPANY_ID:
            continue
        if parsed["version"] != EXPECTED_VERSION:
            continue
        if parsed["exp_code"] != EXPECTED_EXP_CODE:
            continue
        if parsed["node_num"] != EXPECTED_NODE_NUM:
            continue

        if locked_address is None:
            locked_address = device.address
            print(f"Locked BLE benchmark address: {locked_address}")

        if device.address != locked_address:
            continue

        if not remember_sequence(device.address, parsed["seq"]):
            continue

        row = {
            "pi_rx_time_ns": now_ns,
            "address": device.address,
            "name": device.name,
            "rssi": advertisement_data.rssi,
            "company_id": parsed["company_id"],
            "version": parsed["version"],
            "node_num": parsed["node_num"],
            "exp_code": parsed["exp_code"],
            "seq": parsed["seq"],
            "t_local_us": parsed["t_local_us"],
            "raw_hex": parsed["raw_hex"],
            "pipeline_version": PIPELINE_VERSION,
        }

        with ble_file.open("a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writerow(row)

        print("BLE EVENT", row)


def install_shutdown_handlers(stop_event: asyncio.Event):
    loop = asyncio.get_running_loop()
    installed_loop_handlers = []

    def request_shutdown() -> None:
        if not stop_event.is_set():
            print("Shutdown requested, stopping BLE scanner...")
            stop_event.set()

    def fallback_handler(_signum, _frame) -> None:
        request_shutdown()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, request_shutdown)
            installed_loop_handlers.append(sig)
        except NotImplementedError:
            try:
                signal.signal(sig, fallback_handler)
            except ValueError:
                print(f"[WARN] Could not install a shutdown handler for signal {sig}")

    return loop, installed_loop_handlers


async def main():
    stop_event = asyncio.Event()
    loop, installed_loop_handlers = install_shutdown_handlers(stop_event)
    scanner = BleakScanner(detection_callback=detection_callback)
    scanner_started = False

    try:
        await scanner.start()
        scanner_started = True
        print("BLE scanner started")
        print(f"Writing BLE data to: {ble_file}")
        print(
            f"Filter: company_id={EXPECTED_COMPANY_ID}, "
            f"version={EXPECTED_VERSION}, exp_code={EXPECTED_EXP_CODE}, "
            f"node_num={EXPECTED_NODE_NUM}, dedup_window={DEDUP_WINDOW}"
        )
        await stop_event.wait()
    finally:
        for sig in installed_loop_handlers:
            loop.remove_signal_handler(sig)

        if scanner_started:
            await scanner.stop()
            print("BLE scanner stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
