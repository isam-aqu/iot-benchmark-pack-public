# Run R632 Notes

## Status
Complete. Zigbee baseline replicate 3; 100/100 events; P95 8.2 ms; no command-delay spikes

## Run Command
```bash
EXP_RUN_ID=R632 ./run_all.sh --run-id W3_zigbee_auto_baseline --disable-ble --disable-ack --duration-sec 360 --iperf-load 0 --zigbee-trigger --zigbee-entity-id light.benchmark_device --zigbee-events 100 --zigbee-base-interval-ms 3000 --zigbee-jitter-ms 250
```

Home Assistant credentials were loaded from local environment configuration and are intentionally not recorded.

## Verification
- Trigger schedule: 100 commands, all HTTP 200, no errors.
- MQTT state events: 100 rows.
- Expected events: 100
- Missing events: 0
- Extra events: 0
- Repeated HA event/context rows: 0
- Duplicate payload rows: 0
- Command-start to HA delay: 165.14-229.56 ms across 100 matched commands.

## Results
- MAD latency: 1.40 ms
- P95 latency: 8.24 ms
- Max latency: 15.00 ms
- Impact label: baseline

## Anomalies
- None observed.
