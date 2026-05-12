# Experiment Protocol

> **Version:** 0.4.6
> **Source of truth:** `experiments/version_info.yaml`

------------------------------------------------------------------------

## 🧾 Home Assistant Environment (Record Per Run)

-   Installation method: **Home Assistant OS**
-   Core: **2026.3.4**
-   Supervisor: **2026.03.2**
-   Operating System: **17.1**
-   Frontend: **20260312.1**

------------------------------------------------------------------------

## ⚠️ Measurement Requirement (Critical)

-   Logger MUST be **Ethernet-connected**
-   Laptop Wi-Fi MUST be **disabled**

This avoids RF contention and ensures valid latency measurements.

------------------------------------------------------------------------

## 0. System Validation (Pre-Experiment)

Before running formal workloads:

-   Verify MQTT connectivity
-   Verify ACK response (Wi-Fi RTT)
-   Verify Zigbee → MQTT pipeline
-   Verify BLE advertisements are detected
-   Run small test (10--20 events)

⚠️ Not part of W1--W5.

------------------------------------------------------------------------

## Suggested First Pilot

-   1 Wi-Fi node
-   1 BLE node
-   1 Zigbee device
-   Near topology
-   Quiet network
-   50--100 events

------------------------------------------------------------------------

## Workloads

W1--W2 = baseline latency and telemetry energy characterization
W3 = interference robustness across protocols
W4--W5 = future spatial and deployment-scale robustness conditions

------------------------------------------------------------------------

### W1 Instant Actuation (Latency)

-   Button / event trigger
-   Measure:
    -   end-to-end latency
    -   Wi-Fi RTT

------------------------------------------------------------------------

### W2 Periodic Telemetry

-   Fixed-interval Wi-Fi telemetry under the revised W2 v2 method
-   Use matched `control` vs `telemetry` runs at the same interval
-   Log power over the serial path only; reserve MQTT for telemetry events

Measure:
- mean power / total energy
- per-event incremental energy
- jitter / reliability as supporting metrics
- detectability relative to matched-control variability

------------------------------------------------------------------------

### W3 Interference Robustness (2.4 GHz Load)

-   Apply calibrated background traffic using `iperf3`
-   Wi-Fi W3 is complete
-   Zigbee W3 is complete for `R620`--`R639`
-   BLE W3 is complete for `R640`--`R659`

Host:
- `iperf-server` (<private-ip>)

RF/channel context for the completed W3 runs:
- Wi-Fi AP: netis WF2419, firmware `V2.2.36123`
- The AP was later found to use Auto channel selection, so the AP channel used
  for `R600`--`R639` is unknown from preserved metadata and may have changed
  after restarts.
- During `R640`--`R659`, the AP was observed on channel 1, channel width
  40 MHz, control sideband Upper.
- Zigbee: channel 20
- BLE legacy advertising: primary advertising channels 37, 38, and 39
  (`2402`, `2426`, and `2480 MHz`)
- Starting with runs `R678` and later, AP RF fields are captured in
  `run_metadata.json` and `docs/run_sheet.csv`: model, firmware, channel mode,
  primary channel, width, control sideband, and value source.

Interpretation note:
- The completed Wi-Fi and Zigbee W3 runs (`R600`--`R639`) are
  shared-environment robustness tests rather than a channel-specific
  Wi-Fi/Zigbee co-channel study, because the AP channel was not recorded.
- BLE uses legacy advertising channels 37, 38, and 39. During `R640`--`R659`,
  the observed 40 MHz upper-sideband channel-1 AP setup likely overlaps
  advertising channels 37 and 38. Completed runs `R660`--`R677` use AP channels
  1, 6, and 13 at 20 MHz width to target advertising channels 37, 38, and 39
  separately; they did not show a clear channel-specific heavy-load degradation
  pattern for BLE P95 latency.
- Completed Zigbee AP-channel extension runs `R678`--`R697` use AP channel 1
  at 20 MHz as a non-overlap/control block and AP channel 9 at 20 MHz as the
  Zigbee-channel-20 overlap block, with five paired baseline/heavy replicates
  per AP setting. The dedicated analysis is in
  `analysis/w3/reports/w3_zigbee_channel_overlap.md`.

Measure:
- median and tail latency degradation
- variability under load
- reliability / drop-rate changes

------------------------------------------------------------------------

### W4 Spatial Robustness

-   Distance / walls

Measure:
- signal impact
- latency increase

------------------------------------------------------------------------

### W5 Multi-Node / Deployment Robustness

-   Multiple nodes or rooms active

Measure:
- congestion
- packet loss
- delay increase

------------------------------------------------------------------------

## Logging Guidance

-   Use `EXP_RUN_ID=Rxxx`
-   Use unique `RUN_ID`
-   Example:

```bash
EXP_RUN_ID=R106 ./run_all.sh --run-id W1_wifi_near_quiet_v6 --disable-ble
```

Record:
- firmware version
- Home Assistant version
- Wi-Fi AP model, firmware, channel mode, primary channel, width, sideband, and
  whether values came from AP UI, client scan, or another source
- Zigbee coordinator/channel
- BLE advertising channel map if explicitly changed

AP RF automation note: `run_all.sh` stores the AP RF values passed through
`--ap-*` options. Independent automatic verification is possible only if a
separate Wi-Fi client/probe is associated with the AP; the logger laptop Wi-Fi
should remain disabled during measurements.

------------------------------------------------------------------------

## Minimum Repetitions

-   50 → pilot
-   100 → baseline
-   200+ → final

------------------------------------------------------------------------

## Experiment Order

1.  W1 corrected baseline
2.  W2 telemetry energy
3.  W3 interference robustness (Wi-Fi, Zigbee, and BLE complete)
4.  W4 spatial robustness
5.  W5 multi-node / multi-room robustness

------------------------------------------------------------------------

## Version Tracking

-   pipeline_version: 0.4.7
-   firmware_version: 0.4.1
-   logger_version: 0.4.1
-   analysis_version: 0.4.5
-   ha_automation_version: 0.4.0
-   experiment_protocol_version: 0.4.6

------------------------------------------------------------------------

## W3 Interference Procedure

The completed Wi-Fi, Zigbee, and BLE portions of W3 are maintained in
[`docs/w3_experiment_procedure.md`](./w3_experiment_procedure.md).

Refer to that document for the complete objective, run setup, execution steps,
quality checks, and analysis workflow for the W3 interference experiments.

In this protocol, W3 should be treated as the interference robustness campaign.
The Wi-Fi, Zigbee, and BLE subsets are complete through `R659`.
These subsets should be documented without
reclassifying W3 as a different workload.

Per-run records still live alongside the experiment outputs, including
`manifest.yaml`, `notes.md`, and analysis JSON files.

To avoid documentation drift, do not duplicate or update the detailed W3
commands here; update only `docs/w3_experiment_procedure.md`.
