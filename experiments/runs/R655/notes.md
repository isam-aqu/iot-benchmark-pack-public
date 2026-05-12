## R655 - W3 BLE Heavy Replicate rep3

Run ID: `W3_ble_auto_heavy`

Protocol: `ble`

Purpose: W3 BLE automated advertisement run for the heavy condition.

Setup:

- Logger host on Ethernet with Wi-Fi disabled
- BLE logger enabled with expected experiment code `W3BL`
- ACK helper disabled
- iPerf load: `heavy` / 50 Mbps TCP
- ESP32 BLE node reset at run start on `/dev/serial-port`

Command:

```bash
EXP_RUN_ID=R655 ./run_all.sh --run-id W3_ble_auto_heavy --enable-ble --disable-ack --duration-sec 360 --serial-port /dev/serial-port --serial-baud 115200 --iperf-load heavy --reset-esp32
```

Completion:

```text
EXPERIMENT_COMPLETE,exp=W3_ble_auto,boot_id=1782677702,reason=target_event_count,duration_ms=301552,events=100
```

Data quality:

- BLE CSV rows: 96 captured events
- Unique BLE sequences: 96
- Expected BLE advertisements: 100
- Missing sequences: `28`, `29`, `57`, `87`
- Duplicate sequences: 0
- Serial advertised sequences: 100/100
- Serial scheduled intervals: `2753` to `3246 ms`, mean approximately `3009.2 ms`
- Scheduler overruns: 0
- Experiment code: `W3BL`
- RSSI range: `-76` to `-71` dBm, mean approximately `-72.3` dBm
- MQTT and power CSVs are header-only, expected for BLE latency capture

iPerf:

- Target: `50 Mbps`
- Mean interval throughput: `50.00 Mbps`
- Interval samples: 369
- Range: `49.00` to `51.20 Mbps`

Analysis:

```bash
python3 python/summarize_w3_run.py \
  experiments/runs/R655/raw \
  --run-id W3_ble_auto_heavy \
  --expected-events 100

python3 python/analyze_w3_run.py \
  experiments/runs/R655/raw \
  --run-id R655 \
  --run-sheet docs/run_sheet.csv
```

Summary metrics:

- Median normalized latency: `0.0 ms`
- MAD latency: `86.74 ms`
- P95 latency: `143.60 ms`
- P99 latency: `236.49 ms`
- Max latency: `355.94 ms`
- Loss rate: `4%`

Interpretation:

R655 is a valid W3 BLE heavy replicate. The ESP32 emitted the complete 100-event schedule, the BLE logger captured 96 unique advertisements, and the expected experiment code was present on all captured rows. The missed events are recorded as BLE reliability loss for this condition.
