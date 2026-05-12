# Run R555 Notes

## Purpose
W2 v2 telemetry run for the 3 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_3s_quiet_telemetry_v2_rep1`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_3s`
- Run type: `telemetry`
- Replicate ID: `rep1`
- Periodic interval: `3000` ms
- Telemetry MQTT: `enabled`
- Fixed duration: `300000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_3s_quiet_telemetry_v2_rep1_meta.json`
  - `raw/W2_wifi_periodic_3s_quiet_telemetry_v2_rep1_mqtt_events.csv`
  - `raw/W2_wifi_periodic_3s_quiet_telemetry_v2_rep1_power_samples.csv`
  - `raw/W2_wifi_periodic_3s_quiet_telemetry_v2_rep1_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 3001
- Event count: 100
- Mean power: 375.86 mW
- Energy: 112735.56 mJ
- Jitter: 0.045 ms
- Reliability: 100/100 events

## Interpretation
3s telemetry repeat paired with R554
This run contributes to the final W2 grouped analysis via matched baseline `R520`, incremental energy 21.29 mJ/event.
