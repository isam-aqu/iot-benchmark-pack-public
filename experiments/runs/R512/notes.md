# Run R512 Notes

## Purpose
W2 v2 telemetry run for the 5 s condition using the revised measurement methodology.

## Configuration
- Run ID: `W2_wifi_periodic_5s_quiet_telemetry_v2`
- Protocol: Wi-Fi
- Sensor: INA231
- Wi-Fi: connected
- MQTT session: connected
- Telemetry MQTT: enabled
- MQTT power reporting: disabled
- Periodic interval: 5000 ms
- Power sample interval: 100 ms
- Fixed duration: 300000 ms (5 minutes)

## Logging Method
- Serial output captured to file
- Parsed using `scripts/parse_w2_control_serial.py`
- Power samples logged over serial only
- Telemetry events published over MQTT and also represented in the parsed event CSV
- Power was not published over MQTT, preserving the W2 v2 separation between measurement and workload

## Event Association
Each serial power row includes:
- `power_seq`
- `t_local_us`
- `last_event_seq`
- `last_event_t_local_us`
- `dt_since_event_us`

This allows event-centered energy analysis around each transmitted telemetry event.

## Expected Role
- R512 is the matched **5 s telemetry** run for comparison against **R509**
- It quantifies the energy impact of MQTT telemetry at a 5 s reporting interval
- It is part of the energy-versus-reporting-rate sequence together with R511 (1 s) and later R513 (10 s)

## Results Summary
- Parsed 3001 power samples
- Parsed 60 event rows
- Run completed successfully with expected duration (~300 s)

## Quantitative Summary
- Mean power: 366.96 mW
- Median power: 327.33 mW
- Standard deviation: 116.19 mW
- Minimum power: 219.85 mW
- P95 power: 713.28 mW
- Maximum power: 801.22 mW
- Samples above 500 mW: 331 (11.03%)
- Mean current: 73.23 mA
- Median current: 64.59 mA
- Maximum current: 164.45 mA
- Mean bus voltage: 5.027 V
- Minimum bus voltage: 4.843 V
- Maximum bus voltage: 5.083 V
- Duration from `t_local_us`: 299.999 s
- Mean sample interval: 99.9997 ms
- Median sample interval: 100.001 ms
- Maximum sample interval: 100.841 ms
- Total energy (300 s): 110105.69 mJ
- Unique `last_event_seq` values: 61
- Mean `dt_since_event_ms`: 2490.96 ms
- Median `dt_since_event_ms`: 2451.43 ms
- Maximum `dt_since_event_ms`: 4951.47 ms

## Event Timing Summary
- Event count: 60
- First event sequence: 1
- Last event sequence: 60
- Unique event sequences: 60
- Duration from events: 295.000 s
- Mean event interval: 4999.999 ms
- Median event interval: 5000.000 ms
- Maximum event interval: 5000.067 ms
- Trigger counts:
  - `periodic`: 60

## Observations
- The 5 s telemetry scheduler and MQTT publish path behaved stably across the run, producing the expected 60 transmitted events.
- Power sampling remained stable at ~100 ms.
- Event-alignment metadata behaved correctly and covered nearly the full 5 s interval between transmissions.
- The initial real-time visibility of the serial log was inconsistent, but the final parsed dataset was complete and internally consistent.
- The resulting mean power was slightly lower than the matched control run, which is physically counterintuitive for added telemetry and suggests that the true 5 s telemetry effect is near or below the current run-to-run variability floor.

## Comparison to R509
Using the accepted R509 rerun as control:

- Mean power difference: **-1.23 mW** (`R512 - R509`)
- Relative difference: **-0.33%**
- Energy difference over 300 s: **-365.90 mJ**

These values indicate that the measured 5 s telemetry effect is not directionally robust in the current setup.

## Interpretation
R512 confirms that the 5 s telemetry workload executes correctly and that the W2 v2 methodology remains operational at this lower reporting rate. However, the matched comparison with R509 shows that the incremental telemetry effect at 5 s is smaller than, or comparable to, the run-to-run variability of the full system.

Accordingly, the 5 s result should currently be interpreted as **inconclusive with respect to telemetry overhead magnitude**, not as evidence that telemetry reduces power.

## Analytical Role
R512 is the 5 s telemetry point in the energy-versus-reporting-rate series:
- R511 (1 s): clear measurable overhead
- R512 (5 s): telemetry effect approaches system variability floor
- R513 (10 s): planned extension to test whether the effect becomes even less distinguishable

## Assessment
This run completed successfully and is suitable for use as a valid 5 s telemetry experiment. However, its interpretation must be paired with the R509 rerun and framed as a near-noise-floor result rather than a confirmed negative overhead.
