# prepare_timeseries.py
import json
import pandas as pd
from pathlib import Path

# path to your detection log (adjust if different)
LOG_PATH = Path("logs/detection_log.json")
OUT_CSV = Path("logs/vehicle_timeseries.csv")

def main():
    if not LOG_PATH.exists():
        print("ERROR: detection log not found:", LOG_PATH)
        return

    with open(LOG_PATH, "r") as f:
        data = json.load(f)

    # Each entry expected to be {"frame": int, "timestamp": "ISO", "vehicle_count": int, ...}
    rows = []
    for entry in data:
        # some logs may not have vehicle_count; compute from detections if missing
        count = entry.get("vehicle_count")
        if count is None:
            count = sum(1 for d in entry.get("detections", []) if d.get("is_vehicle"))
        rows.append({
            "frame": int(entry.get("frame", 0)),
            "timestamp": entry.get("timestamp"),
            "vehicle_count": int(count)
        })

    df = pd.DataFrame(rows)
    # parse timestamps (some are ISO strings); if parsing fails, keep as string
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    except Exception as e:
        print("Warning: timestamp parse failed:", e)

    # sort by frame/time
    if "timestamp" in df.columns and df["timestamp"].dtype != object:
        df = df.sort_values("timestamp").reset_index(drop=True)
    else:
        df = df.sort_values("frame").reset_index(drop=True)

    # optionally compute time delta between frames if timestamps exist
    if "timestamp" in df.columns and df["timestamp"].dtype != object:
        df["seconds"] = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds()
    else:
        df["seconds"] = df["frame"]  # fallback: use frame index

    # save csv
    df.to_csv(OUT_CSV, index=False)
    print(f"Saved timeseries to {OUT_CSV} (rows: {len(df)})")
    print(df.head())

if __name__ == "__main__":
    main()
