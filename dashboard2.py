import streamlit as st
import json
import time
import pandas as pd
from pathlib import Path
import subprocess
from datetime import datetime

# ---------------- File paths ----------------
DETECTION_LOG = "logs/detection_log.json"
CONGESTION_FILE = "congestion_log.txt"

# ---- Streamlit layout setup ----
st.set_page_config(page_title="Edge AI Traffic Dashboard", layout="wide")

st.sidebar.title("🚦 Edge AI Control Panel")
refresh_rate = st.sidebar.slider("Refresh rate (seconds)", 2, 10, 3)

st.title("AI-POWERED ROAD MONITORING SYSTEM")
st.markdown("Monitoring traffic flow, congestion, and accidents — all locally and visually.")

# ---- Vehicle count display ----
st.subheader("📊 Live Vehicle Analytics")

# ---- Predictive Traffic Insights ----
st.subheader("🔮 Predictive Traffic Insights (Offline AI Simulation)")

# ---- Intelligent Event Log Viewer ----
st.subheader("🧾 Intelligent Event Logging System")

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

# ---- Predictive Traffic Insights Chart ----
PRED_PATH = Path("logs/predicted_traffic.csv")

if PRED_PATH.exists():
    df_pred = pd.read_csv(PRED_PATH)

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

# ---- Vehicle detection log ----
try:
    with open(DETECTION_LOG, "r") as f:
        frames = json.load(f)

    df = pd.DataFrame(frames)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    latest_frame = df.iloc[-1]

    st.metric("🚗 Current Vehicles Detected", int(latest_frame["vehicle_count"]))
    st.line_chart(df.tail(50).set_index("timestamp")["vehicle_count"])

except Exception as e:
    st.warning(f"⚠️ Could not read detection log: {e}")

# ---------------- ADAPTIVE EDGE INTELLIGENCE ----------------
st.subheader("🧠 Adaptive Edge Intelligence (Smart Learning Module)")

import os, json
if os.path.exists("logs/adaptive_config.json"):
    with open("logs/adaptive_config.json") as f:
        config = json.load(f)
    st.metric("🚗 Adaptive Congestion Limit", config["adaptive_limit"])
    st.caption(f"Last updated: {config['timestamp']}")
else:
    st.info("Run adaptive_threshold.py to generate adaptive limit.")

# ---------------- ENERGY-AWARE EDGE SCHEDULER ----------------
st.subheader("🔋 Energy-Aware Edge Scheduler")

import json
from pathlib import Path

SCHED_PATH = Path("logs/energy_scheduler_log.json")
if SCHED_PATH.exists():
    with open(SCHED_PATH, "r", encoding="utf-8") as f:
        sched_data = json.load(f)

    import pandas as pd
    df_sched = pd.DataFrame(sched_data)

    st.metric("⚙️ Avg CPU Usage", f"{df_sched['cpu_usage'].mean():.2f}%")
    st.metric("🔋 Avg Energy Score", f"{df_sched['energy_score'].mean():.3f}")
    st.metric("🧭 Low-Power Frames", df_sched[df_sched['mode'] == 'Low-Power'].shape[0])

    st.line_chart(df_sched[["cpu_usage", "energy_score"]], height=250)
    st.caption("Dynamic mode switching between Normal and Low-Power states based on CPU usage.")
else:
    st.info("Run edge_energy_scheduler.py to generate energy logs first.")


# ---- Congestion Alerts ----
st.subheader("🚧 Congestion Alerts")
try:
    st.text(open(CONGESTION_FILE).read())
except:
    st.info("No congestion alerts yet.")

# ---------------- ACCIDENT DETECTION STATUS ----------------
st.header("🛑 Accident Detection Status")

try:
    with open("logs/dashboard_accident_log.json") as f:
        log = json.load(f)
        accident_flag = log.get("accidents_detected", False)
        persons = log.get("total_persons", 0)
        vehicles = log.get("total_vehicles", 0)
        ts = log.get("timestamp", "Unknown")

        col1, col2, col3 = st.columns(3)
        col1.metric("👤 Persons", persons)
        col2.metric("🚗 Vehicles", vehicles)
        col3.metric("⏱ Last Update", ts)

        if accident_flag:
            st.error("🚨 **Accident Detected! Immediate attention required.**")
        else:
            st.success("✅ **No accidents detected in current video.**")

except FileNotFoundError:
    st.warning("⚠️ Run the accident detection module first to see results.")

# ---- Run Accident Detection ----
if st.button("▶️ Run Accident Detection"):
    st.info("Processing video... please wait ⏳")
    subprocess.run(["python", "edge_trajectory_accident.py"])
    st.success("✅ Detection complete! Refreshing results...")
    st.rerun()

# ---- Lightweight Edge AI Simulation ----
#st.subheader("🧩 Lightweight Edge AI Simulation")

#'''EDGE_SIM_PATH = Path("logs/edge_simulation_log.json")

#if EDGE_SIM_PATH.exists():
 #   with open(EDGE_SIM_PATH, "r", encoding="utf-8") as f:
  #      sim_data = json.load(f)

   # df_sim = pd.DataFrame(sim_data)

    #avg_latency = df_sim["latency_ms"].mean()
    #avg_cpu = df_sim["cpu_percent"].mean()
    #avg_energy = df_sim["energy_score"].mean()

    #col1, col2, col3 = st.columns(3)
    #col1.metric("⚡ Avg Latency (ms/frame)", f"{avg_latency:.2f}")
    #col2.metric("🧠 Avg CPU Usage (%)", f"{avg_cpu:.1f}")
    #col3.metric("🔋 Avg Energy Score", f"{avg_energy:.3f}")

    #st.line_chart(df_sim[["latency_ms", "cpu_percent", "energy_score"]], height=250)
    #st.caption("Simulated Edge AI performance metrics — no hardware required.")
#else:
 #   st.info("Run edge_simulator.py to generate performance data first.")'''
# ---------------- CLOUD VS EDGE COMPARISON ----------------
st.subheader("☁️ Cloud Simulation vs ⚡ Edge AI Comparison")

from pathlib import Path
CLOUD_SIM_PATH = Path("logs/cloud_simulation_log.json")
EDGE_SIM_PATH = Path("logs/edge_simulation_log.json")

if CLOUD_SIM_PATH.exists() and EDGE_SIM_PATH.exists():
    with open(EDGE_SIM_PATH, "r", encoding="utf-8") as f:
        edge_data = json.load(f)
    with open(CLOUD_SIM_PATH, "r", encoding="utf-8") as f:
        cloud_data = json.load(f)

    import pandas as pd
    df_edge = pd.DataFrame(edge_data)
    df_cloud = pd.DataFrame(cloud_data)

    # --- Averages ---
    avg_edge_latency = df_edge["latency_ms"].mean()
    avg_cloud_latency = df_cloud["latency_ms"].mean()
    avg_edge_cpu = df_edge["cpu_percent"].mean()
    avg_cloud_cpu = df_cloud["cpu_percent"].mean()
    avg_edge_energy = df_edge["energy_score"].mean()
    avg_cloud_energy = df_cloud["energy_score"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("⚡ Avg Latency (Edge)", f"{avg_edge_latency:.2f} ms", delta=f"{avg_cloud_latency - avg_edge_latency:.1f} ms slower (Cloud)")
    col2.metric("🧠 Avg CPU Usage (Edge)", f"{avg_edge_cpu:.1f}%", delta=f"{avg_cloud_cpu - avg_edge_cpu:.1f}% higher (Cloud)")
    col3.metric("🔋 Avg Energy (Edge)", f"{avg_edge_energy:.3f}", delta=f"{avg_cloud_energy - avg_edge_energy:.3f}↑ (Cloud)")

    # --- Comparison chart ---
    st.markdown("### 📈 Performance Comparison (Edge vs Cloud)")
    combined = pd.DataFrame({
        "Edge Latency (ms)": df_edge["latency_ms"],
        "Cloud Latency (ms)": df_cloud["latency_ms"],
        "Edge CPU (%)": df_edge["cpu_percent"],
        "Cloud CPU (%)": df_cloud["cpu_percent"]
    })

    st.line_chart(combined[["Edge Latency (ms)", "Cloud Latency (ms)"]])
    st.line_chart(combined[["Edge CPU (%)", "Cloud CPU (%)"]])

    st.caption("Edge AI runs locally with lower latency, CPU, and energy consumption — Cloud adds upload & server overheads.")

else:
    st.info("⚠️ Run edge_simulator.py and cloud_simulator.py to generate both logs first.")




# ---- Auto Refresh ----
time.sleep(refresh_rate)
st.rerun()
