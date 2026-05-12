# Run R535 Notes

## Purpose
W2 v2 telemetry run for the 6 s condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `W2_wifi_periodic_6s_quiet_telemetry_v2`
- Workload: `W2`
- Protocol: `wifi`
- Status: `complete`
- Comparison group: `W2_6s`
- Run type: `telemetry`
- Replicate ID: `primary`
- Periodic interval: `6000` ms
- Telemetry MQTT: `enabled`
- Fixed duration: `360000` ms

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_periodic_6s_quiet_telemetry_v2_meta.json`
  - `raw/W2_wifi_periodic_6s_quiet_telemetry_v2_mqtt_events.csv`
  - `raw/W2_wifi_periodic_6s_quiet_telemetry_v2_power_samples.csv`
  - `raw/W2_wifi_periodic_6s_quiet_telemetry_v2_serial.log`
- Analysis files:
  - `analysis/metrics.json`
  - `analysis/summary.json`
  - `analysis/summary.md`

## Results Summary
- Power samples: 3601
- Event count: 60
- Mean power: 373.73 mW
- Energy: 134560.01 mJ
- Jitter: 0.042 ms
- Reliability: 60/60 events

## Interpretation
6s telemetry transition after equilibrium
This run contributes to the final W2 grouped analysis via total energy 2242.67 mJ/event.
