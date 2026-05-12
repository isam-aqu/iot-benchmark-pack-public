## R679 - W3 Zigbee AP-Channel Extension

Run ID: `W3_zigbee_auto_heavy_ch1`

Protocol: `zigbee`

Purpose: AP channel 1 / 20 MHz control heavy-load run paired with baseline `R678`.

Setup:

- Logger host on Ethernet with Wi-Fi disabled
- Zigbee trigger enabled for `light.benchmark_device`
- ACK helper and BLE logger disabled
- AP RF setting recorded as fixed channel `1`, width `20 MHz`, sideband `none`
- iPerf: heavy 50 Mbps TCP

Command:

```bash
EXP_RUN_ID=R679 ./run_all.sh --run-id W3_zigbee_auto_heavy_ch1 --disable-ble --disable-ack --duration-sec 360 --iperf-load heavy --zigbee-trigger --zigbee-entity-id light.benchmark_device --zigbee-events 100 --zigbee-base-interval-ms 3000 --zigbee-jitter-ms 250 --ap-channel-mode fixed --ap-channel 1 --ap-width-mhz 20 --ap-sideband none --ap-rf-source manual_ap_ui
```

Data quality:

- Trigger commands: 100/100, all HTTP 200
- MQTT state rows: 102
- Missing events: 0
- Extra events: 2
- Repeated event-id rows: 2
- iPerf mean throughput: `50.00 Mbps`

Summary metrics:

- Median normalized latency: `0.0 ms`
- MAD latency: `1.5 ms`
- P95 latency: `10.6 ms`
- P99 latency: `13.6 ms`
- Max latency: `16.1 ms`
- Loss rate: `0.0%`
- P95 change vs `R678`: `-0.7 ms` (`-6.3%`)

Analysis:

```bash
python3 python/summarize_w3_run.py experiments/runs/R679/raw --run-id W3_zigbee_auto_heavy_ch1 --expected-events 100
python3 python/analyze_w3_run.py experiments/runs/R679/raw --run-id R679 --run-sheet docs/run_sheet.csv
```

Interpretation:

This is a valid first ch1/20 MHz control heavy-load run. It did not show a tail-latency increase relative to `R678`; the only reliability caveat is two extra/repeated Zigbee state-event rows, matching the earlier W3 Zigbee pattern.

