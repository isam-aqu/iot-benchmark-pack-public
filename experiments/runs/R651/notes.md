## R651 - W3 BLE Heavy Replicate rep2

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
EXP_RUN_ID=R651 ./run_all.sh --run-id W3_ble_auto_heavy --enable-ble --disable-ack --duration-sec 360 --serial-port /dev/serial-port --serial-baud 115200 --iperf-load heavy --reset-esp32
```

Completion:

```text
EXPERIMENT_COMPLETE,exp=W3_ble_auto,boot_id=975293924,reason=target_event_count,duration_ms=300577,events=100
```

Data quality:

- BLE CSV rows: 97 captured events
- Unique BLE sequences: 97
- Expected BLE advertisements: 100
- Missing sequences: `54`, `58`, `91`
- Duplicate sequences: 0
- Serial advertised sequences: 100/100
- Serial scheduled intervals: `2753` to `3250 ms`, mean approximately `2998.2 ms`
- Scheduler overruns: 0
- Experiment code: `W3BL`
- RSSI range: `-78` to `-71` dBm, mean approximately `-73.0` dBm
- MQTT and power CSVs are header-only, expected for BLE latency capture

iPerf:

- Target: `50 Mbps`
- Mean interval throughput: `50.00 Mbps`
- Interval samples: 369
- Range: `49.10` to `50.70 Mbps`

Analysis:

```bash
python3 python/summarize_w3_run.py \
  experiments/runs/R651/raw \
  --run-id W3_ble_auto_heavy \
  --expected-events 100

python3 python/analyze_w3_run.py \
  experiments/runs/R651/raw \
  --run-id R651 \
  --run-sheet docs/run_sheet.csv
```

Summary metrics:

- Median normalized latency: `0.0 ms`
- MAD latency: `85.51 ms`
- P95 latency: `172.02 ms`
- P99 latency: `302.15 ms`
- Max latency: `322.60 ms`
- Loss rate: `3%`

Interpretation:

R651 is a valid W3 BLE heavy replicate. The ESP32 emitted the complete 100-event schedule, the BLE logger captured 97 unique advertisements, and the expected experiment code was present on all captured rows. The missed events are recorded as BLE reliability loss for this condition.
