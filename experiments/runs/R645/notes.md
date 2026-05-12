## R645 - W3 BLE Light Replicate rep1

Run ID: `W3_ble_auto_light`

Protocol: `ble`

Purpose: W3 BLE automated advertisement run for the light condition.

Setup:

- Logger host on Ethernet with Wi-Fi disabled
- BLE logger enabled with expected experiment code `W3BL`
- ACK helper disabled
- iPerf load: `light` / 5 Mbps TCP
- ESP32 BLE node reset at run start on `/dev/serial-port`

Command:

```bash
EXP_RUN_ID=R645 ./run_all.sh --run-id W3_ble_auto_light --enable-ble --disable-ack --duration-sec 360 --serial-port /dev/serial-port --serial-baud 115200 --iperf-load light --reset-esp32
```

Completion:

```text
EXPERIMENT_COMPLETE,exp=W3_ble_auto,boot_id=895166840,reason=target_event_count,duration_ms=302541,events=100
```

Data quality:

- BLE CSV rows: 99 captured events
- Unique BLE sequences: 99
- Expected BLE advertisements: 100
- Missing sequences: `54`
- Duplicate sequences: 0
- Serial advertised sequences: 100/100
- Serial scheduled intervals: `2758` to `3250 ms`, mean approximately `3022.3 ms`
- Scheduler overruns: 0
- Experiment code: `W3BL`
- RSSI range: `-64` to `-42` dBm, mean approximately `-47.4` dBm
- MQTT and power CSVs are header-only, expected for BLE latency capture

iPerf:

- Target: `5 Mbps`
- Mean interval throughput: `5.00 Mbps`
- Interval samples: 369
- Range: `4.15` to `6.08 Mbps`

Analysis:

```bash
python3 python/summarize_w3_run.py \
  experiments/runs/R645/raw \
  --run-id W3_ble_auto_light \
  --expected-events 100

python3 python/analyze_w3_run.py \
  experiments/runs/R645/raw \
  --run-id R645 \
  --run-sheet docs/run_sheet.csv
```

Summary metrics:

- Median normalized latency: `0.0 ms`
- MAD latency: `85.94 ms`
- P95 latency: `174.19 ms`
- P99 latency: `321.80 ms`
- Max latency: `360.37 ms`
- Loss rate: `1%`

Interpretation:

R645 is a valid W3 BLE light replicate. The ESP32 emitted the complete 100-event schedule, the BLE logger captured 99 unique advertisements, and the expected experiment code was present on all captured rows. The missed events are recorded as BLE reliability loss for this condition.
