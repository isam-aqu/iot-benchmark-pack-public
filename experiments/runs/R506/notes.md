# Run R506 Notes

## Purpose
Control run for periodic (1 s) workload with MQTT reporting disabled.

## Configuration
- Run ID: `W2_wifi_periodic_1s_quiet_ctrl_v1`
- Protocol: Wi-Fi
- Sensor: INA231
- Wi-Fi: connected
- MQTT session: connected
- MQTT reporting: disabled
- Periodic interval: 1000 ms
- Power sample interval: 100 ms
- Fixed duration: 300000 ms (5 minutes)

## Logging Method
- Serial output captured to file
- Parsed using `scripts/parse_w2_control_serial.py`
- No MQTT power/event logging expected

## Results Summary
- Parsed 3001 power samples
- Parsed 301 event rows
- Final completion marker observed:
  - `EXPERIMENT_COMPLETE,exp=W2_wifi_periodic_1s_quiet_ctrl_v1,duration_ms=300000`

## Observations
- Bus voltage remained around 5.05 V for most of the run, with short dips during higher-activity windows
- Baseline current remained in the mid-60 mA range for most samples
- Baseline power remained around the low- to mid-330 mW range for most samples
- Recurring short spikes in current and power were observed at approximately 1 s intervals, consistent with the intended periodic internal workload
- Peak power excursions reached roughly the 700 mW range during these periodic activity windows
- Event cadence matched the intended 1 s schedule over the duration of the run
- No brownout was observed in the completed run

## Assessment
This run completed successfully and is suitable for use as the W2 periodic control baseline.

## Expected Role
Provides the periodic control baseline for comparing against R502 and estimating the incremental energy cost of MQTT reporting under a 1 s telemetry schedule.
