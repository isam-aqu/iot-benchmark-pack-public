# Run R626 Notes

## Status
Complete. Retain as Zigbee moderate-load replicate 1.

## Run Command
```bash
EXP_RUN_ID=R626 ./run_all.sh \
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

## Verification
- Trigger schedule: 100 commands, all HTTP 200, no errors.
- MQTT events: 100 rows, 100 unique event identities.
- Missing events: 0
- Extra events: 0
- Duplicate payload rows: 0
- iPerf: 20.02 Mbps mean over 368 samples.
- Command-start to HA delay: 123.63-189.82 ms, no spikes over 500 ms.

## Results
- MAD latency: 1.85 ms
- P95 latency: 10.60 ms
- Max latency: 13.63 ms
- Impact vs `R620`: negligible
