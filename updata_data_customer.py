import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# ── Extract ────────────────────────────────────────────────
df = pd.read_csv(
    r"C:\Users\Patip\Downloads\BestEnergyDW_Full_Update\BestEnergyDW_Full_Update\DimCustomer_New_2568.csv",
    encoding="utf-8-sig"
)

# ── Transform ──────────────────────────────────────────────
df = df.rename(columns={
    "CustomerID":    "customerid",
    "FirstName":     "firstname",
    "LastName":      "lastname",
    "Gender":        "gender",
    "BirthDate":     "birthdate",
    "MemberLevel":   "memberlevel",
    "RegisterDate":  "registerdate",
})

df["birthdate"]    = pd.to_datetime(df["birthdate"])
df["registerdate"] = pd.to_datetime(df["registerdate"])

# ── Load → เข้าตาราง dimcustomer เดิม ─────────────────────
engine = create_engine(
    "postgresql://postgres:BestSQL123!@localhost:5432/BestEnergyDW"
)

rows = df.to_dict(orient="records")

upsert_sql = text("""
    INSERT INTO dimcustomer
        (customerid, firstname, lastname, gender,
         birthdate, memberlevel, registerdate)
    VALUES
        (:customerid, :firstname, :lastname, :gender,
         :birthdate, :memberlevel, :registerdate)
    ON CONFLICT (customerid) DO UPDATE SET
        firstname    = EXCLUDED.firstname,
        lastname     = EXCLUDED.lastname,
        gender       = EXCLUDED.gender,
        birthdate    = EXCLUDED.birthdate,
        memberlevel  = EXCLUDED.memberlevel,
        registerdate = EXCLUDED.registerdate
""")

with engine.begin() as conn:
    conn.execute(upsert_sql, rows)
    print(f"โหลดข้อมูลสำเร็จ {len(df)} แถว ✓")