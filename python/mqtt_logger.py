import csv
import hashlib
import json
import os
import sys
import time
from collections import deque
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt

from mqtt_settings import load_mqtt_settings
from version_info import load_version_info
from path_utils import raw_dir, get_experiment_run_id

MQTT_SETTINGS = load_mqtt_settings()
MQTT_HOST = MQTT_SETTINGS.host
MQTT_PORT = MQTT_SETTINGS.port
MQTT_USERNAME = MQTT_SETTINGS.username
MQTT_PASSWORD = MQTT_SETTINGS.password

VERSION_INFO = load_version_info()
PIPELINE_VERSION = VERSION_INFO.pipeline_version
SCRIPT_VERSION = VERSION_INFO.logger_version

print(f"[INFO] Pipeline version: {PIPELINE_VERSION} | Logger version: {SCRIPT_VERSION}")

RUN_ID = os.getenv("RUN_ID", "").strip()
if not RUN_ID:
    RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

EXP_RUN_ID = get_experiment_run_id(required=True)
OUT_DIR = raw_dir(EXP_RUN_ID)
RUN_INSTANCE_ID = os.getenv("RUN_INSTANCE_ID", "").strip()


def mqtt_client_id(role: str) -> str:
    instance = RUN_INSTANCE_ID or f"pid-{os.getpid()}"
    digest = hashlib.sha1(
        f"{EXP_RUN_ID}:{RUN_ID}:{role}:{instance}".encode("utf-8")
    ).hexdigest()[:12]
    return f"iotb-{role}-{digest}"


CLIENT_ID = mqtt_client_id("log")

events_file = OUT_DIR / f"{RUN_ID}_mqtt_events.csv"
power_file = OUT_DIR / f"{RUN_ID}_power_samples.csv"

EVENT_FIELDS = [
    "pi_rx_time_ns", "topic", "type", "node", "protocol", "exp",
    "boot_id", "seq", "trigger", "t_local_us", "wifi_rssi", "rtt_us",
    "old_state", "new_state", "ha_time", "event_id", "ha_context_id",
    "mqtt_retain", "pipeline_version"
]

POWER_FIELDS = [
    "pi_rx_time_ns", "topic", "type", "node", "protocol", "exp",
    "t_local_us", "bus_v", "current_mA", "power_mW", "wifi_rssi",
    "mqtt_retain", "pipeline_version"
]

FATAL_CONNECT_REASON_CODES = {133, 134, 135}
fatal_connect_error = None
DEDUP_WINDOW = 2048
seen_message_keys = set()
recent_message_keys = deque()


def remember_message(key: tuple) -> bool:
    if key in seen_message_keys:
        return False

    seen_message_keys.add(key)
    recent_message_keys.append(key)

    while len(recent_message_keys) > DEDUP_WINDOW:
        seen_message_keys.discard(recent_message_keys.popleft())

    return True


def mqtt_payload_key(msg_type: str, topic: str, payload: dict) -> tuple:
    fields_by_type = {
        "event": (
            "node", "protocol", "exp", "seq", "trigger", "t_local_us",
            "boot_id", "event_id", "ha_context_id", "ha_time",
            "old_state", "new_state",
        ),
        "rtt": ("node", "protocol", "exp", "seq", "rtt_us", "boot_id"),
    }
    fields = fields_by_type.get(msg_type, ())
    return (topic, msg_type, *(payload.get(field) for field in fields))


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

    if first_line != expected_header:
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
        print(
            f"[WARN] Existing file had missing/mismatched header{rotation_notice}",
            file=sys.stderr,
        )


ensure_csv_header(events_file, EVENT_FIELDS)
ensure_csv_header(power_file, POWER_FIELDS)


def on_connect(client, userdata, flags, reason_code, properties):
    global fatal_connect_error
    if reason_code.is_failure:
        print(f"MQTT connect failed: {reason_code}", file=sys.stderr)
        if reason_code.value in FATAL_CONNECT_REASON_CODES:
            fatal_connect_error = str(reason_code)
            print("Broker authentication failed.", file=sys.stderr)
            client.disconnect()
        return

    print("Connected:", reason_code)
    print(f"MQTT client id: {CLIENT_ID}")
    if RUN_INSTANCE_ID:
        print(f"Run instance id: {RUN_INSTANCE_ID}")
    print(f"Writing event data to: {events_file}")
    print(f"Writing power data to: {power_file}")
    client.subscribe("iotbench/#")


def on_message(client, userdata, msg):
    if msg.retain:
        print(f"Skipping retained message on {msg.topic}")
        return

    now_ns = time.time_ns()
    try:
        payload = json.loads(msg.payload.decode())
    except Exception as e:
        print("Bad payload:", e, msg.payload, file=sys.stderr)
        return

    msg_type = payload.get("type", "")

    if msg_type in ("event", "rtt"):
        key = mqtt_payload_key(msg_type, msg.topic, payload)
        if not remember_message(key):
            print(
                f"Skipping duplicate MQTT payload type={msg_type}, "
                f"node={payload.get('node')}, seq={payload.get('seq')}"
            )
            return

        row = {
            "pi_rx_time_ns": now_ns,
            "topic": msg.topic,
            "type": msg_type,
            "node": payload.get("node"),
            "protocol": payload.get("protocol"),
            "exp": payload.get("exp"),
            "boot_id": payload.get("boot_id"),
            "seq": payload.get("seq"),
            "trigger": payload.get("trigger"),
            "t_local_us": payload.get("t_local_us"),
            "wifi_rssi": payload.get("wifi_rssi"),
            "rtt_us": payload.get("rtt_us"),
            "old_state": payload.get("old_state"),
            "new_state": payload.get("new_state"),
            "ha_time": payload.get("ha_time"),
            "event_id": payload.get("event_id"),
            "ha_context_id": payload.get("ha_context_id"),
            "mqtt_retain": int(msg.retain),
            "pipeline_version": PIPELINE_VERSION,
        }
        with events_file.open("a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=EVENT_FIELDS).writerow(row)
        print("EVENT", row)

    elif msg_type == "power":
        row = {
            "pi_rx_time_ns": now_ns,
            "topic": msg.topic,
            "type": msg_type,
            "node": payload.get("node"),
            "protocol": payload.get("protocol"),
            "exp": payload.get("exp"),
            "t_local_us": payload.get("t_local_us"),
            "bus_v": payload.get("bus_v"),
            "current_mA": payload.get("current_mA"),
            "power_mW": payload.get("power_mW"),
            "wifi_rssi": payload.get("wifi_rssi"),
            "mqtt_retain": int(msg.retain),
            "pipeline_version": PIPELINE_VERSION,
        }
        with power_file.open("a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=POWER_FIELDS).writerow(row)
        print("POWER", row)


client = mqtt.Client(client_id=CLIENT_ID, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
if MQTT_USERNAME:
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(MQTT_HOST, MQTT_PORT, 60)
except OSError as exc:
    print(f"Unable to connect to MQTT broker at {MQTT_HOST}:{MQTT_PORT}: {exc}.", file=sys.stderr)
    raise SystemExit(1)

client.loop_start()

try:
    while True:
        if fatal_connect_error:
            raise SystemExit(2)
        time.sleep(0.25)
except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
    client.disconnect()
