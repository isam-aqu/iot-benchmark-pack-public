## R640 - W3 BLE Automated Baseline

Run ID: `W3_ble_auto_baseline`

Protocol: `ble`

Purpose: quiet W3 BLE baseline with automated ESP32 advertisements at `3000±250 ms`, matching the Wi-Fi/Zigbee W3 schedule shape.

Setup:

- Logger host on Ethernet with Wi-Fi disabled
- BLE logger enabled with expected experiment code `W3BL`
- ACK helper disabled
- iPerf load disabled (`--iperf-load 0`)
- ESP32 BLE node reset at run start on `/dev/serial-port`

Command:

```bash
EXP_RUN_ID=R640 ./run_all.sh \
  --run-id W3_ble_auto_baseline \
  --enable-ble \
  --disable-ack \
  --duration-sec 360 \
  --serial-port /dev/serial-port \
  --serial-baud 115200 \
  --iperf-load 0 \
  --reset-esp32
```

Completion:

```text
EXPERIMENT_COMPLETE,exp=W3_ble_auto,boot_id=895452206,reason=target_event_count,duration_ms=300319,events=100
```

Data quality:

- BLE CSV rows: 96 captured events
- Unique BLE sequences: 96
- Expected BLE advertisements: 100
- Missing sequences: `13`, `20`, `71`, `98`
- Duplicate sequences: 0
- Serial advertised sequences: 100/100
- Serial scheduled intervals: `2752` to `3248 ms`, mean approximately `2998.5 ms`
- Scheduler overruns: 0
- Experiment code: `W3BL`
- RSSI range: `-80` to `-69` dBm, mean approximately `-75.2` dBm
- MQTT and power CSVs are header-only, expected for BLE latency capture

Analysis:

```bash
python3 python/summarize_w3_run.py \
  experiments/runs/R640/raw \
  --run-id W3_ble_auto_baseline \
  --expected-events 100

python3 python/analyze_w3_run.py \
  experiments/runs/R640/raw \
  --run-id R640 \
  --run-sheet docs/run_sheet.csv
```

Summary metrics:

- Median normalized latency: `0.0 ms`
- MAD latency: `94.78 ms`
- P95 latency: `215.00 ms`
- P99 latency: `314.19 ms`
- Max latency: `343.45 ms`
- Loss rate: `4%`

Interpretation:

R640 is a valid W3 BLE baseline. The ESP32 emitted the complete 100-event schedule and the logger captured 96 unique advertisements. The missed events and broad median-normalized latency spread are consistent with BLE's known advertisement/scanning variability and should be treated as part of the BLE baseline rather than a run failure.
