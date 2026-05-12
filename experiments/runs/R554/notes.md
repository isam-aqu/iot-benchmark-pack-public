# Run R554 Notes

## Purpose
W2 v2 control run for the 3 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_3s_quiet_ctrl_v2_rep1`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_3s`
- Run type: `control`
- Replicate ID: `rep1`
- Periodic interval: `3000` ms
- Telemetry MQTT: `disabled`
- Fixed duration: `300000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_3s_quiet_ctrl_v2_rep1_meta.json`
  - `raw/W2_wifi_periodic_3s_quiet_ctrl_v2_rep1_mqtt_events.csv`
  - `raw/W2_wifi_periodic_3s_quiet_ctrl_v2_rep1_power_samples.csv`
  - `raw/W2_wifi_periodic_3s_quiet_ctrl_v2_rep1_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 3001
- Event count: 100
- Mean power: 363.51 mW
- Energy: 109068.33 mJ
- Jitter: 0.039 ms
- Reliability: 100/100 events

## Interpretation
3s control repeat to strengthen transition region statistics
This run contributes to the final W2 grouped analysis via total energy 1090.68 mJ/event.
