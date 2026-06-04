import sys
import traceback

try:
    import cv2
    print("cv2 module path:", cv2.__file__)
    print("cv2 version:", cv2.__version__)
    cv2.namedWindow("Test", cv2.WINDOW_NORMAL)
    cv2.destroyAllWindows()
    print("SUCCESS")
    sys.exit(0)
except Exception as e:
    print("EXCEPTION:", e)
    traceback.print_exc()
    sys.exit(1)
