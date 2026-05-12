# Run R301 Notes

## Purpose
Final processed BLE W1 latency dataset.

## Status
Complete.

## Context
This run uses the ESP32 BLE beacon node in near-quiet conditions with button-triggered event generation and periodic mode disabled.

## Key Characteristics
- Protocol: BLE
- Node ID: ble01
- Trigger: button press
- Topology: near
- Interference: quiet
- Normalization: median_offset
- Total samples: 50
- Core samples: 49

## Processing
- Latency derived from:
  - device-local timestamp (`t_local_us`)
  - scanner receive time (`pi_rx_time_ns`)
- Offset correction:
  - median normalization
- Filter:
  - latency in (-200 ms, 200 ms)

## Observations
- BLE shows the widest spread and highest jitter among the current W1 protocol datasets.
- It is not reliable for time-critical event detection in the current setup.

## Follow-up
- Add derived BLE latency tables and protocol-specific figures if you want per-run BLE outputs alongside the cross-run CDF.
