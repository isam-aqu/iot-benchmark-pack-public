# Current State

> **Version:** 0.4.7
> **Source of truth:** `experiments/version_info.yaml`

Last updated: 2026-05-03 Repo snapshot: W1/W2 finalized, W3 Wi-Fi, Zigbee, and BLE finalized through R659, BLE channel-overlap extension R660-R677 complete, Zigbee AP-channel extension R678-R697 planned, AP RF metadata capture added for new RF-sensitive runs

------------------------------------------------------------------------

# 🧾 Home Assistant Environment

-   Installation method: **Home Assistant OS**
-   Core: **2026.3.4**
-   Supervisor: **2026.03.2**
-   Operating System: **17.1**
-   Frontend: **20260312.1**

------------------------------------------------------------------------

## ⚠️ Measurement Correction (Critical Update)

Previous runs used a **Wi-Fi-connected logger laptop**, introducing
interference.

### Corrected setup:

-   Logger connected via **Ethernet**
-   Laptop Wi-Fi **disabled**

👉 All baseline conclusions must now be based only on corrected runs.

------------------------------------------------------------------------

## Hardware Setup

-   Controller: Raspberry Pi 4 running Home Assistant OS (MQTT + ZHA)
-   Logger host: external laptop (Ethernet)
-   Wi-Fi node: ESP32
-   BLE node: ESP32 beacon
-   Zigbee device: `light.benchmark_device`
-   Coordinator: Sonoff Zigbee Coordinator
-   Wi-Fi AP: netis WF2419, firmware `V2.2.36123`; AP channel selection was
    later found to be Auto, so the AP channel for runs before `R640` is
    unknown. During `R640`--`R659`, the AP was observed on channel 1 with
    channel width 40 MHz and control sideband Upper.
-   Starting with planned runs `R678` and later, AP RF fields are captured in
    `run_metadata.json` and `docs/run_sheet.csv`.
-   Zigbee channel: 20
-   BLE advertising: legacy primary advertising channels 37, 38, and 39
    (`2402`, `2426`, and `2480 MHz`); the current logger does not record
    per-packet BLE channel.
-   W3 interference server: `iperf-server` (iperf3)

------------------------------------------------------------------------

## Firmware Version

-   Shared firmware: `0.4.1`
-   Source: `firmware/firmware_version.h`

------------------------------------------------------------------------

## Experiment Status (W1/W2 Finalized + W3 Finalized)

### ✅ W1 Near / Quiet Baselines (Corrected)

-   **Wi-Fi:** `R106 / W1_wifi_near_quiet_v6`
    -   100 samples
    -   Median ≈ 10.4 ms
    -   P95 ≈ 15.9 ms
    -   Stable (no heavy tail after correction)
-   **Zigbee:** `R204 / W1_zigbee_near_quiet_v3`
    -   100 samples
    -   Median = 0 (normalized)
    -   P95 ≈ 11.6 ms
    -   Stable, low variability
-   **BLE:** `R303 / W1_ble_near_quiet_v3`
    -   \~100 events
    -   Wide spread
    -   Multi-modal clustered latency

### ✅ W2 Telemetry Energy Characterization

-   Final W2 v2 dataset now extends through `R557`
-   Matched control / telemetry pairs cover `0.5 s` through `10 s`
-   `R507` remains the connected-idle validation reference
-   Grouped outputs are stored in `analysis/w2/tables/groups.csv` and
    `analysis/w2/tables/groups.json`

### ✅ W3 Interference Robustness

-   Wi-Fi W3 runs `R600`--`R619` are complete
-   Five replicates are available for each load level:
    -   baseline: `R600`, `R604`, `R608`, `R612`, `R616`
    -   light: `R601`, `R605`, `R609`, `R613`, `R617`
    -   moderate: `R602`, `R606`, `R610`, `R614`, `R618`
    -   heavy: `R603`, `R607`, `R611`, `R615`, `R619`
-   Aggregate outputs are stored in `analysis/w3/aggregates/w3_replicates.json`
-   Figure outputs are stored in `analysis/w3/figures/`
-   W3 Zigbee runs `R620`--`R639` are complete with Wi-Fi-parity replication
-   Full W3 protocol comparison outputs are stored in:
    -   `analysis/w3/reports/w3_protocol_comparison.md`
    -   `analysis/w3/tables/w3_protocol_comparison.csv`
    -   `analysis/w3/figures/w3_protocol_p95_comparison_ci.png`
    -   `analysis/w3/figures/w3_protocol_mad_anomaly_comparison_ci.png`
-   Current W3 comparison: Wi-Fi shows load-sensitive tail latency and
    variability; Zigbee remains tail-stable under Wi-Fi iperf load but has
    occasional extra state events in moderate/heavy groups
-   W3 BLE runs `R640`--`R659` are complete with Wi-Fi/Zigbee-parity replication.
    BLE remains advertisement-capture dominated: mean P95 by load is roughly
    210 ms baseline, 174 ms light, 170 ms moderate, and 151 ms heavy, with
    missed-advertisement rates between 2.4% and 3.2%.
-   W3 BLE AP-channel extension `R660`--`R677` is complete:
    -   channel 1, 20 MHz, baseline/heavy x3: `R660`--`R665`
    -   channel 6, 20 MHz, baseline/heavy x3: `R666`--`R671`
    -   channel 13, 20 MHz, baseline/heavy x3: `R672`--`R677`
    -   Dedicated outputs:
        `analysis/w3/reports/w3_ble_channel_overlap.md`,
        `analysis/w3/tables/w3_ble_channel_overlap_runs.csv`, and
        `analysis/w3/tables/w3_ble_channel_overlap_summary.csv`
    -   Figure: `analysis/w3/figures/w3_ble_channel_overlap_p95_missing.png`
    -   Result: no AP channel shows a clear heavy-load BLE P95 degradation
        pattern; BLE advertisement/scanner variability remains dominant.
-   W3 Zigbee AP-channel extension is planned in `docs/run_sheet.csv`:
    -   AP channel 1, 20 MHz control block, baseline/heavy x5: `R678`--`R687`
    -   AP channel 9, 20 MHz Zigbee-channel-20 overlap block, baseline/heavy x5:
        `R688`--`R697`

------------------------------------------------------------------------

## 📊 Current Interpretation

-   **Wi-Fi**
    -   Stable RTT after correction
    -   Narrowest corrected-baseline distribution in W1
    -   Previously observed spikes were measurement artifacts
-   **Zigbee**
    -   Stable low-variability behavior
    -   Slightly broader normalized spread than Wi-Fi in W1
-   **BLE**
    -   Highest variability
    -   Clustered latency (not continuous)
    -   Occasional missed events

------------------------------------------------------------------------

## 🔵 BLE Behavior (Revised Understanding)

-   Latency is **multi-modal**
-   Clusters exist but are **not perfectly periodic**
-   High-latency clusters are irregular

👉 Interpretation: BLE timing appears consistent with
scan/advertising interaction rather than a fixed-interval model.

------------------------------------------------------------------------

## ⚡ W2 Interpretation

-   Revised W2 v2 methodology uses **serial-only power logging**
    with MQTT reserved for telemetry events
-   Cross-run interpretation is based on matched control vs telemetry
    comparisons at the same interval
-   **Positive detectable overhead:** `2 s`, `3 s`, `6 s`, `7 s`
-   **Directionally unresolved:** `4 s`
-   **Below present noise floor:** `0.5 s`, `1 s`, `5 s`, `8 s`,
    `9 s`, `10 s`

------------------------------------------------------------------------

## Coverage Status

Completed:
- W1 baseline (corrected)
- W2 telemetry energy characterization
- W3 Wi-Fi interference robustness
- W3 Zigbee interference robustness
- W3 BLE interference robustness
- W3 BLE channel-overlap extension (`R660`--`R677`)

Pending:
- W4 spatial robustness
- W5 multi-node / multi-room robustness

------------------------------------------------------------------------

## Known Constraints (Updated)

-   External logger required (HAOS limitation)
-   Zigbee lacks device timestamps
-   BLE is observation-based
-   BLE variability + missed events
-   Wi-Fi now confirmed stable when measured correctly

------------------------------------------------------------------------

## Key Takeaway

👉 The **measurement setup was the main source of earlier
inconsistencies**.

With corrected setup:

-   Wi-Fi is stable
-   Zigbee remains stable with low variability
-   BLE remains fundamentally variable
-   W2 telemetry overhead is interval-dependent and not monotonic
-   W3 Wi-Fi interference mainly increases tail latency and variability
-   W3 Zigbee remains tail-stable under Wi-Fi iperf load, with occasional extra
    state events rather than missing events
-   W3 BLE remains dominated by advertisement/scanner variability and missed
    advertisements rather than a monotonic response to iperf load
-   AP channel selection was Auto for earlier runs, so channel-specific
    Wi-Fi/Zigbee coexistence claims should not be made for `R600`--`R639`.
-   For `R640`--`R659`, the AP was observed on Wi-Fi channel 1 with 40 MHz
    upper sideband, so BLE exposure likely includes advertising channels 37 and
    38.
-   The completed `R660`--`R677` 20 MHz sweep did not reveal a clear
    channel-specific heavy-load degradation pattern for BLE advertising
    channels 37, 38, or 39.
