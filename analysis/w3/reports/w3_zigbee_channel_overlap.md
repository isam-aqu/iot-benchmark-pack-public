# W3 Zigbee AP-Channel Overlap Extension

Generated: 2026-05-11T17:34:16+03:00

## Scope

- Runs: `R678-R697`.
- Protocol: Zigbee channel 20, measured from Home Assistant state-change time to logger receive time and median-normalized.
- AP settings: manually fixed 20 MHz Wi-Fi channel 1 as the non-overlap/control block and channel 9 as the overlap block for Zigbee channel 20.
- Load levels: baseline and 50 Mbps TCP heavy load, five matched baseline/heavy pairs per AP setting.
- AP RF fields are recorded in `run_metadata.json` and `docs/run_sheet.csv` for every run in this extension.

## Aggregate Results

| AP channel | Zigbee exposure | Load | Runs | P95 mean [95% CI] | MAD mean [95% CI] | Missing mean | Extra mean | Repeated-row mean | iPerf mean |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 | control / non-overlap with Zigbee ch20 | baseline | `R678, R680, R682, R684, R686` | 10.76 [9.50, 12.03] ms | 1.74 [1.52, 1.95] ms | 0.00/100 | 0.00/100 | 0.00/100 | - |
| 1 | control / non-overlap with Zigbee ch20 | heavy | `R679, R681, R683, R685, R687` | 10.38 [9.39, 11.36] ms | 1.69 [1.26, 2.11] ms | 0.00/100 | 0.40/100 | 0.40/100 | 49.99 Mbps |
| 9 | overlap with Zigbee ch20 | baseline | `R688, R690, R692, R694, R696` | 9.88 [8.82, 10.94] ms | 2.23 [1.78, 2.67] ms | 0.00/100 | 0.00/100 | 0.00/100 | - |
| 9 | overlap with Zigbee ch20 | heavy | `R689, R691, R693, R695, R697` | 10.60 [10.08, 11.11] ms | 2.22 [1.75, 2.70] ms | 0.00/100 | 0.80/100 | 1.20/100 | 49.99 Mbps |

## Paired Heavy-vs-Baseline Delta

| AP channel | Zigbee exposure | Pairs | P95 delta mean [95% CI] | P95 delta % | Paired t-test p | Wilcoxon p | MAD delta mean [95% CI] | Missing delta | Extra delta | Repeated-row delta |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | control / non-overlap with Zigbee ch20 | 5 | -0.38 [-2.08, 1.31] ms | -3.6% | 0.564 | 0.812 | -0.05 [-0.47, 0.37] ms | +0.00/100 | +0.40/100 | +0.40/100 |
| 9 | overlap with Zigbee ch20 | 5 | 0.71 [-0.52, 1.95] ms | +7.2% | 0.183 | 0.312 | -0.01 [-0.43, 0.41] ms | +0.00/100 | +0.80/100 | +1.20/100 |

## Channel-Overlap Contrast

- Mean P95 delta under AP channel 1 control: -0.38 ms.
- Mean P95 delta under AP channel 9 overlap: +0.71 ms.
- Difference-in-differences, overlap minus control: +1.10 ms.
- Two-sample comparison of paired P95 deltas: Welch p = 0.188, Mann-Whitney p = 0.222.

## Interpretation

- All 20 runs completed with 100 scheduled Zigbee commands per run.
- No missing Zigbee events occurred in either AP-channel block.
- AP channel 9 overlap produced a small positive mean P95 shift relative to its matched baselines, while the AP channel 1 control block shifted slightly negative.
- The channel-overlap contrast is approximately +1.10 ms in P95, but the five-pair extension does not provide strong statistical evidence of a large channel-specific degradation under the tested 50 Mbps TCP load.
- Heavy-load state-accounting anomalies remain the main Zigbee reliability signal: one channel-1 heavy run has two extra state rows, while channel-9 heavy runs include two one-row repeats and one four-row extra/repeat run.

## Generated Artifacts

- `analysis/w3/tables/w3_zigbee_channel_overlap_runs.csv`
- `analysis/w3/tables/w3_zigbee_channel_overlap_pairs.csv`
- `analysis/w3/tables/w3_zigbee_channel_overlap_summary.csv`
