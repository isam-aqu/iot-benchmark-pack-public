## R663 - W3 BLE AP-Channel Extension

Run ID: `W3_ble_auto_heavy`

Protocol: `ble`

Purpose: BLE AP-channel overlap run for AP channel `1` at 20 MHz, targeting BLE advertising channel `37` (2402 MHz) under `heavy` load.

Setup:

- Logger host on Ethernet with Wi-Fi disabled
- BLE logger enabled with expected experiment code `W3BL`
- ACK helper disabled
- AP RF setting: channel `1`, 20 MHz width, manually/planned for this run block
- RF caveat: raw run metadata does not independently encode AP channel/width
- iPerf: 50 Mbps TCP target; mean interval throughput 50.00 Mbps
- ESP32 BLE node reset at run start on `/dev/serial-port`

Command:

```bash
EXP_RUN_ID=R663 ./run_all.sh --run-id W3_ble_auto_heavy --enable-ble --disable-ack --duration-sec 360 --serial-port /dev/serial-port --serial-baud 115200 --iperf-load heavy --reset-esp32
```

Completion:

```text
EXPERIMENT_COMPLETE,exp=W3_ble_auto,boot_id=1393687854,reason=target_event_count,duration_ms=301364,events=100
```

Data quality:

- BLE captured events: 98/100
- Missing sequences: `22, 26`
- Duplicate payload rows: 0
- Serial advertised sequences: 100/100
- Experiment code: `W3BL`

Summary metrics:

- Median normalized latency: `-0.0 ms`
- MAD latency: `82.7 ms`
- P95 latency: `126.0 ms`
- P99 latency: `134.2 ms`
- Max latency: `139.7 ms`
- Loss rate: `2.0%`

Analysis:

```bash
python3 python/summarize_w3_run.py experiments/runs/R663/raw --run-id W3_ble_auto_heavy --expected-events 100
python3 python/analyze_w3_run.py experiments/runs/R663/raw --run-id R663 --run-sheet docs/run_sheet.csv
```

Interpretation:

This is a valid W3 BLE AP-channel extension run. The ESP32 completed the full schedule; any missing events are BLE logger missed advertisements and are retained as reliability signal for the channel-overlap analysis.
