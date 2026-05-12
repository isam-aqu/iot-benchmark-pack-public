# Run R542 Notes

## Purpose
W2 v2 control run for the 9 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_9s_quiet_ctrl_v2_rep2`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_9s`
- Run type: `control`
- Replicate ID: `rep1`
- Periodic interval: `9000` ms
- Telemetry MQTT: `disabled`
- Fixed duration: `540000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_9s_quiet_ctrl_v2_rep2_meta.json`
  - `raw/W2_wifi_periodic_9s_quiet_ctrl_v2_rep2_mqtt_events.csv`
  - `raw/W2_wifi_periodic_9s_quiet_ctrl_v2_rep2_power_samples.csv`
  - `raw/W2_wifi_periodic_9s_quiet_ctrl_v2_rep2_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 5401
- Event count: 60
- Mean power: 366.68 mW
- Energy: 198020.80 mJ
- Jitter: 0.045 ms
- Reliability: 60/60 events

## Interpretation
9s control near long-interval instability
This run contributes to the final W2 grouped analysis via total energy 3300.35 mJ/event.
