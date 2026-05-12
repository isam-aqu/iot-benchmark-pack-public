# Run R602 Notes

## Purpose
Measure W3 Wi-Fi automated latency under moderate 2.4 GHz load and compare it
with the quiet R600 baseline.

## Configuration
- Workload: W3
- Protocol: Wi-Fi
- Run type: load
- Comparison group: `W3_wifi_auto`
- Baseline reference: R600
- Topology: near
- Interference: iperf
- Load level: moderate
- iperf profile: `20Mbps_tcp`
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: ESP32 RTT (`rtt_us`)
- Replicate: primary

## Load Quality
- Target throughput: 20 Mbps
- Mean interval throughput: 19.994 Mbps
- Throughput standard deviation: 0.307 Mbps
- Throughput range: 18.90 to 21.10 Mbps

## Data Processing
- Summarized with `python/summarize_w3_run.py`
- Compared with R600 using `python/analyze_w3_run.py`
- Latency source: MQTT RTT rows
- Boot-aware selection retained boot ID `1258333111`
- Power sample CSV is present but header-only; W3 interpretation is based on
  latency and reliability metrics.

## Results
- Expected events: 100
- Actual events: 100
- Event loss: 0%
- RTT samples: 100
- Mean latency: 15.11 ms
- Median latency: 13.67 ms
- P95 latency: 23.34 ms
- P99 latency: 27.99 ms
- Maximum latency: 28.02 ms
- Mean interval: 3014.51 ms
- Interval jitter: 141.01 ms

## Comparison With R600
- Mean latency delta: -13.89 ms
- P95 latency delta: +3.31 ms
- Mean latency increase: -47.89%
- P95 latency increase: 16.51%
- Reliability delta: 0.00
- Impact label: negligible

## Interpretation
Moderate iperf load did not cause event loss. The RTT distribution is tighter
than R600 because this run did not contain the baseline's extreme tail sample.
The P95 is modestly higher than R600, but the mean-based W3 classifier labels
the impact as negligible.

## Validity
Status: complete. Retain as the primary moderate-load W3 Wi-Fi run. Note that
boot-aware filtering removed a short stale boot segment before analysis.
