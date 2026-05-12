# R518 — W2 Wi-Fi 5 s Periodic Control (Replication 1)

## Overview

R518 is a W2 v2 control run conducted at a 5 s periodic interval. The internal scheduler is active, but MQTT telemetry publication is disabled. This run serves as a replication of the 5 s control condition to evaluate run-to-run variability near the detectability threshold.

## Objective

- Replicate the 5 s control condition (R509) under identical W2 v2 methodology  
- Quantify variability in mean power and energy at low event rates  
- Provide a matched baseline for comparison with R519 (telemetry)

## Configuration

- Protocol: Wi-Fi  
- Node: ESP32 (wifi01_power)  
- Topology: near  
- Interference: quiet  
- Node count: 1  

### Timing

- Periodic interval: 5000 ms  
- Duration: 300 s  
- Expected events: ~60  
- Power sampling interval: 100 ms  

### Telemetry

- MQTT telemetry: disabled  
- MQTT power reporting: disabled  
- Serial logging: enabled  

### Measurement Stack

- Power measurement: INA231 (high-side)  
- Logging: serial capture (no MQTT logging)  
- Timestamp source: ESP32 `t_local_us`

## Results Summary

- Mean power: **385.75 mW**  
- Median power: 332.21 mW  
- Std dev: 135.32 mW  
- Energy (300 s): **115739.78 mJ**  
- Event count: 60  
- Mean event interval: 4999.99 ms  

## Notes

- Event timing is stable and consistent with configuration  
- Power sampling is stable (~100 ms interval)  
- Mean power is significantly higher than R509 (~+17.6 mW), indicating substantial run-to-run variability  
- This confirms that the 5 s control regime is not stable enough for single-run inference  

## Interpretation

R518 demonstrates that even under controlled conditions, device-level power at low event rates exhibits non-negligible variability. This variability must be considered when interpreting telemetry overhead at or below the 5 s interval.
