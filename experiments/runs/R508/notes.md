# Run R508 Notes

## Purpose
W2 v2 control run for the 1 s condition using the revised measurement methodology.

## Configuration
- Run ID: `W2_wifi_periodic_1s_quiet_ctrl_v2`
- Protocol: Wi-Fi
- Sensor: INA231
- Wi-Fi: connected
- MQTT session: connected
- Telemetry MQTT: `disabled`
- MQTT power reporting: disabled
- Periodic interval: `1000` ms
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
- Parsed 301 event rows
- Final completion marker observed:
  - `EXPERIMENT_COMPLETE,exp=W2_wifi_periodic_1s_quiet_ctrl_v2,duration_ms=300000`

## Quantitative Summary
- Mean power: 358.69 mW
- Median power: 324.89 mW
- Standard deviation: 103.77 mW
- Minimum power: 295.57 mW
- P95 power: 688.85 mW
- Maximum power: 764.58 mW
- Mean current: 72.70 mA
- Median current: 65.17 mA
- Maximum current: 167.57 mA
- Mean bus voltage: 4.982 V
- Minimum bus voltage: 4.683 V
- Maximum bus voltage: 5.014 V
- Mean sample interval: 100.00 ms
- Median sample interval: 100.00 ms
- Maximum sample interval: 100.95 ms
- Total energy (300 s): 107600.56 mJ
- Samples above 500 mW: 278 (9.26%)
- Event count: 301
- Mean event interval: 1000.00 ms
- Median event interval: 1000.00 ms
- Maximum event interval: 1000.71 ms
- Mean `dt_since_event_ms`: 538.33 ms
- Median `dt_since_event_ms`: 538.08 ms
- Maximum `dt_since_event_ms`: 988.79 ms

## Observations
- The 1 s periodic scheduler remained stable across the full run, producing 301 periodic events with negligible interval jitter.
- Power sampling remained stable at approximately 100 ms throughout the full 300 s duration.
- Event alignment metadata behaved as intended: `last_event_seq` advanced correctly and `dt_since_event_us` cycled from near 0 ms to just under 1000 ms between consecutive events.
- The power trace shows recurring activity spikes aligned with the periodic internal scheduler.
- The run completed cleanly without brownout or reset behavior.

## Comparison to R507
- Mean power increase: +3.24 mW
- Relative increase: +0.91%
- Energy increase over 300 s: +950.48 mJ

## Assessment
This run completed successfully and is suitable for use as the W2 v2 1 s control baseline.

## Interpretation
R508 isolates the energy cost of the internal 1 s periodic scheduler without telemetry MQTT traffic. The observed overhead relative to R507 is small but measurable, confirming that the scheduler itself contributes modestly to energy consumption and that later telemetry-enabled runs can attribute additional increases to communication rather than timer logic alone.

## Expected Analytical Role
R508 is the direct control comparator for R511 and will be used to isolate the incremental energy impact of 1 s MQTT telemetry under the revised W2 v2 methodology.
