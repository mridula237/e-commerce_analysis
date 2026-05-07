# TheLook Ecommerce Analytics Pipeline

![Pipeline CI](https://github.com/mridula237/e-commerce_analysis/actions/workflows/pipeline.yml/badge.svg)

## Business Problem

E-commerce companies generate massive amounts of transactional data across orders, customers, products, and web sessions but most of it sits in raw tables that business teams cannot easily access or interpret. Without a structured analytics layer, questions like:

- *Which customer segments are at risk of churning?*
- *Where are users dropping off in the purchase funnel?*
- *Which product categories drive the most margin?*
- *Was last month's revenue dip an anomaly or a trend?*

...require a data engineer to write custom queries every time. Business teams are left waiting, and insights arrive too late to act on.

---

## What I Built

A fully automated ELT pipeline that ingests raw e-commerce data, transforms it into business-ready analytics tables, and serves insights through an interactive dashboard including an AI layer that generates executive summaries and answers business questions in plain English.

The pipeline is validated automatically on every push via GitHub Actions CI, ensuring model integrity is always maintained.

---

## How the Analysis Solves the Problem

| Business Question | Solution |
|---|---|
| Who are our most valuable customers? | RFM segmentation — Champions, At Risk, Hibernating, etc. |
| Are we retaining customers month over month? | Cohort retention heatmap across all monthly cohorts |
| Where are users dropping off before purchase? | Web funnel — Sessions → Product → Cart → Purchase |
| Which categories and brands drive revenue? | Product performance scorecard with margin % and return rates |
| Why did revenue spike or drop last month? | AI-powered anomaly detection with LLM explanation |
| What does our data mean in plain English? | AI executive summary generated from live mart tables |
| Can non-technical teams explore their own data? | CSV upload — upload any file, get instant AI insights |

---

## Architecture

```
TheLook Dataset (Google/Looker)
7 CSV tables — orders, order_items, users,
products, inventory_items, events, distribution_centers
                    │
                    ▼
        Python Ingestion (Pandas)
                    │
                    ▼
            DuckDB (local warehouse)
                    │
                    ▼
    dbt Core — 3-layer transformation
    ┌─────────────────────────────────┐
    │  Staging      → clean & cast    │
    │  Intermediate → business logic  │
    │  Marts        → BI-ready tables │
    └─────────────────────────────────┘
                    │
                    ▼
    GitHub Actions CI — automated validation
    (dbt compile → dbt run → dbt test on every push)
                    │
                    ▼
    Streamlit Dashboard — 5 pages
    + AI Insights layer (Llama3 via Groq)
```

### dbt Models

| Layer | Models |
|-------|--------|
| Staging | stg_orders, stg_order_items, stg_users, stg_products, stg_events |
| Intermediate | int_orders_enriched, int_customer_stats, int_funnel |
| Marts | fct_orders, dim_customers, mart_product_performance, mart_cohort_retention, mart_funnel |

---

## Dashboard

| Page | What It Shows |
|------|---------------|
| Sales & Revenue | $2.7M revenue trend, US state breakdown, traffic source, age/gender split |
| Customer Analytics | RFM segments, cohort retention heatmap, return rate by segment |
| Product Performance | Category revenue, margin vs return scatter, top brands |
| Web Funnel | 681K sessions, 26.66% CVR, monthly conversion trend |
| AI Insights | Executive summaries, anomaly detection, segment recommendations, CSV upload |

---

## Technologies Used

| Layer | Technology | Why |
|-------|-----------|-----|
| Data Storage | DuckDB | Embedded, zero-cost, fast analytical queries |
| Transformation | dbt Core + dbt-duckdb | SQL-based, testable, version-controlled transforms |
| CI/CD | GitHub Actions | Automated pipeline validation on every push |
| Visualization | Streamlit + Plotly | Fast interactive dashboards in pure Python |
| AI Layer | Llama3-70B via Groq | Free, fast LLM for business insight generation |
| Language | Python, SQL | Industry standard for data engineering |

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- Free Kaggle account (for dataset download)
- Free Groq account (for AI features) — console.groq.com

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/mridula237/e-commerce_analysis.git
cd e-commerce_analysis

# 2. Install dependencies
make setup

# 3. Download TheLook dataset
# Go to: https://www.kaggle.com/datasets/mustafakeser4/looker-ecommerce-bigquery-dataset
# Download and unzip all CSVs into data/raw/

# 4. Run the pipeline
make ingest      # Load CSVs into DuckDB
make dbt-run     # Run all 13 dbt models
make dbt-test    # Validate data quality (25 tests)

# 5. Set up AI features (free at console.groq.com)
export GROQ_API_KEY=your_key_here

# 6. Launch dashboard
make dashboard
# Open http://localhost:8501
```

---

## Project Structure

```
e-commerce_analysis/
├── .github/
│   └── workflows/
│       └── pipeline.yml          # GitHub Actions CI
├── ingestion/
│   └── ingest_thelook.py         # CSV → DuckDB loader
├── dbt_project/
│   ├── models/
│   │   ├── staging/              # Clean + type-cast raw data
│   │   ├── intermediate/         # Business logic layer
│   │   └── marts/                # Final BI-ready tables
│   ├── schema.yml                # 25 data quality tests
│   └── dbt_project.yml
├── dashboard/
│   ├── app.py                    # Main 4-page dashboard
│   └── pages/
│       └── 5_AI_Insights.py      # AI insights page
├── Makefile                      # One-command pipeline runner
└── README.md
```
