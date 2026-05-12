# Run R304 Notes

## Purpose
Repeat the BLE W1 near-quiet baseline after identifying a possible ambient BLE confound in the room: a television with a BLE remote control that may have been generating frequent background advertisements.

## Status
Complete.

## Context
This run repeats the BLE button-triggered advertisement experiment using `ble01` under the corrected Ethernet-logger setup, with laptop Wi-Fi disabled as before. The purpose of the rerun was to test whether removing the suspected ambient BLE advertiser would improve baseline BLE behavior.

## Key Characteristics
- Protocol: BLE
- Node ID: ble01
- Trigger: button press
- Topology: near
- Interference: quiet
- Normalization: median_offset
- Total button presses: 100
- Captured events: 97
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
- Logged sequences ranged from 1 to 100
- Missing sequences: 14, 31, and 55
- Captured events: 97 / 100
- No startup miss in this run

## Results

### Full dataset
- Count: 97
- Mean: 8.874 ms
- Median: 0.000 ms
- Min: -136.237 ms
- Max: 346.989 ms
- Std: 107.826 ms
- P95: 167.438 ms

### Core dataset
- Count: 92
- Mean: -7.443 ms
- Median: -2.641 ms
- Min: -136.237 ms
- Max: 142.420 ms
- Std: 83.700 ms
- P95: 123.435 ms

### RSSI
- Mean RSSI: -74.90 dBm

## Observations
- Removing the suspected ambient BLE advertiser did not improve BLE baseline quality
- Compared with R303, this rerun showed more missed events, more filtered outliers, and a worse core P95
- BLE still showed broad spread and event loss under the corrected Ethernet-logger setup
- Mean RSSI was weaker than in R303, so receive conditions were not identical across runs

## Conclusion
This run should be retained as a confound-check rerun documenting control of a possible ambient BLE confound, but it should not replace R303 as the primary BLE baseline.

The results suggest that the previously observed BLE variability is not primarily explained by that specific ambient BLE source. However, because R304 was captured at weaker mean RSSI than R303, the comparison does not fully isolate all physical-layer differences.
