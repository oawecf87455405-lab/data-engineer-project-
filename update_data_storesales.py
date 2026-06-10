import pandas as pd
import math
from sqlalchemy import create_engine, text

# ── Extract ────────────────────────────────────────────────
df = pd.read_csv(
    r"C:\Users\Patip\Downloads\BestEnergyDW_Full_Update\BestEnergyDW_Full_Update\FactStoreSales_2568.csv",
    encoding="utf-8-sig"
)

# ── Transform ──────────────────────────────────────────────
df = df.rename(columns={
    "StoreSaleID": "storesaleid",
    "BranchID":    "branchid",
    "ProductID":   "productid",
    "SaleDate":    "saledate",
    "Quantity":    "quantity",
    "Revenue":     "revenue",
})

df["saledate"] = pd.to_datetime(df["saledate"])
df["quantity"] = pd.to_numeric(df["quantity"])
df["revenue"]  = pd.to_numeric(df["revenue"])

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

# ── Load → เข้าตาราง factstoresales เดิม ──────────────────
engine = create_engine(
    "postgresql://postgres:BestSQL123!@localhost:5432/BestEnergyDW"
)

upsert_sql = text("""
    INSERT INTO factstoresales
        (storesaleid, branchid, productid, saledate,
         quantity, revenue)
    VALUES
        (:storesaleid, :branchid, :productid, :saledate,
         :quantity, :revenue)
    ON CONFLICT (storesaleid) DO UPDATE SET
        branchid  = EXCLUDED.branchid,
        productid = EXCLUDED.productid,
        saledate  = EXCLUDED.saledate,
        quantity  = EXCLUDED.quantity,
        revenue   = EXCLUDED.revenue
""")

with engine.begin() as conn:
    conn.execute(upsert_sql, rows)
    print(f"โหลดข้อมูลสำเร็จ {len(df)} แถว ✓")

