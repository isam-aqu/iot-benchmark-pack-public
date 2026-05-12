# Run R303 Notes

## Purpose
Repeat the BLE W1 near-quiet baseline with the logger moved to Ethernet and laptop Wi-Fi disabled, in order to isolate measurement-induced RF contention.

## Status
Complete.

## Context
This run repeats the BLE button-triggered advertisement experiment using `ble01` under the same near-quiet physical conditions as earlier BLE baselines, but with the measurement node removed from the Wi-Fi medium.

## Key Characteristics
- Protocol: BLE
- Node ID: ble01
- Trigger: button press
- Topology: near
- Interference: quiet
- Normalization: median_offset
- Total button presses: 101
- Captured events: 99
- Core samples: 98

## Processing
- Latency derived from:
  - device-local timestamp (`t_local_us`)
  - scanner receive time (`pi_rx_time_ns`)
- Offset correction:
  - median normalization
- Core dataset filter:
  - latency in [-200 ms, 200 ms]

## Capture Integrity
- Logged sequences ranged from 1 to 101
- Missing sequences: 69 and 100
- Captured events: 99 / 101
- No startup miss in this run

## Results

### Full dataset
- Count: 99
- Mean: -8.756 ms
- Median: 0.000 ms
- Min: -141.065 ms
- Max: 271.474 ms
- Std: 90.053 ms
- P95: 96.096 ms

### Core dataset
- Count: 98
- Mean: -11.616 ms
- Median: -0.347 ms
- Min: -141.065 ms
- Max: 186.116 ms
- Std: 85.879 ms
- P95: 94.868 ms

### RSSI
- Mean RSSI: -66.73 dBm

## Observations
- BLE improved compared with the earlier Wi-Fi-logger baseline
- The number of filtered outliers dropped from 7 to 1
- The upper tail became much shorter than before
- BLE still showed occasional event loss
- BLE remained much less deterministic than Wi-Fi and Zigbee under the corrected setup

## Conclusion
This run should be used as the primary BLE baseline dataset for cross-protocol comparison under the corrected measurement setup.

It shows that the previous logger configuration contributed some extra measurement-side noise, but BLE still exhibits intrinsic limitations due to advertisement-based detection, including broad latency spread and occasional missed events.
