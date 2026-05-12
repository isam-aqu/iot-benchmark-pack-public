# R524 Notes

## Run identity
- EXP_RUN_ID: R524
- RUN_ID: W2_wifi_periodic_7s_quiet_ctrl_v2
- Mode: Control
- Interval: 7000 ms

## Objective
Primary control run for the 7 s interval to investigate system behavior beyond the 5 s equilibrium point.

## Method
- Serial power logging (ESP32 + INA226)
- MQTT events for timing validation
- BLE disabled
- ACK disabled
- Duration: 450 s

## Interpretation
This run represents the first measurement in the post-equilibrium region, where preliminary results suggested increasing energy cost.

## Pairing
- Telemetry: R525
- Group: W2_7s
- Role: control / primary

## Status
Accepted
