# Run R551 Notes

## Purpose
W2 v2 telemetry run for the 1 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_1s_quiet_telemetry_v2_rep1`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_1s`
- Run type: `telemetry`
- Replicate ID: `rep1`
- Periodic interval: `1000` ms
- Telemetry MQTT: `enabled`
- Fixed duration: `300000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_1s_quiet_telemetry_v2_rep1_meta.json`
  - `raw/W2_wifi_periodic_1s_quiet_telemetry_v2_rep1_mqtt_events.csv`
  - `raw/W2_wifi_periodic_1s_quiet_telemetry_v2_rep1_power_samples.csv`
  - `raw/W2_wifi_periodic_1s_quiet_telemetry_v2_rep1_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 3001
- Event count: 301
- Mean power: 374.35 mW
- Energy: 112321.74 mJ
- Jitter: 0.122 ms
- Reliability: 301/301 events

## Interpretation
1s telemetry repeat paired with R550 to finalize strongest signal point
This run contributes to the final W2 grouped analysis via matched baseline `R508`, incremental energy 15.68 mJ/event.
