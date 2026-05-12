# Run R502 Notes

## Purpose
Measure power behavior of the ESP32 + INA231 Wi-Fi telemetry node during periodic telemetry at a 1 s interval.

## Status
Planned.

## Configuration
- Run ID: `W2_wifi_periodic_1s_quiet_v1`
- Experiment run: `R502`
- Protocol: Wi-Fi
- Topology: near
- Interference: quiet
- Trigger: periodic telemetry
- Node: `wifi01_power`
- Telemetry interval: 1000 ms
- Target duration: 5 minutes
- Logger: Ethernet-connected
- Laptop Wi-Fi: disabled

## Expected Outputs
- raw power samples
- raw MQTT events
- average power and peak current
- report count and delivery ratio
- estimated energy per report

## Notes to Record During Run
- actual run duration
- expected vs actual report count
- Wi-Fi RSSI if visible
- reconnects or dropped reports
- unusual power spikes
- room conditions

## Expected Role in W2
This run captures high-rate telemetry power behavior and will be compared against idle, 5 s, and 10 s periodic telemetry runs.
