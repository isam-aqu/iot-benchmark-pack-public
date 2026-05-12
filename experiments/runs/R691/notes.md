## R691 - W3 Zigbee AP-Channel Extension

Run ID: `W3_zigbee_auto_heavy_ch9`

Protocol: `zigbee`

Purpose: AP channel 9 / 20 MHz overlap heavy-load run paired with baseline `R690`.

Setup:

- Logger host on Ethernet with Wi-Fi disabled
- Zigbee trigger enabled for `light.benchmark_device`
- ACK helper and BLE logger disabled
- AP RF setting recorded as fixed channel `9`, width `20 MHz`, sideband `none`
- iPerf: heavy 50 Mbps TCP

Deviations:

- No deviations from the W3 Zigbee AP-channel extension procedure were recorded. ESP32 completion line is not applicable for Home Assistant-driven Zigbee trigger runs.

Command:

```bash
EXP_RUN_ID=R691 ./run_all.sh --run-id W3_zigbee_auto_heavy_ch9 --iperf-load heavy --disable-ble --disable-ack --duration-sec 360 --zigbee-trigger --zigbee-entity-id light.benchmark_device --zigbee-events 100 --zigbee-base-interval-ms 3000 --zigbee-jitter-ms 250 --ap-channel-mode fixed --ap-channel 9 --ap-width-mhz 20 --ap-sideband none --ap-rf-source manual_ap_ui
```

Data quality:

- Trigger commands: 100/100, all HTTP 200
- MQTT state rows: 100
- Missing events: 0
- Extra events: 0
- Repeated event-id rows: 0
- iPerf mean throughput: `49.99 Mbps`

Summary metrics:

- Median normalized latency: `0.0 ms`
- MAD latency: `1.8 ms`
- P95 latency: `10.3 ms`
- P99 latency: `13.1 ms`
- Max latency: `13.5 ms`
- Loss rate: `0.0%`
- P95 change vs `R690`: `-0.2 ms` (`-1.6%`)

Analysis:

```bash
python3 python/summarize_w3_run.py experiments/runs/R691/raw --run-id W3_zigbee_auto_heavy_ch9 --expected-events 100
python3 python/analyze_w3_run.py experiments/runs/R691/raw --run-id R691 --run-sheet docs/run_sheet.csv
```

Interpretation:

This is a valid AP ch9/20 MHz heavy-load replicate paired with `R690`. The run has complete command/event coverage with no reliability caveats.
