# Run R548 Notes

## Purpose
W2 v2 control run for the 500 ms condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_500ms_quiet_ctrl_v2_rep1`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_0.5s`
- Run type: `control`
- Replicate ID: `rep1`
- Periodic interval: `500` ms
- Telemetry MQTT: `disabled`
- Fixed duration: `300000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_500ms_quiet_ctrl_v2_rep1_meta.json`
  - `raw/W2_wifi_periodic_500ms_quiet_ctrl_v2_rep1_mqtt_events.csv`
  - `raw/W2_wifi_periodic_500ms_quiet_ctrl_v2_rep1_power_samples.csv`
  - `raw/W2_wifi_periodic_500ms_quiet_ctrl_v2_rep1_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 3001
- Event count: 601
- Mean power: 374.42 mW
- Energy: 112341.36 mJ
- Jitter: 0.191 ms
- Reliability: 601/601 events

## Interpretation
0.5s control repeat to enable variance estimation for ultra-high rate regime
This run contributes to the final W2 grouped analysis via total energy 186.92 mJ/event.
