# Run R639 Notes

## Status
Complete with extra events. Zigbee heavy replicate 4; 100/100 commands; 102 state events; iperf mean 49.97 Mbps; extra-event rate 2%

## Run Command
```bash
EXP_RUN_ID=R639 ./run_all.sh --run-id W3_zigbee_auto_heavy --disable-ble --disable-ack --duration-sec 360 --iperf-load heavy --zigbee-trigger --zigbee-entity-id light.benchmark_device --zigbee-events 100 --zigbee-base-interval-ms 3000 --zigbee-jitter-ms 250
```

Home Assistant credentials were loaded from local environment configuration and are intentionally not recorded.

## Verification
- Trigger schedule: 100 commands, all HTTP 200, no errors.
- MQTT state events: 102 rows.
- Expected events: 100
- Missing events: 0
- Extra events: 2
- Repeated HA event/context rows: 2
- Duplicate payload rows: 0
- iPerf: 49.97 Mbps mean over 368 samples.
- Command-start to HA delay: 189.24-270.02 ms across 100 matched commands.

## Results
- MAD latency: 2.31 ms
- P95 latency: 8.99 ms
- Max latency: 10.99 ms
- Impact label: negligible

## Anomalies
- 2 extra state events; repeated_event_id_rows=2.

## Extra Event Detail
- Row 24: on->off at 2026-04-30T19:21:55.355251+03:00 with event_id 01KQFK4RCWCT90Z7QTEX07TR3W
- Row 25: off->on at 2026-04-30T19:21:56.776245+03:00 with event_id 01KQFK4RCWCT90Z7QTEX07TR3W
