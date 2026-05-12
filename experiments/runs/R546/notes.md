# Run R546 Notes

## Purpose
W2 v2 control run for the 10 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_10s_quiet_ctrl_v2_rep2`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_10s`
- Run type: `control`
- Replicate ID: `rep2`
- Periodic interval: `10000` ms
- Telemetry MQTT: `disabled`
- Fixed duration: `600000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_10s_quiet_ctrl_v2_rep2_meta.json`
  - `raw/W2_wifi_periodic_10s_quiet_ctrl_v2_rep2_mqtt_events.csv`
  - `raw/W2_wifi_periodic_10s_quiet_ctrl_v2_rep2_power_samples.csv`
  - `raw/W2_wifi_periodic_10s_quiet_ctrl_v2_rep2_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 6001
- Event count: 60
- Mean power: 361.45 mW
- Energy: 216882.22 mJ
- Jitter: 0.062 ms
- Reliability: 60/60 events

## Interpretation
10s control repeat
This run contributes to the final W2 grouped analysis via total energy 3614.70 mJ/event.
