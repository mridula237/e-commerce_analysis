.PHONY: help setup ingest dbt-run dbt-test dbt-docs dashboard pipeline

PYTHON := $(shell if [ -f venv/bin/python ]; then echo venv/bin/python; else echo python3; fi)

export DUCKDB_PATH := $(shell pwd)/data/thelook.duckdb

help:
	@echo "TheLook Ecommerce Pipeline"
	@echo "─────────────────────────────────────────"
	@echo "make setup      Create venv + install deps"
	@echo "make ingest     Load CSVs into DuckDB"
	@echo "make dbt-run    Run all dbt models"
	@echo "make dbt-test   Run dbt tests"
	@echo "make dashboard  Launch Streamlit dashboard"
	@echo "make pipeline   ingest + dbt-run + dbt-test"

setup:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install duckdb==1.1.0 dbt-core==1.8.0 dbt-duckdb==1.8.0 \
	    pandas==2.2.0 streamlit==1.31.0 plotly==5.18.0 python-dotenv==1.0.0

ingest:
	$(PYTHON) ingestion/ingest_thelook.py

dbt-run:
	cd dbt_project && dbt run --profiles-dir . \
	    --select staging intermediate marts

dbt-test:
	cd dbt_project && dbt test --profiles-dir .

dbt-docs:
	cd dbt_project && dbt docs generate --profiles-dir . && \
	    dbt docs serve --profiles-dir . --port 8081

dashboard:
	$(PYTHON) -m streamlit run dashboard/app.py

pipeline: ingest dbt-run dbt-test
	@echo "✅ Pipeline complete!"
