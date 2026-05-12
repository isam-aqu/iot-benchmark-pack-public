# Run R621 Notes

## Purpose
Light Wi-Fi interference run for the W3 Zigbee automated comparison group.

## Status
Complete. Retain as the primary W3 Zigbee light-load run against baseline `R620`.

## Configuration
- Workload: W3
- Protocol: Zigbee
- Run type: load
- Comparison group: `W3_zigbee_auto`
- Replicate ID: primary
- Baseline reference: `R620`
- Topology: near
- Interference: iperf
- Load level: light, 5 Mbps TCP
- Entity: `light.benchmark_device`
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: Home Assistant `ha_time` plus laptop logger `pi_rx_time_ns`
- Pipeline version: 0.4.3

## Run Command
```bash
EXP_RUN_ID=R621 ./run_all.sh \
  --run-id W3_zigbee_auto_light \
  --disable-ble \
  --disable-ack \
  --duration-sec 360 \
  --iperf-load light \
  --zigbee-trigger \
  --zigbee-entity-id light.benchmark_device \
  --zigbee-events 100 \
  --zigbee-base-interval-ms 3000 \
  --zigbee-jitter-ms 250
```

Home Assistant credentials were loaded from local environment configuration and are intentionally not recorded in the command.

## Data Processing
- Summarized with `python/summarize_w3_run.py --expected-events 100`
- Compared with baseline using `python/analyze_w3_run.py`
- Latency source: median-normalized `ha_time -> pi_rx_time_ns`
- Reliability source: unique Home Assistant `event_id` values

## Load Verification
- iPerf profile: 5 Mbps TCP
- Interval samples: 367
- Mean interval throughput: 5.00 Mbps
- Standard deviation: 0.44 Mbps
- Min / max interval throughput: 4.18 / 5.29 Mbps

## Results
- Expected events: 100
- Actual events: 100
- Missing events: 0
- Event loss: 0%
- Duplicate payload rows: 0
- Mean normalized latency: 1.62 ms
- Median normalized latency: 0.00 ms
- MAD latency: 2.71 ms
- P95 latency: 11.52 ms
- P99 latency: 11.81 ms
- Maximum normalized latency: 12.04 ms
- Mean observed event interval: 3000.41 ms

## Baseline Comparison
- Baseline: `R620`
- P95 increase vs baseline: +0.31 ms, about +2.75%
- Mean latency change vs baseline: -0.54 ms
- Drop-rate change vs baseline: 0
- Impact label: negligible

## Trigger Integrity
- Trigger schedule contains 100 commands.
- All trigger commands returned HTTP 200.
- State transitions are balanced:
  - 50 `off -> on`
  - 50 `on -> off`
- Event IDs are unique.

## Anomalies
- None observed.
- Command-start to HA state-change delay stayed between 111.31 ms and 174.90 ms.

## Validity
Status: complete. Retain as the primary W3 Zigbee light-load run.
