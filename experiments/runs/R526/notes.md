# R526 Notes

## Run identity

- **EXP_RUN_ID:** R526
- **RUN_ID:** W2_wifi_periodic_10s_quiet_ctrl_v2
- **Workload:** W2
- **Protocol:** Wi-Fi
- **Mode:** Control
- **Interval:** 10000 ms
- **Environment:** near / quiet / single-node
- **Pipeline version:** 0.3.0

## Objective

Repeat control run for the 10 s Wi-Fi periodic workload under the W2 v2 methodology. This run serves as the second control baseline for the W2_10s comparison group and is paired with R527.

## Method summary

- Power logged over serial from the ESP32 + INA231/INA231-equivalent power node setup used in W2 v2.
- MQTT event stream recorded for periodic timing verification.
- BLE logger disabled.
- ACK helper disabled.
- Run duration set to 450 s to increase event count and reduce uncertainty at long intervals.

## Output integrity

- Parsing completed successfully.
- Summary completed successfully.
- Per-run analysis completed successfully.

## Interpretation

This run was collected to improve confidence in the 10 s regime after the first 10 s pair suggested positive overhead but with only a single matched pair. The repeat is intended to determine whether the apparent 10 s effect is stable or belongs to a high-variance low-frequency regime.

## Acceptance decision

- **Accepted:** Yes

## Pairing

- Matched telemetry run: **R527**
- Comparison group: **W2_10s**
- Role in pair: **control / rep1**
