# Run R5XX Notes

## Purpose
W2 v2 <control/telemetry> run for the
<idle/0.5 s/1 s/2 s/3 s/4 s/5 s/6 s/7 s/8 s/9 s/10 s> condition using
the revised matched-pair energy methodology.

## Configuration
- Run ID: `<RUN_ID>`
- Comparison group: `<none for idle validation | W2_0.5s | W2_1s | W2_2s | W2_3s | W2_4s | W2_5s | W2_6s | W2_7s | W2_8s | W2_9s | W2_10s>`
- Replicate ID: `<primary/rep1/rep2>`
- Protocol: Wi-Fi
- Sensor: INA231
- Wi-Fi: connected
- MQTT session: connected
- Telemetry MQTT: `<enabled/disabled>`
- MQTT power reporting: disabled
- Periodic interval: `<0/500/1000/2000/3000/4000/5000/6000/7000/8000/9000/10000>` ms
- Power sample interval: 100 ms
- Fixed duration: 300000 ms (5 minutes)

## Logging Method
- Serial output captured to file
- Parsed using `scripts/parse_w2_control_serial.py`
- Power samples logged over serial only
- Telemetry events logged over MQTT only when enabled
- Per-run summaries written under `analysis/` after processing

## Event Association
Each serial power row includes:
- `power_seq`
- `t_local_us`
- `last_event_seq`
- `last_event_t_local_us`
- `dt_since_event_us`

This allows power windows to be aligned with the most recent telemetry event.

## Expected Role
- `R507` is the connected-idle validation reference for W2 v2.
- Matched control / telemetry pairs span `0.5 s` through `10 s` under
  comparison groups `W2_0.5s` to `W2_10s`.
- Replicates may be tagged `primary`, `rep1`, or `rep2` depending on
  the pairing plan.
- Final cross-run interpretation is generated from `analysis/w2/tables/groups.csv`.
