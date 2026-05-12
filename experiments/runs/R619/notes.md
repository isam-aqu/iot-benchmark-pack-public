# Run R619 Notes

## Purpose
W3 Wi-Fi automated latency replicate `rep4` under heavy iperf load, compared against baseline `R600`.

## Configuration
- Workload: W3
- Protocol: Wi-Fi
- Run type: load
- Comparison group: `W3_wifi_auto`
- Replicate ID: `rep4`
- Baseline reference: R600
- Topology: near
- Interference: iperf
- Load level: heavy
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: ESP32 RTT (`rtt_us`)
- iperf profile: `50Mbps_tcp`

## Load Quality
- Target throughput: 50 Mbps
- Mean interval throughput: 50.002 Mbps
- Throughput standard deviation: 0.462 Mbps
- Throughput range: 49.10 to 50.70 Mbps

## Data Processing
- Summarized with `python/summarize_w3_run.py`
- Compared with baseline using `python/analyze_w3_run.py`
- Latency source: MQTT RTT rows
- Boot-aware selection retained boot ID `2000637883`
- Power sample CSV is present but header-only; W3 interpretation is based on latency and reliability metrics.

## Results
- Expected events: 100
- Actual events: 100
- Missing events: 0
- Event loss: 0%
- RTT samples: 100
- Mean latency: 21.76 ms
- Median latency: 14.99 ms
- P95 latency: 24.17 ms
- P99 latency: 39.65 ms
- Maximum latency: 598.92 ms
- Mean interval: 2982.33 ms
- Interval jitter: 132.82 ms

## Comparison With R600
- Mean latency delta: -7.25 ms
- P95 latency delta: 4.14 ms
- Drop-rate delta: 0.0000
- Reliability delta: 0.0000
- Impact label: negligible

## Interpretation
Event reliability was complete for the selected boot segment. An extreme RTT tail sample inflates the mean and temporal standard deviation; median and P95 are the more stable summary statistics for this run. Relative to R600, mean RTT delta is -7.25 ms and P95 delta is 4.14 ms.

## Anomalies
- Extreme RTT sample reached 598.921 ms.
- Boot-aware analysis selected 200 rows from 204 original MQTT rows.

## Validity
Status: complete. Retain as `rep4` in the W3 Wi-Fi `heavy` replicate set.
