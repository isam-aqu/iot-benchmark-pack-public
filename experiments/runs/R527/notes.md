# R527 Notes

## Run identity

- **EXP_RUN_ID:** R527
- **RUN_ID:** W2_wifi_periodic_10s_quiet_telemetry_v2
- **Workload:** W2
- **Protocol:** Wi-Fi
- **Mode:** Telemetry
- **Interval:** 10000 ms
- **Environment:** near / quiet / single-node
- **Pipeline version:** 0.3.0

## Objective

Repeat telemetry run for the 10 s Wi-Fi periodic workload under the W2 v2 methodology. This run is paired with R526 and provides the second matched telemetry sample for the W2_10s group.

## Method summary

- Power logged over serial from the ESP32 power node.
- MQTT event stream recorded for periodic timing verification.
- BLE logger disabled.
- ACK helper disabled.
- Run duration set to 450 s to increase event count and reduce uncertainty at long intervals.

## Output integrity

- Parsing completed successfully.
- Summary completed successfully.
- Per-run analysis completed successfully.

## Interpretation

This run was collected to validate the 10 s telemetry overhead after the first 10 s pair suggested a positive but weakly supported effect. The additional pair helps determine whether the 10 s regime is reproducibly positive or statistically unstable.

## Acceptance decision

- **Accepted:** Yes

## Pairing

- Matched control run: **R526**
- Comparison group: **W2_10s**
- Role in pair: **telemetry / rep1**
