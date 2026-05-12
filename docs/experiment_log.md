# Experiment Log (Full + Traceable)

> **Version:** 0.4.0
> **Source of truth:** `experiments/version_info.yaml`

This document contains the **human-readable chronological record** of
major tracked experiments and retained interpretations.
`docs/run_sheet.csv` is the canonical machine-readable chronology for
all runs, including the full W2 series.

------------------------------------------------------------------------

## ⚠️ Global Measurement Constraint

-   Logger MUST be Ethernet-connected
-   Laptop Wi-Fi MUST be disabled

Earlier Wi-Fi-based logger runs are kept but marked as
measurement-affected.

------------------------------------------------------------------------

# 🧪 Wi-Fi Experiments

## 2026-03-27 -- R001 Validation Run

**Status:** 🧪 Pre-Experiment Validation

-   Informal W0 RTT validation
-   Confirmed MQTT + ACK path before formal workloads

------------------------------------------------------------------------

## 2026-03-27 -- R101 Initial W1 Baseline

**Status:** 🔬 Exploratory

-   Manual button-triggered RTT baseline
-   Included an early extreme outlier before retained-message safeguards

------------------------------------------------------------------------

## 2026-03-27 -- Run 1

**Status:** 🔬 Exploratory

-   Events: 50
-   Result: 1 extreme outlier (\~1.13 s)

**Notes:**

-   Suspected retained MQTT or scheduling issue
-   Triggered pipeline fixes

------------------------------------------------------------------------

## 2026-03-27 -- Run 2

**Status:** 🔬 Exploratory

-   Events: 50
-   No outliers

**Insight:**

-   Established reproducibility
-   Highlighted tail variability

------------------------------------------------------------------------

## R102 -- v2 Rerun

**Status:** 🔬 Investigative

-   Outliers: 19%
-   Max RTT: 1786 ms

------------------------------------------------------------------------

## R103 -- v3 Rerun (Spacing Test)

**Status:** 🔬 Hypothesis Test

-   Increased spacing
-   Outliers persisted

**Conclusion:**
Event overlap NOT root cause

------------------------------------------------------------------------

## R104 -- v4 Rerun (Load Reduction Test)

**Status:** 🔬 Hypothesis Test

-   Reduced host load
-   Worse performance

**Conclusion:**
Host load NOT root cause

------------------------------------------------------------------------

## R106 -- Final Wi-Fi Baseline

**Status:** ✅ VALID BASELINE

**Conclusion:**

-   Stable median (\~10.4 ms)
-   No outliers observed in 100 / 100 samples
-   Earlier Wi-Fi heavy tail was measurement-induced, not intrinsic

------------------------------------------------------------------------

# 🧪 Zigbee Experiments

## R201 -- Initial Zigbee Baseline

**Status:** 🔬 Exploratory

-   HA-triggered forwarding baseline
-   Pre-normalization reference run

------------------------------------------------------------------------

## R202 -- Processed Zigbee Dataset (63 samples)

**Status:** 🔬 Exploratory

-   Mean: 10.16 ms
-   Core samples: 62 / 63 after normalization and filtering
-   Outliers present

------------------------------------------------------------------------

## R203 -- Zigbee Baseline (Wi-Fi Logger)

**Status:** ⚠️ Measurement Affected

-   Core mean: 4.65 ms
-   Outliers present

**Issue:**
Logger was using Wi-Fi → inflated variability

------------------------------------------------------------------------

## R204 -- Zigbee (Ethernet Logger)

**Status:** ✅ VALID BASELINE

-   Mean: 2.18 ms
-   P95: 11.63 ms
-   Outliers: 0

**Conclusion:**
True Zigbee performance → highly deterministic

------------------------------------------------------------------------

# 🧪 BLE Experiments

## R301 -- Initial BLE Dataset

**Status:** 🔬 Exploratory

-   50 total samples
-   49 core samples after filtering
-   High variability
-   Wide spread

------------------------------------------------------------------------

## R302 -- BLE Baseline (Wi-Fi Logger)

**Status:** ⚠️ Measurement Affected

-   Clustered latency observed
-   High jitter

------------------------------------------------------------------------

## R303 -- BLE (Ethernet Logger)

**Status:** ✅ VALID BASELINE

-   Core P95: 94.87 ms
-   Missing events observed (99 / 101 captured)

**Key Finding:**
Latency remains **clustered / multi-modal**, but strict fixed-step
quantization should not be assumed

**Conclusion:**
BLE remains non-deterministic

------------------------------------------------------------------------
## 2026-04-07 – W1 BLE Confound-Check Rerun After Removing Suspected Ambient BLE Traffic (`R304`)

### Purpose
Repeat the BLE W1 near-quiet baseline after identifying a possible ambient BLE confound in the room: a television with a BLE remote control that may have been generating frequent advertisements.

### Configuration
- Run ID: `W1_ble_near_quiet_v4`
- Experiment run: `R304`
- Protocol: BLE
- Topology: near
- Interference: quiet
- Trigger: button press
- Node: `ble01`
- Total button presses: 100
- Logger: Ethernet-connected
- Laptop Wi-Fi: disabled

### Motivation
Earlier BLE baseline runs showed high variability and occasional missed events. Because BLE measurements depend on advertisement detection, unrelated ambient BLE traffic in the room was considered a possible source of additional scanner load or timing disturbance. This rerun was performed to test whether removing that confound would improve BLE baseline behavior.

### Capture Integrity
- Captured samples: 97
- Missing sequences: `14`, `31`, and `55`
- Total missed events: 3

### Results
- Full samples: 97
- Core samples: 92
- Filtered outliers: 5

#### Full dataset
- Mean: 8.874 ms
- Median: 0.000 ms
- Min: -136.237 ms
- Max: 346.989 ms
- Std: 107.826 ms
- P95: 167.438 ms

#### Core dataset
- Mean: -7.443 ms
- Median: -2.641 ms
- Min: -136.237 ms
- Max: 142.420 ms
- Std: 83.700 ms
- P95: 123.435 ms

#### RSSI
- Mean RSSI: -74.90 dBm

### Comparison to R303
Relative to `R303`, this rerun did not improve BLE baseline quality:
- More missed events (`97/100` vs `99/101`)
- More filtered outliers (`5` vs `1`)
- Worse core P95 (`123.44 ms` vs `94.87 ms`)

### Interpretation
Removing the suspected ambient BLE advertiser did not improve the BLE baseline in this rerun. This suggests that the previously observed BLE variability is not primarily explained by background BLE traffic from the television remote. However, the weaker mean RSSI in `R304` indicates that receive conditions were not identical across runs and may have contributed to the worse result.

### Conclusion
`R304` should be retained as a confound-check rerun documenting control of a possible ambient BLE confound, but it should **not** replace `R303` as the primary BLE baseline. `R303` remains the retained primary BLE baseline obtained under the corrected Ethernet-logger setup.
------------------------------------------------------------------------

# 🧾 Final Baseline Selection (W1)

-   Wi-Fi → R106
-   Zigbee → R204
-   BLE → R303

These are used for:

-   paper results
-   figures
-   comparison

------------------------------------------------------------------------

# ⚡ W2 Energy Experiments

## 2026-04-10 -- 2026-04-19 -- W2 Telemetry Energy Characterization

**Status:** ✅ COMPLETE DATASET + GROUPED ANALYSIS

-   Early exploratory W2 runs: `R500-R506`
-   Revised W2 v2 matched control / telemetry study: `R507-R557`
-   Interval coverage: connected-idle validation plus paired `0.5 s`
    through `10 s`
-   Full run chronology and pair metadata: `docs/run_sheet.csv`
-   Final grouped outputs: `analysis/w2/tables/groups.csv`,
    `analysis/w2/tables/groups.json`
-   `R522` / `R523` were later invalidated after raw-data review found 
    physically impossible electrical values in `R523`; final `W2_5s` 
    interpretation uses only valid pairs and remains `below_noise_floor`

**Final grouped interpretation:**

-   Positive detectable overhead: `2 s`, `3 s`, `6 s`, `7 s`
-   Directionally unresolved: `4 s`
-   Below present noise floor: `0.5 s`, `1 s`, `5 s`, `8 s`, `9 s`,
    `10 s`

**Notes:**

-   `R507` is the connected-idle validation reference for W2 v2
-   Historical W2 runs use a mix of `manifest.yaml`, `manifest.json`,
    `Rxxx_manifest.yaml`, `notes.md`, `Rxxx_notes.md`, and runs with no
    local notes / manifest
-   Use `docs/run_sheet.csv` as the cross-run index when exact per-run
    artifact coverage matters

------------------------------------------------------------------------

# 🔁 Reproducibility

Runs are stored in:

    experiments/runs/<EXP_RUN_ID>/

Common per-run artifacts include:

-   raw
-   optional derived
-   optional analysis
-   optional manifest / notes

Cross-run metadata is canonical in:

-   `docs/run_sheet.csv`

Later W2 runs often rely on `analysis/summary.*` and `analysis/metrics.json`
for their retained summaries, even when local manifest / notes files are
not present.

------------------------------------------------------------------------

# 📌 Key Scientific Outcome

The log demonstrates:

-   systematic hypothesis testing (Wi-Fi)
-   measurement artifact identification (Zigbee, BLE)
-   protocol-level behavioral differences

------------------------------------------------------------------------

# W3 Wi-Fi Interference Campaign Documentation

The W3 Wi-Fi interference campaign evaluates ESP32 MQTT RTT behavior under quiet, light, moderate, and heavy background TCP traffic. The finalized procedure uses an Ethernet-connected logging laptop, Wi-Fi disabled on the logger, ESP32 reset at run start, boot-aware summarization, duplicate-payload detection, and per-run iperf throughput summaries.

## Final W3 Wi-Fi Run Matrix

| Load level | Primary | Rep1 | Rep2 | Rep3 | Rep4 | iPerf profile |
|---|---:|---:|---:|---:|---:|---|
| Baseline | R600 | R604 | R608 | R612 | R616 | none |
| Light | R601 | R605 | R609 | R613 | R617 | 5 Mbps TCP |
| Moderate | R602 | R606 | R610 | R614 | R618 | 20 Mbps TCP |
| Heavy | R603 | R607 | R611 | R615 | R619 | 50 Mbps TCP |

## Final Analysis Procedure

Per run:

```bash
python python/summarize_w3_run.py experiments/runs/<Rxxx>/raw --run-id <scenario_run_id>
python python/analyze_w3_run.py experiments/runs/<Rxxx>/raw --run-id <Rxxx> --run-sheet docs/run_sheet.csv
```

Across all W3 Wi-Fi runs:

```bash
python python/analyze_w3_replicates.py --run-sheet docs/run_sheet.csv
python python/plot_w3_results.py
```

## Data Quality Requirements

A W3 run is retained only if:

- the selected boot segment is the intended post-reset ESP32 boot;
- retained pre-reset rows are excluded by the summarizer;
- duplicate MQTT payload count is zero or explained;
- loaded runs include an iperf summary JSON;
- iperf mean throughput is close to the target;
- the ESP32 serial log contains `EXPERIMENT_COMPLETE`;
- manifest and notes are present for the run.

## Paper-Level Interpretation Rule

Use median, MAD, P95, tail inflation factor, and drop rate as primary results. Mean latency and temporal standard deviation are retained as supporting metrics because occasional extreme RTT spikes can dominate the mean.

# Version Tracking

-   pipeline_version: 0.4.0
-   firmware_version: 0.4.0
-   logger_version: 0.4.0
-   analysis_version: 0.4.0
-   ha_automation_version: 0.4.0
-   experiment_protocol_version: 0.4.0
