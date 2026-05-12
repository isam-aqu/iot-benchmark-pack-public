# Hardware Setup – ESP32 + INA231 Power Measurement

## Overview

This document describes the wiring and measurement topology used for W2 energy experiments.

## Power Measurement Topology

The ESP32 is powered through an INA231 high-side current and voltage monitor.

### Power Path

External 5V Supply → INA231 VIN+  
INA231 VIN− → ESP32 VIN  
INA231 BUS → ESP32 VIN  

### Ground

All grounds are shared:
- Power supply GND
- ESP32 GND
- INA231 GND
- USB-to-UART GND

### I²C Interface

INA231 VDD → ESP32 3.3V  
INA231 SDA → ESP32 GPIO21  
INA231 SCL → ESP32 GPIO22  

### Serial Monitoring

USB-TTL TX → ESP32 RX  
USB-TTL RX → ESP32 TX  
USB-TTL VCC → not connected  

## Notes

- The BUS pin connection is required for correct bus voltage measurement.
- The ESP32 must not be powered via USB during measurement.
- The INA231 measures node-level electrical behavior only.


## W2 v2 Update
Serial-only power logging; MQTT only for telemetry.
