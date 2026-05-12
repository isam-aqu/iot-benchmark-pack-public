# Run R631 Notes

## Status
Complete with latency spike. Zigbee heavy replicate 2; 100/100 events; iperf mean 49.96 Mbps; P95 10.6 ms; HA-to-logger max 416 ms and 3 command-delay spikes

## Run Command
```bash
EXP_RUN_ID=R631 ./run_all.sh --run-id W3_zigbee_auto_heavy --disable-ble --disable-ack --duration-sec 360 --iperf-load heavy --zigbee-trigger --zigbee-entity-id light.benchmark_device --zigbee-events 100 --zigbee-base-interval-ms 3000 --zigbee-jitter-ms 250
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
- iPerf: 49.96 Mbps mean over 368 samples.
- Command-start to HA delay: 153.94-5311.79 ms across 100 matched commands.

## Results
- MAD latency: 1.57 ms
- P95 latency: 10.55 ms
- Max latency: 416.29 ms
- Impact label: severe

## Anomalies
- Command-delay spikes: command 20 5307.251 ms, command 28 5311.789 ms, command 29 3087.132 ms.
- HA-to-logger normalized latency spike: max 416.294 ms.
