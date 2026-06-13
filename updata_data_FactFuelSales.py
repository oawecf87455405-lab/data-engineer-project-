import pandas as pd
import math
from sqlalchemy import create_engine, text

# ── Extract ────────────────────────────────────────────────
df = pd.read_csv(
    r"C:\Users\Patip\Downloads\BestEnergyDW_Full_Update\BestEnergyDW_Full_Update\FactFuelSales_2568.csv",
    encoding="utf-8-sig"
)

# ── Transform ──────────────────────────────────────────────
df = df.rename(columns={
    "TransactionID": "transactionid",
    "SaleDate":      "saledate",
    "BranchID":      "branchid",
    "CustomerID":    "customerid",
    "FuelTypeID":    "fueltypeid",
    "AmountTHB":     "amountthb",
    "Liters":        "liters",
})

df["saledate"]  = pd.to_datetime(df["saledate"])
df["amountthb"] = pd.to_numeric(df["amountthb"])
df["liters"]    = pd.to_numeric(df["liters"])

# ── แปลง NaN → None ให้ครบทุกกรณี ────────────────────────
def nan_to_none(val):
    if val is None:
        return None
    if val is float('nan'):
        return None
    try:
        if isinstance(val, float) and math.isnan(val):
            return None
        if str(val).lower() == 'nan':      # ← จับ object dtype nan
            return None
    except Exception:
        pass
    return val

rows = [
    {k: nan_to_none(v) for k, v in row.items()}
    for row in df.to_dict(orient="records")
]

# ── ยืนยันว่าไม่มี nan หลุดไป ──────────────────────────────
leaked = [r for r in rows if any(
    isinstance(v, float) and math.isnan(v) for v in r.values()
)]
if leaked:
    print(f"⚠ ยังมี nan หลุด {len(leaked)} แถว — หยุดก่อน load")
else:
    # ── Load → เข้าตาราง factfuelsales เดิม ───────────────
    engine = create_engine(
        "postgresql://postgres:BestSQL123!@localhost:5432/BestEnergyDW"
    )

    upsert_sql = text("""
        INSERT INTO factfuelsales
            (transactionid, saledate, branchid, customerid,
             fueltypeid, amountthb, liters)
        VALUES
            (:transactionid, :saledate, :branchid, :customerid,
             :fueltypeid, :amountthb, :liters)
        ON CONFLICT (transactionid) DO UPDATE SET
            saledate     = EXCLUDED.saledate,
            branchid     = EXCLUDED.branchid,
            customerid   = EXCLUDED.customerid,
            fueltypeid   = EXCLUDED.fueltypeid,
            amountthb    = EXCLUDED.amountthb,
            liters       = EXCLUDED.liters
    """)

    with engine.begin() as conn:
        conn.execute(upsert_sql, rows)
        print(f"โหลดข้อมูลสำเร็จ {len(df)} แถว ✓")