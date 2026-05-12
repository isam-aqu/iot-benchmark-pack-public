# W3 BLE AP-Channel Overlap Extension

Generated: 2026-05-03T07:14:26+03:00

## Scope

- Runs: `R660-R677`.
- Protocol: BLE legacy advertising, logger-side advertisement capture.
- AP settings: manually planned 20 MHz Wi-Fi channels 1, 6, and 13, targeting BLE advertising channels 37, 38, and 39 respectively.
- Load levels: baseline and 50 Mbps TCP heavy load, three replicates per AP channel and load.
- Caveat: AP channel/width is not independently encoded in the raw run metadata; channel labels are based on the manual/planned AP setting for each run block.

## Aggregate Results

| AP channel | Target BLE adv | Load | Runs | Captured mean | Missing mean | Drop mean | P95 mean | MAD mean | iPerf mean |
|---:|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | 37 | baseline | `R660, R662, R664` | 98.67/100 | 1.33 | 1.3% | 166.1 ms | 85.1 ms | - |
| 1 | 37 | heavy | `R661, R663, R665` | 98.67/100 | 1.33 | 1.3% | 145.8 ms | 85.3 ms | 50.00 Mbps |
| 6 | 38 | baseline | `R666, R668, R670` | 98.67/100 | 1.33 | 1.3% | 144.8 ms | 84.0 ms | - |
| 6 | 38 | heavy | `R667, R669, R671` | 98.67/100 | 1.33 | 1.3% | 150.3 ms | 81.5 ms | 50.00 Mbps |
| 13 | 39 | baseline | `R672, R674, R676` | 97.67/100 | 2.33 | 2.3% | 161.5 ms | 72.4 ms | - |
| 13 | 39 | heavy | `R673, R675, R677` | 98.67/100 | 1.33 | 1.3% | 142.1 ms | 84.8 ms | 50.00 Mbps |

## Heavy-vs-Baseline Delta

| AP channel | Target BLE adv | P95 delta | MAD delta | Missing-event delta |
|---:|---:|---:|---:|---:|
| 1 | 37 | -20.3 ms (-12.2%) | +0.2 ms | +0.00/100 |
| 6 | 38 | +5.6 ms (+3.9%) | -2.4 ms | +0.00/100 |
| 13 | 39 | -19.4 ms (-12.0%) | +12.5 ms | -1.00/100 |

## Interpretation

- All 18 runs completed at the device side with 100 scheduled advertisements.
- Logger capture remained high across the sweep, ranging from 94/100 to 100/100 per run.
- No AP channel shows a clear heavy-load degradation pattern in BLE P95 latency. Channel 6 / advertising channel 38 shows a small mean P95 increase under heavy load, while channels 1 and 13 show lower mean P95 under heavy load than baseline.
- The result is consistent with BLE advertisement/scanner timing variability dominating over a simple Wi-Fi-load monotonic effect in this setup.
- The channel 13 baseline group has the highest mean missing-event count because `R672` missed 6 advertisements; this should be treated as a run-level capture anomaly unless repeated in additional data.

## Generated Artifacts

- `analysis/w3/tables/w3_ble_channel_overlap_runs.csv`
- `analysis/w3/tables/w3_ble_channel_overlap_summary.csv`
- `analysis/w3/figures/w3_ble_channel_overlap_p95_missing.png`
