# Run R541 Notes

## Purpose
W2 v2 telemetry run for the 8 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_8s_quiet_telemetry_v2`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_8s`
- Run type: `telemetry`
- Replicate ID: `rep1`
- Periodic interval: `8000` ms
- Telemetry MQTT: `enabled`
- Fixed duration: `480000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_8s_quiet_telemetry_v2_meta.json`
  - `raw/W2_wifi_periodic_8s_quiet_telemetry_v2_mqtt_events.csv`
  - `raw/W2_wifi_periodic_8s_quiet_telemetry_v2_power_samples.csv`
  - `raw/W2_wifi_periodic_8s_quiet_telemetry_v2_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 4801
- Event count: 60
- Mean power: 368.03 mW
- Energy: 176674.76 mJ
- Jitter: 0.041 ms
- Reliability: 60/60 events

## Interpretation
8s telemetry mid high-interval regime
This run contributes to the final W2 grouped analysis via matched baseline `R536`, incremental energy -24.26 mJ/event.
