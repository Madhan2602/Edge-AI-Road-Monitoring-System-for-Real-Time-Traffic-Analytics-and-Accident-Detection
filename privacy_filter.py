import cv2
from ultralytics import YOLO
from pathlib import Path

# Load YOLOv8 model (for detecting people)
model = YOLO("yolov8n.pt")

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Input & Output paths
video_path = Path("videos/sample3.mp4")
output_path = Path("output/output_face_blur.mp4")

cap = cv2.VideoCapture(str(video_path))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(str(output_path), fourcc, 20.0,
                      (int(cap.get(3)), int(cap.get(4))))

if not cap.isOpened():
    print("❌ Error opening video")
    exit()

print("🔒 Privacy-Aware Face Blurring Started...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO inference to find people
    results = model(frame, verbose=False)
    detections = results[0].boxes.data.cpu().numpy()

    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        label = model.names[int(cls)]

        # Only process 'person' class for face blurring
        if label == "person":
            person_region = frame[int(y1):int(y2), int(x1):int(x2)]
            if person_region.size == 0:
                continue

            # Convert person region to grayscale for face detection
            gray = cv2.cvtColor(person_region, cv2.COLOR_BGR2GRAY)

            # Detect faces within the person region
            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=4, minSize=(20, 20))

            # Blur only detected faces
            for (fx, fy, fw, fh) in faces:
                face = person_region[fy:fy+fh, fx:fx+fw]
                blurred_face = cv2.GaussianBlur(face, (55, 55), 30)
                person_region[fy:fy+fh, fx:fx+fw] = blurred_face

            # Put the processed region back
            frame[int(y1):int(y2), int(x1):int(x2)] = person_region

    out.write(frame)
    cv2.imshow("Privacy-Aware Face Blurring", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print("✅ Privacy-Aware Face-Blurred Video Saved at:", output_path)
