## R652 - W3 BLE Baseline Replicate rep3

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
EXP_RUN_ID=R652 ./run_all.sh --run-id W3_ble_auto_baseline --enable-ble --disable-ack --duration-sec 360 --serial-port /dev/serial-port --serial-baud 115200 --iperf-load 0 --reset-esp32
```

Completion:

```text
EXPERIMENT_COMPLETE,exp=W3_ble_auto,boot_id=1031074602,reason=target_event_count,duration_ms=300152,events=100
```

Data quality:

- BLE CSV rows: 99 captured events
- Unique BLE sequences: 99
- Expected BLE advertisements: 100
- Missing sequences: `77`
- Duplicate sequences: 0
- Serial advertised sequences: 100/100
- Serial scheduled intervals: `2754` to `3244 ms`, mean approximately `2994.1 ms`
- Scheduler overruns: 0
- Experiment code: `W3BL`
- RSSI range: `-76` to `-71` dBm, mean approximately `-73.3` dBm
- MQTT and power CSVs are header-only, expected for BLE latency capture

Analysis:

```bash
python3 python/summarize_w3_run.py \
  experiments/runs/R652/raw \
  --run-id W3_ble_auto_baseline \
  --expected-events 100

python3 python/analyze_w3_run.py \
  experiments/runs/R652/raw \
  --run-id R652 \
  --run-sheet docs/run_sheet.csv
```

Summary metrics:

- Median normalized latency: `0.0 ms`
- MAD latency: `86.99 ms`
- P95 latency: `172.88 ms`
- P99 latency: `274.79 ms`
- Max latency: `297.34 ms`
- Loss rate: `1%`

Interpretation:

R652 is a valid W3 BLE baseline replicate. The ESP32 emitted the complete 100-event schedule, the BLE logger captured 99 unique advertisements, and the expected experiment code was present on all captured rows. The missed events are recorded as BLE reliability loss for this condition.
