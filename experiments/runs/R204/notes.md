## R204 – Zigbee Baseline with Ethernet Logger (W1_zigbee_near_quiet_v3)

### Motivation
Previous Zigbee baseline (R203) exhibited moderate variability and rare outliers.
Hypothesis: Variability was introduced by the measurement system (Wi-Fi-connected logger).

### Change Introduced
- Logger connected via Ethernet
- Wi-Fi disabled on laptop

### Result
- Mean normalized delay reduced to ~2.18 ms
- P95 reduced to ~11.63 ms
- Maximum delay ~14.86 ms
- **No outliers observed**
- Very tight latency distribution

### Key Insight
Previously observed Zigbee variability was largely caused by **measurement-induced contention and system effects**, not intrinsic Zigbee behavior.

### Impact
- Establishes **true Zigbee baseline**
- Demonstrates high determinism of Zigbee event propagation
- Confirms sensitivity of measurement pipeline to logger connectivity
