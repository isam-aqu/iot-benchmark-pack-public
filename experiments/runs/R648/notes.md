## R648 - W3 BLE Baseline Replicate rep2

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
EXP_RUN_ID=R648 ./run_all.sh --run-id W3_ble_auto_baseline --enable-ble --disable-ack --duration-sec 360 --serial-port /dev/serial-port --serial-baud 115200 --iperf-load 0 --reset-esp32
```

Completion:

```text
EXPERIMENT_COMPLETE,exp=W3_ble_auto,boot_id=942412233,reason=target_event_count,duration_ms=300727,events=100
```

Data quality:

- BLE CSV rows: 97 captured events
- Unique BLE sequences: 97
- Expected BLE advertisements: 100
- Missing sequences: `26`, `48`, `98`
- Duplicate sequences: 0
- Serial advertised sequences: 100/100
- Serial scheduled intervals: `2760` to `3247 ms`, mean approximately `3001.2 ms`
- Scheduler overruns: 0
- Experiment code: `W3BL`
- RSSI range: `-76` to `-65` dBm, mean approximately `-72.4` dBm
- MQTT and power CSVs are header-only, expected for BLE latency capture

Analysis:

```bash
python3 python/summarize_w3_run.py \
  experiments/runs/R648/raw \
  --run-id W3_ble_auto_baseline \
  --expected-events 100

python3 python/analyze_w3_run.py \
  experiments/runs/R648/raw \
  --run-id R648 \
  --run-sheet docs/run_sheet.csv
```

Summary metrics:

- Median normalized latency: `0.0 ms`
- MAD latency: `91.58 ms`
- P95 latency: `231.20 ms`
- P99 latency: `320.95 ms`
- Max latency: `347.88 ms`
- Loss rate: `3%`

Interpretation:

R648 is a valid W3 BLE baseline replicate. The ESP32 emitted the complete 100-event schedule, the BLE logger captured 97 unique advertisements, and the expected experiment code was present on all captured rows. The missed events are recorded as BLE reliability loss for this condition.
