## R650 - W3 BLE Moderate Replicate rep2

Run ID: `W3_ble_auto_moderate`

Protocol: `ble`

Purpose: W3 BLE automated advertisement run for the moderate condition.

Setup:

- Logger host on Ethernet with Wi-Fi disabled
- BLE logger enabled with expected experiment code `W3BL`
- ACK helper disabled
- iPerf load: `moderate` / 20 Mbps TCP
- ESP32 BLE node reset at run start on `/dev/serial-port`

Command:

```bash
EXP_RUN_ID=R650 ./run_all.sh --run-id W3_ble_auto_moderate --enable-ble --disable-ack --duration-sec 360 --serial-port /dev/serial-port --serial-baud 115200 --iperf-load moderate --reset-esp32
```

Completion:

```text
EXPERIMENT_COMPLETE,exp=W3_ble_auto,boot_id=758647139,reason=target_event_count,duration_ms=298986,events=100
```

Data quality:

- BLE CSV rows: 99 captured events
- Unique BLE sequences: 99
- Expected BLE advertisements: 100
- Missing sequences: `7`
- Duplicate sequences: 0
- Serial advertised sequences: 100/100
- Serial scheduled intervals: `2750` to `3248 ms`, mean approximately `2985.6 ms`
- Scheduler overruns: 0
- Experiment code: `W3BL`
- RSSI range: `-75` to `-66` dBm, mean approximately `-72.3` dBm
- MQTT and power CSVs are header-only, expected for BLE latency capture

iPerf:

- Target: `20 Mbps`
- Mean interval throughput: `20.00 Mbps`
- Interval samples: 369
- Range: `18.90` to `21.10 Mbps`

Analysis:

```bash
python3 python/summarize_w3_run.py \
  experiments/runs/R650/raw \
  --run-id W3_ble_auto_moderate \
  --expected-events 100

python3 python/analyze_w3_run.py \
  experiments/runs/R650/raw \
  --run-id R650 \
  --run-sheet docs/run_sheet.csv
```

Summary metrics:

- Median normalized latency: `0.0 ms`
- MAD latency: `75.51 ms`
- P95 latency: `166.81 ms`
- P99 latency: `267.98 ms`
- Max latency: `314.19 ms`
- Loss rate: `1%`

Interpretation:

R650 is a valid W3 BLE moderate replicate. The ESP32 emitted the complete 100-event schedule, the BLE logger captured 99 unique advertisements, and the expected experiment code was present on all captured rows. The missed events are recorded as BLE reliability loss for this condition.
