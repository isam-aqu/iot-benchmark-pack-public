# Run R627 Notes

## Status
Complete with anomaly. Retain as Zigbee heavy-load replicate 1, but flag the extra state transitions in analysis.

## Run Command
```bash
EXP_RUN_ID=R627 ./run_all.sh \
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

## Verification
- Trigger schedule: 100 commands, all HTTP 200, no errors.
- MQTT state events: 102 rows.
- Unique event identities: 102
- Expected commands: 100
- Missing events: 0
- Extra events: 2
- Repeated HA event/context id rows: 2
- Duplicate payload rows: 0
- iPerf: 49.94 Mbps mean over 368 samples.
- Command-start to HA delay for matched commands: 121.14-197.35 ms, no spikes over 500 ms.

## Extra Event Detail
One HA context id appeared on three distinct transitions around 16:52:25-16:52:28:
- `off -> on`
- `on -> off`
- `off -> on`

The extra `on -> off` and `off -> on` transitions happened between command 83 and command 84. They are retained as extra state events, not deduplicated away.

## Results
- MAD latency: 2.38 ms
- P95 latency: 10.85 ms
- Max latency: 16.18 ms
- Extra-event rate: 2%
