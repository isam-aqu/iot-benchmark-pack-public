# Run R201 Notes

## Purpose
Baseline Zigbee HA-triggered forwarding run for W1.

## Status
Complete.

## Context
This run represents the baseline Zigbee forwarding path and is recorded in the checked-in run sheet with normalization method set to none.

## Key Characteristics
- Protocol: Zigbee
- Device: light.benchmark_device
- Trigger: Home Assistant state change
- Topology: near
- Interference: quiet
- Normalization: none

## Observations
- This run should remain distinct from the later median-normalized final Zigbee dataset.
- The current repository documentation describes a later processed Zigbee dataset with 63 total samples and 62 core samples. That later dataset is better represented as R202.

## Follow-up
- Create and use R202 for the processed median-normalized Zigbee dataset.
