# W2_5s Repeat (R522–R523)

## Status
Invalidated for final analysis.

## Reason
Although the interval misconfiguration from the earlier attempt was fixed, the paired telemetry run `R523` was later found to contain physically invalid raw electrical values in the canonical raw power file, including:
- rows with `bus_v = 0.0`
- rows with `power_mW = 0.0`
- implausible voltage spikes above the hardware supply range
- internally inconsistent voltage/current/power combinations

To preserve matched-pair integrity, both `R522` and `R523` were excluded from the final grouped `W2_5s` analysis.

## Final handling
The final 5 s interpretation is based on the remaining valid pairs:
- `R509 / R512`
- `R518 / R519`

## Impact on conclusions
Excluding `R522–R523` changed the numerical estimate for 5 s but did not change the qualitative interpretation:
- `W2_5s` remains classified as **below_noise_floor**
- no statistically significant telemetry energy overhead is established at 5 s under the present setup