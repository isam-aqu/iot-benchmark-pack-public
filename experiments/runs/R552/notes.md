# Run R552 Notes

## Purpose
W2 v2 control run for the 2 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_2s_quiet_ctrl_v2_rep1`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_2s`
- Run type: `control`
- Replicate ID: `rep1`
- Periodic interval: `2000` ms
- Telemetry MQTT: `disabled`
- Fixed duration: `300000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_2s_quiet_ctrl_v2_rep1_meta.json`
  - `raw/W2_wifi_periodic_2s_quiet_ctrl_v2_rep1_mqtt_events.csv`
  - `raw/W2_wifi_periodic_2s_quiet_ctrl_v2_rep1_power_samples.csv`
  - `raw/W2_wifi_periodic_2s_quiet_ctrl_v2_rep1_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 3001
- Event count: 151
- Mean power: 364.16 mW
- Energy: 109261.45 mJ
- Jitter: 0.150 ms
- Reliability: 151/151 events

## Interpretation
2s control repeat to establish variance in rising regime
This run contributes to the final W2 grouped analysis via total energy 723.59 mJ/event.
