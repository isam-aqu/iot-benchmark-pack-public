# Run R616 Notes

## Purpose
Quiet W3 Wi-Fi automated baseline replicate `rep4` for the `W3_wifi_auto` comparison group.

## Configuration
- Workload: W3
- Protocol: Wi-Fi
- Run type: baseline
- Comparison group: `W3_wifi_auto`
- Replicate ID: `rep4`
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
- Boot-aware selection retained boot ID `1998981849`
- Power sample CSV is present but header-only; W3 interpretation is based on latency and reliability metrics.

## Results
- Expected events: 100
- Actual events: 100
- Missing events: 0
- Event loss: 0%
- RTT samples: 100
- Mean latency: 13.43 ms
- Median latency: 12.97 ms
- P95 latency: 17.98 ms
- P99 latency: 20.06 ms
- Maximum latency: 21.04 ms
- Mean interval: 3001.59 ms
- Interval jitter: 160.69 ms

## Interpretation
Event reliability was complete for the selected boot segment. The RTT distribution is compact, with no extreme tail sample above 500 ms.

## Anomalies
- None recorded.

## Validity
Status: complete. Retain as `rep4` in the W3 Wi-Fi `baseline` replicate set.
