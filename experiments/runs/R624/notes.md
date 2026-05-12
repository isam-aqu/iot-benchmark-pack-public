# Run R624 Notes

## Status
Complete. Retain as Zigbee baseline replicate 1 for `W3_zigbee_auto`.

## Run Command
```bash
EXP_RUN_ID=R624 ./run_all.sh \
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

## Verification
- Trigger schedule: 100 commands, all HTTP 200, no errors.
- MQTT events: 100 rows, 100 unique event identities.
- Missing events: 0
- Extra events: 0
- Duplicate payload rows: 0
- Command-start to HA delay: 113.54-180.79 ms, no spikes over 500 ms.

## Results
- MAD latency: 1.87 ms
- P95 latency: 10.57 ms
- Max latency: 11.70 ms
