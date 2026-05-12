# IoT Smart-Home Benchmark Pack

> **Version:** 0.4.7
> **Source of truth:** `experiments/version_info.yaml`

A reproducible starter pack for benchmarking heterogeneous IoT protocols
in a **Home Assistant-centered smart-home testbed**, using a
**controller-level, application-driven evaluation model**.

------------------------------------------------------------------------

# 🏗️ System Architecture

This system uses a **split architecture**:

-   **Raspberry Pi (Home Assistant OS)** → controller + MQTT broker
-   **Raspberry Pi 4 (4 GB, `iperf-server`)** → dedicated `iperf3` server for
    W3 interference tests
-   **Laptop (external machine)** → logging + data collection
    (Ethernet-connected)
-   **IoT devices (ESP32 + Zigbee)** → event sources

    ESP32 (Wi-Fi) ─────┐
                       │
    ESP32 (BLE) ───────┼──► Raspberry Pi (Home Assistant + MQTT)
                       │
    Zigbee Devices ────┘
                              │
                              ▼
                    Laptop (Python Loggers)
                    - mqtt_logger.py
                    - mqtt_ack.py
                    - ble_logger.py

------------------------------------------------------------------------

# 🧠 Design Rationale

Home Assistant OS (HAOS):

-   ❌ does not support arbitrary Python environments
-   ❌ lacks standard `pip` usage
-   ❌ restricts system-level execution

👉 Therefore:

**All logging, timestamping, and data collection are performed on an
external machine (laptop).**

------------------------------------------------------------------------

## ⚠️ Measurement Correction (Important)

Earlier experiments used a **Wi-Fi-connected logging laptop**, which
introduced unintended RF contention.

👉 This affected results, especially:

-   Wi-Fi latency tails
-   Zigbee variability

### Corrected setup:

-   Logger connected via **Ethernet**
-   Laptop Wi-Fi **disabled**

This correction significantly improved measurement validity and is now
the **standard configuration**.

------------------------------------------------------------------------

## ✅ Advantages

-   Stable Python environment
-   Accurate centralized timestamping
-   Full control over logging and data pipeline
-   No measurement-induced Wi-Fi interference
-   Reliable BLE scanning
-   Clean separation of control vs measurement

------------------------------------------------------------------------

# 📦 Included Benchmark Paths

-   Wi-Fi ESP32 → MQTT → **Laptop logger**
-   Wi-Fi ESP32 → MQTT → ACK → ESP32 RTT measurement
-   Wi-Fi ESP32 + INA231 power sampling → serial logger (MQTT used only for telemetry events in W2 v2)
-   BLE ESP32 advertising → **Laptop BLE logger**
-   Zigbee (ZHA in Home Assistant) → MQTT forwarding → Laptop logger

------------------------------------------------------------------------

# 📊 Current Baseline Comparison Set (Corrected)

The current **validated W1 near-quiet baseline comparison** uses:

-   **Wi-Fi:** `R106 / W1_wifi_near_quiet_v6`
-   **Zigbee:** `R204 / W1_zigbee_near_quiet_v3`
-   **BLE:** `R303 / W1_ble_near_quiet_v3`

These runs were collected under the **corrected Ethernet-logger setup**
and should be used for all cross-protocol comparisons.

------------------------------------------------------------------------

## 📈 Current Interpretation

-   **Wi-Fi**
    -   Low median RTT (\~10 ms)
    -   Narrowest corrected-baseline distribution in W1
    -   Previously observed heavy tail disappeared after measurement
        correction
    -   Now shows stable and bounded latency
-   **Zigbee**
    -   Stable low-variability behavior
    -   Slightly broader normalized spread than Wi-Fi in W1
-   **BLE**
    -   Widest latency spread
    -   Occasional missed events (e.g., 99/101 captured in R303)
    -   **Clustered (multi-modal) latency distribution**
    -   Less deterministic than Wi-Fi and Zigbee

------------------------------------------------------------------------

## 🔵 Important BLE Insight (Updated)

BLE latency is **not continuous**:

-   Shows **clustered / multi-modal structure**
-   Earlier runs suggested \~45 ms spacing between clusters
-   In corrected runs (R303):
    -   clustering remains
    -   upper regions are less regular
    -   strict fixed-step quantization should not be assumed

👉 Interpretation:

> BLE latency is dominated by advertisement and scanning behavior,
> producing discrete timing bands with additional variability from scan
> scheduling and host-side effects.

------------------------------------------------------------------------

## 🔁 Normalization Note

For cross-protocol comparison:

-   Wi-Fi RTT is **median-normalized**
-   Zigbee and BLE are already offset-normalized

👉 This allows fair comparison of:

-   distribution shape
-   variability
-   determinism

Absolute Wi-Fi RTT values remain available separately.

------------------------------------------------------------------------

## ⚡ W2 Telemetry Energy Status

The revised W2 v2 energy study is now completed under the
**serial-power / MQTT-telemetry split methodology**.

-   Matched control / telemetry pairs cover `0.5 s` through `10 s`,
    with repeated runs extending through `R557`
-   Grouped outputs live in `analysis/w2/tables/groups.csv` and
    `analysis/w2/tables/groups.json`
-   **Positive detectable overhead:** `2 s`, `3 s`, `6 s`, `7 s`
-   **Directionally unresolved:** `4 s`
-   **Below present noise floor:** `0.5 s`, `1 s`, `5 s`, `8 s`,
    `9 s`, `10 s`

------------------------------------------------------------------------

## 📊 Plotting Approach

Dedicated scripts are used for each figure:

-   `plot_w1_final_cdf.py` → core latency comparison
-   `plot_w1_full_boxplot.py` → distribution comparison
-   `plot_ble_histogram.py` → BLE structure analysis

Older combined plotting scripts were removed to reduce duplication and
ensure methodological clarity.

------------------------------------------------------------------------

# 🧾 Home Assistant Environment (Reference)

The benchmark was validated on the following Home Assistant stack:

-   Installation method: **Home Assistant OS**
-   Core: **2026.3.4**
-   Supervisor: **2026.03.2**
-   Operating System: **17.1**
-   Frontend: **20260312.1**

This information should be recorded for reproducibility and included in
experiment documentation when relevant.

------------------------------------------------------------------------

# 📁 Folder Structure

-   `analysis/` → cross-run grouped outputs (for example final W2
    summaries)
-   `firmware/` → Arduino sketches for ESP32 nodes
-   `python/` → logging and support scripts (**run on laptop**)
-   `home_assistant/` → YAML snippets and automations
-   `docs/` → protocol, run sheets, and analysis notes
-   `experiments/` → per-run structured data (`raw/`, optional
    `derived/`, `analysis/`, `figures/`, manifests / notes when
    present)
-   `data/` → legacy / archived outputs

------------------------------------------------------------------------

# 🚀 Quick Start

## 1) Edit Configuration

### Firmware

    cp firmware/secrets.example.h firmware/secrets.h

Update `firmware/secrets.h`:

-   `IOT_WIFI_SSID`
-   `IOT_WIFI_PASS`
-   `IOT_MQTT_HOST`
-   `IOT_MQTT_PORT`
-   `IOT_MQTT_USERNAME` and `IOT_MQTT_PASSWORD` if your broker requires
    login

Per sketch, also update node-specific values such as `NODE_ID`, `EXP_ID`,
`EXP_CODE`, `PERIODIC_INTERVAL_MS`, and any pin mappings.

Shared firmware semantic versioning lives in `firmware/firmware_version.h`.
Pipeline component versions live in `experiments/version_info.yaml`, and
firmware bump rules are documented in `firmware/VERSIONING.md`.

------------------------------------------------------------------------

### Python scripts

The MQTT Python scripts read shared MQTT settings from `firmware/secrets.h`.
You can still override `MQTT_HOST`, `MQTT_PORT`, `MQTT_USERNAME`, and
`MQTT_PASSWORD` from the environment when needed.

The runner and BLE logger support:

-   `EXP_RUN_ID=<Rxxx>`
-   `RUN_ID` or `./run_all.sh --run-id <id>`
-   `ENABLE_BLE=0|1` or `./run_all.sh --enable-ble` /
    `--disable-ble`
-   `BLE_EXPECTED_COMPANY_ID`
-   `BLE_EXPECTED_VERSION`
-   `BLE_EXPECTED_EXP_CODE`
-   `BLE_EXPECTED_NODE_NUM`
-   `BLE_DEDUP_WINDOW`

------------------------------------------------------------------------

### Home Assistant

Update:

-   MQTT configuration
-   Zigbee entity IDs

------------------------------------------------------------------------

### W3 `iperf3` Server

-   Host: `iperf-server`
-   IP: `<private-ip>`
-   Role: dedicated `iperf3` server for W3 congestion and interference tests
-   Network: connected to the AP via Ethernet
-   Run: `iperf3 -s`
-   Do not store lab credentials in this repository

### `iperf3` TCP Rate Control

For W3 load runs, `run_all.sh` intentionally passes `-b <Mbps>` for both UDP
and TCP iperf clients. The light/moderate/heavy conditions are defined by
target throughput, so removing `-b` from TCP changes the experiment. Use an
iperf3 build with TCP bitrate pacing support; the 600-series Wi-Fi runs were
validated with iperf3 3.21. The runner also enables `--forceflush` when
available so the watchdog can verify that interval output is still reaching
the log during the experiment.

### Automatic Metadata Stamps

`run_all.sh` writes `raw/run_metadata.json` at run start and updates it during
cleanup with the final status, timestamps, versions, git commit, the non-secret
shell command used to start the run, and key run configuration. W3 summary,
metrics, replicate-analysis JSON files, and plot sidecar files also include
metadata generated from `python/version_info.py`. Keep
`experiments/version_info.yaml` current before collecting or regenerating
analysis outputs.

Current pipeline component versions are tracked in `experiments/version_info.yaml`.
Record the relevant version values in `docs/run_sheet.csv`, per-run
`manifest.yaml`, or per-run notes whenever logic changes.

------------------------------------------------------------------------

## 2) Install Python Environment

    cd python
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

------------------------------------------------------------------------

## 3) Start Services

-   Home Assistant
-   Mosquitto
-   Zigbee (ZHA)
-   For W3 load tests, `iperf3 -s` on `iperf-server`

RF/channel notes for completed and rerunnable W3 runs:

-   Wi-Fi AP: netis WF2419, firmware `V2.2.36123`
-   The AP was configured for Auto channel selection, so the AP channel used
    before `R640` is not known from the preserved run metadata.
-   During `R640`--`R659`, the AP was observed on channel 1, channel width
    40 MHz, control sideband Upper.
-   Zigbee: channel 20
-   BLE legacy advertising: primary advertising channels 37, 38, and 39
    (`2402`, `2426`, and `2480 MHz`)
-   Starting with planned runs `R678` and later, AP RF metadata is captured in
    both `run_metadata.json` and `docs/run_sheet.csv`: AP model, firmware,
    channel mode, primary channel, width, sideband, and RF value source.

Interpretation note: do not make channel-specific Wi-Fi/Zigbee coexistence
claims for `R600`--`R639`, because the AP channel was not recorded and may have
changed under Auto channel selection. For `R640`--`R659`, the observed channel-1
40 MHz upper-sideband AP setting likely exposed BLE advertising channels 37 and
38, so that BLE set is not a clean one-advertising-channel overlap test.

AP RF values can be supplied to `run_all.sh` with `--ap-channel-mode`,
`--ap-channel`, `--ap-width-mhz`, `--ap-sideband`, and `--ap-rf-source`.
Independent automatic capture is only partial: use a separate Wi-Fi probe/client
for channel/frequency checks, and keep the logger laptop Wi-Fi disabled.

------------------------------------------------------------------------

## 4) Flash ESP32 Nodes

Flash Wi-Fi, BLE, and power nodes as needed. For the Wi-Fi node button/LED
wiring, see `docs/wifi_node_connection_diagram.md`.

For W2 power-node reruns, the INA231 firmware supports host-side serial
configuration of interval, control/telemetry mode, and duration. The batch
workflow is documented in `docs/w2_batch_automation.md`.

------------------------------------------------------------------------

## 5) Run Loggers

Example:

    EXP_RUN_ID=R106 ./run_all.sh --run-id W1_wifi_near_quiet_v6 --disable-ble

For BLE-inclusive runs:

    EXP_RUN_ID=R301 ./run_all.sh --run-id W1_ble_near_quiet --enable-ble

For W3 Wi-Fi 600-series runs, reset the ESP32 after loggers and iperf are ready:

    EXP_RUN_ID=R600 ./run_all.sh --run-id W3_wifi_auto_baseline --disable-ble --serial-port /dev/serial-port --reset-esp32

For W3 BLE AP-channel extension reruns, use 20 MHz AP width and record the
actual AP channel/width/sideband before each pair. The completed extension
`R660`--`R677` is summarized in `analysis/w3/reports/w3_ble_channel_overlap.md`.

    EXP_RUN_ID=R660 ./run_all.sh --run-id W3_ble_auto_baseline --enable-ble --disable-ack --duration-sec 360 --serial-port /dev/serial-port --serial-baud 115200 --iperf-load 0 --reset-esp32 --ap-channel-mode fixed --ap-channel 1 --ap-width-mhz 20 --ap-sideband none --ap-rf-source manual_ap_ui
    EXP_RUN_ID=R661 ./run_all.sh --run-id W3_ble_auto_heavy --enable-ble --disable-ack --duration-sec 360 --serial-port /dev/serial-port --serial-baud 115200 --iperf-load heavy --reset-esp32 --ap-channel-mode fixed --ap-channel 1 --ap-width-mhz 20 --ap-sideband none --ap-rf-source manual_ap_ui

For planned Zigbee AP-channel extension runs, use five paired baseline/heavy
replicates per AP setting: `R678`--`R687` for AP channel 1 / 20 MHz control and
`R688`--`R697` for AP channel 9 / 20 MHz overlap with Zigbee channel 20.

    EXP_RUN_ID=R678 ./run_all.sh --run-id W3_zigbee_auto_baseline_ch1 --disable-ble --disable-ack --duration-sec 360 --iperf-load 0 --zigbee-trigger --zigbee-entity-id light.benchmark_device --zigbee-events 100 --zigbee-base-interval-ms 3000 --zigbee-jitter-ms 250 --ap-channel-mode fixed --ap-channel 1 --ap-width-mhz 20 --ap-sideband none --ap-rf-source manual_ap_ui
    EXP_RUN_ID=R679 ./run_all.sh --run-id W3_zigbee_auto_heavy_ch1 --disable-ble --disable-ack --duration-sec 360 --iperf-load heavy --zigbee-trigger --zigbee-entity-id light.benchmark_device --zigbee-events 100 --zigbee-base-interval-ms 3000 --zigbee-jitter-ms 250 --ap-channel-mode fixed --ap-channel 1 --ap-width-mhz 20 --ap-sideband none --ap-rf-source manual_ap_ui

Other useful patterns:

-   `./run_all.sh --help`
-   `./run_all.sh W1_wifi_near_quiet` for the backward-compatible
    positional `RUN_ID`
-   `EXP_RUN_ID=R301 RUN_ID=W1_ble_near_quiet BLE_EXPECTED_EXP_CODE=W1BL python python/ble_logger.py`
    when running the BLE logger manually from the repo root

------------------------------------------------------------------------

## 6) Test

    python -c "import paho.mqtt.publish as p; p.single('iotbench/test', payload='{\"type\":\"event\",\"node\":\"test\"}', hostname='<private-ip>', port=1883)"

------------------------------------------------------------------------

# 📊 Output Files

    experiments/runs/<EXP_RUN_ID>/raw/
    ├── run_metadata.json
    ├── <RUN_ID>_mqtt_events.csv
    ├── <RUN_ID>_power_samples.csv
    ├── <RUN_ID>_ble_events.csv
    ├── <RUN_ID>_serial.log
    ├── <RUN_ID>_iperf.log
    └── <RUN_ID>_iperf_summary.json

Logger safety behavior:

-   MQTT retained messages are skipped before payload decoding.
-   MQTT and BLE CSV writers validate the header on startup.
-   If an existing CSV has a mismatched header, it is rotated to a
    timestamped `_badheader_...` file before a new file is created.

------------------------------------------------------------------------

# 🧪 Recommended First Pilot

-   1 Wi-Fi node
-   1 BLE node
-   1 Zigbee device
-   50--100 events

------------------------------------------------------------------------

# 🧠 Benchmark Model

Controller-centered, application-level benchmarking.

------------------------------------------------------------------------

# 🔵 BLE Notes

BLE is advertisement-based and scalable. The BLE manufacturer payload includes
a compact experiment code so `<RUN_ID>_ble_events.csv` can be correlated to
named runs without relying only on the external run sheet.

The BLE logger defaults to benchmark-specific filters, but these can be
configured without code edits:

-   `BLE_EXPECTED_COMPANY_ID` default `0x1234`
-   `BLE_EXPECTED_VERSION` default `2`
-   `BLE_EXPECTED_EXP_CODE` default `W1BL`
-   `BLE_EXPECTED_NODE_NUM` default `1`
-   `BLE_DEDUP_WINDOW` default `512`

The scanner locks onto the first matching sender, deduplicates only within the
bounded recent sequence window, and stops cleanly on `Ctrl+C`.

------------------------------------------------------------------------

# 🟡 Zigbee Notes

-   Tuya devices + ZHA
-   Coordinator: Sonoff

------------------------------------------------------------------------

# ⚡ Power Measurement

-   INA231 inline sensing
-   INA226 firmware support is also present for compatible power-node runs

------------------------------------------------------------------------

# ⏱️ Timing Model

-   All timestamps recorded on laptop

------------------------------------------------------------------------

# ⚠️ Known Constraints

-   HAOS limitations
-   BLE scan limitations
-   Zigbee lacks device-side timestamps

------------------------------------------------------------------------

# 📶 W3 Interference Procedure

The finalized W3 procedure is documented in
`docs/w3_experiment_procedure.md`. It complements per-run `manifest.yaml`,
`notes.md`, and `docs/run_sheet.csv` entries.

W3 evaluates protocol behavior under controlled 2.4 GHz background traffic
from `iperf3`. Wi-Fi uses ESP32 MQTT RTT. Zigbee uses Home Assistant
state-change time to logger receive time, median-normalized as in W1. Primary
paper metrics are:

-   median latency
-   MAD latency
-   P95 latency
-   tail inflation factor (`P95 / median`)
-   drop rate
-   extra-event rate for Zigbee state-change validation

Secondary metrics are mean latency and temporal standard deviation.

Before each W3 run:

-   Home Assistant OS and MQTT broker are running.
-   Logging laptop is connected by Ethernet and laptop Wi-Fi is disabled.
-   `iperf-server` is running `iperf3 -s` at `<private-ip>`.
-   No stale logger, ACK helper, BLE logger, Zigbee trigger driver, serial
    monitor, or `iperf3` process is running.

Wi-Fi replicate matrix:

| Load level | Primary | Rep1 | Rep2 | Rep3 | Rep4 | iPerf profile |
|---|---:|---:|---:|---:|---:|---|
| Baseline | R600 | R604 | R608 | R612 | R616 | none |
| Light | R601 | R605 | R609 | R613 | R617 | 5 Mbps TCP |
| Moderate | R602 | R606 | R610 | R614 | R618 | 20 Mbps TCP |
| Heavy | R603 | R607 | R611 | R615 | R619 | 50 Mbps TCP |

BLE replicate matrix:

| Load level | Primary | Rep1 | Rep2 | Rep3 | Rep4 | iPerf profile |
|---|---:|---:|---:|---:|---:|---|
| Baseline | R640 | R644 | R648 | R652 | R656 | none |
| Light | R641 | R645 | R649 | R653 | R657 | 5 Mbps TCP |
| Moderate | R642 | R646 | R650 | R654 | R658 | 20 Mbps TCP |
| Heavy | R643 | R647 | R651 | R655 | R659 | 50 Mbps TCP |

Status:

-   W3 Wi-Fi is complete for `R600`--`R619`.
-   W3 Zigbee is complete for `R620`--`R639`.
-   W3 BLE is complete for `R640`--`R659`.
-   Full three-protocol W3 comparison artifacts are available under
    `analysis/w3/aggregates/`, `analysis/w3/tables/`, `analysis/w3/figures/`,
    and `analysis/w3/reports/`.

Example run shape:

    EXP_RUN_ID=R601 ./run_all.sh \
      --run-id W3_wifi_auto_light \
      --disable-ble \
      --enable-ack \
      --duration-sec 360 \
      --serial-port /dev/serial-port \
      --serial-baud 115200 \
      --iperf-load light \
      --reset-esp32

Per-run analysis:

    python python/summarize_w3_run.py experiments/runs/R601/raw --run-id W3_wifi_auto_light
    python python/analyze_w3_run.py experiments/runs/R601/raw --run-id R601 --run-sheet docs/run_sheet.csv

Zigbee runs use the same runner plus the Home Assistant trigger driver:

    export HA_URL=http://<private-ip>:8123
    export HA_TOKEN=<home-assistant-long-lived-token>

    EXP_RUN_ID=R620 ./run_all.sh \
      --run-id W3_zigbee_auto_baseline \
      --disable-ble \
      --disable-ack \
      --duration-sec 360 \
      --iperf-load 0 \
      --zigbee-trigger \
      --zigbee-entity-id light.benchmark_device \
      --zigbee-events 100 \
      --zigbee-base-interval-ms 3000 \
      --zigbee-jitter-ms 250

Zigbee per-run analysis includes the expected event count:

    python python/summarize_w3_run.py experiments/runs/R620/raw --run-id W3_zigbee_auto_baseline --expected-events 100
    python python/analyze_w3_run.py experiments/runs/R620/raw --run-id R620 --run-sheet docs/run_sheet.csv

BLE runs use the W3 BLE auto-advertising firmware and the BLE logger:

    EXP_RUN_ID=R640 ./run_all.sh \
      --run-id W3_ble_auto_baseline \
      --enable-ble \
      --disable-ack \
      --duration-sec 360 \
      --serial-port /dev/serial-port \
      --serial-baud 115200 \
      --iperf-load 0 \
      --reset-esp32

BLE per-run analysis also includes the expected event count:

    python python/summarize_w3_run.py experiments/runs/R640/raw --run-id W3_ble_auto_baseline --expected-events 100
    python python/analyze_w3_run.py experiments/runs/R640/raw --run-id R640 --run-sheet docs/run_sheet.csv

Cross-run W3 analysis and figures:

    python python/analyze_w3_replicates.py --run-sheet docs/run_sheet.csv
    python python/plot_w3_results.py
    python python/report_w3_protocol_comparison.py

Expected figure outputs:

-   `analysis/w3/aggregates/w3_replicates.json`
-   `analysis/w3/figures/w3_latency_plot_ci.png`
-   `analysis/w3/figures/w3_latency_plot_ci.png.meta.json`
-   `analysis/w3/figures/w3_mad_drop_plot_ci.png`
-   `analysis/w3/figures/w3_mad_drop_plot_ci.png.meta.json`
-   `analysis/w3/figures/w3_protocol_p95_comparison_ci.png`
-   `analysis/w3/figures/w3_protocol_p95_comparison_ci.png.meta.json`
-   `analysis/w3/figures/w3_protocol_mad_anomaly_comparison_ci.png`
-   `analysis/w3/figures/w3_protocol_mad_anomaly_comparison_ci.png.meta.json`
-   `analysis/w3/reports/w3_protocol_comparison.md`
-   `analysis/w3/tables/w3_protocol_comparison.csv`

Quality checks:

-   Check `analysis/summary.json` for the selected boot segment.
-   Check `data_quality` duplicate counts; expected duplicates should be
    zero unless explained in notes.
-   For loaded runs, check `<RUN_ID>_iperf_summary.json` and the tail of
    `<RUN_ID>_iperf.log`.
-   For Wi-Fi, check the serial log for `EXPERIMENT_COMPLETE`.
-   For BLE, check the serial log for `EXPERIMENT_COMPLETE` and the BLE CSV
    for `exp_code` = `W3BL`.
-   For Zigbee, check `<RUN_ID>_zigbee_trigger_schedule.csv` for 100 commands
    and empty `error` values.

Each formal W3 run should include:

    experiments/runs/<EXP_RUN_ID>/
    ├── manifest.yaml
    ├── notes.md
    ├── raw/
    │   ├── <RUN_ID>_mqtt_events.csv
    │   ├── <RUN_ID>_power_samples.csv
    │   ├── run_metadata.json
    │   ├── <RUN_ID>_ble_events.csv         # BLE runs only
    │   ├── <RUN_ID>_serial.log             # Wi-Fi and BLE runs
    │   ├── <RUN_ID>_zigbee_trigger_schedule.csv  # Zigbee runs only
    │   ├── <RUN_ID>_iperf.log              # loaded runs only
    │   └── <RUN_ID>_iperf_summary.json     # loaded runs only
    └── analysis/
        ├── summary.json
        └── metrics.json

Minimum manifest content: run ID, scenario ID, workload, protocol, topology,
interference, load level, comparison group, run type, replicate ID, versions,
actual `run_all.sh` command used for the experiment, analysis commands, and
quality checks. Omit secrets such as Home Assistant tokens from recorded
commands.

Minimum notes content: purpose, setup, deviations from protocol, ESP32
completion line, iperf confirmation for loaded runs, data-quality
observations, and interpretation.

------------------------------------------------------------------------

# 🚀 Next Steps

-   Define and execute the remaining W4/W5 robustness scope
-   Prepare publication

## Public Artifact Export

Before publishing the data and analysis package, generate a fresh sanitized
artifact repository instead of making this private working repository public.
Usage is documented in `docs/public_artifact_export.md`.
