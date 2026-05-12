# Run R105 Notes

## Purpose
Obtain a cleaner Wi-Fi baseline with reduced variability and verify whether outlier rate can be minimized.

## Status
Complete.

## Context
This run continues the Wi-Fi W1 baseline under near-quiet conditions with increased inter-event spacing. It follows R102–R104 and aims to validate whether stable behavior is achievable.

## Key Characteristics
- Protocol: Wi-Fi
- Node ID: wifi01
- Trigger: button press
- Topology: near
- Interference: quiet
- Inter-event spacing: increased
- Normalization: none
- Total samples: 100
- Core samples: 91

## Processing
- RTT derived from ESP32 publish-to-ACK timing
- Core dataset defined as RTT in [0 ms, 200 ms]

## Observations
- Lowest outlier rate observed so far (9%)
- Median RTT stable (~15 ms)
- Core P95 improved compared to most previous runs
- Rare extreme spikes still present (max >1.5 s)

## Conclusion
This is the most stable Wi-Fi run obtained so far and should be used as the primary Wi-Fi baseline for core latency comparison.

However, the persistence of rare extreme delays confirms that the Wi-Fi stack exhibits inherent tail-latency behavior that must be discussed in the paper.
