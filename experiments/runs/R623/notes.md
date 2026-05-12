# Run R623 Notes

## Purpose
Heavy Wi-Fi interference run for the W3 Zigbee automated comparison group.

## Status
Complete. Retain as the primary W3 Zigbee heavy-load run against baseline `R620`.

## Configuration
- Workload: W3
- Protocol: Zigbee
- Run type: load
- Comparison group: `W3_zigbee_auto`
- Replicate ID: primary
- Baseline reference: `R620`
- Topology: near
- Interference: iperf
- Load level: heavy, 50 Mbps TCP
- Entity: `light.benchmark_device`
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: Home Assistant `ha_time` plus laptop logger `pi_rx_time_ns`
- Pipeline version: 0.4.3

## Run Command
```bash
EXP_RUN_ID=R623 ./run_all.sh \
  --run-id W3_zigbee_auto_heavy \
  --disable-ble \
  --disable-ack \
  --duration-sec 360 \
  --iperf-load heavy \
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
- iPerf profile: 50 Mbps TCP
- Interval samples: 368
- Mean interval throughput: 49.98 Mbps
- Standard deviation: 0.59 Mbps
- Min / max interval throughput: 43.40 / 50.70 Mbps

## Results
- Expected events: 100
- Actual events: 100
- Missing events: 0
- Event loss: 0%
- Duplicate payload rows: 0
- Mean normalized latency: 2.55 ms
- Median normalized latency: 0.00 ms
- MAD latency: 2.50 ms
- P95 latency: 11.45 ms
- P99 latency: 13.41 ms
- Maximum normalized latency: 15.62 ms
- Mean observed event interval: 2991.09 ms

## Baseline Comparison
- Baseline: `R620`
- P95 increase vs baseline: +0.23 ms, about +2.08%
- Mean latency change vs baseline: +0.39 ms
- Drop-rate change vs baseline: 0
- Impact label: moderate

## Trigger Integrity
- Trigger schedule contains 100 commands.
- All trigger commands returned HTTP 200.
- State transitions are balanced:
  - 50 `off -> on`
  - 50 `on -> off`
- Event IDs are unique.

## Anomalies
- One actuation-side command-to-HA-state delay occurred at command 52.
- Command 52 took about 5.27 s from service-call send time to HA state-change timestamp.
- This caused one long observed event interval followed by a short catch-up interval.
- The HA-to-logger latency metric remained bounded.

## Validity
Status: complete. Retain as the primary W3 Zigbee heavy-load run.
