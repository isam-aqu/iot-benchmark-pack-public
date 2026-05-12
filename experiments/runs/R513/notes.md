# Run Notes — R513

## Experiment
- EXP_RUN_ID: R513
- RUN_ID: W2_wifi_periodic_10s_quiet_telemetry_v2
- Workload: W2 (Wi-Fi energy characterization)
- Type: Telemetry (MQTT enabled)

## Objective
Measure the incremental energy cost of MQTT telemetry at a 10 s reporting interval under the W2 v2 methodology.

## Configuration

- Periodic interval: 10 s
- MQTT telemetry: Enabled
- MQTT power reporting: Disabled
- Power logging: Serial (UART)
- Sampling interval: 100 ms
- Duration: 300 s
- Network: Wi-Fi connected (local network only)

## Environment

- Scenario: W1-equivalent (near distance, low interference)
- Single node operation
- Stable Wi-Fi connection
- No intentional background traffic

## Execution Summary

- Power samples: 3001
- Events: 30
- Mean event interval: 10000 ms
- Mean sample interval: 100 ms

## Results (Key Metrics)

- Mean power: 370.03 mW
- Median power: 327.33 mW
- Std dev: 117.28 mW
- P95 power: 715.73 mW
- Energy (300 s): 111023.85 mJ

## Derived Comparison (vs R510)

- Mean power increase: +4.72 mW
- Relative increase: ~1.29%
- Energy increase (300 s): +1418 mJ
- Estimated energy per event: ~47.3 mJ/event

## Observations

- Event timing is stable and matches expected 10 s interval.
- Power distribution slightly wider than control.
- Increase in samples above 500 mW suggests transmission bursts.

- Compared to 5 s results:
  - Unlike 5 s, telemetry overhead shows consistent positive direction
  - However, magnitude remains small

## Interpretation

- Telemetry overhead at 10 s is:
  - physically present (positive)
  - small relative to system variability

- Indicates transition toward detectability limit:
  - overhead is no longer clearly separable from background variation

## Validity Assessment

- Power data: VALID
- Event data: VALID
- Run status: ACCEPTED

## Notes

- Result supports emerging pattern:
  - 1 s → clearly detectable
  - 5 s → ambiguous
  - 10 s → weak but positive

- Further replication required (especially at 5 s) to confirm threshold behavior.
