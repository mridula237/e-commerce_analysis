"""
TheLook Ecommerce Ingestion Script
Loads all TheLook CSVs into DuckDB raw schema
Dataset: https://www.kaggle.com/datasets/mustafakeser4/looker-ecommerce-bigquery-dataset
"""

import duckdb
import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_PATH      = os.path.join(PROJECT_ROOT, "data", "thelook.duckdb")
RAW_DIR      = os.path.join(PROJECT_ROOT, "data", "raw")

# CSV filename → DuckDB table name
TABLES = {
    "orders.csv":               "raw_orders",
    "order_items.csv":          "raw_order_items",
    "users.csv":                "raw_users",
    "products.csv":             "raw_products",
    "inventory_items.csv":      "raw_inventory_items",
    "events.csv":               "raw_events",
    "distribution_centers.csv": "raw_distribution_centers",
}


def check_csvs_exist() -> bool:
    missing = [f for f in TABLES if not os.path.exists(os.path.join(RAW_DIR, f))]
    if missing:
        log.warning(f"Missing files: {missing}")
        return False
    return True


def load_csvs(conn):
    for fname, table in TABLES.items():
        fpath = os.path.join(RAW_DIR, fname)
        if not os.path.exists(fpath):
            log.warning(f"  Skipping {fname} — not found")
            continue
        log.info(f"  Loading {fname} → {table}")
        df = pd.read_csv(fpath, low_memory=False)
        conn.execute(f"DROP TABLE IF EXISTS {table}")
        conn.execute(f"CREATE TABLE {table} AS SELECT * FROM df")
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        log.info(f"    ✓ {n:,} rows")


def print_instructions():
    log.info("")
    log.info("=" * 60)
    log.info("Download TheLook dataset from Kaggle:")
    log.info("https://www.kaggle.com/datasets/mustafakeser4/looker-ecommerce-bigquery-dataset")
    log.info(f"Unzip all CSVs into: {RAW_DIR}")
    log.info("")
    log.info("Or via Kaggle CLI:")
    log.info("  pip install kaggle")
    log.info("  kaggle datasets download -d mustafakeser4/looker-ecommerce-bigquery-dataset")
    log.info(f"  unzip looker-ecommerce-bigquery-dataset.zip -d {RAW_DIR}")
    log.info("=" * 60)


def run_ingestion():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    if not check_csvs_exist():
        print_instructions()
        return False

    log.info(f"Connecting to DuckDB: {DB_PATH}")
    conn = duckdb.connect(DB_PATH)
    load_csvs(conn)

    tables = conn.execute("SHOW TABLES").df()
    log.info(f"\n✅ {len(tables)} tables loaded into DuckDB")
    conn.close()
    return True


if __name__ == "__main__":
    run_ingestion()
