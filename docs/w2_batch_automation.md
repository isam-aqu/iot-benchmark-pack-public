# W2 Batch Automation

This workflow configures the ESP32 INA231 power node from the host, runs the
selected W2 run-sheet rows, and regenerates per-run W2 analysis outputs.

## Firmware Serial Commands

The power-node firmware accepts line-based serial commands at `115200` baud.
Configuration is persisted in ESP32 NVS, so a reset after configuration starts
the next experiment with the requested settings.

```text
CONFIG exp=W2_wifi_periodic_2s_quiet_telemetry_v2_rep2 interval_ms=2000 telemetry=1 duration_ms=300000 power_ms=100
SHOW_CONFIG
CLEAR_CONFIG
STOP
START
```

`telemetry=1` enables MQTT telemetry events. `telemetry=0` keeps periodic serial
event markers but suppresses MQTT event publishing, which is the W2 control
condition.

## Single Run

Flash once, configure `R698`, run it, parse the serial log, and regenerate W2
summary/metrics:

```bash
python3 python/run_w2_batch.py \
  --run-id R698 \
  --serial-port /dev/serial-port \
  --upload
```

After the correct firmware is already on the ESP32, omit `--upload`:

```bash
python3 python/run_w2_batch.py \
  --run-id R699 \
  --serial-port /dev/serial-port
```

If the ESP32 is connected through an external USB-to-serial adapter on
`TX0/RX0` and the adapter is not wired to the ESP32 reset/enable circuit, use
serial start instead of hardware reset:

```bash
python3 python/run_w2_batch.py \
  --run-id R698 \
  --serial-port /dev/serial-port \
  --start-over-serial
```

## Planned Rerun Block

Run the planned W2 reruns in run-sheet order:

```bash
python3 python/run_w2_batch.py \
  --from-run R698 \
  --to-run R733 \
  --serial-port /dev/serial-port \
  --upload
```

For an external `TX0/RX0` serial adapter without reset wiring:

```bash
python3 python/run_w2_batch.py \
  --from-run R698 \
  --to-run R733 \
  --serial-port /dev/serial-port \
  --start-over-serial
```

Use `--dry-run` to print the generated configuration and runner commands
without touching the ESP32 or writing new experiment outputs.

```bash
python3 python/run_w2_batch.py \
  --from-run R698 \
  --to-run R733 \
  --serial-port /dev/serial-port \
  --dry-run
```

If `arduino-cli` needs a non-default config file, pass it through:

```bash
python3 python/run_w2_batch.py \
  --run-id R698 \
  --serial-port /dev/serial-port \
  --upload \
  --arduino-config-file /path/to/arduino-cli.yaml
```

## Notes

- The script derives the raw firmware/run identifier from `docs/run_sheet.csv`.
  For example, `R698` becomes
  `W2_wifi_periodic_2s_quiet_telemetry_v2_rep2`.
- The firmware experiment duration defaults to `300 s`; the host runner
  defaults to `320 s` to leave a small post-completion capture margin.
- `--upload` compiles/uploads once before the batch. `--upload-each-run` exists
  for troubleshooting, but repeated flashing is not recommended for normal W2
  energy runs.
- `--start-over-serial` leaves reset disabled, starts serial capture, then sends
  `START` to the firmware after the MQTT logger is running. This is the preferred
  mode when only `TX0/RX0` are connected to the logging computer.
- The runner calls `run_all.sh`, then
  `scripts/parse_w2_control_serial.py`, `python/summarize_w2_run.py`, and
  `python/analyze_w2_run.py`. At the end it regenerates grouped W2 tables
  unless `--skip-group-analysis` is set.
