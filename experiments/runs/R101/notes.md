# Run R101 Notes

## Purpose
Manual Wi-Fi RTT baseline for the W1 latency benchmark.

## Status
Complete.

## Context
This run uses the ESP32 Wi-Fi node with button-triggered MQTT event publish and ACK-based RTT measurement.

## Key Characteristics
- Protocol: Wi-Fi
- Node ID: wifi01
- Trigger: button press
- Topology: near
- Interference: quiet
- Normalization: none

## Observations
- The experiment log records two Wi-Fi runs on 2026-03-27.
- Run 1 had one extreme RTT outlier around 1.13 seconds.
- Retained-message handling was improved before the repeat run.
- Run 2 showed tighter latency distribution and better stability.

## Follow-up
- Keep processed RTT artifacts tied to this run or split into separate repetitions if you later decide to record each Wi-Fi repeat independently.
