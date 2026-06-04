# edge_dashboard.py
import streamlit as st
import json
import time
import pandas as pd

# File paths
DETECTION_LOG = "logs/detection_log.json"
CONGESTION_FILE = "congestion_log.txt"
ACCIDENT_FILE = "accident_log.txt"

# ---- Streamlit layout setup ----
st.set_page_config(page_title="Edge AI Traffic Dashboard", layout="wide")

st.sidebar.title("🚦 Edge AI Control Panel")
refresh_rate = st.sidebar.slider("Refresh rate (seconds)", 2, 10, 3)

st.title("🧠 Real-Time Edge AI Traffic Monitoring System")
st.markdown("Monitoring traffic flow, congestion, and accidents — all locally and visually.")

# ---- Vehicle count display ----
st.subheader("📊 Live Vehicle Analytics")

# ---- Predictive Traffic Insights ----
st.subheader("🔮 Predictive Traffic Insights (Offline AI Simulation)")

# ---- Intelligent Event Log Viewer ----
st.subheader("🧾 Intelligent Event Logging System")

import json
from pathlib import Path

MASTER_LOG = Path("logs/master_event_log.json")

if MASTER_LOG.exists():
    with open(MASTER_LOG, "r", encoding="utf-8") as f:
        events = json.load(f)

    # sort newest first
    events = sorted(events, key=lambda e: e["timestamp"], reverse=True)

    # sidebar filter
    types = list({e["event"] for e in events})
    selected = st.sidebar.multiselect("Filter events by type", types, default=types)

    filtered = [e for e in events if e["event"] in selected]

    for e in filtered:
        if e["severity"].upper() == "HIGH":
            color = "🔴"
        elif e["severity"].upper() == "MEDIUM":
            color = "🟡"
        else:
            color = "🟢"

        st.markdown(
            f"**{color} [{e['timestamp']}] {e['event']}** — {e['details']}"
        )
else:
    st.info("No master event log found yet. Run merge_event_logs.py first.")


import pandas as pd
from pathlib import Path

PRED_PATH = Path("logs/predicted_traffic.csv")

if PRED_PATH.exists():
    df_pred = pd.read_csv(PRED_PATH)

    # determine where actual data ends
    if "actual_count" in df_pred.columns:
        actual = df_pred.dropna(subset=["actual_count"])
        predicted = df_pred.dropna(subset=["predicted_count"])

        st.line_chart(
            data={
                "Actual Count": actual["actual_count"].values,
                "Predicted Count": predicted["predicted_count"].values
            },
            height=250
        )

        # risk evaluation (same logic as predictive_insight.py)
        if len(predicted):
            avg_pred = predicted["predicted_count"].mean()
            CONGESTION_LIMIT = 15
            if avg_pred < CONGESTION_LIMIT * 0.5:
                risk = "🟢 LOW"
            elif avg_pred < CONGESTION_LIMIT:
                risk = "🟡 MEDIUM"
            else:
                risk = "🔴 HIGH"

            st.metric(label="Predicted Congestion Risk", value=risk)
else:
    st.info("Run predictive_insight.py to generate predictions first.")


try:
    with open(DETECTION_LOG, "r") as f:
        frames = json.load(f)

    # convert detection log to dataframe
    df = pd.DataFrame(frames)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    latest_frame = df.iloc[-1]

    st.metric("🚗 Current Vehicles Detected", int(latest_frame["vehicle_count"]))

    # show trends (recent 50 frames)
    st.line_chart(df.tail(50).set_index("timestamp")["vehicle_count"])

except Exception as e:
    st.warning(f"⚠️ Could not read detection log: {e}")

# ---- Alerts ----
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚧 Congestion Alerts")
    try:
        st.text(open(CONGESTION_FILE).read())
    except:
        st.info("No congestion alerts yet.")

with col2:
    st.subheader("🛑 Accident Alerts")
    try:
        st.text(open(ACCIDENT_FILE).read())
    except:
        st.info("No accident alerts yet.")
# ---- Lightweight Edge AI Simulation ----
st.subheader("🧩 Lightweight Edge AI Simulation")

import json
import pandas as pd
from pathlib import Path

EDGE_SIM_PATH = Path("logs/edge_simulation_log.json")

if EDGE_SIM_PATH.exists():
    with open(EDGE_SIM_PATH, "r", encoding="utf-8") as f:
        sim_data = json.load(f)

    df_sim = pd.DataFrame(sim_data)

    avg_latency = df_sim["latency_ms"].mean()
    avg_cpu = df_sim["cpu_percent"].mean()
    avg_energy = df_sim["energy_score"].mean()

    # Display key metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("⚡ Avg Latency (ms/frame)", f"{avg_latency:.2f}")
    col2.metric("🧠 Avg CPU Usage (%)", f"{avg_cpu:.1f}")
    col3.metric("🔋 Avg Energy Score", f"{avg_energy:.3f}")

    # Trend charts
    st.line_chart(
        df_sim[["latency_ms", "cpu_percent", "energy_score"]],
        height=250
    )

    st.caption("Simulated Edge AI performance metrics — no hardware required.")
else:
    st.info("Run edge_simulator.py to generate performance data first.")



# ---- Refresh ----
time.sleep(refresh_rate)
if hasattr(st, "rerun"):
    st.rerun()
else:
    st.experimental_rerun()
