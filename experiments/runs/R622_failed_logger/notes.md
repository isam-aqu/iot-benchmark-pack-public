# Run R622 Notes

## Purpose
Moderate Wi-Fi interference run for the W3 Zigbee automated comparison group.

## Status
Invalid. Do not use as the formal moderate-load Zigbee result.

## Configuration
- Workload: W3
- Protocol: Zigbee
- Run type: load
- Comparison group: `W3_zigbee_auto`
- Replicate ID: primary
- Baseline reference: `R620`
- Topology: near
- Interference: iperf
- Load level: moderate, 20 Mbps TCP
- Entity: `light.benchmark_device`
- Event schedule: automatic, 3000 ms nominal interval with 250 ms jitter
- Timestamp source: Home Assistant `ha_time` plus laptop logger `pi_rx_time_ns`
- Pipeline version: 0.4.3

## Run Command
```bash
EXP_RUN_ID=R622 ./run_all.sh \
  --run-id W3_zigbee_auto_moderate \
  --disable-ble \
  --disable-ack \
  --duration-sec 360 \
  --iperf-load moderate \
  --zigbee-trigger \
  --zigbee-entity-id light.benchmark_device \
  --zigbee-events 100 \
  --zigbee-base-interval-ms 3000 \
  --zigbee-jitter-ms 250
```

Home Assistant credentials were loaded from local environment configuration and are intentionally not recorded in the command.

## Load Verification
- iPerf profile: 20 Mbps TCP
- Interval samples: 368
- Mean interval throughput: 20.02 Mbps
- Standard deviation: 0.45 Mbps
- Min / max interval throughput: 19.00 / 26.50 Mbps

## Data Quality
- Expected trigger commands: 100
- Trigger commands recorded: 76
- HTTP 200 trigger commands: 75
- Trigger errors: 1
- Captured MQTT events: 75
- Missing events relative to planned experiment: 25
- Duplicate payload rows: 0

## Failure Details
- Command 76 timed out.
- The trigger driver stopped after the timeout, so commands 77-100 were never issued.
- Many `off` commands had command-start to HA state-change delays around 5.3 s.
- The runner metadata still says `status: complete`, but the trigger schedule proves the experiment is invalid.

## Validity
Status: invalid. Rerun `R622` before moving to conclusions for moderate Zigbee interference.
