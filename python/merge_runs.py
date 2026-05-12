from pathlib import Path
import pandas as pd
from pandas.errors import EmptyDataError

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "experiments" / "runs"
OUT = ROOT / "analysis" / "merged"
OUT.mkdir(parents=True, exist_ok=True)

suffixes = {
    "mqtt_events": "*_mqtt_events.csv",
    "power_samples": "*_power_samples.csv",
    "ble_events": "*_ble_events.csv",
}

for dataset_name, pattern in suffixes.items():
    frames = []
    file_count = 0
    for path in sorted(RUNS.glob(f"*/raw/{pattern}")):
        file_count += 1
        exp_run_id = path.parts[-3]
        run_id = path.name.replace(f"_{dataset_name}.csv", "")
        try:
            df = pd.read_csv(path)
        except EmptyDataError:
            print(f"Skipping empty file with no columns: {path.relative_to(ROOT)}")
            continue
        df.insert(0, "exp_run_id", exp_run_id)
        df.insert(1, "run_id", run_id)
        df.insert(2, "source_file", str(path.relative_to(ROOT)))
        frames.append(df)

    if not frames:
        print(f"No files found for pattern {pattern}")
        continue

    non_empty_frames = [df for df in frames if not df.empty]
    if non_empty_frames:
        merged = pd.concat(non_empty_frames, ignore_index=True)
    else:
        print(
            f"Skipping {dataset_name}: found {file_count} matching files but all were empty/header-only."
        )
        continue

    out = OUT / f"{dataset_name}.parquet"
    merged.to_parquet(out, index=False)
    print(f"Wrote {out} ({len(merged)} rows from {file_count} files)")
