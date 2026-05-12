## R656 - W3 BLE Baseline Replicate rep4

Run ID: `W3_ble_auto_baseline`

Protocol: `ble`

Purpose: W3 BLE automated advertisement run for the baseline condition.

Setup:

- Logger host on Ethernet with Wi-Fi disabled
- BLE logger enabled with expected experiment code `W3BL`
- ACK helper disabled
- iPerf load: `0` / 0 Mbps TCP
- ESP32 BLE node reset at run start on `/dev/serial-port`

Command:

```bash
EXP_RUN_ID=R656 ./run_all.sh --run-id W3_ble_auto_baseline --enable-ble --disable-ack --duration-sec 360 --serial-port /dev/serial-port --serial-baud 115200 --iperf-load 0 --reset-esp32
```

Completion:

```text
EXPERIMENT_COMPLETE,exp=W3_ble_auto,boot_id=1946155111,reason=target_event_count,duration_ms=300804,events=100
```

Data quality:

- BLE CSV rows: 97 captured events
- Unique BLE sequences: 97
- Expected BLE advertisements: 100
- Missing sequences: `9`, `17`, `44`
- Duplicate sequences: 0
- Serial advertised sequences: 100/100
- Serial scheduled intervals: `2754` to `3248 ms`, mean approximately `3004.3 ms`
- Scheduler overruns: 0
- Experiment code: `W3BL`
- RSSI range: `-76` to `-71` dBm, mean approximately `-72.9` dBm
- MQTT and power CSVs are header-only, expected for BLE latency capture

Analysis:

```bash
python3 python/summarize_w3_run.py \
  experiments/runs/R656/raw \
  --run-id W3_ble_auto_baseline \
  --expected-events 100

python3 python/analyze_w3_run.py \
  experiments/runs/R656/raw \
  --run-id R656 \
  --run-sheet docs/run_sheet.csv
```

Summary metrics:

- Median normalized latency: `0.0 ms`
- MAD latency: `85.94 ms`
- P95 latency: `254.52 ms`
- P99 latency: `327.40 ms`
- Max latency: `331.62 ms`
- Loss rate: `3%`

Interpretation:

R656 is a valid W3 BLE baseline replicate. The ESP32 emitted the complete 100-event schedule, the BLE logger captured 97 unique advertisements, and the expected experiment code was present on all captured rows. The missed events are recorded as BLE reliability loss for this condition.
