#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PY_DIR="$ROOT_DIR/python"
INVOCATION_CWD="$PWD"
ORIGINAL_ARGV=("$0" "$@")

LOCAL_ENV_FILE="$ROOT_DIR/.env.local"
if [ -f "$LOCAL_ENV_FILE" ]; then
  set -a
  # Local-only secrets and lab endpoints. This file is ignored by git.
  . "$LOCAL_ENV_FILE"
  set +a
fi

if [ -z "${RUN_SHEET:-}" ]; then
  if [ -f "$ROOT_DIR/docs/run_sheet.csv" ]; then
    RUN_SHEET="$ROOT_DIR/docs/run_sheet.csv"
  else
    RUN_SHEET="$ROOT_DIR/run_sheet.csv"
  fi
fi

# -------------------------------
# W3 / iPerf configuration
# -------------------------------
IPERF_SERVER_IP="${IPERF_SERVER_IP:-<private-ip>}"
IPERF_PORT="${IPERF_PORT:-5201}"
IPERF_PROTO="${IPERF_PROTO:-tcp}"
IPERF_LOAD="${IPERF_LOAD:-0}"          # 0 | light | moderate | heavy | integer Mbps
IPERF_STABILIZATION_SEC="${IPERF_STABILIZATION_SEC:-5}"
IPERF_STALE_SEC="${IPERF_STALE_SEC:-15}"
IPERF_LOG_HEALTH_ENABLED="0"

LOAD_LIGHT="${LOAD_LIGHT:-5}"
LOAD_MODERATE="${LOAD_MODERATE:-20}"
LOAD_HEAVY="${LOAD_HEAVY:-50}"

# -------------------------------
# RF metadata captured with each run
# -------------------------------
AP_MODEL="${AP_MODEL:-netis WF2419}"
AP_FIRMWARE="${AP_FIRMWARE:-V2.2.36123}"
AP_CHANNEL_MODE="${AP_CHANNEL_MODE:-unknown}"          # fixed | auto | unknown
AP_CHANNEL="${AP_CHANNEL:-unknown}"                    # 2.4 GHz primary channel
AP_CHANNEL_WIDTH_MHZ="${AP_CHANNEL_WIDTH_MHZ:-unknown}"
AP_CONTROL_SIDEBAND="${AP_CONTROL_SIDEBAND:-unknown}"  # none | upper | lower | unknown
AP_RF_SOURCE="${AP_RF_SOURCE:-not_recorded}"

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS] [RUN_ID]

Options:
  --run-id ID           Explicitly set the run identifier.
  --disable-ble         Disable BLE logging (equivalent to ENABLE_BLE=0).
  --enable-ble          Enable BLE logging (equivalent to ENABLE_BLE=1).
  --disable-ack         Disable MQTT ACK helper (equivalent to ENABLE_ACK=0).
  --enable-ack          Enable MQTT ACK helper (equivalent to ENABLE_ACK=1).
  --duration-sec N      Automatically stop after N seconds.
  --serial-port PORT    Capture serial output from PORT.
  --serial-baud N       Serial baud rate for monitor (default: 115200).
  --serial-start-command TEXT
                        Write one serial command after capture starts.
  --serial-start-delay-sec N
                        Delay before writing serial start command (default: 0).
  --reset-esp32         Reset the ESP32 node before the experiment window starts.
  --no-reset-esp32      Disable ESP32 reset (default).
  --reset-port PORT     Serial port used for ESP32 reset (default: SERIAL_PORT).
  --reset-settle-sec N  Seconds to wait after reset before continuing (default: 2).
  --iperf-load X        Background iperf load: 0 | light | moderate | heavy | integer Mbps.
  --iperf-server IP     iperf3 server IP/host (default: $IPERF_SERVER_IP).
  --iperf-port N        iperf3 server port (default: $IPERF_PORT).
  --ap-model TEXT       AP model recorded in metadata (default: $AP_MODEL).
  --ap-firmware TEXT    AP firmware recorded in metadata (default: $AP_FIRMWARE).
  --ap-channel-mode X   AP channel mode: fixed | auto | unknown (default: $AP_CHANNEL_MODE).
  --ap-channel N        AP 2.4 GHz primary channel, e.g. 1, 6, 9, 13.
  --ap-width-mhz N      AP channel width in MHz, e.g. 20 or 40.
  --ap-sideband X       AP control sideband: none | upper | lower | unknown.
  --ap-rf-source X      Source for AP RF values, e.g. manual_ap_ui or client_scan.
  --zigbee-trigger      Start the Home Assistant Zigbee trigger driver.
  --no-zigbee-trigger   Disable the Home Assistant Zigbee trigger driver (default).
  --zigbee-entity-id ID Zigbee entity to toggle (default: $ZIGBEE_ENTITY_ID).
  --zigbee-events N     Number of Zigbee state-change commands (default: $ZIGBEE_EVENT_COUNT).
  --zigbee-base-interval-ms N
                        Zigbee trigger nominal interval in ms (default: $ZIGBEE_BASE_INTERVAL_MS).
  --zigbee-jitter-ms N  Zigbee trigger ± jitter in ms (default: $ZIGBEE_JITTER_MS).
  -h, --help            Show this help message and exit.

You can also set:
  EXP_RUN_ID            via environment variable
  RUN_ID                via environment variable
  ENABLE_BLE            to 0 or 1 via environment variable
  ENABLE_ACK            to 0 or 1 via environment variable
  SERIAL_PORT           serial port for optional serial capture
  SERIAL_BAUD           serial baud rate for optional serial capture
  SERIAL_START_COMMAND  optional command written after serial capture starts
  SERIAL_START_DELAY_SEC
                        delay before writing SERIAL_START_COMMAND
  RESET_ESP32           set to 1 to reset ESP32 before the run window
  ESP32_RESET_PORT      serial port used for reset (defaults to SERIAL_PORT)
  ESP32_RESET_PULSE_SEC reset pulse length (default: 0.2)
  ESP32_RESET_SETTLE_SEC seconds to wait after reset (default: 2)
  IPERF_LOAD            same as --iperf-load
  IPERF_SERVER_IP       same as --iperf-server
  IPERF_PORT            same as --iperf-port
  IPERF_PROTO           iperf3 protocol: tcp or udp (default: $IPERF_PROTO)
  IPERF_STALE_SEC       fail if the iperf log has not updated for this many seconds (default: $IPERF_STALE_SEC)
  AP_MODEL / AP_FIRMWARE
                        AP identity recorded with the run
  AP_CHANNEL_MODE       AP channel mode: fixed | auto | unknown
  AP_CHANNEL            AP 2.4 GHz primary channel
  AP_CHANNEL_WIDTH_MHZ  AP channel width in MHz
  AP_CONTROL_SIDEBAND   AP sideband: none | upper | lower | unknown
  AP_RF_SOURCE          source for AP RF values, e.g. manual_ap_ui or client_scan
  ZIGBEE_TRIGGER        set to 1 to run python/ha_zigbee_trigger.py
  ZIGBEE_ENTITY_ID      entity toggled by the Zigbee trigger driver
  ZIGBEE_EVENT_COUNT    number of Zigbee trigger commands
  ZIGBEE_BASE_INTERVAL_MS / ZIGBEE_JITTER_MS
                        Zigbee automatic schedule shape
  HA_URL                Home Assistant base URL for Zigbee trigger control
  HA_TOKEN              Home Assistant long-lived access token
  RUN_SHEET             path to run_sheet.csv (default: $RUN_SHEET)

TCP iperf note:
  The W3 load profiles intentionally pass -b to iperf3 for TCP and UDP. This
  requires an iperf3 build with TCP bitrate pacing support; without it, use a
  compatible iperf3 version rather than removing -b, because the light/moderate/
  heavy labels are defined by target Mbps.
EOF
}

RUN_ID_ARG=""
ENABLE_BLE_ARG=""
ENABLE_ACK_ARG=""
DURATION_SEC=""
SERIAL_PORT="${SERIAL_PORT:-}"
SERIAL_BAUD="${SERIAL_BAUD:-115200}"
SERIAL_START_COMMAND="${SERIAL_START_COMMAND:-}"
SERIAL_START_DELAY_SEC="${SERIAL_START_DELAY_SEC:-0}"
RESET_ESP32_ARG=""
RESET_ESP32="${RESET_ESP32:-0}"
ESP32_RESET_PORT="${ESP32_RESET_PORT:-}"
ESP32_RESET_PULSE_SEC="${ESP32_RESET_PULSE_SEC:-0.2}"
ESP32_RESET_SETTLE_SEC="${ESP32_RESET_SETTLE_SEC:-2}"
ZIGBEE_TRIGGER_ARG=""
ZIGBEE_TRIGGER="${ZIGBEE_TRIGGER:-0}"
ZIGBEE_ENTITY_ID="${ZIGBEE_ENTITY_ID:-light.benchmark_device}"
ZIGBEE_EVENT_COUNT="${ZIGBEE_EVENT_COUNT:-100}"
ZIGBEE_BASE_INTERVAL_MS="${ZIGBEE_BASE_INTERVAL_MS:-3000}"
ZIGBEE_JITTER_MS="${ZIGBEE_JITTER_MS:-250}"
POSITIONAL_RUN_ID=""
RUN_SHEET_ROW_APPENDED="0"
RUN_FINAL_STATUS="failed"
RUN_STOP_SIGNAL="0"

shell_join_words() {
  local out=""
  local quoted
  for word in "$@"; do
    printf -v quoted '%q' "$word"
    if [ -n "$out" ]; then
      out+=" "
    fi
    out+="$quoted"
  done
  printf '%s' "$out"
}

build_run_command() {
  local command_parts=("EXP_RUN_ID=$EXP_RUN_ID" "${ORIGINAL_ARGV[@]}")
  shell_join_words "${command_parts[@]}"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --run-id)
      if [ "$#" -lt 2 ]; then
        echo "Error: --run-id requires an argument." >&2
        usage >&2
        exit 1
      fi
      RUN_ID_ARG="$2"
      shift 2
      ;;
    --disable-ble)
      ENABLE_BLE_ARG="0"
      shift
      ;;
    --enable-ble)
      ENABLE_BLE_ARG="1"
      shift
      ;;
    --disable-ack)
      ENABLE_ACK_ARG="0"
      shift
      ;;
    --enable-ack)
      ENABLE_ACK_ARG="1"
      shift
      ;;
    --duration-sec)
      if [ "$#" -lt 2 ]; then
        echo "Error: --duration-sec requires an argument." >&2
        usage >&2
        exit 1
      fi
      DURATION_SEC="$2"
      shift 2
      ;;
    --serial-port)
      if [ "$#" -lt 2 ]; then
        echo "Error: --serial-port requires an argument." >&2
        usage >&2
        exit 1
      fi
      SERIAL_PORT="$2"
      shift 2
      ;;
    --serial-baud)
      if [ "$#" -lt 2 ]; then
        echo "Error: --serial-baud requires an argument." >&2
        usage >&2
        exit 1
      fi
      SERIAL_BAUD="$2"
      shift 2
      ;;
    --serial-start-command)
      if [ "$#" -lt 2 ]; then
        echo "Error: --serial-start-command requires an argument." >&2
        usage >&2
        exit 1
      fi
      SERIAL_START_COMMAND="$2"
      shift 2
      ;;
    --serial-start-delay-sec)
      if [ "$#" -lt 2 ]; then
        echo "Error: --serial-start-delay-sec requires an argument." >&2
        usage >&2
        exit 1
      fi
      SERIAL_START_DELAY_SEC="$2"
      shift 2
      ;;
    --reset-esp32)
      RESET_ESP32_ARG="1"
      shift
      ;;
    --no-reset-esp32)
      RESET_ESP32_ARG="0"
      shift
      ;;
    --reset-port)
      if [ "$#" -lt 2 ]; then
        echo "Error: --reset-port requires an argument." >&2
        usage >&2
        exit 1
      fi
      ESP32_RESET_PORT="$2"
      shift 2
      ;;
    --reset-settle-sec)
      if [ "$#" -lt 2 ]; then
        echo "Error: --reset-settle-sec requires an argument." >&2
        usage >&2
        exit 1
      fi
      ESP32_RESET_SETTLE_SEC="$2"
      shift 2
      ;;
    --iperf-load)
      if [ "$#" -lt 2 ]; then
        echo "Error: --iperf-load requires an argument." >&2
        usage >&2
        exit 1
      fi
      IPERF_LOAD="$2"
      shift 2
      ;;
    --iperf-server)
      if [ "$#" -lt 2 ]; then
        echo "Error: --iperf-server requires an argument." >&2
        usage >&2
        exit 1
      fi
      IPERF_SERVER_IP="$2"
      shift 2
      ;;
    --iperf-port)
      if [ "$#" -lt 2 ]; then
        echo "Error: --iperf-port requires an argument." >&2
        usage >&2
        exit 1
      fi
      IPERF_PORT="$2"
      shift 2
      ;;
    --ap-model)
      if [ "$#" -lt 2 ]; then
        echo "Error: --ap-model requires an argument." >&2
        usage >&2
        exit 1
      fi
      AP_MODEL="$2"
      shift 2
      ;;
    --ap-firmware)
      if [ "$#" -lt 2 ]; then
        echo "Error: --ap-firmware requires an argument." >&2
        usage >&2
        exit 1
      fi
      AP_FIRMWARE="$2"
      shift 2
      ;;
    --ap-channel-mode)
      if [ "$#" -lt 2 ]; then
        echo "Error: --ap-channel-mode requires an argument." >&2
        usage >&2
        exit 1
      fi
      AP_CHANNEL_MODE="$2"
      shift 2
      ;;
    --ap-channel)
      if [ "$#" -lt 2 ]; then
        echo "Error: --ap-channel requires an argument." >&2
        usage >&2
        exit 1
      fi
      AP_CHANNEL="$2"
      shift 2
      ;;
    --ap-width-mhz)
      if [ "$#" -lt 2 ]; then
        echo "Error: --ap-width-mhz requires an argument." >&2
        usage >&2
        exit 1
      fi
      AP_CHANNEL_WIDTH_MHZ="$2"
      shift 2
      ;;
    --ap-sideband)
      if [ "$#" -lt 2 ]; then
        echo "Error: --ap-sideband requires an argument." >&2
        usage >&2
        exit 1
      fi
      AP_CONTROL_SIDEBAND="$2"
      shift 2
      ;;
    --ap-rf-source)
      if [ "$#" -lt 2 ]; then
        echo "Error: --ap-rf-source requires an argument." >&2
        usage >&2
        exit 1
      fi
      AP_RF_SOURCE="$2"
      shift 2
      ;;
    --zigbee-trigger)
      ZIGBEE_TRIGGER_ARG="1"
      shift
      ;;
    --no-zigbee-trigger)
      ZIGBEE_TRIGGER_ARG="0"
      shift
      ;;
    --zigbee-entity-id)
      if [ "$#" -lt 2 ]; then
        echo "Error: --zigbee-entity-id requires an argument." >&2
        usage >&2
        exit 1
      fi
      ZIGBEE_ENTITY_ID="$2"
      shift 2
      ;;
    --zigbee-events)
      if [ "$#" -lt 2 ]; then
        echo "Error: --zigbee-events requires an argument." >&2
        usage >&2
        exit 1
      fi
      ZIGBEE_EVENT_COUNT="$2"
      shift 2
      ;;
    --zigbee-base-interval-ms)
      if [ "$#" -lt 2 ]; then
        echo "Error: --zigbee-base-interval-ms requires an argument." >&2
        usage >&2
        exit 1
      fi
      ZIGBEE_BASE_INTERVAL_MS="$2"
      shift 2
      ;;
    --zigbee-jitter-ms)
      if [ "$#" -lt 2 ]; then
        echo "Error: --zigbee-jitter-ms requires an argument." >&2
        usage >&2
        exit 1
      fi
      ZIGBEE_JITTER_MS="$2"
      shift 2
      ;;
    --*)
      echo "Error: Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      if [ -z "$POSITIONAL_RUN_ID" ]; then
        POSITIONAL_RUN_ID="$1"
        shift
      else
        echo "Error: Unexpected extra positional argument: $1" >&2
        usage >&2
        exit 1
      fi
      ;;
  esac
done

if [ ! -d "$PY_DIR/.venv" ]; then
  echo "Python virtual environment not found."
  echo "Create it first:"
  echo "  cd python && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

source "$PY_DIR/.venv/bin/activate"

if [ -z "$RUN_ID_ARG" ] && [ -n "$POSITIONAL_RUN_ID" ]; then
  RUN_ID_ARG="$POSITIONAL_RUN_ID"
fi
if [ -n "$RUN_ID_ARG" ]; then
  RUN_ID="$RUN_ID_ARG"
else
  RUN_ID="${RUN_ID:-$(date +%Y%m%d_%H%M%S)}"
fi
if [ -z "${RUN_ID//[[:space:]]/}" ]; then
  echo "Error: RUN_ID resolved to an empty or whitespace-only value." >&2
  echo "If you are using a multi-line command, make sure each trailing '\\' is the final character on its line." >&2
  exit 1
fi
export RUN_ID

EXP_RUN_ID="${EXP_RUN_ID:-}"
if [ -z "$EXP_RUN_ID" ]; then
  echo "Error: EXP_RUN_ID is required for the experiments/ path layout." >&2
  echo "Example: EXP_RUN_ID=R304 ./run_all.sh --run-id W1_wifi_near_quiet_v7" >&2
  exit 1
fi
export EXP_RUN_ID

RUN_INSTANCE_ID="${RUN_INSTANCE_ID:-$(date +%Y%m%d%H%M%S)-$$}"
export RUN_INSTANCE_ID

RUN_COMMAND="$(build_run_command)"
export RUN_COMMAND
export INVOCATION_CWD

OUTPUT_DIR="$ROOT_DIR/experiments/runs/$EXP_RUN_ID/raw"
mkdir -p "$OUTPUT_DIR"

RUN_LOCK_TOKEN="$(printf '%s_%s' "$EXP_RUN_ID" "$RUN_ID" | tr -c 'A-Za-z0-9_.-' '_')"
RUN_LOCK_DIR="${TMPDIR:-/tmp}/iotbench_${RUN_LOCK_TOKEN}.lock"
RUN_LOCK_ACQUIRED="0"

if [ -n "$ENABLE_BLE_ARG" ]; then
  ENABLE_BLE="$ENABLE_BLE_ARG"
else
  ENABLE_BLE="${ENABLE_BLE:-1}"
fi

if [ -n "$ENABLE_ACK_ARG" ]; then
  ENABLE_ACK="$ENABLE_ACK_ARG"
else
  ENABLE_ACK="${ENABLE_ACK:-1}"
fi

if [ "$ENABLE_BLE" != "0" ] && [ "$ENABLE_BLE" != "1" ]; then
  echo "Error: ENABLE_BLE must be either 0 or 1 (got: '$ENABLE_BLE')." >&2
  exit 1
fi

if [ "$ENABLE_ACK" != "0" ] && [ "$ENABLE_ACK" != "1" ]; then
  echo "Error: ENABLE_ACK must be either 0 or 1 (got: '$ENABLE_ACK')." >&2
  exit 1
fi

if [ "$ENABLE_BLE" = "1" ] && [ -z "${BLE_EXPECTED_EXP_CODE:-}" ]; then
  case "$RUN_ID" in
    W3_*ble*|W3_ble_auto*)
      BLE_EXPECTED_EXP_CODE="W3BL"
      export BLE_EXPECTED_EXP_CODE
      ;;
    W1_*ble*)
      BLE_EXPECTED_EXP_CODE="W1BL"
      export BLE_EXPECTED_EXP_CODE
      ;;
  esac
fi

if [ "$IPERF_PROTO" != "tcp" ] && [ "$IPERF_PROTO" != "udp" ]; then
  echo "Error: IPERF_PROTO must be either tcp or udp (got: '$IPERF_PROTO')." >&2
  exit 1
fi

if [ -n "$DURATION_SEC" ] && ! [[ "$DURATION_SEC" =~ ^[0-9]+$ ]]; then
  echo "Error: --duration-sec must be an integer number of seconds." >&2
  exit 1
fi

if ! [[ "$IPERF_STALE_SEC" =~ ^[0-9]+$ ]] || [ "$IPERF_STALE_SEC" -eq 0 ]; then
  echo "Error: IPERF_STALE_SEC must be a positive integer number of seconds (got: '$IPERF_STALE_SEC')." >&2
  exit 1
fi

if [ -n "$RESET_ESP32_ARG" ]; then
  RESET_ESP32="$RESET_ESP32_ARG"
fi

if [ "$RESET_ESP32" != "0" ] && [ "$RESET_ESP32" != "1" ]; then
  echo "Error: RESET_ESP32 must be either 0 or 1 (got: '$RESET_ESP32')." >&2
  exit 1
fi

if [ -n "$ZIGBEE_TRIGGER_ARG" ]; then
  ZIGBEE_TRIGGER="$ZIGBEE_TRIGGER_ARG"
fi

if [ "$ZIGBEE_TRIGGER" != "0" ] && [ "$ZIGBEE_TRIGGER" != "1" ]; then
  echo "Error: ZIGBEE_TRIGGER must be either 0 or 1 (got: '$ZIGBEE_TRIGGER')." >&2
  exit 1
fi

if ! [[ "$ZIGBEE_EVENT_COUNT" =~ ^[0-9]+$ ]] || [ "$ZIGBEE_EVENT_COUNT" -eq 0 ]; then
  echo "Error: --zigbee-events must be a positive integer (got: '$ZIGBEE_EVENT_COUNT')." >&2
  exit 1
fi

if ! [[ "$ZIGBEE_BASE_INTERVAL_MS" =~ ^[0-9]+$ ]] || [ "$ZIGBEE_BASE_INTERVAL_MS" -eq 0 ]; then
  echo "Error: --zigbee-base-interval-ms must be a positive integer (got: '$ZIGBEE_BASE_INTERVAL_MS')." >&2
  exit 1
fi

if ! [[ "$ZIGBEE_JITTER_MS" =~ ^[0-9]+$ ]]; then
  echo "Error: --zigbee-jitter-ms must be a non-negative integer (got: '$ZIGBEE_JITTER_MS')." >&2
  exit 1
fi

if [ "$ZIGBEE_TRIGGER" = "1" ] && [ -z "${HA_TOKEN:-${HOME_ASSISTANT_TOKEN:-}}" ]; then
  echo "Error: --zigbee-trigger requires HA_TOKEN or HOME_ASSISTANT_TOKEN." >&2
  exit 1
fi

if ! [[ "$ESP32_RESET_PULSE_SEC" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
  echo "Error: ESP32_RESET_PULSE_SEC must be a non-negative number (got: '$ESP32_RESET_PULSE_SEC')." >&2
  exit 1
fi

if ! [[ "$ESP32_RESET_SETTLE_SEC" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
  echo "Error: --reset-settle-sec must be a non-negative number (got: '$ESP32_RESET_SETTLE_SEC')." >&2
  exit 1
fi

if ! [[ "$SERIAL_START_DELAY_SEC" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
  echo "Error: --serial-start-delay-sec must be a non-negative number (got: '$SERIAL_START_DELAY_SEC')." >&2
  exit 1
fi

resolve_iperf_load_mbps() {
  case "$IPERF_LOAD" in
    0|"0"|none|off|quiet)
      echo "0"
      ;;
    light)
      echo "$LOAD_LIGHT"
      ;;
    moderate)
      echo "$LOAD_MODERATE"
      ;;
    heavy)
      echo "$LOAD_HEAVY"
      ;;
    *)
      if [[ "$IPERF_LOAD" =~ ^[0-9]+$ ]]; then
        echo "$IPERF_LOAD"
      else
        echo "INVALID"
      fi
      ;;
  esac
}

IPERF_LOAD_MBPS="$(resolve_iperf_load_mbps)"
if [ "$IPERF_LOAD_MBPS" = "INVALID" ]; then
  echo "Error: --iperf-load must be one of 0|light|moderate|heavy|<integer Mbps> (got '$IPERF_LOAD')." >&2
  exit 1
fi

VERSION_FIELDS="$(
  cd "$PY_DIR"
  python - <<'PY'
from version_info import load_version_info
info = load_version_info()
print("|".join([
    info.pipeline_version,
    info.firmware_version,
    info.analysis_version,
    info.ha_config_version,
]))
PY
)"
IFS='|' read -r PIPELINE_VERSION FIRMWARE_VERSION ANALYSIS_VERSION HA_CONFIG_VERSION <<< "$VERSION_FIELDS"

TODAY="$(date +%Y-%m-%d)"
RUN_PATH="experiments/runs/$EXP_RUN_ID"

get_run_sheet_fields() {
  local protocol="wifi"
  local topology="near"
  local interference="quiet"
  local load_level="single"
  local node_count="1"
  local interval_ms="manual"
  local timestamp_source="python_logger"
  local workload="W1"
  local comparison_group=""
  local run_type="other"
  local replicate_id="primary"
  local is_baseline="False"
  local baseline_ref=""
  local interval_nominal_ms=""
  local interval_jitter_ms=""
  local iperf_profile=""
  local notes="auto-added by run_all.sh"

  case "$RUN_ID" in
    W1_*wifi*)
      workload="W1"
      protocol="wifi"
      timestamp_source="ESP32_RTT"
      run_type="baseline"
      ;;
    W1_*zigbee*)
      workload="W1"
      protocol="zigbee"
      timestamp_source="ha_time + python_logger"
      run_type="baseline"
      ;;
    W1_*ble*)
      workload="W1"
      protocol="ble"
      timestamp_source="t_local_us + python_logger"
      run_type="baseline"
      ;;
    W2_*ctrl*|W2_*control*)
      workload="W2"
      protocol="wifi"
      timestamp_source="ESP32 t_local_us + serial_power + MQTT_event"
      interval_ms="3000"
      run_type="control"
      ;;
    W2_*telemetry*)
      workload="W2"
      protocol="wifi"
      timestamp_source="ESP32 t_local_us + serial_power + MQTT_event"
      interval_ms="3000"
      run_type="telemetry"
      ;;
    W3_A_wifi_*|W3_wifi_auto_light*|W3_wifi_auto_moderate*|W3_wifi_auto_heavy*)
      workload="W3"
      protocol="wifi"
      timestamp_source="ESP32_RTT"
      topology="near"
      interval_ms="3000±250"
      interval_nominal_ms="3000"
      interval_jitter_ms="250"
      comparison_group="W3_wifi_auto"
      run_type="load"
      baseline_ref="R600"
      notes="auto-added W3 Wi-Fi run with automated trigger and iperf stress"
      ;;
    W3_A_zigbee_*|W3_zigbee_auto_light*|W3_zigbee_auto_moderate*|W3_zigbee_auto_heavy*)
      workload="W3"
      protocol="zigbee"
      timestamp_source="ha_time + python_logger"
      topology="near"
      interval_ms="3000±250"
      interval_nominal_ms="3000"
      interval_jitter_ms="250"
      comparison_group="W3_zigbee_auto"
      run_type="load"
      baseline_ref="R620"
      notes="auto-added W3 Zigbee run with automated trigger and iperf stress"
      ;;
    W3_A_ble_*|W3_ble_auto_light*|W3_ble_auto_moderate*|W3_ble_auto_heavy*)
      workload="W3"
      protocol="ble"
      timestamp_source="t_local_us + python_logger"
      topology="near"
      interval_ms="3000±250"
      interval_nominal_ms="3000"
      interval_jitter_ms="250"
      comparison_group="W3_ble_auto"
      run_type="load"
      baseline_ref="R640"
      notes="auto-added W3 BLE run with automated trigger and iperf stress"
      ;;
    W3_B0_wifi_*|W3_A0_wifi_*|W3_wifi_auto_baseline*)
      workload="W3"
      protocol="wifi"
      timestamp_source="ESP32_RTT"
      topology="near"
      interval_ms="3000±250"
      interval_nominal_ms="3000"
      interval_jitter_ms="250"
      comparison_group="W3_wifi_auto"
      run_type="baseline"
      is_baseline="True"
      notes="auto-added W3 Wi-Fi automated baseline"
      ;;
    W3_B0_zigbee_*|W3_A0_zigbee_*|W3_zigbee_auto_baseline*)
      workload="W3"
      protocol="zigbee"
      timestamp_source="ha_time + python_logger"
      topology="near"
      interval_ms="3000±250"
      interval_nominal_ms="3000"
      interval_jitter_ms="250"
      comparison_group="W3_zigbee_auto"
      run_type="baseline"
      is_baseline="True"
      notes="auto-added W3 Zigbee automated baseline"
      ;;
    W3_B0_ble_*|W3_A0_ble_*|W3_ble_auto_baseline*)
      workload="W3"
      protocol="ble"
      timestamp_source="t_local_us + python_logger"
      topology="near"
      interval_ms="3000±250"
      interval_nominal_ms="3000"
      interval_jitter_ms="250"
      comparison_group="W3_ble_auto"
      run_type="baseline"
      is_baseline="True"
      notes="auto-added W3 BLE automated baseline"
      ;;
  esac

  if [ "$workload" = "W3" ]; then
    if [ "$IPERF_LOAD_MBPS" -eq 0 ]; then
      interference="quiet"
      load_level="baseline"
    else
      interference="iperf"
      load_level="$IPERF_LOAD"
      iperf_profile="${IPERF_LOAD_MBPS}Mbps_${IPERF_PROTO}"
    fi
  else
    interference="quiet"
    load_level="single"
  fi

  printf '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' \
    "$workload" "$protocol" "$topology" "$interference" "$load_level" \
    "$node_count" "$interval_ms" "$timestamp_source" "$comparison_group" \
    "$run_type" "$replicate_id" "$is_baseline" "$baseline_ref" \
    "$interval_nominal_ms" "$interval_jitter_ms" "$iperf_profile"
  printf '|%s\n' "$notes"
}

append_run_sheet_row() {
  if [ ! -f "$RUN_SHEET" ]; then
    echo "Warning: run_sheet.csv not found at $RUN_SHEET; skipping auto-update." >&2
    return
  fi

  if grep -q "^${EXP_RUN_ID}," "$RUN_SHEET"; then
    echo "Info: run_sheet already contains row for $EXP_RUN_ID; updating status only."
    RUN_SHEET_ROW_APPENDED="1"
    update_run_sheet_status "running"
    return
  fi

  local fields
  fields="$(get_run_sheet_fields)"

  local workload protocol topology interference load_level node_count interval_ms timestamp_source comparison_group run_type replicate_id is_baseline baseline_ref interval_nominal_ms interval_jitter_ms iperf_profile notes
  IFS='|' read -r workload protocol topology interference load_level node_count interval_ms timestamp_source comparison_group run_type replicate_id is_baseline baseline_ref interval_nominal_ms interval_jitter_ms iperf_profile notes <<< "$fields"

  python - "$RUN_SHEET" \
    "$EXP_RUN_ID" "$TODAY" "$workload" "testbed-dev" "auto" "" \
    "$FIRMWARE_VERSION" "$HA_CONFIG_VERSION" "$ANALYSIS_VERSION" \
    "$workload" "$protocol" "$topology" "$interference" "$load_level" \
    "$node_count" "$interval_ms" "$timestamp_source" "$RUN_PATH" \
    "running" "$notes" "$PIPELINE_VERSION" "$is_baseline" "$comparison_group" \
    "$run_type" "$replicate_id" "$baseline_ref" "$interval_nominal_ms" \
    "$interval_jitter_ms" "$iperf_profile" "$AP_MODEL" "$AP_FIRMWARE" \
    "$AP_CHANNEL_MODE" "$AP_CHANNEL" "$AP_CHANNEL_WIDTH_MHZ" \
    "$AP_CONTROL_SIDEBAND" "$AP_RF_SOURCE" <<'PY'
import csv
import sys

run_sheet = sys.argv[1]
values = sys.argv[2:]
field_names = [
    "run_id",
    "date",
    "plan_id",
    "branch",
    "commit",
    "tag",
    "firmware_version",
    "ha_config_version",
    "analysis_version",
    "workload",
    "protocol",
    "topology",
    "interference",
    "load_level",
    "node_count",
    "interval_ms",
    "timestamp_source",
    "run_path",
    "status",
    "notes",
    "pipeline_version",
    "is_baseline",
    "comparison_group",
    "run_type",
    "replicate_id",
    "baseline_ref",
    "interval_nominal_ms",
    "interval_jitter_ms",
    "iperf_profile",
    "ap_model",
    "ap_firmware",
    "ap_channel_mode",
    "ap_channel",
    "ap_width_mhz",
    "ap_control_sideband",
    "ap_rf_source",
]

with open(run_sheet, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader, [])

row_by_name = dict(zip(field_names, values))
row = [row_by_name.get(column, "") for column in header]
with open(run_sheet, "a", newline="", encoding="utf-8") as f:
    csv.writer(f, lineterminator="\n").writerow(row)
PY

  RUN_SHEET_ROW_APPENDED="1"
}

update_run_sheet_status() {
  local new_status="$1"
  if [ "$RUN_SHEET_ROW_APPENDED" != "1" ]; then
    return
  fi
  if [ ! -f "$RUN_SHEET" ]; then
    return
  fi

  python - "$RUN_SHEET" "$EXP_RUN_ID" "$new_status" <<'PY'
import csv
import sys
from pathlib import Path

run_sheet = Path(sys.argv[1])
exp_run_id = sys.argv[2]
new_status = sys.argv[3]

rows = []
with run_sheet.open(newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

if not rows:
    sys.exit(0)

header = rows[0]
try:
    run_id_idx = header.index("run_id")
    status_idx = header.index("status")
except ValueError:
    sys.exit(0)

for i in range(1, len(rows)):
    if rows[i][run_id_idx] == exp_run_id:
        rows[i][status_idx] = new_status
        break

with run_sheet.open('w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerows(rows)
PY
}

write_run_metadata() {
  local phase="$1"
  local status="$2"
  local exit_code="${3:-0}"
  local metadata_path="$OUTPUT_DIR/run_metadata.json"

  PYTHONPATH="$PY_DIR" \
    EXP_RUN_ID="$EXP_RUN_ID" \
    RUN_ID="$RUN_ID" \
    RUN_INSTANCE_ID="$RUN_INSTANCE_ID" \
    RUN_SHEET="$RUN_SHEET" \
    DURATION_SEC="$DURATION_SEC" \
    SERIAL_START_COMMAND="$SERIAL_START_COMMAND" \
    SERIAL_START_DELAY_SEC="$SERIAL_START_DELAY_SEC" \
    ENABLE_BLE="$ENABLE_BLE" \
    ENABLE_ACK="$ENABLE_ACK" \
    RESET_ESP32="$RESET_ESP32" \
    IPERF_LOAD="$IPERF_LOAD" \
    IPERF_LOAD_MBPS="$IPERF_LOAD_MBPS" \
    IPERF_PROTO="$IPERF_PROTO" \
    IPERF_SERVER_IP="$IPERF_SERVER_IP" \
    IPERF_PORT="$IPERF_PORT" \
    AP_MODEL="$AP_MODEL" \
    AP_FIRMWARE="$AP_FIRMWARE" \
    AP_CHANNEL_MODE="$AP_CHANNEL_MODE" \
    AP_CHANNEL="$AP_CHANNEL" \
    AP_CHANNEL_WIDTH_MHZ="$AP_CHANNEL_WIDTH_MHZ" \
    AP_CONTROL_SIDEBAND="$AP_CONTROL_SIDEBAND" \
    AP_RF_SOURCE="$AP_RF_SOURCE" \
    ZIGBEE_TRIGGER="$ZIGBEE_TRIGGER" \
    ZIGBEE_ENTITY_ID="$ZIGBEE_ENTITY_ID" \
    ZIGBEE_EVENT_COUNT="$ZIGBEE_EVENT_COUNT" \
    ZIGBEE_BASE_INTERVAL_MS="$ZIGBEE_BASE_INTERVAL_MS" \
    ZIGBEE_JITTER_MS="$ZIGBEE_JITTER_MS" \
    RUN_COMMAND="$RUN_COMMAND" \
    INVOCATION_CWD="$INVOCATION_CWD" \
    python - "$metadata_path" "$phase" "$status" "$exit_code" <<'PY'
import json
import os
import sys
from pathlib import Path

from version_info import build_metadata, display_path

path = Path(sys.argv[1])
phase = sys.argv[2]
status = sys.argv[3]
exit_code = int(sys.argv[4])

existing = {}
if path.exists():
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        existing = {}

run_sheet = os.getenv("RUN_SHEET", "")
inputs = [run_sheet] if run_sheet else []

metadata = build_metadata(
    "run_all.sh",
    inputs=inputs,
    outputs=[path],
    extra={
        "phase": phase,
        "exp_run_id": os.getenv("EXP_RUN_ID"),
        "run_id": os.getenv("RUN_ID"),
    },
)

run = dict(existing.get("run", {}))
run.update({
    "exp_run_id": os.getenv("EXP_RUN_ID"),
    "run_id": os.getenv("RUN_ID"),
    "run_instance_id": os.getenv("RUN_INSTANCE_ID"),
    "command": {
        "cwd": os.getenv("INVOCATION_CWD"),
        "shell": os.getenv("RUN_COMMAND"),
        "secrets_omitted": [
            "HA_TOKEN",
            "HOME_ASSISTANT_TOKEN",
        ],
    },
    "status": status,
    "exit_code": exit_code,
    "duration_sec": os.getenv("DURATION_SEC") or None,
    "serial_start_command": os.getenv("SERIAL_START_COMMAND") or None,
    "serial_start_delay_sec": os.getenv("SERIAL_START_DELAY_SEC") or None,
    "enable_ble": os.getenv("ENABLE_BLE"),
    "ble_expected_exp_code": os.getenv("BLE_EXPECTED_EXP_CODE"),
    "enable_ack": os.getenv("ENABLE_ACK"),
    "reset_esp32": os.getenv("RESET_ESP32"),
    "iperf_load": os.getenv("IPERF_LOAD"),
    "iperf_load_mbps": os.getenv("IPERF_LOAD_MBPS"),
    "iperf_proto": os.getenv("IPERF_PROTO"),
    "iperf_server": os.getenv("IPERF_SERVER_IP"),
    "iperf_port": os.getenv("IPERF_PORT"),
    "ap_rf": {
        "model": os.getenv("AP_MODEL"),
        "firmware": os.getenv("AP_FIRMWARE"),
        "channel_mode": os.getenv("AP_CHANNEL_MODE"),
        "channel": os.getenv("AP_CHANNEL"),
        "ap_width_mhz": os.getenv("AP_CHANNEL_WIDTH_MHZ"),
        "control_sideband": os.getenv("AP_CONTROL_SIDEBAND"),
        "source": os.getenv("AP_RF_SOURCE"),
    },
    "zigbee_trigger": os.getenv("ZIGBEE_TRIGGER"),
    "zigbee_entity_id": os.getenv("ZIGBEE_ENTITY_ID"),
    "zigbee_event_count": os.getenv("ZIGBEE_EVENT_COUNT"),
    "zigbee_base_interval_ms": os.getenv("ZIGBEE_BASE_INTERVAL_MS"),
    "zigbee_jitter_ms": os.getenv("ZIGBEE_JITTER_MS"),
})

if phase == "start":
    run["started_at_utc"] = metadata["generated_at_utc"]
    run["started_at_local"] = metadata["generated_at_local"]
elif phase == "end":
    run.setdefault("started_at_utc", None)
    run.setdefault("started_at_local", None)
    run["ended_at_utc"] = metadata["generated_at_utc"]
    run["ended_at_local"] = metadata["generated_at_local"]

history = list(existing.get("history", []))
history.append({
    "phase": phase,
    "status": status,
    "exit_code": exit_code,
    "generated_at_utc": metadata["generated_at_utc"],
    "generated_at_local": metadata["generated_at_local"],
})

payload = {
    "metadata": metadata,
    "run": run,
    "history": history,
}

path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(f"[OK] Saved run metadata -> {display_path(path)}")
PY
}

start_iperf() {
  if [ "$IPERF_LOAD_MBPS" -eq 0 ]; then
    echo "[IPERF] Disabled (baseline run)"
    return
  fi

  if ! command -v iperf3 >/dev/null 2>&1; then
    echo "Error: iperf3 is required for --iperf-load." >&2
    exit 1
  fi

  IPERF_LOG="$OUTPUT_DIR/${RUN_ID}_iperf.log"

  if [ -n "$DURATION_SEC" ]; then
    IPERF_RUN_SEC=$((DURATION_SEC + IPERF_STABILIZATION_SEC + 30))
  else
    IPERF_RUN_SEC=86400
  fi

  echo "[IPERF] Starting (${IPERF_LOAD_MBPS} Mbps, ${IPERF_PROTO}, duration=${IPERF_RUN_SEC}s)..."
  echo "[IPERF] Server: ${IPERF_SERVER_IP}:${IPERF_PORT}" | tee "$IPERF_LOG"
  echo "[IPERF] START_TS=$(date +%s)" | tee -a "$IPERF_LOG"
  echo "[IPERF] TARGET_MBPS=${IPERF_LOAD_MBPS}" | tee -a "$IPERF_LOG"
  echo "[IPERF] PROTO=${IPERF_PROTO}" | tee -a "$IPERF_LOG"
  echo "[IPERF] DURATION_SEC=${IPERF_RUN_SEC}" | tee -a "$IPERF_LOG"
  if [ "$IPERF_PROTO" = "tcp" ]; then
    echo "[IPERF] TCP_RATE_CONTROL=iperf3 -b target Mbps pacing" | tee -a "$IPERF_LOG"
  fi

  local iperf_flush_args=()
  if iperf3 --help 2>&1 | grep -q -- "--forceflush"; then
    iperf_flush_args=(--forceflush)
    IPERF_LOG_HEALTH_ENABLED="1"
    echo "[IPERF] FORCEFLUSH=enabled" | tee -a "$IPERF_LOG"
  else
    IPERF_LOG_HEALTH_ENABLED="0"
    echo "[WARNING] iperf3 lacks --forceflush; disabling stale-log watchdog" | tee -a "$IPERF_LOG"
  fi

  if [ "$IPERF_PROTO" = "udp" ]; then
    iperf3 -c "$IPERF_SERVER_IP" -p "$IPERF_PORT" \
      -u -b "${IPERF_LOAD_MBPS}M" \
      -t "$IPERF_RUN_SEC" -i 1 "${iperf_flush_args[@]}" >> "$IPERF_LOG" 2>&1 &
  else
    # Keep -b for TCP. W3 load levels are target-throughput conditions, and
    # validated iperf3 builds provide TCP bitrate pacing with this option.
    iperf3 -c "$IPERF_SERVER_IP" -p "$IPERF_PORT" \
      -b "${IPERF_LOAD_MBPS}M" \
      -t "$IPERF_RUN_SEC" -i 1 "${iperf_flush_args[@]}" >> "$IPERF_LOG" 2>&1 &
  fi

  IPERF_PID=$!
  echo "[IPERF] PID=$IPERF_PID"

  sleep "$IPERF_STABILIZATION_SEC"

  if ! ps -p "$IPERF_PID" > /dev/null; then
    echo "[ERROR] iperf process died immediately!"
    exit 1
  fi

  if ! grep -qE "connected|Interval" "$IPERF_LOG"; then
    echo "[WARNING] iperf did not confirm connection"
  fi

  echo "[IPERF] Running and stabilized"
}

iperf_log_mtime() {
  local path="$1"
  local mtime

  mtime="$(stat -c %Y "$path" 2>/dev/null || true)"
  if [[ "$mtime" =~ ^[0-9]+$ ]]; then
    echo "$mtime"
    return
  fi

  mtime="$(stat -f %m "$path" 2>/dev/null || true)"
  if [[ "$mtime" =~ ^[0-9]+$ ]]; then
    echo "$mtime"
    return
  fi

  echo 0
}

fail_iperf_health() {
  local message="$1"
  echo "[ERROR] $message"
  RUN_FINAL_STATUS="failed"
  kill -INT "$MAIN_PID" 2>/dev/null || true
}

check_iperf_health() {
  if [ "$IPERF_LOAD_MBPS" -eq 0 ]; then
    return
  fi

  if ! ps -p "$IPERF_PID" > /dev/null; then
    fail_iperf_health "iperf process died during experiment!"
    return
  fi

  if [ "$IPERF_LOG_HEALTH_ENABLED" != "1" ]; then
    return
  fi

  local last_update
  last_update="$(iperf_log_mtime "$IPERF_LOG")"
  local now
  now=$(date +%s)
  local age
  age=$((now - last_update))

  if [ "$last_update" -eq 0 ] || [ "$age" -gt "$IPERF_STALE_SEC" ]; then
    fail_iperf_health "iperf log has not updated for ${age}s (threshold: ${IPERF_STALE_SEC}s)"
    return
  fi
}

stop_iperf() {
  if [ -n "${IPERF_WATCHDOG_PID:-}" ]; then
    kill "$IPERF_WATCHDOG_PID" 2>/dev/null || true
  fi

  if [ -n "${IPERF_PID:-}" ]; then
    echo "[IPERF] Stopping..."
    kill -INT "$IPERF_PID" 2>/dev/null || true
    wait "$IPERF_PID" 2>/dev/null || true
    echo "[IPERF] Stopped"
  fi
}

resolved_esp32_reset_port() {
  if [ -n "$ESP32_RESET_PORT" ]; then
    echo "$ESP32_RESET_PORT"
  else
    echo "$SERIAL_PORT"
  fi
}

reset_esp32_node() {
  if [ "$RESET_ESP32" != "1" ]; then
    return
  fi

  local reset_port
  reset_port="$(resolved_esp32_reset_port)"
  if [ -z "$reset_port" ]; then
    echo "Error: --reset-esp32 requires --reset-port or --serial-port." >&2
    exit 1
  fi

  if [ ! -e "$reset_port" ]; then
    echo "Error: ESP32 reset port does not exist: $reset_port" >&2
    exit 1
  fi

  echo "Resetting ESP32 node on $reset_port..."
  python "$PY_DIR/reset_esp32.py" \
    --port "$reset_port" \
    --pulse-sec "$ESP32_RESET_PULSE_SEC" \
    --settle-sec "$ESP32_RESET_SETTLE_SEC"
}

start_serial_monitor() {
  if [ -z "$SERIAL_PORT" ] || [ "${SERIAL_STARTED:-0}" = "1" ]; then
    return
  fi

  if [ -n "$SERIAL_START_COMMAND" ]; then
    python serial_capture.py \
      --port "$SERIAL_PORT" \
      --baud "$SERIAL_BAUD" \
      --write-line "$SERIAL_START_COMMAND" \
      --write-delay-sec "$SERIAL_START_DELAY_SEC" \
      | tee "$OUTPUT_DIR/${RUN_ID}_serial.log" &
  else
    if ! command -v arduino-cli >/dev/null 2>&1; then
      echo "Error: arduino-cli is required for --serial-port capture without --serial-start-command." >&2
      exit 1
    fi

    arduino-cli monitor -p "$SERIAL_PORT" -c "baudrate=$SERIAL_BAUD" | tee "$OUTPUT_DIR/${RUN_ID}_serial.log" &
  fi

  SERIAL_PID=$!
  SERIAL_STARTED="1"
}

start_zigbee_trigger() {
  if [ "$ZIGBEE_TRIGGER" != "1" ]; then
    return
  fi

  python ha_zigbee_trigger.py \
    --run-id "$RUN_ID" \
    --entity-id "$ZIGBEE_ENTITY_ID" \
    --events "$ZIGBEE_EVENT_COUNT" \
    --base-interval-ms "$ZIGBEE_BASE_INTERVAL_MS" \
    --jitter-ms "$ZIGBEE_JITTER_MS" &
  ZIGBEE_TRIGGER_PID=$!

  sleep 1
  if ! ps -p "$ZIGBEE_TRIGGER_PID" >/dev/null 2>&1; then
    if wait "$ZIGBEE_TRIGGER_PID"; then
      echo "[ZIGBEE] Trigger driver completed during startup check"
    else
      echo "Error: Zigbee trigger driver exited during startup." >&2
      exit 1
    fi
  fi
}

watch_zigbee_trigger() {
  if [ "$ZIGBEE_TRIGGER" != "1" ] || [ -z "${ZIGBEE_TRIGGER_PID:-}" ]; then
    return
  fi

  (
    local schedule_path="$OUTPUT_DIR/${RUN_ID}_zigbee_trigger_schedule.csv"
    while true; do
      sleep 2
      if ps -p "$ZIGBEE_TRIGGER_PID" >/dev/null 2>&1; then
        continue
      fi

      local row_count="0"
      local error_count="1"
      if [ -f "$schedule_path" ]; then
        row_count="$(awk 'NR > 1 {count++} END {print count + 0}' "$schedule_path")"
        error_count="$(awk -F, 'NR > 1 && $7 != "" {count++} END {print count + 0}' "$schedule_path")"
      fi

      if [ "$row_count" -lt "$ZIGBEE_EVENT_COUNT" ] || [ "$error_count" -gt 0 ]; then
        echo "[ERROR] Zigbee trigger driver ended before a clean schedule was captured (${row_count}/${ZIGBEE_EVENT_COUNT} commands, errors=${error_count})"
        kill -TERM "$MAIN_PID" 2>/dev/null || true
      fi
      break
    done
  ) &
  ZIGBEE_TRIGGER_WATCHDOG_PID=$!
}

analyze_iperf_log() {
  if [ "$IPERF_LOAD_MBPS" -eq 0 ]; then
    return
  fi
  if [ -z "${IPERF_LOG:-}" ] || [ ! -f "$IPERF_LOG" ]; then
    return
  fi

  echo "[IPERF] Summary:"

  python - "$IPERF_LOG" "$OUTPUT_DIR/${RUN_ID}_iperf_summary.json" <<'PY'
import json
import re
import sys
from pathlib import Path
from statistics import mean, stdev

from version_info import build_metadata

log_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])

text = log_path.read_text(errors="ignore")

# Match interval lines such as:
# [  5]   1.00-2.00   sec  640 KBytes  5.24 Mbits/sec
pattern = re.compile(r"\]\s+\d+\.\d+-\d+\.\d+\s+sec\s+[\d.]+\s+\w+Bytes\s+([\d.]+)\s+Mbits/sec")

samples = [float(x) for x in pattern.findall(text)]

summary = {
    "metadata": build_metadata(
        "run_all.sh:analyze_iperf_log",
        inputs=[log_path],
        outputs=[out_path],
        extra={
            "run_id": log_path.name.replace("_iperf.log", ""),
        },
    ),
    "iperf_log": log_path.name,
    "interval_samples": len(samples),
    "target_mbps": None,
    "mean_interval_mbps": None,
    "std_interval_mbps": None,
    "min_interval_mbps": None,
    "max_interval_mbps": None,
}

m = re.search(r"\[IPERF\] TARGET_MBPS=(\d+)", text)
if m:
    summary["target_mbps"] = int(m.group(1))

if samples:
    summary["mean_interval_mbps"] = mean(samples)
    summary["std_interval_mbps"] = stdev(samples) if len(samples) > 1 else 0.0
    summary["min_interval_mbps"] = min(samples)
    summary["max_interval_mbps"] = max(samples)

out_path.write_text(json.dumps(summary, indent=2))

print(json.dumps(summary, indent=2))
PY
}

ensure_no_existing_helpers() {
  if ! command -v pgrep >/dev/null 2>&1; then
    return
  fi

  local existing
  existing="$(pgrep -fl 'mqtt_logger.py|mqtt_ack.py|ble_logger.py|ha_zigbee_trigger.py' 2>/dev/null || true)"
  if [ -z "$existing" ]; then
    return
  fi

  echo "Error: benchmark helper processes are already running:" >&2
  echo "$existing" >&2
  echo >&2
  echo "Stop them before starting a new run, for example:" >&2
  echo "  pgrep -fl 'run_all.sh|mqtt_logger.py|mqtt_ack.py|ble_logger.py'" >&2
  echo "  kill <pid> ..." >&2
  echo >&2
  echo "Shared MQTT topics make parallel loggers/ACK helpers unsafe for W3 timing." >&2
  exit 1
}

acquire_run_lock() {
  if mkdir "$RUN_LOCK_DIR" 2>/dev/null; then
    RUN_LOCK_ACQUIRED="1"
    printf '%s\n' "$$" > "$RUN_LOCK_DIR/pid"
    printf '%s\n' "$RUN_INSTANCE_ID" > "$RUN_LOCK_DIR/run_instance_id"
    return
  fi

  local lock_pid=""
  if [ -f "$RUN_LOCK_DIR/pid" ]; then
    lock_pid="$(cat "$RUN_LOCK_DIR/pid" 2>/dev/null || true)"
  fi

  if [ -n "$lock_pid" ] && ! ps -p "$lock_pid" >/dev/null 2>&1; then
    echo "Warning: removing stale run lock: $RUN_LOCK_DIR" >&2
    rm -f "$RUN_LOCK_DIR/pid" "$RUN_LOCK_DIR/run_instance_id" 2>/dev/null || true
    rmdir "$RUN_LOCK_DIR" 2>/dev/null || true
    if mkdir "$RUN_LOCK_DIR" 2>/dev/null; then
      RUN_LOCK_ACQUIRED="1"
      printf '%s\n' "$$" > "$RUN_LOCK_DIR/pid"
      printf '%s\n' "$RUN_INSTANCE_ID" > "$RUN_LOCK_DIR/run_instance_id"
      return
    fi
  fi

  echo "Error: another benchmark run appears active for EXP_RUN_ID=$EXP_RUN_ID RUN_ID=$RUN_ID." >&2
  echo "Lock directory: $RUN_LOCK_DIR" >&2
  if [ -n "$lock_pid" ]; then
    echo "Lock owner PID: $lock_pid" >&2
  fi
  exit 1
}

release_run_lock() {
  if [ "$RUN_LOCK_ACQUIRED" != "1" ]; then
    return
  fi

  rm -f "$RUN_LOCK_DIR/pid" "$RUN_LOCK_DIR/run_instance_id" 2>/dev/null || true
  rmdir "$RUN_LOCK_DIR" 2>/dev/null || true
  RUN_LOCK_ACQUIRED="0"
}

stop_background_jobs() {
  local pids
  pids="$(jobs -p || true)"
  if [ -z "$pids" ]; then
    return
  fi

  kill -TERM $pids 2>/dev/null || true
  sleep 1
  kill -KILL $pids 2>/dev/null || true
}

echo "======================================"
echo " IoT Benchmark Runner"
echo "======================================"
echo "EXP_RUN_ID       : $EXP_RUN_ID"
echo "RUN_ID           : $RUN_ID"
echo "RUN_INSTANCE_ID  : $RUN_INSTANCE_ID"
echo "PIPELINE_VERSION : $PIPELINE_VERSION"
echo "MQTT_HOST        : ${MQTT_HOST:-unset}"
echo "MQTT_PORT        : ${MQTT_PORT:-unset}"
echo "MQTT_USERNAME    : ${MQTT_USERNAME:-unset}"
echo "BLE Logger       : $([ "$ENABLE_BLE" = "1" ] && echo ENABLED || echo DISABLED)"
if [ "$ENABLE_BLE" = "1" ]; then
  echo "BLE_EXP_CODE     : ${BLE_EXPECTED_EXP_CODE:-W1BL (logger default)}"
fi
echo "ACK Helper       : $([ "$ENABLE_ACK" = "1" ] && echo ENABLED || echo DISABLED)"
echo "Zigbee Trigger   : $([ "$ZIGBEE_TRIGGER" = "1" ] && echo ENABLED || echo DISABLED)"
if [ "$ZIGBEE_TRIGGER" = "1" ]; then
  echo "ZIGBEE_ENTITY_ID : $ZIGBEE_ENTITY_ID"
  echo "ZIGBEE_EVENTS    : $ZIGBEE_EVENT_COUNT"
  echo "ZIGBEE_INTERVAL  : ${ZIGBEE_BASE_INTERVAL_MS}±${ZIGBEE_JITTER_MS} ms"
fi
echo "SERIAL_PORT      : ${SERIAL_PORT:-disabled}"
if [ -n "$SERIAL_START_COMMAND" ]; then
  echo "SERIAL_START_CMD : $SERIAL_START_COMMAND"
fi
echo "ESP32_RESET      : $([ "$RESET_ESP32" = "1" ] && echo ENABLED || echo DISABLED)"
if [ "$RESET_ESP32" = "1" ]; then
  echo "ESP32_RESET_PORT : $(resolved_esp32_reset_port)"
  echo "RESET_SETTLE_SEC : $ESP32_RESET_SETTLE_SEC"
fi
echo "AP_RF            : ${AP_MODEL} (${AP_FIRMWARE}), mode=${AP_CHANNEL_MODE}, ch=${AP_CHANNEL}, width=${AP_CHANNEL_WIDTH_MHZ}MHz, sideband=${AP_CONTROL_SIDEBAND}, source=${AP_RF_SOURCE}"
echo "IPERF_LOAD       : ${IPERF_LOAD} (${IPERF_LOAD_MBPS} Mbps)"
if [ "$IPERF_LOAD_MBPS" -gt 0 ]; then
  echo "IPERF_SERVER     : ${IPERF_SERVER_IP}:${IPERF_PORT}"
fi
if [ -n "$DURATION_SEC" ]; then
  echo "DURATION_SEC     : $DURATION_SEC"
else
  echo "DURATION_SEC     : manual stop"
fi
echo "--------------------------------------"
echo "Output files will be:"
echo "  $OUTPUT_DIR/run_metadata.json"
echo "  $OUTPUT_DIR/${RUN_ID}_mqtt_events.csv"
echo "  $OUTPUT_DIR/${RUN_ID}_power_samples.csv"
if [ "$ENABLE_BLE" = "1" ]; then
  echo "  $OUTPUT_DIR/${RUN_ID}_ble_events.csv"
fi
if [ -n "$SERIAL_PORT" ]; then
  echo "  $OUTPUT_DIR/${RUN_ID}_serial.log"
fi
if [ "$IPERF_LOAD_MBPS" -gt 0 ]; then
  echo "  $OUTPUT_DIR/${RUN_ID}_iperf.log"
fi
if [ "$ZIGBEE_TRIGGER" = "1" ]; then
  echo "  $OUTPUT_DIR/${RUN_ID}_zigbee_trigger_schedule.csv"
fi
echo "======================================"
echo

cleanup() {
  local exit_code=$?
  local final_status="failed"
  echo "Stopping background processes..."
  trap - EXIT INT TERM USR1

  stop_iperf
  analyze_iperf_log

  stop_background_jobs

  if [ "$RUN_FINAL_STATUS" = "complete" ] && { [ "$exit_code" -eq 0 ] || [ "$RUN_STOP_SIGNAL" = "1" ]; }; then
    final_status="complete"
    exit_code=0
  fi
  write_run_metadata "end" "$final_status" "$exit_code" || true
  update_run_sheet_status "$final_status"

  release_run_lock

  exit "$exit_code"
}
trap cleanup EXIT INT TERM
trap 'RUN_FINAL_STATUS="complete"; RUN_STOP_SIGNAL="1"; cleanup' USR1

ensure_no_existing_helpers
acquire_run_lock
append_run_sheet_row
write_run_metadata "start" "running" 0 || true

cd "$PY_DIR"

python mqtt_logger.py &
LOGGER_PID=$!

if [ "$ENABLE_ACK" = "1" ]; then
  python mqtt_ack.py &
  ACK_PID=$!
fi

if [ "$ENABLE_BLE" = "1" ]; then
  python ble_logger.py &
  BLE_PID=$!
fi

SERIAL_STARTED="0"
RESET_PORT="$(resolved_esp32_reset_port)"
if [ "$RESET_ESP32" != "1" ] || [ -z "$SERIAL_PORT" ] || [ "$RESET_PORT" != "$SERIAL_PORT" ]; then
  start_serial_monitor
fi

start_iperf
reset_esp32_node
start_serial_monitor
start_zigbee_trigger

echo "Started processes:"
echo "  mqtt_logger.py (PID $LOGGER_PID)"
if [ "$ENABLE_ACK" = "1" ]; then
  echo "  mqtt_ack.py    (PID $ACK_PID)"
fi
if [ "$ENABLE_BLE" = "1" ]; then
  echo "  ble_logger.py  (PID $BLE_PID)"
fi
if [ -n "$SERIAL_PORT" ]; then
  echo "  arduino-cli    (PID $SERIAL_PID)"
fi
if [ "$ZIGBEE_TRIGGER" = "1" ]; then
  echo "  zigbee trigger (PID $ZIGBEE_TRIGGER_PID)"
fi
echo

MAIN_PID=$$
watch_zigbee_trigger

# ---- IPERF WATCHDOG ----
if [ "$IPERF_LOAD_MBPS" -gt 0 ]; then
  (
    while true; do
      sleep 5
      check_iperf_health
    done
  ) &
  IPERF_WATCHDOG_PID=$!
fi


if [ -n "$DURATION_SEC" ]; then
  echo "Auto-stop enabled: run will stop after $DURATION_SEC seconds."
  (
    sleep "$DURATION_SEC"
    echo
    echo "Duration reached ($DURATION_SEC s). Stopping run..."
    kill -USR1 "$MAIN_PID"
  ) &
fi

echo "Press Ctrl+C to stop."
wait
RUN_FINAL_STATUS="complete"
