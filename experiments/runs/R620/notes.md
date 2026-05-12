# Run R620 Notes

## Purpose
Quiet W3 Zigbee automated baseline for the `W3_zigbee_auto` comparison group.

## Status
Complete. Retain as the primary W3 Zigbee baseline, with one actuation-side timing anomaly noted below.

## Configuration
- Workload: W3
- Protocol: Zigbee
- Run type: baseline
- Comparison group: `W3_zigbee_auto`
- Replicate ID: primary
- Topology: near
- Interference: quiet
- Load level: baseline
- Entity: `light.benchmark_device`
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: Home Assistant `ha_time` plus laptop logger `pi_rx_time_ns`
- Pipeline version: 0.4.2

## Run Command
```bash
EXP_RUN_ID=R620 ./run_all.sh \
  --run-id W3_zigbee_auto_baseline \
  --disable-ble \
  --disable-ack \
  --duration-sec 360 \
  --iperf-load 0 \
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

## Results
- Expected events: 100
- Actual events: 100
- Missing events: 0
- Event loss: 0%
- Duplicate payload rows: 0
- Mean normalized latency: 2.16 ms
- Median normalized latency: 0.00 ms
- MAD latency: 1.46 ms
- P95 latency: 11.22 ms
- P99 latency: 12.79 ms
- Maximum normalized latency: 13.41 ms
- Mean observed event interval: 2988.75 ms

## Trigger Integrity
- Trigger schedule contains 100 commands.
- All trigger commands returned HTTP 200.
- State transitions are balanced:
  - 50 `off -> on`
  - 50 `on -> off`
- Event IDs are unique.

## Anomalies
- One actuation-side command-to-HA-state delay occurred at command 51.
- Command 51 took about 5.18 s from service-call send time to HA state-change timestamp.
- This caused one long observed event interval followed by short catch-up intervals.
- The W3 Zigbee latency metric is anchored at HA state-change time, so this anomaly is not included in the `ha_time -> pi_rx_time_ns` latency value, but it should be noted when discussing actuation responsiveness.

## Validity
Status: complete. Retain as the primary W3 Zigbee baseline for HA-to-logger latency and reliability. Use later baseline replicates to determine whether the command-to-state delay recurs.
