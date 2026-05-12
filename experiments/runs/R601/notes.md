# Run R601 Notes

## Purpose
Measure W3 Wi-Fi automated latency under light 2.4 GHz load and compare it with
the quiet R600 baseline.

## Configuration
- Workload: W3
- Protocol: Wi-Fi
- Run type: load
- Comparison group: `W3_wifi_auto`
- Baseline reference: R600
- Topology: near
- Interference: iperf
- Load level: light
- iperf profile: `5Mbps_tcp`
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: ESP32 RTT (`rtt_us`)
- Replicate: primary

## Load Quality
- Target throughput: 5 Mbps
- Mean interval throughput: 4.999 Mbps
- Throughput standard deviation: 0.443 Mbps
- Throughput range: 4.17 to 5.27 Mbps

## Data Processing
- Summarized with `python/summarize_w3_run.py`
- Compared with R600 using `python/analyze_w3_run.py`
- Latency source: MQTT RTT rows
- Power sample CSV is present but header-only; W3 interpretation is based on
  latency and reliability metrics.

## Results
- Expected events: 100
- Actual events: 100
- Event loss: 0%
- RTT samples: 100
- Mean latency: 30.01 ms
- Median latency: 14.00 ms
- P95 latency: 23.10 ms
- P99 latency: 55.55 ms
- Maximum latency: 1478.98 ms
- Mean interval: 3000.14 ms
- Interval jitter: 144.33 ms

## Comparison With R600
- Mean latency delta: +1.01 ms
- P95 latency delta: +3.06 ms
- Mean latency increase: 3.47%
- P95 latency increase: 15.28%
- Reliability delta: 0.00
- Impact label: negligible

## Interpretation
Light iperf load did not cause event loss and only modestly increased latency
relative to R600. As with the baseline, a single extreme RTT sample inflates
the mean and standard deviation; the median and P95 remain in the low tens of
milliseconds.

## Validity
Status: complete. Retain as the primary light-load W3 Wi-Fi run.
