# Run R509 Notes

## Purpose
W2 v2 control run for the 5 s condition using the revised measurement methodology.

## Configuration
- Run ID: `W2_wifi_periodic_5s_quiet_ctrl_v2`
- Protocol: Wi-Fi
- Sensor: INA231
- Wi-Fi: connected
- MQTT session: connected
- Telemetry MQTT: disabled
- MQTT power reporting: disabled
- Periodic interval: 5000 ms
- Power sample interval: 100 ms
- Fixed duration: 300000 ms (5 minutes)

## Logging Method
- Serial output captured to file
- Parsed using `scripts/parse_w2_control_serial.py`
- Power samples logged over serial only
- Telemetry events logged over serial and parsed into the event CSV
- MQTT logger remained active for pipeline consistency, but telemetry MQTT was disabled for this control run

## Event Association
Each serial power row includes:
- `power_seq`
- `t_local_us`
- `last_event_seq`
- `last_event_t_local_us`
- `dt_since_event_us`

This allows power windows to be aligned with the most recent periodic event.

## Expected Role
- R509 is the matched **5 s control** run for comparison against **R512**
- It isolates the internal periodic scheduler cost at 5 s without telemetry transmission
- It is used to estimate the incremental energy cost of 5 s MQTT telemetry by comparing `R512 - R509`

## Results Summary
- Parsed 3001 power samples
- Parsed 60 event rows
- Run completed successfully with expected duration (~300 s)

## Quantitative Summary
- Mean power: 368.19 mW
- Median power: 327.33 mW
- Standard deviation: 115.30 mW
- Minimum power: 224.73 mW
- P95 power: 720.61 mW
- Maximum power: 771.91 mW
- Samples above 500 mW: 319 (10.63%)
- Mean current: 73.83 mA
- Median current: 65.47 mA
- Maximum current: 160.44 mA
- Mean bus voltage: 5.025 V
- Minimum bus voltage: 4.821 V
- Maximum bus voltage: 5.080 V
- Duration from `t_local_us`: 299.999 s
- Mean sample interval: 99.9997 ms
- Median sample interval: 100.000 ms
- Maximum sample interval: 100.988 ms
- Total energy (300 s): 110471.59 mJ
- Unique `last_event_seq` values: 61
- Mean `dt_since_event_ms`: 2524.97 ms
- Median `dt_since_event_ms`: 2485.43 ms
- Maximum `dt_since_event_ms`: 4985.50 ms

## Event Timing Summary
- Event count: 60
- First event sequence: 1
- Last event sequence: 60
- Unique event sequences: 60
- Duration from events: 295.000 s
- Mean event interval: 5000.000 ms
- Median event interval: 4999.998 ms
- Maximum event interval: 5000.073 ms
- Trigger counts:
  - `periodic`: 60

## Observations
- The 5 s internal scheduler behaved stably across the run, producing the expected 60 periodic events.
- Power sampling remained stable at ~100 ms over the full 300 s run.
- Event alignment metadata behaved correctly: `last_event_seq` advanced as expected, and `dt_since_event_us` spanned nearly the full 5 s window between events.
- The power trace exhibited recurring elevated-power regions aligned with periodic activity, but no telemetry transmission was present.
- This rerun differed from the earlier R509 result, indicating non-negligible run-to-run variability in the 5 s condition.

## Interpretation
R509 provides the matched 5 s non-telemetry baseline for the revised W2 v2 methodology. It captures the combined cost of Wi-Fi connectivity, INA231 sampling, ESP32 system activity, and the internal 5 s scheduler, but excludes MQTT telemetry transmission.

The comparison between the first and rerun versions of R509 indicates that the experimental system exhibits a natural variability on the order of several milliwatts. This is important for interpreting low-rate telemetry experiments, because effects near this scale may fall within the system noise floor.

## Analytical Role
R509 is used as the control comparator for R512:
- `R512 - R509` estimates the incremental energy cost of 5 s MQTT telemetry
- The R509 rerun helps estimate the system variability floor for 5 s experiments
- Together with R507, R508, and R511, this run contributes to the emerging energy-versus-reporting-rate analysis

## Assessment
This run completed successfully and is suitable for analysis as the accepted 5 s control baseline for the current phase of W2.
