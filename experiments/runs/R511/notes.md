# Run R511 Notes

## Purpose
W2 v2 telemetry run for the 1 s condition using the revised measurement methodology.

## Configuration
- Run ID: `W2_wifi_periodic_1s_quiet_telemetry_v2`
- Protocol: Wi-Fi
- Sensor: INA231
- Wi-Fi: connected
- MQTT session: connected
- Telemetry MQTT: `enabled`
- MQTT power reporting: disabled
- Periodic interval: `1000` ms
- Power sample interval: 100 ms
- Fixed duration: 300000 ms (5 minutes)

## Logging Method
- Serial output captured to file
- Parsed using `scripts/parse_w2_control_serial.py`
- Power samples logged over serial only
- Telemetry events logged over MQTT only when enabled

## Event Association
Each serial power row includes:
- `power_seq`
- `t_local_us`
- `last_event_seq`
- `last_event_t_local_us`
- `dt_since_event_us`

This allows power windows to be aligned with the most recent telemetry event.

## Expected Role
- Control runs (R507-R510) establish non-telemetry baselines for each interval condition.
- Telemetry runs (R511-R513) quantify the incremental energy impact of MQTT telemetry at 1 s, 5 s, and 10 s.


## Results Summary
- Parsed 3001 power samples
- Parsed 301 event rows

## Quantitative Summary
- Mean power: 373.58 mW
- Energy: 112090.72 mJ

## Comparison to R508
- Δ Mean power: +14.89 mW
- Δ Energy: +4490.16 mJ
- ~14.9 mJ/event
