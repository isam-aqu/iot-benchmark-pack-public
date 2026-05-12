# Run R600 Notes

## Purpose
Establish the quiet W3 Wi-Fi automated baseline for the `W3_wifi_auto`
comparison group. This run is the reference for the R601-R603 iperf load
experiments.

## Configuration
- Workload: W3
- Protocol: Wi-Fi
- Run type: baseline
- Comparison group: `W3_wifi_auto`
- Topology: near
- Interference: quiet
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: ESP32 RTT (`rtt_us`)
- Replicate: primary

## Data Processing
- Summarized with `python/summarize_w3_run.py`
- W3 deltas generated with `python/analyze_w3_run.py`
- Latency source: MQTT RTT rows
- Power sample CSV is present but header-only; W3 interpretation is based on
  latency and reliability metrics.

## Results
- Expected events: 100
- Actual events: 100
- Event loss: 0%
- RTT samples: 100
- Mean latency: 29.00 ms
- Median latency: 14.01 ms
- P95 latency: 20.03 ms
- P99 latency: 42.41 ms
- Maximum latency: 1455.25 ms
- Mean interval: 2972.26 ms
- Interval jitter: 137.07 ms

## Interpretation
The quiet baseline completed cleanly with full event reliability. Most samples
remain tightly bounded, with a median near 14 ms and P95 near 20 ms. A single
extreme RTT outlier dominates the mean and standard deviation, so percentile
and reliability metrics are more representative of typical behavior.

## Validity
Status: complete. Retain as the primary W3 Wi-Fi baseline for R601-R603.
