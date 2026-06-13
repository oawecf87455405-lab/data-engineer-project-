import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# ── Extract ────────────────────────────────────────────────
df = pd.read_csv(
    r"C:\Users\Patip\Downloads\BestEnergyDW_Full_Update\BestEnergyDW_Full_Update\DimBranch_New_2568.csv",
    encoding="utf-8-sig"
)

# ── Transform ──────────────────────────────────────────────
df = df.rename(columns={
    "BranchID":     "branchid",
    "BranchName":   "branchname",
    "ProvinceID":   "provinceid",
    "ProvinceName": "provincename",
    "OpenDate":     "opendate",
    "Latitude":     "latitude",
    "Longitude":    "longitude",
})

df["opendate"]  = pd.to_datetime(df["opendate"])
df["latitude"]  = pd.to_numeric(df["latitude"])
df["longitude"] = pd.to_numeric(df["longitude"])

# ── Load → เข้าตาราง dimbranch เดิม ───────────────────────
engine = create_engine(
    "postgresql://postgres:BestSQL123!@localhost:5432/BestEnergyDW"
)

rows = df.to_dict(orient="records")

upsert_sql = text("""
    INSERT INTO dimbranch
        (branchid, branchname, provinceid, provincename,
         opendate, latitude, longitude)
    VALUES
        (:branchid, :branchname, :provinceid, :provincename,
         :opendate, :latitude, :longitude)
    ON CONFLICT (branchid) DO UPDATE SET
        branchname   = EXCLUDED.branchname,
        provinceid   = EXCLUDED.provinceid,
        provincename = EXCLUDED.provincename,
        opendate     = EXCLUDED.opendate,
        latitude     = EXCLUDED.latitude,
        longitude    = EXCLUDED.longitude
""")

with engine.begin() as conn:
    conn.execute(upsert_sql, rows)
    print(f"โหลดข้อมูลสำเร็จ {len(df)} แถว ✓")