# Run R638 Notes

## Status
Complete with extra events. Zigbee moderate replicate 4; 100/100 commands; 104 state events; iperf mean 20.00 Mbps; extra-event rate 4%

## Run Command
```bash
EXP_RUN_ID=R638 ./run_all.sh --run-id W3_zigbee_auto_moderate --disable-ble --disable-ack --duration-sec 360 --iperf-load moderate --zigbee-trigger --zigbee-entity-id light.benchmark_device --zigbee-events 100 --zigbee-base-interval-ms 3000 --zigbee-jitter-ms 250
```

Home Assistant credentials were loaded from local environment configuration and are intentionally not recorded.

## Verification
- Trigger schedule: 100 commands, all HTTP 200, no errors.
- MQTT state events: 104 rows.
- Expected events: 100
- Missing events: 0
- Extra events: 4
- Repeated HA event/context rows: 4
- Duplicate payload rows: 0
- iPerf: 20.00 Mbps mean over 368 samples.
- Command-start to HA delay: 184.40-5350.81 ms across 100 matched commands.

## Results
- MAD latency: 1.86 ms
- P95 latency: 11.19 ms
- Max latency: 12.97 ms
- Impact label: negligible

## Anomalies
- 4 extra state events; repeated_event_id_rows=4.
- Command-delay spikes: command 20 1797.612 ms, command 62 1789.644 ms, command 78 5350.811 ms, command 84 5337.651 ms.

## Extra Event Detail
- Row 22: on->off at 2026-04-30T19:05:10.007081+03:00 with event_id 01KQFJ63C4X6X50FE6S1M3SSPP
- Row 23: off->on at 2026-04-30T19:05:12.509890+03:00 with event_id 01KQFJ63C4X6X50FE6S1M3SSPP
- Row 66: on->off at 2026-04-30T19:07:16.062516+03:00 with event_id 01KQFJ9YEA1HAB4VRZMMZB8533
- Row 67: off->on at 2026-04-30T19:07:18.565864+03:00 with event_id 01KQFJ9YEA1HAB4VRZMMZB8533
