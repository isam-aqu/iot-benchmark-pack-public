# Run R606 Notes

## Purpose
W3 Wi-Fi automated latency replicate `rep1` under moderate iperf load, compared against baseline `R600`.

## Configuration
- Workload: W3
- Protocol: Wi-Fi
- Run type: load
- Comparison group: `W3_wifi_auto`
- Replicate ID: `rep1`
- Baseline reference: R600
- Topology: near
- Interference: iperf
- Load level: moderate
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: ESP32 RTT (`rtt_us`)
- iperf profile: `20Mbps_tcp`

## Load Quality
- Target throughput: 20 Mbps
- Mean interval throughput: 19.999 Mbps
- Throughput standard deviation: 0.319 Mbps
- Throughput range: 18.90 to 21.10 Mbps

## Data Processing
- Summarized with `python/summarize_w3_run.py`
- Compared with baseline using `python/analyze_w3_run.py`
- Latency source: MQTT RTT rows
- Boot-aware selection retained boot ID `319740107`
- Power sample CSV is present but header-only; W3 interpretation is based on latency and reliability metrics.

## Results
- Expected events: 100
- Actual events: 100
- Missing events: 0
- Event loss: 0%
- RTT samples: 100
- Mean latency: 31.63 ms
- Median latency: 13.97 ms
- P95 latency: 23.09 ms
- P99 latency: 300.17 ms
- Maximum latency: 1409.01 ms
- Mean interval: 3030.14 ms
- Interval jitter: 147.48 ms

## Comparison With R600
- Mean latency delta: 2.63 ms
- P95 latency delta: 3.06 ms
- Drop-rate delta: 0.0000
- Reliability delta: 0.0000
- Impact label: moderate

## Interpretation
Event reliability was complete for the selected boot segment. An extreme RTT tail sample inflates the mean and temporal standard deviation; median and P95 are the more stable summary statistics for this run. Relative to R600, mean RTT delta is 2.63 ms and P95 delta is 3.06 ms.

## Anomalies
- Extreme RTT sample reached 1409.010 ms.
- Boot-aware analysis selected 200 rows from 204 original MQTT rows.

## Validity
Status: complete. Retain as `rep1` in the W3 Wi-Fi `moderate` replicate set.
