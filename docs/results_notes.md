# Results Notes

> **Version:** 0.4.3
> **Source of truth:** `experiments/version_info.yaml`

This document summarizes processed results and provides paper-ready
interpretations.

------------------------------------------------------------------------

# 🧾 Home Assistant Environment

-   Installation method: **Home Assistant OS**
-   Core: **2026.3.4**
-   Supervisor: **2026.03.2**
-   Operating System: **17.1**
-   Frontend: **20260312.1**

------------------------------------------------------------------------

## ⚠️ Measurement Correction (Critical)

Earlier Wi-Fi and Zigbee results were affected by a **Wi-Fi-connected
logging laptop**.

👉 This introduced interference and inflated latency tails.

### Corrected baseline:

-   Logger connected via Ethernet
-   Laptop Wi-Fi disabled

All conclusions below are based on **corrected baseline comparison runs
(R106, R204, R303)**.

------------------------------------------------------------------------

# 📊 W1 FINAL BASELINE RESULTS (Near / Quiet)

## Wi-Fi (R106)

-   Samples: 100
-   Mean: 11.21 ms
-   Median: 10.44 ms
-   Min: 9.23 ms
-   Max: 17.96 ms
-   Std: 1.96 ms
-   P95: 15.88 ms

### Observations

-   Very tight distribution
-   No extreme outliers
-   Stable RTT behavior

### Interpretation

Wi-Fi provides **stable, low-latency performance** when measurement
artifacts are removed.\
Previously observed long-tail spikes were not intrinsic to Wi-Fi.

------------------------------------------------------------------------

## Zigbee (R204)

-   Samples: 100
-   Median: 0 ms (normalized)
-   Mean: 2.18 ms
-   Min: -1.62 ms
-   Max: 14.86 ms
-   Std: 4.56 ms
-   P95: 11.63 ms

### Observations

-   Highly concentrated distribution
-   Slight right tail
-   Very low variability

### Interpretation

Zigbee provides **stable low-variability latency** under the corrected
baseline, though its normalized spread is broader than Wi-Fi in this
W1 scenario.

------------------------------------------------------------------------

## BLE (R303)

-   \~100 events
-   Median: \~0 ms (normalized)
-   Wide spread
-   Multiple latency clusters
-   Occasional missed events

### Observations

-   Strong multi-modal structure
-   High variance
-   Non-uniform tail

### Interpretation

BLE latency is **non-deterministic and clustered**, driven by
advertisement and scan timing interactions.

------------------------------------------------------------------------

# 🔵 BLE Key Finding (Revised)

-   Latency distribution is **multi-modal**
-   Earlier assumption of fixed \~45 ms spacing is **not strictly
    valid**
-   Cluster spacing becomes irregular at higher latencies

👉 Conclusion:

BLE latency is governed by: - advertisement intervals - scan windows -
host-side scheduling

NOT by a fixed periodic structure.

------------------------------------------------------------------------

# 📈 Cross-Protocol Comparison

  Metric        Wi-Fi     Zigbee      BLE
  ------------- --------- ----------- -----------
  Median        \~10 ms   \~0 ms      \~0 ms
  P95           \~16 ms   \~12 ms     High
  Variability   Very Low  Low         Very High
  Determinism   Very High High        Low

------------------------------------------------------------------------

## Key Insights

### 1. Wi-Fi = Narrowest Corrected W1 Distribution

-   Tightest corrected-baseline spread
-   No heavy tail after correction

### 2. Zigbee = Stable Low Variability

-   Tight normalized distribution
-   Slightly broader spread than Wi-Fi

### 3. BLE = Fundamentally Variable

-   Wide spread
-   Multi-modal behavior
-   Missed events possible

------------------------------------------------------------------------

# ⚠️ Important Methodological Note

-   Wi-Fi uses **RTT (device-level measurement)**
-   Zigbee & BLE use **controller + logger timestamps**

👉 Therefore: - Absolute latency is not directly comparable -
Comparisons focus on: - distribution shape - variability - determinism

------------------------------------------------------------------------

# 📊 Figure Guidance (Final)

Recommended paper figures:

1.  **CDF (median-normalized)**
    -   Main comparison figure
2.  **Boxplot (full dataset)**
    -   Shows spread and tails
3.  **BLE Histogram**
    -   Demonstrates clustering behavior

------------------------------------------------------------------------

# 🧠 Final Interpretation

Under controlled conditions:

-   **Wi-Fi** → stable and tightly bounded corrected-baseline behavior
-   **Zigbee** → stable low-variability behavior with slightly broader normalized spread
-   **BLE** → unsuitable for deterministic real-time applications

------------------------------------------------------------------------

# 🔑 Key Takeaway

👉 Earlier conclusions about Wi-Fi instability were **measurement
artifacts**.

With corrected setup:

-   Wi-Fi performance is stable and tightly bounded
-   Zigbee remains stable with low variability
-   BLE behavior is inherently variable

# ⚡ W2 FINAL ENERGY RESULTS

## Final grouped interpretation
- Positive detectable overhead: `2 s`, `3 s`, `6 s`, `7 s`
- Directionally unresolved: `4 s`
- Below present noise floor: `0.5 s`, `1 s`, `5 s`, `8 s`, `9 s`, `10 s`

## Data quality note
- `R523` was excluded due to physically invalid raw electrical measurements
- `R522` was invalidated together with `R523` to preserve matched-pair consistency
- Excluding this pair changed the 5 s numerical estimate but not its final interpretation

------------------------------------------------------------------------

# 📶 W3 THREE-PROTOCOL INTERFERENCE RESULTS

W3 Wi-Fi is complete for runs `R600`--`R619`, W3 Zigbee is complete for
runs `R620`--`R639`, and W3 BLE is complete for runs `R640`--`R659`.

Cross-protocol W3 artifacts:

-   `analysis/w3/aggregates/w3_replicates.json`
-   `analysis/w3/reports/w3_protocol_comparison.md`
-   `analysis/w3/tables/w3_protocol_comparison.csv`
-   `analysis/w3/figures/w3_protocol_p95_comparison_ci.png`
-   `analysis/w3/figures/w3_protocol_mad_anomaly_comparison_ci.png`

RF/channel context:

-   Wi-Fi AP: netis WF2419, firmware `V2.2.36123`
-   The AP was later found to use Auto channel selection, so the AP channel for
    `R600`--`R639` is unknown from preserved metadata and may have changed after
    restarts.
-   During `R640`--`R659`, the AP was observed on channel 1, channel width
    40 MHz, control sideband Upper.
-   Zigbee: channel 20
-   BLE legacy advertising: primary advertising channels 37, 38, and 39
    (`2402`, `2426`, and `2480 MHz`)

This means the completed Wi-Fi and Zigbee W3 runs (`R600`--`R639`) should not be
used for channel-specific coexistence claims, because the AP channel was not
recorded. Their interpretation should be framed as system-level robustness under
the tested 2.4 GHz background-load condition. For BLE (`R640`--`R659`), the
observed channel-1 AP configuration is wider than a clean single-channel
overlap case: 40 MHz with upper sideband likely exposes BLE advertising
channels 37 and 38. The completed `R660`--`R677` extension uses 20 MHz AP width
on channels 1, 6, and 13 to target BLE advertising channels 37, 38, and 39
separately.

Starting with runs `R678` and later, AP RF fields are captured directly in the
run sheet and per-run metadata. The completed Zigbee AP-channel extension uses
`R678`--`R687` for AP channel 1 / 20 MHz control and `R688`--`R697` for AP
channel 9 / 20 MHz overlap with Zigbee channel 20.

Important measurement caveat: Wi-Fi uses ESP32 MQTT publish-to-ACK RTT, Zigbee
uses Home Assistant state-change time to logger receive time, median-normalized
as in W1, and BLE uses ESP32 advertiser timestamp to logger receive time,
median-normalized as in W1. Therefore, W3 comparison focuses on robustness
trends, tails, variability, and reliability rather than identical link-layer
latency.

## Replicate matrix

### Wi-Fi

| Load level | Runs | iPerf profile |
|---|---|---|
| Baseline | `R600`, `R604`, `R608`, `R612`, `R616` | none |
| Light | `R601`, `R605`, `R609`, `R613`, `R617` | 5 Mbps TCP |
| Moderate | `R602`, `R606`, `R610`, `R614`, `R618` | 20 Mbps TCP |
| Heavy | `R603`, `R607`, `R611`, `R615`, `R619` | 50 Mbps TCP |

### Zigbee

| Load level | Runs | iPerf profile |
|---|---|---|
| Baseline | `R620`, `R624`, `R628`, `R632`, `R636` | none |
| Light | `R621`, `R625`, `R629`, `R633`, `R637` | 5 Mbps TCP |
| Moderate | `R622`, `R626`, `R630`, `R634`, `R638` | 20 Mbps TCP |
| Heavy | `R623`, `R627`, `R631`, `R635`, `R639` | 50 Mbps TCP |

### Zigbee AP-channel extension

| AP setting | Zigbee exposure | Runs |
|---|---|---|
| Channel 1, 20 MHz | control/non-overlap for Zigbee ch20 | `R678`--`R687` |
| Channel 9, 20 MHz | overlaps Zigbee ch20 near 2450 MHz | `R688`--`R697` |

Dedicated outputs:

-   `analysis/w3/reports/w3_zigbee_channel_overlap.md`
-   `analysis/w3/tables/w3_zigbee_channel_overlap_runs.csv`
-   `analysis/w3/tables/w3_zigbee_channel_overlap_pairs.csv`
-   `analysis/w3/tables/w3_zigbee_channel_overlap_summary.csv`

Aggregate Zigbee AP-channel extension results:

| AP channel | Zigbee exposure | Load | P95 mean | MAD mean | Missing mean | Extra/repeated mean |
|---:|---|---|---:|---:|---:|---:|
| 1 | control/non-overlap | baseline | 10.76 ms | 1.74 ms | 0.00/100 | 0.00/100 |
| 1 | control/non-overlap | heavy | 10.38 ms | 1.69 ms | 0.00/100 | 0.40/100 |
| 9 | overlap with ch20 | baseline | 9.88 ms | 2.23 ms | 0.00/100 | 0.00/100 |
| 9 | overlap with ch20 | heavy | 10.60 ms | 2.22 ms | 0.00/100 | 0.80 extra/100; 1.20 repeated/100 |

Paired heavy-minus-baseline analysis gives a small negative P95 shift for the
channel-1 control block (`-0.38 ms`) and a small positive P95 shift for the
channel-9 overlap block (`+0.71 ms`). The overlap-minus-control contrast is
approximately `+1.10 ms`, with no missing Zigbee events in either block.
Therefore, the extension supports the bounded conclusion that deliberate AP
channel-9 overlap does not produce a large Zigbee tail-latency degradation under
the tested 50 Mbps TCP load, while extra/repeated Home Assistant state rows
remain the main reliability signal.

### BLE

| Load level | Runs | iPerf profile |
|---|---|---|
| Baseline | `R640`, `R644`, `R648`, `R652`, `R656` | none |
| Light | `R641`, `R645`, `R649`, `R653`, `R657` | 5 Mbps TCP |
| Moderate | `R642`, `R646`, `R650`, `R654`, `R658` | 20 Mbps TCP |
| Heavy | `R643`, `R647`, `R651`, `R655`, `R659` | 50 Mbps TCP |

### BLE AP-channel extension

| AP setting | Target BLE advertising channel | Runs |
|---|---|---|
| Channel 1, 20 MHz | adv 37 (`2402 MHz`) | `R660`--`R665` |
| Channel 6, 20 MHz | adv 38 (`2426 MHz`) | `R666`--`R671` |
| Channel 13, 20 MHz | adv 39 (`2480 MHz`) | `R672`--`R677` |

Dedicated outputs:

-   `analysis/w3/reports/w3_ble_channel_overlap.md`
-   `analysis/w3/tables/w3_ble_channel_overlap_runs.csv`
-   `analysis/w3/tables/w3_ble_channel_overlap_summary.csv`
-   `analysis/w3/figures/w3_ble_channel_overlap_p95_missing.png`

Aggregate BLE AP-channel extension results:

| AP channel | Target BLE adv | Load | Captured mean | Missing mean | P95 mean | MAD mean |
|---:|---:|---|---:|---:|---:|---:|
| 1 | 37 | baseline | 98.67/100 | 1.33 | 166.1 ms | 85.1 ms |
| 1 | 37 | heavy | 98.67/100 | 1.33 | 145.8 ms | 85.3 ms |
| 6 | 38 | baseline | 98.67/100 | 1.33 | 144.8 ms | 84.0 ms |
| 6 | 38 | heavy | 98.67/100 | 1.33 | 150.3 ms | 81.5 ms |
| 13 | 39 | baseline | 97.67/100 | 2.33 | 161.5 ms | 72.4 ms |
| 13 | 39 | heavy | 98.67/100 | 1.33 | 142.1 ms | 84.8 ms |

Interpretation: the `R660`--`R677` sweep does not show a clear
channel-specific heavy-load degradation pattern for BLE P95 latency. Channel 6
/ BLE advertising channel 38 shows only a small mean P95 increase under heavy
load (+5.6 ms, +3.9%), while channels 1 and 13 show lower mean P95 under heavy
load than their local baselines. BLE advertisement/scanner timing variability
continues to dominate the observed latency behavior.

## Wi-Fi aggregate results

| Load level | Median | P95 | MAD | Drop rate |
|---|---:|---:|---:|---:|
| Baseline | 13.24 ms | 19.83 ms | 1.05 ms | 0.0% |
| Light | 13.44 ms | 22.88 ms | 1.61 ms | 0.0% |
| Moderate | 13.96 ms | 24.17 ms | 1.93 ms | 0.0% |
| Heavy | 15.68 ms | 24.05 ms | 3.38 ms | 1.4% |

## Zigbee aggregate results

| Load level | Median | P95 | MAD | Drop rate | Extra-event rate |
|---|---:|---:|---:|---:|---:|
| Baseline | 0.00 ms | 10.12 ms | 1.79 ms | 0.0% | 0.0% |
| Light | 0.00 ms | 10.97 ms | 1.93 ms | 0.0% | 0.0% |
| Moderate | 0.00 ms | 10.19 ms | 2.22 ms | 0.0% | 0.8% |
| Heavy | 0.00 ms | 10.73 ms | 2.07 ms | 0.0% | 0.8% |

## Change vs protocol baseline

| Protocol | Load | P95 change | MAD change |
|---|---|---:|---:|
| Wi-Fi | Light | +15.4% | +52.7% |
| Wi-Fi | Moderate | +21.8% | +83.3% |
| Wi-Fi | Heavy | +21.3% | +221.7% |
| Zigbee | Light | +8.4% | +7.9% |
| Zigbee | Moderate | +0.6% | +24.1% |
| Zigbee | Heavy | +6.0% | +15.5% |

## Interpretation

-   Median Wi-Fi RTT remains mostly stable through moderate load.
-   Tail latency and variability increase under interference, so mean or median
    alone are not sufficient robustness metrics.
-   Wi-Fi reliability degradation appears only at heavy load in the completed
    Wi-Fi data.
-   Zigbee P95 remains near 10--11 ms across all W3 load levels, with no missing
    events in the completed runs.
-   Zigbee's main quality signal is occasional extra state events rather than
    event loss. Extra-event rates appear in the moderate and heavy aggregate
    groups, driven by `R627`, `R638`, and `R639`.
-   BLE W3 remains dominated by advertisement/scanner variability and missed
    advertisements. Mean P95 is roughly 210 ms at baseline, 174 ms under light
    load, 170 ms under moderate load, and 151 ms under heavy load; aggregate
    missed-advertisement rates remain between 2.4% and 3.2%.
-   Under this setup, Zigbee is less sensitive than Wi-Fi to Wi-Fi iperf load in
    tail-latency terms, while BLE does not show a monotonic iperf-load response
    in the completed replicate set.

------------------------------------------------------------------------

# 🚀 Next Steps

-   Define the remaining W4/W5 robustness scope after W3 is closed
-   Prepare publication
