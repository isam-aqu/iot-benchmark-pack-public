# Run R547 Notes

## Purpose
W2 v2 telemetry run for the 10 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_10s_quiet_telemetry_v2_rep2`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_10s`
- Run type: `telemetry`
- Replicate ID: `rep2`
- Periodic interval: `10000` ms
- Telemetry MQTT: `enabled`
- Fixed duration: `600000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_10s_quiet_telemetry_v2_rep2_meta.json`
  - `raw/W2_wifi_periodic_10s_quiet_telemetry_v2_rep2_mqtt_events.csv`
  - `raw/W2_wifi_periodic_10s_quiet_telemetry_v2_rep2_power_samples.csv`
  - `raw/W2_wifi_periodic_10s_quiet_telemetry_v2_rep2_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 6002
- Event count: 60
- Mean power: 365.14 mW
- Energy: 219098.07 mJ
- Jitter: 0.041 ms
- Reliability: 60/60 events

## Interpretation
10s telemetry repeat
This run contributes to the final W2 grouped analysis via matched baseline `R510`, incremental energy -1.91 mJ/event.
