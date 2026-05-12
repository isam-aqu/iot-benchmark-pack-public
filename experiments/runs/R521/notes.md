# R521 Notes

## Run identity

- **EXP_RUN_ID:** R521
- **RUN_ID:** W2_wifi_periodic_3s_quiet_telemetry_v2
- **Workload:** W2
- **Protocol:** Wi-Fi
- **Mode:** Telemetry
- **Interval:** 3000 ms
- **Environment:** near / quiet / single-node
- **Pipeline version:** 0.3.0

## Objective

Telemetry run for the 3 s Wi-Fi energy experiment under the W2 v2 methodology. This run measures device-level power consumption with telemetry publication enabled at a 3 s interval. It is the matched telemetry counterpart to R520.

## Method summary

- Power samples logged over serial from the ESP32 power node.
- MQTT event stream recorded for periodic event timing.
- BLE logger disabled.
- ACK helper disabled.
- Duration set to 330 s to ensure a clean 300 s effective window after startup.
- Serial-based power logging used to avoid self-interference from measurement transport.

## Output integrity

### Parse results
- Power CSV generated successfully
- Event CSV generated successfully
- Meta JSON generated successfully

### Summary results
- Power samples: **3001**
- Events: **100**
- Mean power: **391.49 mW**
- Total energy: **117465.65 mJ**
- Mean event interval: **2999.9998 ms**
- Jitter: **0.0386 ms**
- Reliability: **100 / 100 events captured**
- Latency: **not available in current W2 design**

## Interpretation

R521 is a clean and valid telemetry run for the 3 s condition.

Relative to the matched control run R520:
- Mean power is substantially higher.
- Total energy per event is higher.
- Timing stability remains effectively unchanged.
- Reliability remains perfect.
- This suggests a clearly measurable telemetry overhead at 3 s under the present setup.

## Acceptance decision

- **Accepted:** Yes

## Pairing

- Matched control run: **R520**
- Comparison group: **W2_3s**
- Role in pair: **telemetry / primary**
