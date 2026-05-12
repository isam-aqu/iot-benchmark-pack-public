# Run R610 Notes

## Purpose
W3 Wi-Fi automated latency replicate `rep2` under moderate iperf load, compared against baseline `R600`.

## Configuration
- Workload: W3
- Protocol: Wi-Fi
- Run type: load
- Comparison group: `W3_wifi_auto`
- Replicate ID: `rep2`
- Baseline reference: R600
- Topology: near
- Interference: iperf
- Load level: moderate
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: ESP32 RTT (`rtt_us`)
- iperf profile: `20Mbps_tcp`

## Load Quality
- Target throughput: 20 Mbps
- Mean interval throughput: 19.994 Mbps
- Throughput standard deviation: 0.310 Mbps
- Throughput range: 18.90 to 21.10 Mbps

## Data Processing
- Summarized with `python/summarize_w3_run.py`
- Compared with baseline using `python/analyze_w3_run.py`
- Latency source: MQTT RTT rows
- Boot-aware selection retained boot ID `631503868`
- Power sample CSV is present but header-only; W3 interpretation is based on latency and reliability metrics.

## Results
- Expected events: 100
- Actual events: 100
- Missing events: 0
- Event loss: 0%
- RTT samples: 100
- Mean latency: 15.68 ms
- Median latency: 14.16 ms
- P95 latency: 23.96 ms
- P99 latency: 26.03 ms
- Maximum latency: 31.97 ms
- Mean interval: 3029.89 ms
- Interval jitter: 140.06 ms

## Comparison With R600
- Mean latency delta: -13.32 ms
- P95 latency delta: 3.92 ms
- Drop-rate delta: 0.0000
- Reliability delta: 0.0000
- Impact label: negligible

## Interpretation
Event reliability was complete for the selected boot segment. The RTT distribution is compact, with no extreme tail sample above 500 ms. Relative to R600, mean RTT delta is -13.32 ms and P95 delta is 3.92 ms.

## Anomalies
- Boot-aware analysis selected 200 rows from 202 original MQTT rows.

## Validity
Status: complete. Retain as `rep2` in the W3 Wi-Fi `moderate` replicate set.
