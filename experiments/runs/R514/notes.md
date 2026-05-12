# Run Notes — R514 (W2 Wi-Fi 0.5 s Control)

## Objective
Establish a high-frequency control baseline at a 0.5 s interval under W2 v2 methodology, isolating scheduler overhead without MQTT telemetry.

## Configuration
- Workload: W2 (energy characterization)
- Protocol: Wi-Fi (MQTT connected, telemetry disabled)
- Interval: 500 ms (internal periodic scheduler active)
- Duration: ~300 s
- Node count: 1 (single-node setup)
- Topology: near
- Interference: quiet

## Measurement Method
- Power sampling via ESP32 serial output (INA226-based measurement pipeline)
- Timestamp source: ESP32 `t_local_us`
- Event stream: MQTT (disabled for telemetry; periodic trigger events still logged)

## Data Processing
- Parsed using: `parse_w2_control_serial.py`
- Summarized using: `summarize_w2_run.py`
- No filtering required

## Power Statistics
- Samples: 3001
- Mean power: ~363.00 mW
- Median power: ~330–335 mW (stable baseline cluster)
- Std deviation: ~110 mW (burst-driven variability)
- Min power: ~235 mW
- P95 power: ~710 mW
- Max power: ~750 mW

## Electrical Characteristics
- Mean current: ~72–73 mA
- Max current: ~150–160 mA
- Mean bus voltage: ~5.03 V

## Energy
- Total energy: ~108,900 mJ over 300 s

## Event Characteristics
- Event count: 601
- Mean interval: ~500 ms
- Timing stability: high (tight distribution around target interval)

## Interpretation
- Scheduler overhead remains modest even at 0.5 s
- No instability or saturation observed at high event rate
- Provides a **clean high-rate baseline** for telemetry comparison
- Confirms that scheduler activity alone does not dominate energy behavior

## Validity
- Status: ACCEPTED
- No anomalies detected
- Suitable as control baseline for R515

## Role in Study
- Anchors the **high-frequency region** of the interval spectrum
- Enables evaluation of **energy amortization effects** at short intervals
