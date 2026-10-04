# analyze.py
# Summary: km_since_service is the dominant predictor of breakdown (r=0.40), with avg_daily_km
# (r=0.25) and load_factor (r=0.22) as secondary signals. Total odometer and age are noise (r~0).
# Risk score combines these three columns, normalised 0-100, so the fleet team can act before the
# 80%-rule ever triggers.

import pandas as pd

df = pd.read_csv("fleet_history.csv")

# --- Step 1: compare breakdown vs non-breakdown groups column by column ---
print("=== Group means (broke_down=1 vs 0) ===")
print(df.groupby("broke_down").mean(numeric_only=True).T.rename(columns={0: "no_breakdown", 1: "breakdown"}))

print("\n=== Correlation with broke_down ===")
corr = df.corr(numeric_only=True)["broke_down"].drop("broke_down").sort_values(ascending=False)
print(corr)

# Result:
#   km_since_service  0.40  <-- strongest by far
#   avg_daily_km      0.25
#   load_factor       0.22
#   odometer_km       0.002 <-- total mileage does NOT separate the groups
#   age_years        -0.001 <-- age does NOT separate the groups either

# --- Step 2: build a 0-100 risk score from the three separating columns ---
# Normalise each to [0, 1] then weight by their correlation magnitude.
W_KM_SINCE   = 0.404
W_DAILY_KM   = 0.252
W_LOAD       = 0.215
TOTAL_W      = W_KM_SINCE + W_DAILY_KM + W_LOAD


def normalise(series: pd.Series) -> pd.Series:
    lo, hi = series.min(), series.max()
    return (series - lo) / (hi - lo) if hi > lo else pd.Series(0.0, index=series.index)


df["risk_score"] = (
    (
        W_KM_SINCE * normalise(df["km_since_service"])
        + W_DAILY_KM * normalise(df["avg_daily_km"])
        + W_LOAD    * normalise(df["load_factor"])
    )
    / TOTAL_W
    * 100
).round(1)

# --- Step 3: print cars ranked by risk, highest first ---
ranked = df[["car_id", "km_since_service", "avg_daily_km", "load_factor", "risk_score", "broke_down"]].sort_values(
    "risk_score", ascending=False
)

print("\n=== Fleet ranked by breakdown risk (highest first) ===")
print(ranked.to_string(index=False))

print(
    f"\nFleet size: {len(df)}  |  Historical breakdowns: {df['broke_down'].sum()}  "
    f"({100 * df['broke_down'].mean():.1f}%)"
)
print("Top 10 by risk score:")
print(ranked.head(10)[["car_id", "risk_score", "broke_down"]].to_string(index=False))
