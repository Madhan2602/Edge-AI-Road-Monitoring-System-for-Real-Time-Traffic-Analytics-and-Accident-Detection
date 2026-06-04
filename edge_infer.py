# edge_infer.py
import cv2
import time
import json
import os
from datetime import datetime
import torch
import numpy as np

# ----------------- CONFIG -----------------
VIDEO_PATH = "videos/sample3.mp4"   # change if your video name/path differs
#VIDEO_PATH="videos/sample1.mp4"
OUT_VIDEO = "output/annotated_output.mp4"
LOG_JSON = "logs/detection_log.json"
#VIDEO_PATH="videos/acci2.mp4"
#OUT_VIDEO="output/acci2_output.mp4"
#LOG_JSON="logs/acci2_logs.json"
CONF_THRESHOLD = 0.40
FRAME_SKIP = 1   # process every FRAME_SKIP-th frame (1 = every frame)
# Vehicle class ids in COCO (used by YOLOv5 pretrained on COCO)
VEHICLE_CLASS_IDS = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
# ------------------------------------------

def main():
    # Load YOLOv5 model from torch.hub (will download first time)
    print("Loading model... (may take a moment first run)")
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    model.conf = CONF_THRESHOLD  # confidence threshold
    model.eval()

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print("ERROR: cannot open video:", VIDEO_PATH)
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUT_VIDEO, fourcc, fps, (width, height))

    logs = []
    frame_no = 0
    start_time = time.time()
    print("Starting inference...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_no += 1
        if (frame_no % FRAME_SKIP) != 0:
            continue

        t0 = time.time()
        # YOLOv5 takes images in RGB
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model(img, size=450)  # size=640 (rescale)

        # results.xyxy[0] => [x1, y1, x2, y2, conf, cls]
        det = results.xyxy[0].cpu().numpy() if hasattr(results, 'xyxy') else results.pred[0].cpu().numpy()
        detections = []
        vehicle_count = 0

        for *box, conf, cls in det:
            cls = int(cls)
            conf = float(conf)
            x1, y1, x2, y2 = map(int, box)
            label = results.names[cls] if hasattr(results, 'names') else str(cls)
            # mark as vehicle if class in VEHICLE_CLASS_IDS
            is_vehicle = cls in VEHICLE_CLASS_IDS
            if is_vehicle:
                vehicle_count += 1

            detections.append({
                "class_id": cls,
                "label": label,
                "conf": round(conf, 3),
                "bbox": [x1, y1, x2, y2],
                "is_vehicle": bool(is_vehicle)
            })

            # draw bounding box
            color = (0, 255, 0) if is_vehicle else (255, 165, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

        timestamp = datetime.utcnow().isoformat() + "Z"
        frame_log = {
            "frame": frame_no,
            "timestamp": timestamp,
            "vehicle_count": vehicle_count,
            "detections": detections
        }
        logs.append(frame_log)

        # overlay summary text on frame
        # overlay summary text on frame
        cv2.putText(frame, f"Frame: {frame_no}  Vehicles: {vehicle_count}", (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        out.write(frame)

# ----- show video window -----
        cv2.namedWindow("Edge AI - Inference", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Edge AI - Inference", 900, 800)  # custom size
        cv2.imshow("Edge AI - Inference", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # save logs to JSON
    with open(LOG_JSON, 'w') as f:
        json.dump(logs, f, indent=2)

    elapsed = time.time() - start_time
    print(f"Done. Processed {frame_no} frames in {elapsed:.1f}s. Output saved to {OUT_VIDEO} and {LOG_JSON}")

if __name__ == "__main__":
    main()
