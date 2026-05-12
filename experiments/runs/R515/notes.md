# Run Notes — R515 (W2 Wi-Fi 0.5 s Telemetry)

## Objective
Quantify MQTT telemetry overhead at a 0.5 s interval and evaluate energy amortization behavior at high reporting rates.

## Configuration
- Workload: W2 (energy characterization)
- Protocol: Wi-Fi (MQTT telemetry enabled)
- Interval: 500 ms
- Duration: ~300 s
- Node count: 1
- Topology: near
- Interference: quiet

## Measurement Method
- Power sampling via ESP32 serial output (INA226-based pipeline)
- Timestamp source: ESP32 `t_local_us`
- Event stream: MQTT telemetry events

## Data Processing
- Parsed using: `parse_w2_control_serial.py`
- Summarized using: `summarize_w2_run.py`
- Data cleaning applied:
  - Removed 1 invalid sample (`bus_v = 0`)

## Power Statistics (after filtering)
- Samples: 3000
- Mean power: 367.40 mW
- Median power: 332.21 mW
- Std deviation: 111.63 mW
- Min power: 236.95 mW
- P95 power: 715.73 mW
- Max power: 752.37 mW

## Electrical Characteristics
- Mean current: 73.41 mA
- Max current: 156.34 mA
- Mean bus voltage: 5.03 V

## Energy
- Total energy: 110,229.84 mJ over 300 s

## Event Characteristics
- Event count: 601
- Mean interval: 499.99 ms
- Timing stability: high

## Comparison with Control (R514)
- Δ mean power: +4.40 mW
- Relative increase: ~1.21%
- Energy difference: ~1,315 mJ over run

Estimated energy per event:
\[
E_{event} \approx 2.19 \text{ mJ/event}
\]

## Interpretation
- Telemetry overhead is:
  - **positive and physically consistent**
  - **significantly smaller per event** than at 1 s
- Strong evidence of:
  - **energy amortization at high rates**
- Indicates that:
  - communication cost is not fixed per event
  - system behavior depends on radio/idle state interaction

## Validity
- Status: ACCEPTED (after filtering)
- Single corrupted sample removed
- No further anomalies

## Role in Study
- Provides **critical high-rate datapoint**
- Challenges assumption of constant per-event energy
- Supports transition from discrete regimes → continuous model
