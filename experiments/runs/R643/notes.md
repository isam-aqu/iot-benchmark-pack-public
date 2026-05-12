## R643 - W3 BLE Heavy Load

Run ID: `W3_ble_auto_heavy`

Protocol: `ble`

Purpose: W3 BLE automated advertisement run under heavy Wi-Fi iperf load.

Setup:

- Logger host on Ethernet with Wi-Fi disabled
- BLE logger enabled with expected experiment code `W3BL`
- ACK helper disabled
- iPerf load: `heavy` / 50 Mbps TCP
- ESP32 BLE node reset at run start on `/dev/serial-port`

Completion:

```text
EXPERIMENT_COMPLETE,exp=W3_ble_auto,boot_id=912516799,reason=target_event_count,duration_ms=301708,events=100
```

Data quality:

- BLE CSV rows: 99 captured events
- Expected BLE advertisements: 100
- Missing sequences: `84`
- Duplicate sequences: 0
- Serial advertised sequences: 100/100
- Serial scheduled intervals: `2756` to `3248 ms`, mean approximately `3013.9 ms`
- Scheduler overruns: 0
- Experiment code: `W3BL`
- RSSI range: `-77` to `-73` dBm, mean approximately `-74.8` dBm
- MQTT and power CSVs are header-only, expected for BLE latency capture

iPerf:

- Target: `50 Mbps`
- Mean interval throughput: `49.99 Mbps`
- Interval samples: 369
- Range: `48.9` to `51.3 Mbps`

Summary metrics:

- Median normalized latency: `0.0 ms`
- MAD latency: `89.31 ms`
- P95 latency: `142.72 ms`
- P99 latency: `184.00 ms`
- Max latency: `303.52 ms`
- Loss rate: `1%`

Interpretation:

R643 is a valid W3 BLE heavy-load run. It completed the device schedule and held the intended iperf profile. BLE missed one advertisement, which is lower loss than the R640 baseline in this single primary run.
