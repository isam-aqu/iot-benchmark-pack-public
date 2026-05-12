# Run R500 Notes

## Purpose
W2 v2 control run for the idle condition under the revised matched control-versus-telemetry energy methodology.

## Configuration
- Run ID: `R500`
- Workload: `W2`
- Protocol: `wifi`
- Status: `planned`
- Comparison group: `none`
- Run type: `control`
- Replicate ID: `primary`
- Periodic interval: `0` ms
- Telemetry MQTT: `disabled`

## Artifact Coverage
- Raw files:
  - `raw/W2_wifi_idle_quiet_test_mqtt_events.csv`
  - `raw/W2_wifi_idle_quiet_test_power_samples.csv`

## Interpretation
Idle connected baseline for ESP32 + INA231 power node; Wi-Fi and MQTT connected; periodic telemetry disabled; target duration 5 min
