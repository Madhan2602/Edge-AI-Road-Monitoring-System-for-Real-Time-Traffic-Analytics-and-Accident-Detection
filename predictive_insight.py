# predictive_insight.py
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from pathlib import Path

DATA_PATH = Path("logs/vehicle_timeseries.csv")
OUT_PATH = Path("logs/predicted_traffic.csv")
CONGESTION_LIMIT = 15  # adjust for your road type

def main():
    if not DATA_PATH.exists():
        print("❌ vehicle_timeseries.csv not found.")
        return

    df = pd.read_csv(DATA_PATH)
    if "seconds" not in df.columns:
        df["seconds"] = range(len(df))

    # recent window (use last 200 samples if available)
    df_recent = df.tail(200)
    X = df_recent[["seconds"]]
    y = df_recent["vehicle_count"]

    # --- train simple regression model ---
    model = LinearRegression()
    model.fit(X, y)

    # predict next 30 seconds
    future_steps = 30
    future_times = np.arange(df["seconds"].iloc[-1] + 1,
                             df["seconds"].iloc[-1] + future_steps + 1)
    y_pred = model.predict(future_times.reshape(-1, 1))

    # build prediction frame
    df_pred = pd.DataFrame({
        "seconds": future_times,
        "predicted_count": y_pred
    })

    # risk assessment
    avg_pred = np.mean(y_pred)
    if avg_pred < CONGESTION_LIMIT * 0.5:
        risk = "LOW"
    elif avg_pred < CONGESTION_LIMIT:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    print(f"✅ Average predicted vehicle count: {avg_pred:.2f}")
    print(f"🚦 Congestion Risk Level: {risk}")

    # merge recent actuals + predictions for visualization
    df_recent = df_recent.rename(columns={"vehicle_count": "actual_count"})
    merged = pd.concat([df_recent[["seconds", "actual_count"]],
                        df_pred], ignore_index=True)
    merged.to_csv(OUT_PATH, index=False)
    print(f"Saved predictions to {OUT_PATH}")

if __name__ == "__main__":
    main()
