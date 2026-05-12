# R519 — W2 Wi-Fi 5 s Periodic Telemetry (Replication 1)

## Overview

R519 is the telemetry-enabled counterpart to R518, conducted under identical conditions except with MQTT telemetry publication enabled. This run forms a matched pair with R518 for evaluating telemetry energy overhead at a 5 s interval.

## Objective

- Measure telemetry energy impact at 5 s reporting interval  
- Compare against R518 control under identical scheduling conditions  
- Evaluate detectability of telemetry overhead relative to system variability  

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

- MQTT telemetry: enabled  
- MQTT power reporting: disabled  
- Serial logging: enabled  

### Measurement Stack

- Power measurement: INA231 (high-side)  
- Logging: serial capture (power) + MQTT (events)  
- Timestamp source: ESP32 `t_local_us`

## Results Summary

- Mean power: **371.96 mW**  
- Median power: 327.33 mW  
- Std dev: 120.56 mW  
- Energy (300 s): **111605.45 mJ**  
- Event count: 60  
- Mean event interval: 5000.00 ms  

## Notes

- Event timing is stable and matches configuration  
- Power sampling is consistent (~100 ms interval)  
- Mean power is lower than R518 (control), yielding a negative difference  

## Interpretation

The observed negative power difference relative to R518 is not physically meaningful and indicates that the telemetry-induced energy effect at 5 s is smaller than the underlying system variability. This result confirms that telemetry overhead at this interval is experimentally indistinguishable under current conditions.
