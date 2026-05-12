# Run R603 Notes

## Purpose
Measure W3 Wi-Fi automated latency under heavy 2.4 GHz load and compare it with
the quiet R600 baseline.

## Configuration
- Workload: W3
- Protocol: Wi-Fi
- Run type: load
- Comparison group: `W3_wifi_auto`
- Baseline reference: R600
- Topology: near
- Interference: iperf
- Load level: heavy
- iperf profile: `50Mbps_tcp`
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: ESP32 RTT (`rtt_us`)
- Replicate: primary

## Load Quality
- Target throughput: 50 Mbps
- Mean interval throughput: 49.999 Mbps
- Throughput standard deviation: 0.488 Mbps
- Throughput range: 49.00 to 51.20 Mbps

## Data Processing
- Summarized with `python/summarize_w3_run.py`
- Compared with R600 using `python/analyze_w3_run.py`
- Latency source: MQTT RTT rows
- Boot-aware selection retained boot ID `779575726`
- Power sample CSV is present but header-only; W3 interpretation is based on
  latency and reliability metrics.

## Results
- Expected events: 100
- Actual events: 93
- Missing events: 7
- Event loss: 7%
- RTT samples: 88
- Mean latency: 42.55 ms
- Median latency: 16.91 ms
- P95 latency: 24.97 ms
- P99 latency: 937.22 ms
- Maximum latency: 1395.92 ms
- Mean interval: 3245.56 ms
- Interval jitter: 2195.03 ms

## Comparison With R600
- Mean latency delta: +13.55 ms
- P95 latency delta: +4.93 ms
- Mean latency increase: 46.71%
- P95 latency increase: 24.63%
- Drop-rate delta: +0.07
- Reliability delta: -0.07
- Impact label: high

## Interpretation
Heavy iperf load produced the first clear W3 Wi-Fi robustness degradation in
this primary sequence. The run shows both reliability loss and timing
instability: seven events were missing, only 88 RTT samples were available, and
event intervals became highly irregular. Although the median latency remains in
the same general range as lighter runs, the tail and reliability metrics show
substantial degradation.

## Validity
Status: complete. Retain as the primary heavy-load W3 Wi-Fi run and treat it
as the clearest degradation point among R600-R603.
