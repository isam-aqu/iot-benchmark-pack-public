# Run R544 Notes

## Purpose
W2 v2 control run for the 6 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_6s_quiet_ctrl_v2_rep1`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_6s`
- Run type: `control`
- Replicate ID: `rep1`
- Periodic interval: `6000` ms
- Telemetry MQTT: `disabled`
- Fixed duration: `360000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_6s_quiet_ctrl_v2_rep1_meta.json`
  - `raw/W2_wifi_periodic_6s_quiet_ctrl_v2_rep1_mqtt_events.csv`
  - `raw/W2_wifi_periodic_6s_quiet_ctrl_v2_rep1_power_samples.csv`
  - `raw/W2_wifi_periodic_6s_quiet_ctrl_v2_rep1_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 3601
- Event count: 60
- Mean power: 362.36 mW
- Energy: 130463.06 mJ
- Jitter: 0.043 ms
- Reliability: 60/60 events

## Interpretation
6s control transition after equilibrium
This run contributes to the final W2 grouped analysis via total energy 2174.38 mJ/event.
