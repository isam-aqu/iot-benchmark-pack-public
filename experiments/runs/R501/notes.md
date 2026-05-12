# Run R501 Notes

## Purpose
Measure the connected idle power baseline of the ESP32 + INA231 Wi-Fi telemetry node with periodic telemetry disabled.

## Status
Planned.

## Configuration
- Run ID: `W2_wifi_idle_quiet_v1`
- Experiment run: `R501`
- Protocol: Wi-Fi
- Topology: near
- Interference: quiet
- Trigger: idle connected
- Node: `wifi01_power`
- Telemetry interval: disabled / 0 ms
- Target duration: 5 minutes
- Logger: Ethernet-connected
- Laptop Wi-Fi: disabled

## Expected Outputs
- raw power samples
- raw MQTT events
- derived power summary
- energy baseline for comparison with periodic telemetry runs

## Notes to Record During Run
- actual run duration
- Wi-Fi RSSI if visible
- reconnects or MQTT disconnects
- power supply used
- room conditions
- whether any unexpected traffic was present

## Expected Role in W2
This run provides the baseline connected idle power reference used to estimate incremental telemetry energy in R502–R504.

## Quantitative Results

- Mean Power: 373.6 mW
- Median Power: 332.2 mW
- P95 Power: 715.7 mW
- Max Power: 835.4 mW
- Mean Current: 75.02 mA
- Total Energy (5 min): 112104 mJ

## Comparison with R505

- Mean Power Increase: +6.6 mW
- Relative Increase: +1.8%
- Energy Increase: +1967 mJ

## Interpretation

Despite publishing approximately 10 MQTT messages per second,
the increase in average power consumption is modest (~1.8%).

This indicates that:
- Wi-Fi connectivity dominates energy consumption
- MQTT transmission adds only a small incremental cost
- Communication overhead is not the primary contributor to energy usage in idle nodes

## Key Insight

The dominant energy cost in connected IoT devices is maintaining the wireless link,
not the transmission of small telemetry messages.
