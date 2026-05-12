# Run R302 Notes

## Purpose
Final BLE W1 baseline rerun with approximately 100 captured points under the stabilized 0.1.1 pipeline.

## Status
Complete.

## Context
This run repeats the BLE W1 near-quiet experiment using the ESP32 beacon node (`ble01`) and button-triggered event generation. It is intended to provide a balanced dataset for comparison with Wi-Fi and Zigbee.

## Key Characteristics
- Protocol: BLE
- Node ID: ble01
- Trigger: button press
- Topology: near
- Interference: quiet
- Normalization: median_offset
- Total triggers: 101
- Captured samples: 99
- Core samples: 92

## Processing
- Latency derived from:
  - device-local timestamp (`t_local_us`)
  - scanner receive time (`pi_rx_time_ns`)
- Offset correction:
  - median normalization
- Core dataset filter:
  - latency in [-200 ms, 200 ms]

## Capture Integrity
- Logged sequences ranged from 2 to 101
- Sequence 1 was missed at startup and is excluded from interpretation
- One additional sequence (83) was missing during the run
- Effective capture count: 99 / 101 triggers

## Results
### Full dataset
- Count: 99
- Mean: 28.982 ms
- Median: 0.000 ms
- Min: -98.466 ms
- Max: 321.209 ms
- Std: 115.271 ms
- P95: 266.919 ms

### Core dataset
- Count: 92
- Mean: 9.745 ms
- Median: -4.389 ms
- Min: -98.466 ms
- Max: 183.295 ms
- Std: 94.548 ms
- P95: 164.259 ms

### RSSI
- Mean RSSI: -54.60 dBm

## Observations
- BLE remains the least deterministic of the three protocols
- Latency spread is much wider than Zigbee and Wi-Fi
- Tail behavior is substantial even after median normalization
- In addition to latency variability, the BLE path also showed occasional event loss

## Quantized BLE Detection Behavior

Post-run analysis of the core BLE latency dataset revealed seven distinct latency clusters. The spacing between cluster centers was approximately:

- mean: 44.5 ms
- median: 45.4 ms
- min: 40.6 ms
- max: 48.4 ms

This indicates that BLE latency in the current setup is not smoothly distributed. Instead, event detection occurs in discrete timing bands, most likely due to the asynchronous interaction between BLE advertisement timing and scanner listen windows.

This explains the plateau-and-jump pattern seen in the BLE CDF and the multi-peak structure seen in the BLE histogram.

## Conclusion
This run should be used as the primary BLE baseline dataset for cross-protocol comparison.

It confirms that BLE advertisement-based detection in the current setup is:
- high-jitter
- occasionally lossy
- quantized in time due to scan/advertisement timing interaction

This makes BLE less suitable for time-critical event detection than Zigbee or Wi-Fi in the present testbed.
