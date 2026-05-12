# Run R622 Notes

## Status
Complete. This rerun replaces the previous invalid `R622` attempt archived separately.

## Run Command
```bash
EXP_RUN_ID=R622 ./run_all.sh \
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

Home Assistant credentials were loaded from local environment configuration and are intentionally not recorded.

## Verification
- Trigger schedule: 100 commands, all HTTP 200, no errors.
- MQTT events: 100 rows, 100 unique event identities.
- Missing events: 0
- Extra events: 0
- Duplicate payload rows: 0
- iPerf: 20.01 Mbps mean over 368 samples.
- Command-start to HA delay: 106.80-187.54 ms, no spikes over 500 ms.

## Results
- MAD latency: 2.13 ms
- P95 latency: 10.18 ms
- Max latency: 11.28 ms
- Impact vs `R620`: negligible
