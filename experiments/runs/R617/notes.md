# Run R617 Notes

## Purpose
W3 Wi-Fi automated latency replicate `rep4` under light iperf load, compared against baseline `R600`.

## Configuration
- Workload: W3
- Protocol: Wi-Fi
- Run type: load
- Comparison group: `W3_wifi_auto`
- Replicate ID: `rep4`
- Baseline reference: R600
- Topology: near
- Interference: iperf
- Load level: light
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: ESP32 RTT (`rtt_us`)
- iperf profile: `5Mbps_tcp`

## Load Quality
- Target throughput: 5 Mbps
- Mean interval throughput: 5.003 Mbps
- Throughput standard deviation: 0.446 Mbps
- Throughput range: 4.16 to 6.17 Mbps

## Data Processing
- Summarized with `python/summarize_w3_run.py`
- Compared with baseline using `python/analyze_w3_run.py`
- Latency source: MQTT RTT rows
- Boot-aware selection retained boot ID `1766900655`
- Power sample CSV is present but header-only; W3 interpretation is based on latency and reliability metrics.

## Results
- Expected events: 100
- Actual events: 100
- Missing events: 0
- Event loss: 0%
- RTT samples: 99
- Mean latency: 38.52 ms
- Median latency: 12.97 ms
- P95 latency: 26.03 ms
- P99 latency: 666.29 ms
- Maximum latency: 1719.96 ms
- Mean interval: 3000.85 ms
- Interval jitter: 142.25 ms

## Comparison With R600
- Mean latency delta: 9.52 ms
- P95 latency delta: 6.00 ms
- Drop-rate delta: 0.0000
- Reliability delta: 0.0000
- Impact label: high

## Interpretation
Event reliability was complete for the selected boot segment. An extreme RTT tail sample inflates the mean and temporal standard deviation; median and P95 are the more stable summary statistics for this run. Relative to R600, mean RTT delta is 9.52 ms and P95 delta is 6.00 ms.

## Anomalies
- Latency sample count (99) differs from actual event count (100).
- Extreme RTT sample reached 1719.957 ms.
- Boot-aware analysis selected 199 rows from 203 original MQTT rows.

## Validity
Status: complete. Retain as `rep4` in the W3 Wi-Fi `light` replicate set.
