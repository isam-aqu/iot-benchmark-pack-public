## R642 - W3 BLE Moderate Load

Run ID: `W3_ble_auto_moderate`

Protocol: `ble`

Purpose: W3 BLE automated advertisement run under moderate Wi-Fi iperf load.

Setup:

- Logger host on Ethernet with Wi-Fi disabled
- BLE logger enabled with expected experiment code `W3BL`
- ACK helper disabled
- iPerf load: `moderate` / 20 Mbps TCP
- ESP32 BLE node reset at run start on `/dev/serial-port`

Completion:

```text
EXPERIMENT_COMPLETE,exp=W3_ble_auto,boot_id=1746242066,reason=target_event_count,duration_ms=302588,events=100
```

Data quality:

- BLE CSV rows: 97 captured events
- Expected BLE advertisements: 100
- Missing sequences: `12`, `16`, `85`
- Duplicate sequences: 0
- Serial advertised sequences: 100/100
- Serial scheduled intervals: `2758` to `3250 ms`, mean approximately `3018.7 ms`
- Scheduler overruns: 0
- Experiment code: `W3BL`
- RSSI range: `-77` to `-74` dBm, mean approximately `-75.6` dBm
- MQTT and power CSVs are header-only, expected for BLE latency capture

iPerf:

- Target: `20 Mbps`
- Mean interval throughput: `20.00 Mbps`
- Interval samples: 369
- Range: `18.9` to `21.0 Mbps`

Summary metrics:

- Median normalized latency: `0.0 ms`
- MAD latency: `64.67 ms`
- P95 latency: `108.55 ms`
- P99 latency: `236.90 ms`
- Max latency: `264.37 ms`
- Loss rate: `3%`

Interpretation:

R642 is a valid W3 BLE moderate-load run. It completed the device schedule and held the intended iperf profile. BLE missed three advertisements, which should be retained as the run's reliability signal.
