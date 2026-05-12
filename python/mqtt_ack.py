import hashlib
import json
import os
import sys
import time
from collections import deque

import paho.mqtt.client as mqtt

from mqtt_settings import load_mqtt_settings
from version_info import load_version_info

MQTT_SETTINGS = load_mqtt_settings()
MQTT_HOST = MQTT_SETTINGS.host
MQTT_PORT = MQTT_SETTINGS.port
MQTT_USERNAME = MQTT_SETTINGS.username
MQTT_PASSWORD = MQTT_SETTINGS.password

VERSION_INFO = load_version_info()
PIPELINE_VERSION = VERSION_INFO.pipeline_version
SCRIPT_VERSION = VERSION_INFO.logger_version

print(f"[INFO] Pipeline version: {PIPELINE_VERSION} | ACK script version: {SCRIPT_VERSION}")

RUN_ID = os.getenv("RUN_ID", "").strip() or "manual"
EXP_RUN_ID = os.getenv("EXP_RUN_ID", "").strip() or "manual"
RUN_INSTANCE_ID = os.getenv("RUN_INSTANCE_ID", "").strip()


def mqtt_client_id(role: str) -> str:
    instance = RUN_INSTANCE_ID or f"pid-{os.getpid()}"
    digest = hashlib.sha1(
        f"{EXP_RUN_ID}:{RUN_ID}:{role}:{instance}".encode("utf-8")
    ).hexdigest()[:12]
    return f"iotb-{role}-{digest}"


CLIENT_ID = mqtt_client_id("ack")
FATAL_CONNECT_REASON_CODES = {133, 134, 135}
fatal_connect_error = None
DEDUP_WINDOW = 2048
seen_events = set()
recent_events = deque()


def remember_event(key: tuple) -> bool:
    if key in seen_events:
        return False

    seen_events.add(key)
    recent_events.append(key)

    while len(recent_events) > DEDUP_WINDOW:
        seen_events.discard(recent_events.popleft())

    return True


def on_connect(client, userdata, flags, reason_code, properties):
    global fatal_connect_error
    if reason_code.is_failure:
        print(f"MQTT connect failed: {reason_code}", file=sys.stderr)
        if reason_code.value in FATAL_CONNECT_REASON_CODES:
            fatal_connect_error = str(reason_code)
            print(
                "Broker authentication failed. Set MQTT_USERNAME and "
                "MQTT_PASSWORD before running this script.",
                file=sys.stderr,
            )
            client.disconnect()
        return

    print("Connected:", reason_code)
    print(f"MQTT client id: {CLIENT_ID}")
    if RUN_INSTANCE_ID:
        print(f"Run instance id: {RUN_INSTANCE_ID}")
    client.subscribe("iotbench/wifi/+/event")


def on_message(client, userdata, msg):
    if msg.retain:
        print(f"Skipping retained ACK source on {msg.topic}")
        return

    try:
        payload = json.loads(msg.payload.decode())
    except Exception as exc:
        print(f"Bad payload on {msg.topic}: {exc}", file=sys.stderr)
        return

    if payload.get("type") != "event":
        return

    node = payload.get("node")
    seq = payload.get("seq")

    if not node or seq is None:
        return

    event_key = (
        msg.topic,
        node,
        payload.get("exp"),
        payload.get("boot_id"),
        seq,
        payload.get("t_local_us"),
    )
    if not remember_event(event_key):
        print(f"Skipping duplicate event ACK for node={node}, seq={seq}")
        return

    ack_topic = f"iotbench/wifi/{node}/ack"
    ack_payload_data = {
        "type": "ack",
        "node": node,
        "seq": seq,
        "pipeline_version": PIPELINE_VERSION,
    }
    for key in ("protocol", "exp", "boot_id"):
        if payload.get(key) is not None:
            ack_payload_data[key] = payload.get(key)

    ack_payload = json.dumps(ack_payload_data)

    client.publish(ack_topic, ack_payload, retain=False)
    print(
        f"ACK for node={node}, exp={payload.get('exp')}, "
        f"boot_id={payload.get('boot_id')}, seq={seq}"
    )


client = mqtt.Client(client_id=CLIENT_ID, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
if MQTT_USERNAME:
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
elif MQTT_PASSWORD:
    print(
        "MQTT_PASSWORD is set but MQTT_USERNAME is missing; connecting "
        "without credentials.",
        file=sys.stderr,
    )

client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(MQTT_HOST, MQTT_PORT, 60)
except OSError as exc:
    print(
        f"Unable to connect to MQTT broker at {MQTT_HOST}:{MQTT_PORT}: {exc}.",
        file=sys.stderr,
    )
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
