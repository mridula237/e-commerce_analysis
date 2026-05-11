"""
TheLook Ecommerce Ingestion Script
Loads all TheLook CSVs into BigQuery raw dataset
Dataset: https://www.kaggle.com/datasets/mustafakeser4/looker-ecommerce-bigquery-dataset
"""

import pandas as pd
import os
import logging
from google.cloud import bigquery
from google.oauth2 import service_account

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DIR      = os.path.join(PROJECT_ROOT, "data", "raw")

PROJECT_ID   = os.getenv("GCP_PROJECT", "thelook-pipeline")
DATASET      = "raw"
CREDENTIALS  = os.getenv("GOOGLE_APPLICATION_CREDENTIALS",
                          os.path.join(PROJECT_ROOT, "credentials.json"))

TABLES = {
    "orders.csv":               "raw_orders",
    "order_items.csv":          "raw_order_items",
    "users.csv":                "raw_users",
    "products.csv":             "raw_products",
    "inventory_items.csv":      "raw_inventory_items",
    "events.csv":               "raw_events",
    "distribution_centers.csv": "raw_distribution_centers",
}


def get_client() -> bigquery.Client:
    creds = service_account.Credentials.from_service_account_file(CREDENTIALS)
    return bigquery.Client(project=PROJECT_ID, credentials=creds)


def ensure_dataset(client: bigquery.Client):
    dataset_ref = bigquery.Dataset(f"{PROJECT_ID}.{DATASET}")
    dataset_ref.location = "US"
    client.create_dataset(dataset_ref, exists_ok=True)
    log.info(f"Dataset {PROJECT_ID}.{DATASET} ready")


def load_csvs(client: bigquery.Client):
    for fname, table in TABLES.items():
        fpath = os.path.join(RAW_DIR, fname)
        if not os.path.exists(fpath):
            log.warning(f"  Skipping {fname} — not found")
            continue

        log.info(f"  Loading {fname} → {DATASET}.{table}")
        df = pd.read_csv(fpath, low_memory=False)

        table_ref = f"{PROJECT_ID}.{DATASET}.{table}"
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            autodetect=True,
        )
        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()
        log.info(f"    ✓ {len(df):,} rows loaded")


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

    missing = [f for f in TABLES if not os.path.exists(os.path.join(RAW_DIR, f))]
    if missing:
        log.warning(f"Missing files: {missing}")
        print_instructions()
        return False

    client = get_client()
    ensure_dataset(client)
    load_csvs(client)

    log.info(f"\n✅ All tables loaded into BigQuery {PROJECT_ID}.{DATASET}")
    return True


if __name__ == "__main__":
    run_ingestion()
