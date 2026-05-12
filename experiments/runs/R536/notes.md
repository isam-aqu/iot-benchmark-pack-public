# Run R536 Notes

## Purpose
W2 v2 control run for the 8 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_8s_quiet_ctrl_v2`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_8s`
- Run type: `control`
- Replicate ID: `primary`
- Periodic interval: `8000` ms
- Telemetry MQTT: `disabled`
- Fixed duration: `480000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_8s_quiet_ctrl_v2_meta.json`
  - `raw/W2_wifi_periodic_8s_quiet_ctrl_v2_mqtt_events.csv`
  - `raw/W2_wifi_periodic_8s_quiet_ctrl_v2_power_samples.csv`
  - `raw/W2_wifi_periodic_8s_quiet_ctrl_v2_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 4801
- Event count: 60
- Mean power: 371.08 mW
- Energy: 178130.15 mJ
- Jitter: 0.046 ms
- Reliability: 60/60 events

## Interpretation
8s control mid high-interval regime
This run contributes to the final W2 grouped analysis via total energy 2968.84 mJ/event.
