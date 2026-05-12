# Run R104 Notes

## Purpose
Test whether reducing laptop background load improves Wi-Fi latency stability.

## Status
Complete.

## Context
This run repeats the Wi-Fi W1 baseline under near-quiet conditions with increased inter-event spacing preserved from R103, while minimizing background activity on the external logger host.

## Key Characteristics
- Protocol: Wi-Fi
- Node ID: wifi01
- Trigger: button press
- Topology: near
- Interference: quiet
- Inter-event spacing: increased
- Host-side application load: reduced
- Normalization: none
- Total samples: 100
- Core samples: 75

## Processing
- RTT derived directly from ESP32 publish-to-ACK timing
- Core dataset defined as RTT in [0 ms, 200 ms]

## Observations
- Outlier rate increased further
- Full median worsened
- Core P95 worsened
- Tail instability remained pronounced

## Conclusion
Reducing ordinary host-side application load did not resolve the Wi-Fi tail-latency issue. The observed behavior appears intrinsic to the current system stack.
