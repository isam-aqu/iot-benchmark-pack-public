# Run R634 Notes

## Status
Complete. Zigbee moderate replicate 3; 100/100 events; iperf mean 20.00 Mbps; P95 9.2 ms; no command-delay spikes

## Run Command
```bash
EXP_RUN_ID=R634 ./run_all.sh --run-id W3_zigbee_auto_moderate --disable-ble --disable-ack --duration-sec 360 --iperf-load moderate --zigbee-trigger --zigbee-entity-id light.benchmark_device --zigbee-events 100 --zigbee-base-interval-ms 3000 --zigbee-jitter-ms 250
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
- iPerf: 20.00 Mbps mean over 368 samples.
- Command-start to HA delay: 165.30-254.71 ms across 100 matched commands.

## Results
- MAD latency: 2.56 ms
- P95 latency: 9.18 ms
- Max latency: 20.82 ms
- Impact label: negligible

## Anomalies
- None observed.
