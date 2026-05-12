# Run R202 Notes

## Purpose
Final processed Zigbee W1 latency dataset.

## Status
Complete.

## Context
This run captures the near-quiet Zigbee path using Home Assistant state change triggering and processed latency estimation.

## Key Characteristics
- Protocol: Zigbee
- Device: light.benchmark_device
- Trigger: Home Assistant state change
- Topology: near
- Interference: quiet
- Normalization: median_offset
- Total samples: 63
- Core samples: 62

## Processing
- Latency derived from:
  - Home Assistant event timestamp (`ha_time`)
  - receive timestamp (`pi_rx_time_ns`)
- Offset correction:
  - median normalization
- Filter:
  - latency in (-200 ms, 200 ms)

## Observations
- Lowest average latency among the current protocols in the near-quiet W1 dataset.
- Moderate jitter still exists.
- This dataset is the processed/final Zigbee representation in the current repo state.

## Follow-up
- Add figures if you generate Zigbee-specific plots for the final dataset.
