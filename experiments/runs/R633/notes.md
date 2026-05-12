# Run R633 Notes

## Status
Complete. Zigbee light replicate 3; 100/100 events; iperf mean 5.00 Mbps; P95 11.4 ms; max 32.5 ms

## Run Command
```bash
EXP_RUN_ID=R633 ./run_all.sh --run-id W3_zigbee_auto_light --disable-ble --disable-ack --duration-sec 360 --iperf-load light --zigbee-trigger --zigbee-entity-id light.benchmark_device --zigbee-events 100 --zigbee-base-interval-ms 3000 --zigbee-jitter-ms 250
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
- iPerf: 5.00 Mbps mean over 367 samples.
- Command-start to HA delay: 166.19-249.55 ms across 100 matched commands.

## Results
- MAD latency: 1.74 ms
- P95 latency: 11.41 ms
- Max latency: 32.48 ms
- Impact label: high

## Anomalies
- None observed.
