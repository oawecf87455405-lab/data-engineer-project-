import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
import logging
import time

logging.basicConfig(
    filename="etl_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
print("ETL START")
logging.info("ETL START")

start_time = time.time()

# PostgreSQL Connection
DB_USER = "postgres"
DB_PASSWORD = "BestSQL123!"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "BestEnergyDW"
engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
print("เชื่อม PostgreSQL สำเร็จ")
logging.info("Connected PostgreSQL SUCCESS")
# วันที่ปัจจุบัน
today = datetime.today().date()
print("วันนี้ =", today)
logging.info(f"Running date {today}")
# =========================
# DimBranch
# =========================
for period in ["2026", "2027", "2028"]:
    df = pd.read_csv(
        f"raw_data/DimBranch_New_{period}.csv"
    )
    print("อ่าน CSV สำเร็จ")
    df.columns = [
        "branchid",
        "branchname",
        "provinceid",
        "provincename",
        "opendate",
        "latitude",
        "longitude"
    ]
    df.to_sql(
        "dimbranch",
        engine,
        if_exists="append",
        index=False,
        method=lambda table, conn, keys, data_iter: conn.execute(
            __import__("sqlalchemy").text(
                f"INSERT INTO dimbranch ({','.join(keys)}) VALUES ({','.join([':'+k for k in keys])}) ON CONFLICT (branchid) DO NOTHING"
            ),
            [dict(zip(keys, row)) for row in data_iter]
        )
    )
    print("โหลดเข้า PostgreSQL สำเร็จ")
    logging.info("Load PostgreSQL SUCCESS")
# =========================
# DimCustomer
# =========================
for period in ["2026", "2027", "2028"]:
    df = pd.read_csv(
        f"raw_data/DimCustomer_New_{period}.csv"
    )
    print("อ่าน CSV สำเร็จ")
    df.columns = [
        "customerid",
        "firstname",
        "lastname",
        "gender",
        "birthdate",
        "memberlevel",
        "registerdate"
    ]
    df.to_sql(
        "dimcustomer",
        engine,
        if_exists="append",
        index=False,
        method=lambda table, conn, keys, data_iter: conn.execute(
            __import__("sqlalchemy").text(
                f"INSERT INTO dimcustomer ({','.join(keys)}) VALUES ({','.join([':'+k for k in keys])}) ON CONFLICT (customerid) DO NOTHING"
            ),
            [dict(zip(keys, row)) for row in data_iter]
        )
    )
    print("โหลดเข้า PostgreSQL สำเร็จ")
    logging.info("Load PostgreSQL SUCCESS")
# =========================
# FactFuelSales
# =========================
for period in ["2026", "2027", "2028"]:
    filename = f"raw_data/FactFuelSales_{period}.csv"
    df = pd.read_csv(filename)
    df["SaleDate"] = pd.to_datetime(
        df["SaleDate"]
    ).dt.date
    df_today = df[
        df["SaleDate"] == today
    ]
    print(f"{filename} → วันนี้มีข้อมูล {len(df_today)} รายการ")
    logging.info(
        f"{filename} today rows = {len(df_today)}"
    )
    if len(df_today) > 0:
        df_today.columns = [
            "transactionid",
            "saledate",
            "branchid",
            "customerid",
            "fueltypeid",
            "amountthb",
            "liters"
        ]
        df_today.to_sql(
            "factfuelsales",
            engine,
            if_exists="append",
            index=False,
            method=lambda table, conn, keys, data_iter: conn.execute(
                __import__("sqlalchemy").text(
                    f"INSERT INTO factfuelsales ({','.join(keys)}) VALUES ({','.join([':'+k for k in keys])}) ON CONFLICT (transactionid) DO NOTHING"
                ),
                [dict(zip(keys, row)) for row in data_iter]
            )
        )
        print("โหลดเข้า PostgreSQL สำเร็จ")
        logging.info("Load PostgreSQL SUCCESS")
    else:
        print("วันนี้ไม่มีข้อมูล")
# =========================
# FactCafeSales
# =========================
for period in ["2026", "2027", "2028"]:
    filename = f"raw_data/FactCafeSales_{period}.csv"
    df = pd.read_csv(filename)
    df["SaleDate"] = pd.to_datetime(
        df["SaleDate"]
    ).dt.date
    df_today = df[
        df["SaleDate"] == today
    ]
    print(f"{filename} → วันนี้มีข้อมูล {len(df_today)} รายการ")
    logging.info(
        f"{filename} today rows = {len(df_today)}"
    )
    if len(df_today) > 0:
        df_today.columns = [
            "cafesaleid",
            "branchid",
            "productid",
            "saledate",
            "quantity",
            "revenue"
        ]
        df_today.to_sql(
            "factcafesales",
            engine,
            if_exists="append",
            index=False,
            method=lambda table, conn, keys, data_iter: conn.execute(
                __import__("sqlalchemy").text(
                    f"INSERT INTO factcafesales ({','.join(keys)}) VALUES ({','.join([':'+k for k in keys])}) ON CONFLICT (cafesaleid) DO NOTHING"
                ),
                [dict(zip(keys, row)) for row in data_iter]
            )
        )
        print("โหลดเข้า PostgreSQL สำเร็จ")
        logging.info("Load PostgreSQL SUCCESS")
    else:
        print("วันนี้ไม่มีข้อมูล")
# =========================
# FactStoreSales
# =========================
for period in ["2026", "2027", "2028"]:
    filename = f"raw_data/FactStoreSales_{period}.csv"
    df = pd.read_csv(filename)
    df["SaleDate"] = pd.to_datetime(
        df["SaleDate"]
    ).dt.date
    df_today = df[
        df["SaleDate"] == today
    ]
    print(f"{filename} → วันนี้มีข้อมูล {len(df_today)} รายการ")
    logging.info(
        f"{filename} today rows = {len(df_today)}"
    )
    if len(df_today) > 0:
        df_today.columns = [
            "storesaleid",
            "branchid",
            "productid",
            "saledate",
            "quantity",
            "revenue"
        ]
        df_today.to_sql(
            "factstoresales",
            engine,
            if_exists="append",
            index=False,
            method=lambda table, conn, keys, data_iter: conn.execute(
                __import__("sqlalchemy").text(
                    f"INSERT INTO factstoresales ({','.join(keys)}) VALUES ({','.join([':'+k for k in keys])}) ON CONFLICT (storesaleid) DO NOTHING"
                ),
                [dict(zip(keys, row)) for row in data_iter]
            )
        )
        print("โหลดเข้า PostgreSQL สำเร็จ")
        logging.info("Load PostgreSQL SUCCESS")
    else:
        print("วันนี้ไม่มีข้อมูล")
# =========================
# FactProfitLoss
# =========================
for period in ["2026", "2027", "2028"]:
    df = pd.read_csv(
        f"raw_data/FactProfitLoss_{period}.csv"
    )
    print("อ่าน CSV สำเร็จ")
    df.columns = [
        "profitlossid",
        "branchid",
        "yearmonth",
        "revenue",
        "cogs",
        "operatingexpense",
        "netprofit"
    ]
    df.to_sql(
        "factprofitloss",
        engine,
        if_exists="append",
        index=False,
        method=lambda table, conn, keys, data_iter: conn.execute(
            __import__("sqlalchemy").text(
                f"INSERT INTO factprofitloss ({','.join(keys)}) VALUES ({','.join([':'+k for k in keys])}) ON CONFLICT (profitlossid) DO NOTHING"
            ),
            [dict(zip(keys, row)) for row in data_iter]
        )
    )
    print("โหลดเข้า PostgreSQL สำเร็จ")
    logging.info("Load PostgreSQL SUCCESS")

print("ETL COMPLETE")
logging.info("ETL COMPLETE")

end_time = time.time()
runtime = end_time - start_time

etl_log = pd.DataFrame([{
    "run_time": datetime.now(),
    "status": "SUCCESS",
    "message": f"ETL finished in {runtime:.2f} seconds"
}])

etl_log.to_sql(
    "etl_history",
    engine,
    if_exists="append",
    index=False
)