import cv2
import numpy as np

def extract_license_plate(reader, frame, bbox):
    """
    Extracts license plate text from a vehicle bounding box.
    Optimized for Edge AI: Only scans the bottom 50% of the vehicle crop.
    
    Args:
        reader: An initialized easyocr.Reader instance.
        frame: The full original frame from cv2.
        bbox: The bounding box of the vehicle [x1, y1, x2, y2].
        
    Returns:
        tuple (plate_text, confidence) if found, else (None, 0.0)
    """
    x1, y1, x2, y2 = map(int, bbox)
    
    # Ensure coordinates are within frame bounds Minimum size check
    h, w = frame.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    
    # print(f"[ALPR Debug] Bbox size: {x2-x1}x{y2-y1}")
    if x2 - x1 < 20 or y2 - y1 < 20:
        return None, 0.0 # Bbox insanely small
        
    # Crop the vehicle (pass the entire vehicle for testing to ensure we catch plates)
    vehicle_crop = frame[y1:y2, x1:x2]
    
    # EDGE OPTIMIZATION REMOVED FOR TESTING: 
    # Usually plates are in the bottom 50%. Scanning whole vehicle for debug.
    
    # Preprocessing to improve OCR accuracy
    gray = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2GRAY)
    
    # Run EasyOCR
    # detail=1 gives us bounding boxes, text, and confidence
    results = reader.readtext(gray, detail=1)
    
    best_text = None
    best_conf = 0.0
    
    for (bbox_ocr, text, conf) in results:
        # Basic filtering: License plates are typically alphanumeric and 4-10 chars
        clean_text = "".join(e for e in text if e.isalnum()).upper()
        # Debugging hook: what is EasyOCR seeing?
        print(f"[ALPR Debug] Raw: {text} | Cleaned: {clean_text} | Conf: {conf}")
        
        # Lowered thresholds heavily for sample testing on lower-res video
        if len(clean_text) >= 2 and conf > 0.05:
            if conf > best_conf:
                best_text = clean_text
                best_conf = conf
                
    return best_text, round(float(best_conf), 3)
