# Run R605 Notes

## Purpose
W3 Wi-Fi automated latency replicate `rep1` under light iperf load, compared against baseline `R600`.

## Configuration
- Workload: W3
- Protocol: Wi-Fi
- Run type: load
- Comparison group: `W3_wifi_auto`
- Replicate ID: `rep1`
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
- Throughput standard deviation: 0.447 Mbps
- Throughput range: 4.18 to 6.20 Mbps

## Data Processing
- Summarized with `python/summarize_w3_run.py`
- Compared with baseline using `python/analyze_w3_run.py`
- Latency source: MQTT RTT rows
- Boot-aware selection retained boot ID `1231879173`
- Power sample CSV is present but header-only; W3 interpretation is based on latency and reliability metrics.

## Results
- Expected events: 100
- Actual events: 100
- Missing events: 0
- Event loss: 0%
- RTT samples: 100
- Mean latency: 14.36 ms
- Median latency: 13.01 ms
- P95 latency: 21.07 ms
- P99 latency: 23.96 ms
- Maximum latency: 25.99 ms
- Mean interval: 3004.03 ms
- Interval jitter: 149.53 ms

## Comparison With R600
- Mean latency delta: -14.64 ms
- P95 latency delta: 1.04 ms
- Drop-rate delta: 0.0000
- Reliability delta: 0.0000
- Impact label: negligible

## Interpretation
Event reliability was complete for the selected boot segment. The RTT distribution is compact, with no extreme tail sample above 500 ms. Relative to R600, mean RTT delta is -14.64 ms and P95 delta is 1.04 ms.

## Anomalies
- None recorded.

## Validity
Status: complete. Retain as `rep1` in the W3 Wi-Fi `light` replicate set.
