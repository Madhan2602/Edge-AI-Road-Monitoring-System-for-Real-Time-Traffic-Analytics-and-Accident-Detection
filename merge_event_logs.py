# merge_event_logs.py
import json
from pathlib import Path
from datetime import datetime

# Input files
CONGESTION_LOG = Path("congestion_log.txt")
ACCIDENT_LOG = Path("accident_log.txt")
PREDICTED_FILE = Path("logs/predicted_traffic.csv")

# Output
MASTER_LOG = Path("logs/master_event_log.json")

def parse_txt_log(path, event_type, severity):
    events = []
    if not path.exists():
        return events
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Try to split timestamp and message
            if line.startswith("["):
                ts = line.split("]")[0].strip("[]")
                msg = line.split("]")[1].strip()
            else:
                ts, msg = datetime.utcnow().isoformat(), line
            events.append({
                "timestamp": ts,
                "event": event_type,
                "details": msg,
                "severity": severity
            })
    return events

def parse_predictive_risk(path):
    events = []
    if not path.exists():
        return events
    import pandas as pd
    df = pd.read_csv(path)
    avg_pred = df["predicted_count"].dropna().mean()
    CONGESTION_LIMIT = 15
    if avg_pred < CONGESTION_LIMIT * 0.5:
        risk, severity = "LOW", "LOW"
    elif avg_pred < CONGESTION_LIMIT:
        risk, severity = "MEDIUM", "MEDIUM"
    else:
        risk, severity = "HIGH", "HIGH"
    events.append({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "PREDICTIVE_RISK",
        "details": f"Forecasted average vehicle count {avg_pred:.2f}, Risk={risk}",
        "severity": severity
    })
    return events

def main():
    all_events = []
    all_events += parse_txt_log(CONGESTION_LOG, "CONGESTION", "MEDIUM")
    all_events += parse_txt_log(ACCIDENT_LOG, "ACCIDENT", "HIGH")
    all_events += parse_predictive_risk(PREDICTED_FILE)

    # Sort by timestamp
    try:
        all_events.sort(key=lambda e: e["timestamp"])
    except Exception:
        pass

    MASTER_LOG.parent.mkdir(exist_ok=True)
    with open(MASTER_LOG, "w", encoding="utf-8") as f:
        json.dump(all_events, f, indent=2)
    print(f"✅ Master event log saved → {MASTER_LOG} ({len(all_events)} events)")

if __name__ == "__main__":
    main()
