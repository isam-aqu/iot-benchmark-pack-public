# Run R637 Notes

## Status
Complete. Zigbee light replicate 4; 100/100 events; iperf mean 5.00 Mbps; P95 11.4 ms; no command-delay spikes

## Run Command
```bash
EXP_RUN_ID=R637 ./run_all.sh --run-id W3_zigbee_auto_light --disable-ble --disable-ack --duration-sec 360 --iperf-load light --zigbee-trigger --zigbee-entity-id light.benchmark_device --zigbee-events 100 --zigbee-base-interval-ms 3000 --zigbee-jitter-ms 250
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
- Command-start to HA delay: 179.35-245.75 ms across 100 matched commands.

## Results
- MAD latency: 1.56 ms
- P95 latency: 11.45 ms
- Max latency: 16.09 ms
- Impact label: negligible

## Anomalies
- None observed.
