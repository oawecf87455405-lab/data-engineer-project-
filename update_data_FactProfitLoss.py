import pandas as pd
import math
from sqlalchemy import create_engine, text

# ── Extract ────────────────────────────────────────────────
df = pd.read_csv(
    r"C:\Users\Patip\Downloads\BestEnergyDW_Full_Update\BestEnergyDW_Full_Update\FactProfitLoss_2568.csv",
    encoding="utf-8-sig"
)

# ── Transform ──────────────────────────────────────────────
df = df.rename(columns={
    "ProfitLossID":      "profitlossid",
    "BranchID":          "branchid",
    "YearMonth":         "yearmonth",
    "Revenue":           "revenue",
    "COGS":              "cogs",
    "OperatingExpense":  "operatingexpense",
    "NetProfit":         "netprofit",
})

df["yearmonth"]        = pd.to_datetime(df["yearmonth"])
df["revenue"]          = pd.to_numeric(df["revenue"])
df["cogs"]             = pd.to_numeric(df["cogs"])
df["operatingexpense"] = pd.to_numeric(df["operatingexpense"])
df["netprofit"]        = pd.to_numeric(df["netprofit"])

# ── แปลง NaN → None ────────────────────────────────────────
def nan_to_none(val):
    try:
        if val is None:
            return None
        if isinstance(val, float) and math.isnan(val):
            return None
        return val
    except Exception:
        return val

rows = [
    {k: nan_to_none(v) for k, v in row.items()}
    for row in df.to_dict(orient="records")
]

# ── Load → เข้าตาราง factprofitloss เดิม ──────────────────
engine = create_engine(
    "postgresql://postgres:BestSQL123!@localhost:5432/BestEnergyDW"
)

upsert_sql = text("""
    INSERT INTO factprofitloss
        (profitlossid, branchid, yearmonth, revenue,
         cogs, operatingexpense, netprofit)
    VALUES
        (:profitlossid, :branchid, :yearmonth, :revenue,
         :cogs, :operatingexpense, :netprofit)
    ON CONFLICT (profitlossid) DO UPDATE SET
        branchid         = EXCLUDED.branchid,
        yearmonth        = EXCLUDED.yearmonth,
        revenue          = EXCLUDED.revenue,
        cogs             = EXCLUDED.cogs,
        operatingexpense = EXCLUDED.operatingexpense,
        netprofit        = EXCLUDED.netprofit
""")

with engine.begin() as conn:
    conn.execute(upsert_sql, rows)
    print(f"โหลดข้อมูลสำเร็จ {len(df)} แถว ✓")