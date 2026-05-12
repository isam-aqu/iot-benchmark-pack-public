# Run R203 Notes

## Purpose
Final Zigbee W1 baseline rerun with 100 samples under the stabilized 0.1.1 pipeline.

## Status
Complete.

## Context
This run repeats the Zigbee W1 near-quiet experiment using the Home Assistant → MQTT forwarding path with the same benchmark device (`light.benchmark_device`) and the same median-normalization method used in earlier Zigbee analysis.

## Key Characteristics
- Protocol: Zigbee
- Node ID: light.benchmark_device
- Trigger: state change
- Topology: near
- Interference: quiet
- Normalization: median_offset
- Total samples: 100
- Core samples: 97

## Processing
- Latency derived from:
  - Home Assistant timestamp (`ha_time`)
  - logger receive time (`pi_rx_time_ns`)
- Offset correction:
  - median normalization
- Core dataset filter:
  - latency in [-200 ms, 200 ms]

## Observations
- Zigbee showed the most stable behavior observed so far
- Only 3 outliers were removed from 100 total samples
- Core mean: 4.65 ms
- Core median: -0.904 ms
- Core P95: 43.355 ms
- Full-dataset spike: 1119.017 ms
- Event IDs were unique for all 100 samples
- State transitions were perfectly balanced:
  - 50 off→on
  - 50 on→off

## Conclusion
This run should be used as the primary Zigbee baseline dataset for cross-protocol comparison.

It demonstrates that Zigbee offers both low latency and strong determinism in the current setup, with rare high-latency events occurring at much lower frequency than in Wi-Fi.
