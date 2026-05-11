.PHONY: help setup dbt-run dbt-test dbt-docs dashboard pipeline

PYTHON := $(shell if [ -f venv/bin/python ]; then echo venv/bin/python; else echo python3; fi)

export GOOGLE_APPLICATION_CREDENTIALS := $(shell pwd)/credentials.json
export GCP_PROJECT := thelook-pipeline

help:
	@echo "TheLook Ecommerce Pipeline"
	@echo "─────────────────────────────────────────"
	@echo "make setup      Create venv + install deps"
	@echo "make dbt-run    Build all dbt models"
	@echo "make dbt-test   Run dbt data quality tests"
	@echo "make dashboard  Launch Streamlit dashboard"
	@echo "make pipeline   dbt-run + dbt-test"

setup:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements-pipeline.txt

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

pipeline: dbt-run dbt-test
	@echo "✅ Pipeline complete!"
