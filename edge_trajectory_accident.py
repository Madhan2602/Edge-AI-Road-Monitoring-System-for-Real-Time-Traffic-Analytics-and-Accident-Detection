import cv2
import numpy as np
from ultralytics import YOLO
from filterpy.kalman import KalmanFilter
from collections import defaultdict
import math
import pyttsx3
import json, time, os

LOG_FILE = "logs/dashboard_accident_log.json"
if not os.path.exists("logs"):
    os.makedirs("logs")

# Initialize voice alert engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

# ---------------- SORT Tracker Class ----------------
class SimpleTracker:
    def __init__(self):
        self.next_id = 0
        self.tracks = {}  # id -> [x, y]
        self.centers = defaultdict(list)

    def update(self, detections):
        updated_ids = []
        for det in detections:
            x1, y1, x2, y2, conf, cls = det
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            # Assign new ID if far from existing
            matched_id = None
            for tid, (tx, ty) in self.tracks.items():
                if math.hypot(cx - tx, cy - ty) < 40:  # close enough
                    matched_id = tid
                    break
            if matched_id is None:
                matched_id = self.next_id
                self.next_id += 1
            self.tracks[matched_id] = (cx, cy)
            self.centers[matched_id].append((cx, cy))
            updated_ids.append(matched_id)
        # Clean old tracks
        self.tracks = {tid: self.tracks[tid] for tid in updated_ids}
        return self.tracks, self.centers

# ---------------- Utility Functions ----------------
def line_intersection(p1, p2, p3, p4):
    """Check if two line segments intersect"""
    def ccw(a,b,c): return (c[1]-a[1])*(b[0]-a[0]) > (b[1]-a[1])*(c[0]-a[0])
    return ccw(p1,p3,p4) != ccw(p2,p3,p4) and ccw(p1,p2,p3) != ccw(p1,p2,p4)

def trajectory_intersect(traj1, traj2):
    """Check if trajectories intersect at any point"""
    for i in range(1, len(traj1)):
        for j in range(1, len(traj2)):
            if line_intersection(traj1[i-1], traj1[i], traj2[j-1], traj2[j]):
                return True
    return False

def avg_speed(traj):
    if len(traj) < 2: return 0
    dist = sum(math.hypot(traj[i][0]-traj[i-1][0], traj[i][1]-traj[i-1][1]) for i in range(1, len(traj)))
    return dist / len(traj)

# ---------------- Main Detection ----------------
model = YOLO("yolov8n.pt")
video_path = "videos/acci_video.mp4"
output_path = "output/output_trajectory_accident.mp4"

cap = cv2.VideoCapture(video_path)
out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'),
                      20.0, (int(cap.get(3)), int(cap.get(4))))

tracker = SimpleTracker()
accident_detected = set()

print("🚦 Trajectory-based accident detection running...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)
    detections = results[0].boxes.data.cpu().numpy()

    # Keep only vehicles
    # Keep only vehicles (and define persons for logging)
    persons = [d for d in detections if int(d[5]) == 0]  # person class id = 0
    vehicles = [d for d in detections if int(d[5]) in [2, 3, 5, 7]]  # car, motorbike, bus, truck


    # Update tracker
    track_positions, trajectories = tracker.update(vehicles)

    # Draw trajectories
    for tid, points in trajectories.items():
        for i in range(1, len(points)):
            cv2.line(frame, (int(points[i-1][0]), int(points[i-1][1])),
                     (int(points[i][0]), int(points[i][1])), (0, 255, 0), 2)
        cx, cy = map(int, points[-1])
        cv2.putText(frame, f"ID:{tid}", (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    # ---- Accident detection via trajectory intersection + low speed ----
    ids = list(trajectories.keys())
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            id1, id2 = ids[i], ids[j]
            t1, t2 = trajectories[id1], trajectories[id2]

            if len(t1) > 5 and len(t2) > 5:
                if trajectory_intersect(t1[-10:], t2[-10:]):
                    s1, s2 = avg_speed(t1[-10:]), avg_speed(t2[-10:])
                    if s1 < 2 and s2 < 2:  # both nearly stopped
                        pair = tuple(sorted([id1, id2]))
                        if pair not in accident_detected:
                            accident_detected.add(pair)
                            msg = f"🛑 Accident between vehicles {id1} & {id2}"
                            print(msg)
                            cv2.putText(frame, "ACCIDENT!", (50, 50),
                                        cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 255), 3)
                            # 🔊 Voice alert
                            engine.say("Accident detected between vehicles")
                            engine.runAndWait()

    out.write(frame)
    cv2.imshow("Trajectory Accident Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
engine.stop()
cv2.destroyAllWindows()
summary = {
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "total_persons": len(persons),
    "total_vehicles": len(vehicles),
    "accidents_detected": len(accident_detected) > 0
}

try:
    with open(LOG_FILE, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"🗂️ Dashboard log updated at {LOG_FILE}")
except Exception as e:
    print(f"❌ Error writing dashboard log: {e}")

print("✅ Processing complete. Saved:", output_path)
import sys, atexit

def cleanup_tts():
    try:
        engine.stop()
    except:
        pass

atexit.register(cleanup_tts)
sys.exit(0)

