# Run R549 Notes

## Purpose
W2 v2 telemetry run for the 500 ms condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_500ms_quiet_telemetry_v2_rep1`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_0.5s`
- Run type: `telemetry`
- Replicate ID: `rep1`
- Periodic interval: `500` ms
- Telemetry MQTT: `enabled`
- Fixed duration: `300000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_500ms_quiet_telemetry_v2_rep1_meta.json`
  - `raw/W2_wifi_periodic_500ms_quiet_telemetry_v2_rep1_mqtt_events.csv`
  - `raw/W2_wifi_periodic_500ms_quiet_telemetry_v2_rep1_power_samples.csv`
  - `raw/W2_wifi_periodic_500ms_quiet_telemetry_v2_rep1_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 3001
- Event count: 601
- Mean power: 374.26 mW
- Energy: 112295.42 mJ
- Jitter: 0.178 ms
- Reliability: 601/601 events

## Interpretation
0.5s telemetry repeat paired with R548 to quantify variability at saturation rate
This run contributes to the final W2 grouped analysis via matched baseline `R514`, incremental energy 5.63 mJ/event.
