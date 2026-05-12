# Run R635 Notes

## Status
Complete. Zigbee heavy replicate 3; 100/100 events; iperf mean 49.96 Mbps; P95 11.8 ms; one command-delay spike

## Run Command
```bash
EXP_RUN_ID=R635 ./run_all.sh --run-id W3_zigbee_auto_heavy --disable-ble --disable-ack --duration-sec 360 --iperf-load heavy --zigbee-trigger --zigbee-entity-id light.benchmark_device --zigbee-events 100 --zigbee-base-interval-ms 3000 --zigbee-jitter-ms 250
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
- Command-start to HA delay: 170.04-5332.09 ms across 100 matched commands.

## Results
- MAD latency: 1.57 ms
- P95 latency: 11.79 ms
- Max latency: 28.40 ms
- Impact label: moderate

## Anomalies
- Command-delay spikes: command 94 5332.088 ms.
