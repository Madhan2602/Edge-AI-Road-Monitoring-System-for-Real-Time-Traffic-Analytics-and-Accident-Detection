# edge_simulator.py
import time
import psutil
import json
from pathlib import Path
import random

LOG_PATH = Path("logs/edge_simulation_log.json")

def simulate_inference(frames=200):
    """
    Simulate edge inference latency & resource usage.
    Replace the 'random' parts later with real YOLO timings if desired.
    """
    results = []
    for i in range(frames):
        start = time.time()
        # --- simulate model work ---
        time.sleep(random.uniform(0.015, 0.04))  # 15–40 ms
        latency = (time.time() - start) * 1000  # ms
        cpu = psutil.cpu_percent(interval=None)
        power_est = latency * cpu * 0.0001  # fake energy score

        results.append({
            "frame": i,
            "latency_ms": round(latency, 2),
            "cpu_percent": cpu,
            "energy_score": round(power_est, 3)
        })

    LOG_PATH.parent.mkdir(exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Edge simulation data saved → {LOG_PATH}")

if __name__ == "__main__":
    simulate_inference()
