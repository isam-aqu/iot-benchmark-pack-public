# Run R556 Notes

## Purpose
W2 v2 control run for the 4 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_4s_quiet_ctrl_v2_rep1`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_4s`
- Run type: `control`
- Replicate ID: `rep1`
- Periodic interval: `4000` ms
- Telemetry MQTT: `disabled`
- Fixed duration: `300000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_4s_quiet_ctrl_v2_rep1_meta.json`
  - `raw/W2_wifi_periodic_4s_quiet_ctrl_v2_rep1_mqtt_events.csv`
  - `raw/W2_wifi_periodic_4s_quiet_ctrl_v2_rep1_power_samples.csv`
  - `raw/W2_wifi_periodic_4s_quiet_ctrl_v2_rep1_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 3001
- Event count: 75
- Mean power: 364.18 mW
- Energy: 109267.39 mJ
- Jitter: 0.086 ms
- Reliability: 75/75 events

## Interpretation
4s control repeat to complete mid-range coverage
This run contributes to the final W2 grouped analysis via total energy 1456.90 mJ/event.
