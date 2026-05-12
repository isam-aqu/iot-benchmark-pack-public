# Run R505 Notes

## Purpose
Control run for connected idle behavior with MQTT reporting disabled.

## Configuration
- Run ID: `W2_wifi_idle_quiet_ctrl_v1`
- Protocol: Wi-Fi
- Sensor: INA231
- Wi-Fi: connected
- MQTT session: connected
- MQTT reporting: disabled
- Periodic interval: 0 ms
- Power sample interval: 100 ms
- Fixed duration: 300000 ms (5 minutes)

## Logging Method
- Serial output captured to file
- Parsed using `scripts/parse_w2_control_serial.py`
- No MQTT power/event logging expected

## Results Summary
- Parsed 3001 power samples
- Parsed 0 event rows
- Final completion marker observed:
  - `EXPERIMENT_COMPLETE,exp=W2_wifi_idle_quiet_ctrl_v1,duration_ms=300000`

## Observations
- Bus voltage remained around 5.05 V for most of the run
- Idle current remained around the mid-60 mA range for most samples
- Power remained around the low-300 mW range for most samples
- Occasional short spikes were observed, consistent with normal ESP32/Wi-Fi background activity
- No brownout was observed in the completed run

## Assessment
This run completed successfully and is suitable for use as the W2 idle control baseline.

## Expected Role
Provides control baseline for comparing against R501 and estimating reporting overhead.

## Quantitative Results

- Mean Power: 367.0 mW
- Median Power: 327.3 mW
- P95 Power: 708.4 mW
- Max Power: 735.3 mW
- Mean Current: 73.27 mA
- Total Energy (5 min): 110137 mJ

## Interpretation (Updated)

This run establishes the baseline energy consumption of a connected IoT node.
The majority of power is consumed by maintaining Wi-Fi connectivity and system activity,
with no contribution from application-level communication.

