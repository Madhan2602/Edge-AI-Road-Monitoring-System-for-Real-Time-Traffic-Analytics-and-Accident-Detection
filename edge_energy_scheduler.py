import cv2
import psutil
import time
from ultralytics import YOLO
import json
import os
from datetime import datetime

# ---------------- CONFIG ----------------
VIDEO_PATH = "videos/sample3.mp4"
OUTPUT_PATH = "output/output_energy_scheduler.mp4"
LOG_PATH = "logs/energy_scheduler_log.json"
os.makedirs("logs", exist_ok=True)

# Thresholds
CPU_LIMIT = 70       # % usage to trigger low-power mode
ENERGY_MODE = False  # current mode flag

# YOLO model
model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(VIDEO_PATH)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(OUTPUT_PATH, fourcc, 20.0,
                      (int(cap.get(3)), int(cap.get(4))))

frame_id = 0
results_log = []

print("⚡ Energy-Aware Edge Scheduler started...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_id += 1

    # ---------------- MONITOR CPU ----------------
    cpu_usage = psutil.cpu_percent(interval=0.1)
    energy_score = cpu_usage / 100 + (frame_id % 5) * 0.02  # mock metric

    # ---------------- ADAPTIVE MODE ----------------
    if cpu_usage > CPU_LIMIT:
        ENERGY_MODE = True
        skip = 1   # process fewer frames
    else:
        ENERGY_MODE = False
        skip = 0   # process all frames

    # Skip frame in low-energy mode
    if ENERGY_MODE and frame_id % 2 == 0:
        out.write(frame)
        continue

    # ---------------- DETECTION ----------------
    results = model(frame, verbose=False)
    detections = results[0].boxes.data.cpu().numpy()
    vehicle_count = len([d for d in detections if int(d[5]) in [2, 3, 5, 7]])

    mode_text = "Low-Power Mode" if ENERGY_MODE else "Normal Mode"
    color = (0, 255, 0) if not ENERGY_MODE else (0, 0, 255)
    cv2.putText(frame, f"{mode_text} | CPU: {cpu_usage:.1f}%", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    out.write(frame)

    results_log.append({
        "frame": frame_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_usage": cpu_usage,
        "energy_score": round(energy_score, 3),
        "mode": "Low-Power" if ENERGY_MODE else "Normal",
        "vehicles": vehicle_count
    })

    cv2.imshow("Energy-Aware Scheduler", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

with open(LOG_PATH, "w") as f:
    json.dump(results_log, f, indent=2)

print(f"✅ Energy-Aware Edge Scheduling completed.\nLogs saved at {LOG_PATH}")
