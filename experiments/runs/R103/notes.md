# Run R103 Notes

## Purpose
Test whether increased inter-event spacing reduces Wi-Fi latency outliers.

## Status
Complete.

## Context
This run repeats the Wi-Fi W1 baseline under the same near-quiet setup as R102, but with intentionally increased spacing between button presses.

## Key Characteristics
- Protocol: Wi-Fi
- Node ID: wifi01
- Trigger: button press
- Topology: near
- Interference: quiet
- Inter-event spacing: increased
- Normalization: none
- Total samples: 100
- Core samples: 78

## Processing
- RTT derived directly from ESP32 publish-to-ACK timing
- Core dataset defined as RTT in [0 ms, 200 ms]

## Observations
- Heavy-tail RTT behavior persisted
- Outlier count increased relative to R102
- Core P95 worsened relative to R102

## Conclusion
Event overlap is not the main source of the Wi-Fi tail-latency problem in the current stack.
