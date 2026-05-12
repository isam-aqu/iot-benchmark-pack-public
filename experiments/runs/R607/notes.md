# Run R607 Notes

## Purpose
W3 Wi-Fi automated latency replicate `rep1` under heavy iperf load, compared against baseline `R600`.

## Configuration
- Workload: W3
- Protocol: Wi-Fi
- Run type: load
- Comparison group: `W3_wifi_auto`
- Replicate ID: `rep1`
- Baseline reference: R600
- Topology: near
- Interference: iperf
- Load level: heavy
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: ESP32 RTT (`rtt_us`)
- iperf profile: `50Mbps_tcp`

## Load Quality
- Target throughput: 50 Mbps
- Mean interval throughput: 49.999 Mbps
- Throughput standard deviation: 0.479 Mbps
- Throughput range: 48.90 to 51.00 Mbps

## Data Processing
- Summarized with `python/summarize_w3_run.py`
- Compared with baseline using `python/analyze_w3_run.py`
- Latency source: MQTT RTT rows
- Boot-aware selection retained boot ID `1211311573`
- Power sample CSV is present but header-only; W3 interpretation is based on latency and reliability metrics.

## Results
- Expected events: 100
- Actual events: 100
- Missing events: 0
- Event loss: 0%
- RTT samples: 100
- Mean latency: 16.68 ms
- Median latency: 15.97 ms
- P95 latency: 23.94 ms
- P99 latency: 32.26 ms
- Maximum latency: 32.98 ms
- Mean interval: 3025.07 ms
- Interval jitter: 153.32 ms

## Comparison With R600
- Mean latency delta: -12.32 ms
- P95 latency delta: 3.90 ms
- Drop-rate delta: 0.0000
- Reliability delta: 0.0000
- Impact label: negligible

## Interpretation
Event reliability was complete for the selected boot segment. The RTT distribution is compact, with no extreme tail sample above 500 ms. Relative to R600, mean RTT delta is -12.32 ms and P95 delta is 3.90 ms.

## Anomalies
- Boot-aware analysis selected 200 rows from 204 original MQTT rows.

## Validity
Status: complete. Retain as `rep1` in the W3 Wi-Fi `heavy` replicate set.
