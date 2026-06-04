import json
import os
import numpy as np
from datetime import datetime

LOG_FILE = "logs/detection_log.json"
ADAPTIVE_CONFIG = "logs/adaptive_config.json"

def compute_adaptive_threshold():
    if not os.path.exists(LOG_FILE):
        print("❌ detection_log.json not found. Run edge_infer.py first.")
        return

    with open(LOG_FILE, "r") as f:
        data = json.load(f)

    # Extract vehicle counts from last 200 frames
    vehicle_counts = [frame["vehicle_count"] for frame in data[-200:] if "vehicle_count" in frame]

    if not vehicle_counts:
        print("⚠️ No vehicle count data found in log.")
        return

    # Calculate adaptive threshold dynamically
    mean_count = np.mean(vehicle_counts)
    std_dev = np.std(vehicle_counts)
    adaptive_limit = int(mean_count + 1.2 * std_dev)

    adaptive_config = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mean_vehicle_count": float(mean_count),
        "std_dev": float(std_dev),
        "adaptive_limit": int(adaptive_limit)
    }

    # Save updated adaptive threshold
    os.makedirs("logs", exist_ok=True)
    with open(ADAPTIVE_CONFIG, "w") as f:
        json.dump(adaptive_config, f, indent=2)

    print(f"✅ Adaptive threshold updated → {adaptive_limit} vehicles (based on recent data).")

if __name__ == "__main__":
    compute_adaptive_threshold()
