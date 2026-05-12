## R659 - W3 BLE Heavy Replicate rep4

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
EXP_RUN_ID=R659 ./run_all.sh --run-id W3_ble_auto_heavy --enable-ble --disable-ack --duration-sec 360 --serial-port /dev/serial-port --serial-baud 115200 --iperf-load heavy --reset-esp32
```

Completion:

```text
EXPERIMENT_COMPLETE,exp=W3_ble_auto,boot_id=1726669321,reason=target_event_count,duration_ms=300411,events=100
```

Data quality:

- BLE CSV rows: 98 captured events
- Unique BLE sequences: 98
- Expected BLE advertisements: 100
- Missing sequences: `15`, `32`
- Duplicate sequences: 0
- Serial advertised sequences: 100/100
- Serial scheduled intervals: `2763` to `3249 ms`, mean approximately `2997.1 ms`
- Scheduler overruns: 0
- Experiment code: `W3BL`
- RSSI range: `-75` to `-70` dBm, mean approximately `-72.1` dBm
- MQTT and power CSVs are header-only, expected for BLE latency capture

iPerf:

- Target: `50 Mbps`
- Mean interval throughput: `50.00 Mbps`
- Interval samples: 369
- Range: `48.70` to `51.40 Mbps`

Analysis:

```bash
python3 python/summarize_w3_run.py \
  experiments/runs/R659/raw \
  --run-id W3_ble_auto_heavy \
  --expected-events 100

python3 python/analyze_w3_run.py \
  experiments/runs/R659/raw \
  --run-id R659 \
  --run-sheet docs/run_sheet.csv
```

Summary metrics:

- Median normalized latency: `0.0 ms`
- MAD latency: `87.37 ms`
- P95 latency: `139.82 ms`
- P99 latency: `269.36 ms`
- Max latency: `319.84 ms`
- Loss rate: `2%`

Interpretation:

R659 is a valid W3 BLE heavy replicate. The ESP32 emitted the complete 100-event schedule, the BLE logger captured 98 unique advertisements, and the expected experiment code was present on all captured rows. The missed events are recorded as BLE reliability loss for this condition.
