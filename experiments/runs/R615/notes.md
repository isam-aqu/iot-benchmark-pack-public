# Run R615 Notes

## Purpose
W3 Wi-Fi automated latency replicate `rep3` under heavy iperf load, compared against baseline `R600`.

## Configuration
- Workload: W3
- Protocol: Wi-Fi
- Run type: load
- Comparison group: `W3_wifi_auto`
- Replicate ID: `rep3`
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
- Throughput standard deviation: 0.477 Mbps
- Throughput range: 49.00 to 51.10 Mbps

## Data Processing
- Summarized with `python/summarize_w3_run.py`
- Compared with baseline using `python/analyze_w3_run.py`
- Latency source: MQTT RTT rows
- Boot-aware selection retained boot ID `1366518800`
- Power sample CSV is present but header-only; W3 interpretation is based on latency and reliability metrics.

## Results
- Expected events: 100
- Actual events: 100
- Missing events: 0
- Event loss: 0%
- RTT samples: 100
- Mean latency: 16.73 ms
- Median latency: 15.93 ms
- P95 latency: 23.93 ms
- P99 latency: 30.10 ms
- Maximum latency: 40.92 ms
- Mean interval: 3008.48 ms
- Interval jitter: 147.84 ms

## Comparison With R600
- Mean latency delta: -12.27 ms
- P95 latency delta: 3.89 ms
- Drop-rate delta: 0.0000
- Reliability delta: 0.0000
- Impact label: negligible

## Interpretation
Event reliability was complete for the selected boot segment. The RTT distribution is compact, with no extreme tail sample above 500 ms. Relative to R600, mean RTT delta is -12.27 ms and P95 delta is 3.89 ms.

## Anomalies
- Boot-aware analysis selected 200 rows from 202 original MQTT rows.

## Validity
Status: complete. Retain as `rep3` in the W3 Wi-Fi `heavy` replicate set.
