# Run R604 Notes

## Purpose
Quiet W3 Wi-Fi automated baseline replicate `rep1` for the `W3_wifi_auto` comparison group.

## Configuration
- Workload: W3
- Protocol: Wi-Fi
- Run type: baseline
- Comparison group: `W3_wifi_auto`
- Replicate ID: `rep1`
- Baseline reference: none
- Topology: near
- Interference: quiet
- Load level: baseline
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: ESP32 RTT (`rtt_us`)

## Data Processing
- Summarized with `python/summarize_w3_run.py`
- Compared with baseline using `python/analyze_w3_run.py`
- Latency source: MQTT RTT rows
- Boot-aware selection retained boot ID `1009542261`
- Power sample CSV is present but header-only; W3 interpretation is based on latency and reliability metrics.

## Results
- Expected events: 100
- Actual events: 100
- Missing events: 0
- Event loss: 0%
- RTT samples: 100
- Mean latency: 14.60 ms
- Median latency: 13.04 ms
- P95 latency: 22.99 ms
- P99 latency: 30.13 ms
- Maximum latency: 36.99 ms
- Mean interval: 3011.75 ms
- Interval jitter: 148.31 ms

## Interpretation
Event reliability was complete for the selected boot segment. The RTT distribution is compact, with no extreme tail sample above 500 ms.

## Anomalies
- None recorded.

## Validity
Status: complete. Retain as `rep1` in the W3 Wi-Fi `baseline` replicate set.
