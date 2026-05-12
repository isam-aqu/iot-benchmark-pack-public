# Run R102 Notes

## Purpose
Wi-Fi baseline rerun under the stabilized 0.1.1 pipeline.

## Status
Complete.

## Context
This run uses the ESP32 Wi-Fi node in near-quiet conditions with button-triggered event generation. It was designed to establish a 100-sample baseline under the finalized measurement pipeline.

## Key Characteristics
- Protocol: Wi-Fi
- Node ID: wifi01
- Trigger: button press
- Topology: near
- Interference: quiet
- Normalization: none
- Total samples: 100
- Core samples: 81

## Processing
- RTT derived directly from ESP32 publish-to-ACK timing
- Core dataset defined as RTT in [0 ms, 200 ms]
- Full dataset retained for tail-latency interpretation

## Observations
- Typical RTT remained low
- Heavy-tail behavior remained significant
- 19% of RTT samples exceeded 200 ms
- Maximum RTT reached 1786.036 ms

## Conclusion
This run provides the strongest Wi-Fi baseline under pipeline 0.1.1 and should be used as the main Wi-Fi reference for cross-protocol comparison, with explicit discussion of the full-dataset tail behavior.
