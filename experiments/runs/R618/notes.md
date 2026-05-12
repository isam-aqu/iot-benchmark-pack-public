# Run R618 Notes

## Purpose
W3 Wi-Fi automated latency replicate `rep4` under moderate iperf load, compared against baseline `R600`.

## Configuration
- Workload: W3
- Protocol: Wi-Fi
- Run type: load
- Comparison group: `W3_wifi_auto`
- Replicate ID: `rep4`
- Baseline reference: R600
- Topology: near
- Interference: iperf
- Load level: moderate
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: ESP32 RTT (`rtt_us`)
- iperf profile: `20Mbps_tcp`

## Load Quality
- Target throughput: 20 Mbps
- Mean interval throughput: 19.995 Mbps
- Throughput standard deviation: 0.346 Mbps
- Throughput range: 18.80 to 21.20 Mbps

## Data Processing
- Summarized with `python/summarize_w3_run.py`
- Compared with baseline using `python/analyze_w3_run.py`
- Latency source: MQTT RTT rows
- Boot-aware selection retained boot ID `346572485`
- Power sample CSV is present but header-only; W3 interpretation is based on latency and reliability metrics.

## Results
- Expected events: 100
- Actual events: 100
- Missing events: 0
- Event loss: 0%
- RTT samples: 100
- Mean latency: 40.79 ms
- Median latency: 13.99 ms
- P95 latency: 26.13 ms
- P99 latency: 1263.44 ms
- Maximum latency: 1310.26 ms
- Mean interval: 2978.36 ms
- Interval jitter: 140.64 ms

## Comparison With R600
- Mean latency delta: 11.79 ms
- P95 latency delta: 6.10 ms
- Drop-rate delta: 0.0000
- Reliability delta: 0.0000
- Impact label: high

## Interpretation
Event reliability was complete for the selected boot segment. An extreme RTT tail sample inflates the mean and temporal standard deviation; median and P95 are the more stable summary statistics for this run. Relative to R600, mean RTT delta is 11.79 ms and P95 delta is 6.10 ms.

## Anomalies
- Extreme RTT sample reached 1310.258 ms.
- Boot-aware analysis selected 200 rows from 204 original MQTT rows.

## Validity
Status: complete. Retain as `rep4` in the W3 Wi-Fi `moderate` replicate set.
