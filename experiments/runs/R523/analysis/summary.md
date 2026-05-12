# Summary for W2_wifi_periodic_5s_quiet_telemetry_v2

## Energy
- energy_mJ: unavailable
- status: excluded_from_grouped_analysis
- reason: Invalid electrical samples detected; corrected energy must be regenerated from filtered telemetry.

## Power
- status: invalid_unfiltered_samples_present
- power_sample_count_raw: 4201
- valid_for_comparison: False
- reason: Raw summary contains clearly invalid electrical measurements (`min_power_mW = 0.0`, `min_bus_v = 0.0`, `max_bus_v = 11.0`).
- required_action: Filter invalid bus-voltage/power samples and regenerate energy/power statistics before using this run in grouped analysis.
- observed_mean_bus_v_raw: 5.00443227802904
- observed_min_bus_v_raw: 0.0
- observed_max_bus_v_raw: 11.0
- observed_min_power_mW_raw: 0.0

## Latency
- available: False
- source: None
- kind: None
- sample_count: 0
- reason: No recognized latency column with valid numeric samples.

## Timing
- mean_interval_ms: 4999.999951807229
- median_interval_ms: 5000.0
- std_interval_ms: 0.04169865869468255
- jitter_ms: 0.04169865869468255
- max_interval_ms: 5000.084
- min_interval_ms: 4999.904

## Reliability
- expected_events: 84
- actual_events: 84
- missing_events: 0
- loss_rate: 0.0
- duplicates: 0

## Events
- event_count: 84
- mean_event_interval_ms: 4999.999951807229
- median_event_interval_ms: 5000.0
- max_event_interval_ms: 5000.084
