# Run R553 Notes

## Purpose
W2 v2 telemetry run for the 2 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_2s_quiet_telemetry_v2_rep1`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_2s`
- Run type: `telemetry`
- Replicate ID: `rep1`
- Periodic interval: `2000` ms
- Telemetry MQTT: `enabled`
- Fixed duration: `300000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_2s_quiet_telemetry_v2_rep1_meta.json`
  - `raw/W2_wifi_periodic_2s_quiet_telemetry_v2_rep1_mqtt_events.csv`
  - `raw/W2_wifi_periodic_2s_quiet_telemetry_v2_rep1_power_samples.csv`
  - `raw/W2_wifi_periodic_2s_quiet_telemetry_v2_rep1_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 3001
- Event count: 150
- Mean power: 382.94 mW
- Energy: 114903.34 mJ
- Jitter: 0.039 ms
- Reliability: 150/150 events

## Interpretation
2s telemetry repeat paired with R552
This run contributes to the final W2 grouped analysis via matched baseline `R530`, incremental energy 32.69 mJ/event.
