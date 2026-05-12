## R641 - W3 BLE Light Load

Run ID: `W3_ble_auto_light`

Protocol: `ble`

Purpose: W3 BLE automated advertisement run under light Wi-Fi iperf load.

Setup:

- Logger host on Ethernet with Wi-Fi disabled
- BLE logger enabled with expected experiment code `W3BL`
- ACK helper disabled
- iPerf load: `light` / 5 Mbps TCP
- ESP32 BLE node reset at run start on `/dev/serial-port`

Completion:

```text
EXPERIMENT_COMPLETE,exp=W3_ble_auto,boot_id=1575703842,reason=target_event_count,duration_ms=298675,events=100
```

Data quality:

- BLE CSV rows: 98 captured events
- Expected BLE advertisements: 100
- Missing sequences: `5`, `37`
- Duplicate sequences: 0
- Serial advertised sequences: 100/100
- Serial scheduled intervals: `2753` to `3242 ms`, mean approximately `2983.7 ms`
- Scheduler overruns: 0
- Experiment code: `W3BL`
- RSSI range: `-77` to `-71` dBm, mean approximately `-75.1` dBm
- MQTT and power CSVs are header-only, expected for BLE latency capture

iPerf:

- Target: `5 Mbps`
- Mean interval throughput: `5.00 Mbps`
- Interval samples: 369
- Range: `3.74` to `5.30 Mbps`

Summary metrics:

- Median normalized latency: `0.0 ms`
- MAD latency: `83.84 ms`
- P95 latency: `147.99 ms`
- P99 latency: `274.67 ms`
- Max latency: `337.66 ms`
- Loss rate: `2%`

Interpretation:

R641 is a valid W3 BLE light-load run. It completed the device schedule and held the intended iperf profile. BLE still missed advertisements, but fewer than the R640 quiet baseline in this single run.
