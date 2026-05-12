# Run R613 Notes

## Purpose
W3 Wi-Fi automated latency replicate `rep3` under light iperf load, compared against baseline `R600`.

## Configuration
- Workload: W3
- Protocol: Wi-Fi
- Run type: load
- Comparison group: `W3_wifi_auto`
- Replicate ID: `rep3`
- Baseline reference: R600
- Topology: near
- Interference: iperf
- Load level: light
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: ESP32 RTT (`rtt_us`)
- iperf profile: `5Mbps_tcp`

## Load Quality
- Target throughput: 5 Mbps
- Mean interval throughput: 5.000 Mbps
- Throughput standard deviation: 0.444 Mbps
- Throughput range: 4.15 to 5.29 Mbps

## Data Processing
- Summarized with `python/summarize_w3_run.py`
- Compared with baseline using `python/analyze_w3_run.py`
- Latency source: MQTT RTT rows
- Boot-aware selection retained boot ID `1808720066`
- Power sample CSV is present but header-only; W3 interpretation is based on latency and reliability metrics.

## Results
- Expected events: 100
- Actual events: 100
- Missing events: 0
- Event loss: 0%
- RTT samples: 100
- Mean latency: 29.50 ms
- Median latency: 13.26 ms
- P95 latency: 21.05 ms
- P99 latency: 195.87 ms
- Maximum latency: 1370.94 ms
- Mean interval: 2987.30 ms
- Interval jitter: 147.56 ms

## Comparison With R600
- Mean latency delta: 0.50 ms
- P95 latency delta: 1.01 ms
- Drop-rate delta: 0.0000
- Reliability delta: 0.0000
- Impact label: negligible

## Interpretation
Event reliability was complete for the selected boot segment. An extreme RTT tail sample inflates the mean and temporal standard deviation; median and P95 are the more stable summary statistics for this run. Relative to R600, mean RTT delta is 0.50 ms and P95 delta is 1.01 ms.

## Anomalies
- Extreme RTT sample reached 1370.937 ms.
- Boot-aware analysis selected 200 rows from 204 original MQTT rows.

## Validity
Status: complete. Retain as `rep3` in the W3 Wi-Fi `light` replicate set.
