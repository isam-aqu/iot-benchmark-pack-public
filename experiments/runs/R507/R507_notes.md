# Run R507 Notes

## Purpose
W2 v2 control run for the idle condition using the revised measurement methodology.

## Configuration
- Run ID: `W2_wifi_idle_quiet_ctrl_v2`
- Protocol: Wi-Fi
- Sensor: INA231
- Wi-Fi: connected
- MQTT session: connected
- Telemetry MQTT: `disabled`
- MQTT power reporting: disabled
- Periodic interval: `0` ms
- Power sample interval: 100 ms
- Fixed duration: 300000 ms (5 minutes)

## Logging Method
- Serial output captured to file
- Parsed using `scripts/parse_w2_control_serial.py`
- Power samples logged over serial only
- Telemetry events logged over MQTT only when enabled

## Event Association
Each serial power row includes:
- `power_seq`
- `t_local_us`
- `last_event_seq`
- `last_event_t_local_us`
- `dt_since_event_us`

This allows power windows to be aligned with the most recent telemetry event.

## Expected Role
- Control runs (R507-R510) establish non-telemetry baselines for each interval condition.
- Telemetry runs (R511-R513) quantify the incremental energy impact of MQTT telemetry at 1 s, 5 s, and 10 s.


## Results Summary
- Parsed 3001 power samples
- Parsed 0 event rows
- Final completion marker observed:
  - `EXPERIMENT_COMPLETE,exp=W2_wifi_idle_quiet_ctrl_v2,duration_ms=300000`

## Quantitative Summary
- Mean power: 355.45 mW
- Median power: 324.89 mW
- Standard deviation: 101.84 mW
- Minimum power: 219.85 mW
- P95 power: 683.97 mW
- Maximum power: 779.24 mW
- Mean current: 71.68 mA
- Median current: 64.59 mA
- Maximum current: 162.00 mA
- Mean bus voltage: 4.996 V
- Minimum bus voltage: 4.780 V
- Maximum bus voltage: 5.064 V
- Mean sample interval: 100.00 ms
- Median sample interval: 100.01 ms
- Maximum sample interval: 100.96 ms
- Total energy (300 s): 106650.08 mJ
- Samples above 500 mW: 264 (8.80%)

## Observations
- Power sampling remained stable over the full 300 s run with the expected ~100 ms cadence.
- No event records were produced, which is correct for the idle control configuration with telemetry MQTT disabled.
- `last_event_seq=0`, `last_event_t_local_us=0`, and `dt_since_event_us=-1` remained fixed throughout the run, confirming the absence of telemetry events.
- The power trace shows a stable connected-idle baseline with occasional short spikes attributable to normal Wi-Fi/background ESP32 activity.
- The run completed cleanly without brownout or reset behavior.

## Assessment
This run completed successfully and is suitable for use as the W2 v2 connected-idle baseline.

## Interpretation
R507 establishes the reference energy consumption of the Wi-Fi-connected node under the revised W2 v2 methodology. Because both telemetry MQTT and power MQTT reporting are disabled, the measured energy reflects background Wi-Fi connectivity, INA231 sampling, and normal ESP32 system activity only.

## Expected Analytical Role
R507 is the baseline comparator for:
- R508, to isolate the cost of the internal 1 s periodic scheduler
- R511, to later quantify the combined cost of periodic scheduling plus 1 s MQTT telemetry
