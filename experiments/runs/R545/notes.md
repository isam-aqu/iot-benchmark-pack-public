# Run R545 Notes

## Purpose
W2 v2 telemetry run for the 6 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_6s_quiet_telemetry_v2_rep1`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_6s`
- Run type: `telemetry`
- Replicate ID: `rep1`
- Periodic interval: `6000` ms
- Telemetry MQTT: `enabled`
- Fixed duration: `360000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_6s_quiet_telemetry_v2_rep1_meta.json`
  - `raw/W2_wifi_periodic_6s_quiet_telemetry_v2_rep1_mqtt_events.csv`
  - `raw/W2_wifi_periodic_6s_quiet_telemetry_v2_rep1_power_samples.csv`
  - `raw/W2_wifi_periodic_6s_quiet_telemetry_v2_rep1_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 3601
- Event count: 60
- Mean power: 365.92 mW
- Energy: 131707.47 mJ
- Jitter: 0.097 ms
- Reliability: 60/60 events

## Interpretation
6s telemetry transition after equilibrium
This run contributes to the final W2 grouped analysis via matched baseline `R534`, incremental energy -2.14 mJ/event.
