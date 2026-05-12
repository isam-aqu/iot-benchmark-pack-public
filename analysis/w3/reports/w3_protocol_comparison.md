# W3 Protocol Comparison

Generated: 2026-05-11T17:30:36+03:00

## Scope

- Wi-Fi W3 runs: `R600-R619`, five replicates per load level.
- Zigbee W3 runs: `R620-R639`, five replicates per load level.
- BLE W3 runs: `R640-R659`, five replicates per load level.
- Load levels: baseline, 5 Mbps TCP, 20 Mbps TCP, and 50 Mbps TCP background traffic.
- Means are computed across completed W3 replicates; confidence intervals are in `analysis/w3/aggregates/w3_replicates.json` and the generated figures.

## RF Channel Context

- Wi-Fi AP: netis WF2419, firmware `V2.2.36123`.
- The AP was later found to use Auto channel selection, so the AP channel for `R600-R639` is unknown from preserved metadata and may have changed after restarts.
- During `R640-R659`, the AP was observed on channel 1, channel width 40 MHz, control sideband Upper.
- Zigbee: channel 20.
- BLE legacy advertising: primary advertising channels 37, 38, and 39 (`2402`, `2426`, and `2480 MHz`).

The Wi-Fi and Zigbee W3 results therefore represent system-level robustness under the tested 2.4 GHz background-load condition, not a channel-specific Wi-Fi/Zigbee coexistence experiment. For BLE, the observed `R640-R659` channel-1 40 MHz upper-sideband setting likely overlaps advertising channels 37 and 38, so the BLE results should be treated as shared-load behavior rather than a clean single-advertising-channel overlap test.

Focused AP-channel extensions were completed separately from the main W3 aggregate: BLE runs `R660-R677` use 20 MHz AP width on channels 1, 6, and 13 to target advertising channels 37, 38, and 39; Zigbee runs `R678-R697` use AP channel 1 as a 20 MHz non-overlap/control block and AP channel 9 as the Zigbee-channel-20 overlap block. Their dedicated analyses are in `analysis/w3/reports/w3_ble_channel_overlap.md` and `analysis/w3/reports/w3_zigbee_channel_overlap.md`.

## Measurement Caveat

Wi-Fi uses ESP32 MQTT publish-to-ACK RTT. Zigbee uses Home Assistant state-change time to logger receive time, median-normalized. BLE uses ESP32 advertiser timestamp to logger receive time, median-normalized. The comparison therefore emphasizes robustness trends, tail behavior, variability, and event reliability rather than absolute link-layer latency.

## Aggregate Metrics

| Protocol | Load | Runs | Median | P95 | MAD | Drop rate | Extra-event rate |
|---|---|---|---:|---:|---:|---:|---:|
| Wi-Fi | Baseline | `R600`, `R604`, `R608`, `R612`, `R616` | 13.24 ms | 19.83 ms | 1.05 ms | 0.0% | 0.0% |
| Wi-Fi | Light | `R601`, `R605`, `R609`, `R613`, `R617` | 13.44 ms | 22.88 ms | 1.61 ms | 0.0% | 0.0% |
| Wi-Fi | Moderate | `R602`, `R606`, `R610`, `R614`, `R618` | 13.96 ms | 24.17 ms | 1.93 ms | 0.0% | 0.0% |
| Wi-Fi | Heavy | `R603`, `R607`, `R611`, `R615`, `R619` | 15.68 ms | 24.05 ms | 3.38 ms | 1.4% | 0.0% |
| Zigbee | Baseline | `R620`, `R624`, `R628`, `R632`, `R636` | 0.00 ms | 10.12 ms | 1.79 ms | 0.0% | 0.0% |
| Zigbee | Light | `R621`, `R625`, `R629`, `R633`, `R637` | 0.00 ms | 10.97 ms | 1.93 ms | 0.0% | 0.0% |
| Zigbee | Moderate | `R622`, `R626`, `R630`, `R634`, `R638` | 0.00 ms | 10.19 ms | 2.22 ms | 0.0% | 0.8% |
| Zigbee | Heavy | `R623`, `R627`, `R631`, `R635`, `R639` | 0.00 ms | 10.73 ms | 2.07 ms | 0.0% | 0.8% |
| BLE | Baseline | `R640`, `R644`, `R648`, `R652`, `R656` | 0.00 ms | 210.29 ms | 89.34 ms | 2.4% | 0.0% |
| BLE | Light | `R641`, `R645`, `R649`, `R653`, `R657` | 0.00 ms | 173.75 ms | 78.75 ms | 3.2% | 0.0% |
| BLE | Moderate | `R642`, `R646`, `R650`, `R654`, `R658` | 0.00 ms | 169.68 ms | 75.31 ms | 2.8% | 0.0% |
| BLE | Heavy | `R643`, `R647`, `R651`, `R655`, `R659` | 0.00 ms | 151.47 ms | 87.28 ms | 2.4% | 0.0% |

## Change vs Protocol Baseline

| Protocol | Load | P95 change | MAD change |
|---|---|---:|---:|
| Wi-Fi | Light | +15.4% | +52.7% |
| Wi-Fi | Moderate | +21.8% | +83.3% |
| Wi-Fi | Heavy | +21.3% | +221.7% |
| Zigbee | Light | +8.4% | +7.9% |
| Zigbee | Moderate | +0.6% | +24.1% |
| Zigbee | Heavy | +6.0% | +15.5% |
| BLE | Light | -17.4% | -11.9% |
| BLE | Moderate | -19.3% | -15.7% |
| BLE | Heavy | -28.0% | -2.3% |

## Interpretation

- Wi-Fi W3 shows increasing tail latency and variability under load. P95 rises from 19.83 ms at baseline to 24.17 ms at moderate load and 24.05 ms at heavy load.
- Zigbee W3 remains tightly bounded across the same load levels. P95 stays near 10.12 ms to 10.73 ms, with no missing events in the completed Zigbee runs.
- The main Zigbee quality signal is not event loss, but occasional extra state events: the moderate group averages 0.8% and the heavy group averages 0.8% extra events, driven by R627, R638, and R639.
- BLE W3 is interpreted through median-normalized advertisement capture latency and missed-advertisement rate. Heavy-load P95 is 151.47 ms with a drop rate of 2.4%.
- Under this W3 setup, Zigbee is less sensitive to Wi-Fi iperf load in latency-tail terms, while Wi-Fi is more affected by shared-network contention at the tail and variability levels.

## Generated Artifacts

- `analysis/w3/aggregates/w3_replicates.json`
- `analysis/w3/figures/w3_latency_plot_ci.png`
- `analysis/w3/figures/w3_mad_drop_plot_ci.png`
- `analysis/w3/figures/w3_protocol_p95_comparison_ci.png`
- `analysis/w3/figures/w3_protocol_mad_anomaly_comparison_ci.png`
- `analysis/w3/tables/w3_protocol_comparison.csv`
