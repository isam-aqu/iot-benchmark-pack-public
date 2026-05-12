import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


DEFAULT_MQTT_HOST = "<private-ip>"
DEFAULT_MQTT_PORT = 1883
SECRETS_PATH = Path(__file__).resolve().parents[1] / "firmware" / "secrets.h"

_MACRO_PATTERN = re.compile(
    r'^\s*#define\s+'
    r'(IOT_MQTT_HOST|IOT_MQTT_PORT|IOT_MQTT_USERNAME|IOT_MQTT_PASSWORD)'
    r'\s+(".*?"|\d+)\s*$'
)


@dataclass(frozen=True)
class MQTTSettings:
    host: str
    port: int
    username: Optional[str]
    password: Optional[str]


def _parse_secrets_file(path: Path):
    if not path.exists():
        return {}

    values = {}
    for line in path.read_text().splitlines():
        match = _MACRO_PATTERN.match(line)
        if not match:
            continue

        key, raw_value = match.groups()
        if raw_value.startswith('"') and raw_value.endswith('"'):
            values[key] = raw_value[1:-1]
        else:
            values[key] = raw_value

    return values


def load_mqtt_settings():
    file_values = _parse_secrets_file(SECRETS_PATH)

    host = os.getenv("MQTT_HOST") or file_values.get("IOT_MQTT_HOST") or DEFAULT_MQTT_HOST
    port = int(os.getenv("MQTT_PORT") or file_values.get("IOT_MQTT_PORT") or DEFAULT_MQTT_PORT)
    username = os.getenv("MQTT_USERNAME")
    if username is None:
        username = file_values.get("IOT_MQTT_USERNAME") or None

    password = os.getenv("MQTT_PASSWORD")
    if password is None:
        password = file_values.get("IOT_MQTT_PASSWORD") or None

    return MQTTSettings(
        host=host,
        port=port,
        username=username,
        password=password,
    )
