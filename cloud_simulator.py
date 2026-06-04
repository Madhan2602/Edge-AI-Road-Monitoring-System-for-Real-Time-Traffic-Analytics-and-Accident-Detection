import json, os

# File paths
EDGE_LOG = "logs/edge_simulation_log.json"
CLOUD_LOG = "logs/cloud_simulation_log.json"
os.makedirs("logs", exist_ok=True)

# Simulation parameters (realistic values)
UPLOAD_DELAY_MS = 120      # network upload latency (ms/frame)
DOWNLOAD_DELAY_MS = 40     # response delay (ms/frame)
SERVER_SLOWDOWN_FACTOR = 1.8   # server takes 1.8× longer than edge CPU
CPU_OVERHEAD_FACTOR = 1.6      # cloud CPU load is 60% higher due to virtualization

try:
    # Load actual edge performance data
    with open(EDGE_LOG, "r") as f:
        edge_data = json.load(f)

    cloud_data = []
    for frame in edge_data:
        # Base from edge latency
        edge_latency = frame.get("latency_ms", 0)
        edge_cpu = frame.get("cpu_percent", 0)

        # Add realistic cloud effects
        cloud_latency = (
            edge_latency * SERVER_SLOWDOWN_FACTOR
            + UPLOAD_DELAY_MS
            + DOWNLOAD_DELAY_MS
        )
        cloud_cpu = edge_cpu * CPU_OVERHEAD_FACTOR

        # Approximate energy score based on latency and CPU
        energy_score = (cloud_latency * cloud_cpu) / 10000

        cloud_data.append({
            "frame": frame["frame"],
            "latency_ms": round(cloud_latency, 2),
            "cpu_percent": round(cloud_cpu, 2),
            "energy_score": round(energy_score, 4)
        })

    # Save simulated cloud results
    with open(CLOUD_LOG, "w") as f:
        json.dump(cloud_data, f, indent=2)

    print(f"✅ Cloud Simulation Completed → {CLOUD_LOG}")
    print(f"Frames simulated: {len(cloud_data)}")
    print(f"Added avg upload delay: {UPLOAD_DELAY_MS} ms/frame")
    print(f"Server overhead factor: {SERVER_SLOWDOWN_FACTOR}×")
    print(f"CPU overhead factor: {CPU_OVERHEAD_FACTOR}×")

except FileNotFoundError:
    print("❌ Edge simulation data not found. Run edge_infer.py or edge_simulator.py first.")
