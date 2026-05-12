# R532 Notes

## Run identity
- EXP_RUN_ID: R532
- RUN_ID: W2_wifi_periodic_4s_quiet_ctrl_v2
- Mode: Control
- Interval: 4000 ms

## Objective
Control run for 4 s interval to refine the transition between the rising-overhead regime (≤3 s) and the equilibrium region (~5 s).

## Method
- Serial power logging (ESP32 + INA226 setup)
- MQTT events for timing verification
- BLE disabled
- ACK disabled
- Duration: 450 s

## Interpretation
This run fills the gap between 3 s and 5 s, helping determine whether the energy curve decreases smoothly toward the 5 s equilibrium or shows non-linear behavior.

## Pairing
- Telemetry: R533
- Group: W2_4s
- Role: control / primary

## Status
Accepted

