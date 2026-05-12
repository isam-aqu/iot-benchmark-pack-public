# Run Notes — R510

## Experiment
- EXP_RUN_ID: R510
- RUN_ID: W2_wifi_periodic_10s_quiet_ctrl_v2
- Workload: W2 (Wi-Fi energy characterization)
- Type: Control (no MQTT telemetry)

## Objective
Establish the 10 s periodic control baseline for device-level power consumption under the W2 v2 methodology, isolating scheduler overhead without telemetry communication.

## Configuration

- Periodic interval: 10 s
- MQTT telemetry: Disabled
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

- Mean power: 365.31 mW
- Median power: 332.21 mW
- Std dev: 107.83 mW
- P95 power: 708.40 mW
- Energy (300 s): 109606.22 mJ

## Observations

- Event timing is stable and matches expected 10 s interval.
- Power readings are consistent with previous W2 runs.
- No anomalies in sampling or event alignment.

- Compared to:
  - R507 (idle): lower baseline difference than expected
  - R509 (5 s control): slightly lower mean power

- Indicates:
  - scheduler overhead at 10 s is minimal
  - run-to-run variability remains a significant component

## Validity Assessment

- Power data: VALID
- Event data: VALID
- Run status: ACCEPTED

## Notes

- Earlier suspicion of ground connection issue not supported by observed data.
- Run retained without repetition.
