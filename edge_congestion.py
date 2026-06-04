# edge_congestion.py
import json
from datetime import datetime

LOG_FILE = "logs/detection_log.json"
CONGESTION_LOG = "congestion_log.txt"

import json, os

# Load adaptive congestion limit if available
adaptive_file = "logs/adaptive_config.json"
if os.path.exists(adaptive_file):
    with open(adaptive_file) as f:
        config = json.load(f)
        VEHICLE_LIMIT = config.get("adaptive_limit", 20)
else:
    VEHICLE_LIMIT = 20  # default fallback
  # set according to your video (try 3–5 for low-traffic)
CONGESTION_COOLDOWN = 100  # number of frames before logging again

def main():
    with open(LOG_FILE, "r") as f:
        frames = json.load(f)

    alerts = []
    congestion_active = False
    last_alert_frame = 0

    for f in frames:
        fid = f["frame"]
        timestamp = f["timestamp"]
        vcount = f["vehicle_count"]

        if vcount >= VEHICLE_LIMIT:
            if not congestion_active or fid - last_alert_frame > CONGESTION_COOLDOWN:
                alerts.append(f"[{timestamp}] 🚗 TRAFFIC CONGESTION: {vcount} vehicles")
                congestion_active = True
                last_alert_frame = fid
        else:
            congestion_active = False

    # remove duplicates
    alerts = sorted(set(alerts))
    with open(CONGESTION_LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(alerts))

    print(f"✅ Congestion analysis complete. {len(alerts)} alerts saved to {CONGESTION_LOG}")

if __name__ == "__main__":
    main()
