# R520 Notes

## Run identity

- **EXP_RUN_ID:** R520
- **RUN_ID:** W2_wifi_periodic_3s_quiet_ctrl_v2
- **Workload:** W2
- **Protocol:** Wi-Fi
- **Mode:** Control
- **Interval:** 3000 ms
- **Environment:** near / quiet / single-node
- **Pipeline version:** 0.3.0

## Objective

Control run for the 3 s Wi-Fi telemetry energy experiment under the W2 v2 methodology. This run measures device-level power consumption with the internal periodic scheduler enabled at 3 s, while telemetry publication is disabled. It serves as the matched baseline for R521.

## Method summary

- Power samples logged over serial from the ESP32 power node.
- MQTT event stream recorded for periodic event timing.
- BLE logger disabled.
- ACK helper disabled.
- Duration set to 330 s to ensure a clean 300 s effective measurement window after startup.
- Serial capture used for power logging to avoid self-interference from measurement traffic.

## Output integrity

### Parse results
- Power CSV generated successfully
- Event CSV generated successfully
- Meta JSON generated successfully

### Summary results
- Power samples: **3001**
- Events: **100**
- Mean power: **368.77 mW**
- Total energy: **110606.56 mJ**
- Mean event interval: **2999.999 ms**
- Jitter: **0.0380 ms**
- Reliability: **100 / 100 events captured**
- Latency: **not available in current W2 design**

## Interpretation

R520 is a clean and valid control run for the 3 s condition.

Key observations:
- Event count matches expectation for a 300 s run at 3 s interval.
- Scheduler timing is highly stable.
- No event loss or duplication was observed.
- Power behavior appears consistent with prior W2 control runs.
- This run is suitable as the matched control baseline for R521.

## Acceptance decision

- **Accepted:** Yes

## Pairing

- Matched telemetry run: **R521**
- Comparison group: **W2_3s**
- Role in pair: **control / primary**
