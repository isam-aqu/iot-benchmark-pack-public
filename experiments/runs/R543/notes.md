# Run R543 Notes

## Purpose
W2 v2 telemetry run for the 9 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_9s_quiet_telemetry_v2_rep2`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_9s`
- Run type: `telemetry`
- Replicate ID: `rep1`
- Periodic interval: `9000` ms
- Telemetry MQTT: `enabled`
- Fixed duration: `540000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_9s_quiet_telemetry_v2_rep2_meta.json`
  - `raw/W2_wifi_periodic_9s_quiet_telemetry_v2_rep2_mqtt_events.csv`
  - `raw/W2_wifi_periodic_9s_quiet_telemetry_v2_rep2_power_samples.csv`
  - `raw/W2_wifi_periodic_9s_quiet_telemetry_v2_rep2_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 5401
- Event count: 60
- Mean power: 365.42 mW
- Energy: 197343.61 mJ
- Jitter: 0.038 ms
- Reliability: 60/60 events

## Interpretation
9s telemetry near long-interval instability
This run contributes to the final W2 grouped analysis via matched baseline `R538`, incremental energy 14.23 mJ/event.
