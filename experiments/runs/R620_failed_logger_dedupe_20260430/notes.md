# Run R620 Notes

## Purpose
Quiet W3 Zigbee automated baseline for the `W3_zigbee_auto` comparison group.

## Status
Failed / invalid capture.

## Setup
- Workload: W3
- Protocol: Zigbee
- Entity: `light.benchmark_device`
- Trigger: Home Assistant REST service calls through `python/ha_zigbee_trigger.py`
- Schedule: 100 commands at `3000±250 ms`
- Interference: quiet / no iperf load
- Logger: Ethernet-connected laptop, Wi-Fi disabled

## Data Quality
- Runner completed with exit code 0.
- Trigger schedule contains 100 commands.
- All trigger commands returned HTTP 200.
- MQTT log contains only 1 Zigbee state-change event.
- Analysis reports 1 actual event out of 100 expected events.
- Drop rate is therefore 99%.

## Interpretation
This run must not be retained as the W3 Zigbee baseline. The Home Assistant
REST calls were accepted, but the Zigbee entity did not produce corresponding
state-change events after the first `off -> on` transition. This suggests the
device state did not continue toggling, the entity was not reachable/responding
after the first command, or Home Assistant did not observe/report the later
state changes.

Follow-up diagnosis showed that Home Assistant did record later state changes.
The actual root cause was the MQTT logger duplicate filter: Zigbee events used
`seq=0` and `t_local_us=0`, so all later Zigbee events looked duplicate to the
logger. The logger was fixed in pipeline `0.4.2` / logger `0.4.1` to include
`event_id`, `ha_context_id`, and state-change fields in the event dedupe key.
A four-event probe after the fix captured all four events.

## Next Step
Rerun formal R620 with pipeline `0.4.2` or newer before moving to R621.
