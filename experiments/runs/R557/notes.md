# Run R557 Notes

## Purpose
W2 v2 telemetry run for the 4 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_4s_quiet_telemetry_v2_rep1`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_4s`
- Run type: `telemetry`
- Replicate ID: `rep1`
- Periodic interval: `4000` ms
- Telemetry MQTT: `enabled`
- Fixed duration: `300000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_4s_quiet_telemetry_v2_rep1_meta.json`
  - `raw/W2_wifi_periodic_4s_quiet_telemetry_v2_rep1_mqtt_events.csv`
  - `raw/W2_wifi_periodic_4s_quiet_telemetry_v2_rep1_power_samples.csv`
  - `raw/W2_wifi_periodic_4s_quiet_telemetry_v2_rep1_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 3001
- Event count: 75
- Mean power: 367.24 mW
- Energy: 110187.20 mJ
- Jitter: 0.039 ms
- Reliability: 75/75 events

## Interpretation
4s telemetry repeat paired with R556
This run contributes to the final W2 grouped analysis via matched baseline `R532`, incremental energy -29.62 mJ/event.
