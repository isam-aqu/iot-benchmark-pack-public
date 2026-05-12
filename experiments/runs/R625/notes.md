# Run R625 Notes

## Status
Complete. Retain as Zigbee light-load replicate 1.

## Run Command
```bash
EXP_RUN_ID=R625 ./run_all.sh \
  --run-id W3_zigbee_auto_light \
  --disable-ble \
  --disable-ack \
  --duration-sec 360 \
  --iperf-load light \
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
- iPerf: 5.00 Mbps mean over 367 samples.
- One command-start to HA state-change delay spike occurred at command 50, about 5.26 s.

## Results
- MAD latency: 2.24 ms
- P95 latency: 9.59 ms
- Max latency: 10.35 ms
- Impact vs `R620`: negligible
