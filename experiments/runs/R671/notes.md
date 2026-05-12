## R671 - W3 BLE AP-Channel Extension

Run ID: `W3_ble_auto_heavy`

Protocol: `ble`

Purpose: BLE AP-channel overlap run for AP channel `6` at 20 MHz, targeting BLE advertising channel `38` (2426 MHz) under `heavy` load.

Setup:

- Logger host on Ethernet with Wi-Fi disabled
- BLE logger enabled with expected experiment code `W3BL`
- ACK helper disabled
- AP RF setting: channel `6`, 20 MHz width, manually/planned for this run block
- RF caveat: raw run metadata does not independently encode AP channel/width
- iPerf: 50 Mbps TCP target; mean interval throughput 50.00 Mbps
- ESP32 BLE node reset at run start on `/dev/serial-port`

Command:

```bash
EXP_RUN_ID=R671 ./run_all.sh --run-id W3_ble_auto_heavy --enable-ble --disable-ack --duration-sec 360 --serial-port /dev/serial-port --serial-baud 115200 --iperf-load heavy --reset-esp32
```

Completion:

```text
EXPERIMENT_COMPLETE,exp=W3_ble_auto,boot_id=631098573,reason=target_event_count,duration_ms=299521,events=100
```

Data quality:

- BLE captured events: 99/100
- Missing sequences: `11`
- Duplicate payload rows: 0
- Serial advertised sequences: 100/100
- Experiment code: `W3BL`

Summary metrics:

- Median normalized latency: `0.0 ms`
- MAD latency: `81.8 ms`
- P95 latency: `136.1 ms`
- P99 latency: `150.7 ms`
- Max latency: `165.3 ms`
- Loss rate: `1.0%`

Analysis:

```bash
python3 python/summarize_w3_run.py experiments/runs/R671/raw --run-id W3_ble_auto_heavy --expected-events 100
python3 python/analyze_w3_run.py experiments/runs/R671/raw --run-id R671 --run-sheet docs/run_sheet.csv
```

Interpretation:

This is a valid W3 BLE AP-channel extension run. The ESP32 completed the full schedule; any missing events are BLE logger missed advertisements and are retained as reliability signal for the channel-overlap analysis.
