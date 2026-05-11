# TheLook Ecommerce Analytics Pipeline

![Pipeline CI](https://github.com/mridula237/e-commerce_analysis/actions/workflows/pipeline.yml/badge.svg)

## Business Problem

E-commerce companies generate massive amounts of transactional data across orders, customers, products, and web sessions — but most of it sits in raw tables that business teams cannot easily access or interpret. Without a structured analytics layer, questions like:

- *Which customer segments are at risk of churning?*
- *Where are users dropping off in the purchase funnel?*
- *Which product categories drive the most margin?*
- *Was last month's revenue dip an anomaly or a trend?*

...require a data engineer to write custom queries every time. Business teams are left waiting, and insights arrive too late to act on.

---

## What I Built

A fully automated ELT pipeline that reads from a **live BigQuery public dataset**, transforms it into business-ready analytics tables using dbt, and serves insights through an interactive Streamlit dashboard — including an AI layer that generates executive summaries and answers business questions in plain English.

No manual data loading. No static files. The pipeline always reflects live data and is validated automatically on every push via GitHub Actions CI.

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
bigquery-public-data.thelook_ecommerce
  (live dataset — orders, users, products,
   order_items, events, inventory, distribution_centers)
                    │
                    ▼
    dbt Core — 3-layer transformation
    ┌─────────────────────────────────────┐
    │  Staging      → clean & type-cast   │
    │  Intermediate → business logic      │
    │  Marts        → BI-ready tables     │
    └─────────────────────────────────────┘
                    │
                    ▼
        Google BigQuery (thelook-pipeline)
        datasets: staging | intermediate | marts
                    │
                    ▼
    GitHub Actions CI — automated validation
    (dbt compile → dbt run → dbt test on every push)
                    │
                    ▼
    Streamlit Dashboard — 5 pages
    + AI Insights layer (Llama3-70B via Groq)
```

### dbt Models

| Layer | Models | Materialized as |
|-------|--------|-----------------|
| Staging | stg_orders, stg_order_items, stg_users, stg_products, stg_events | Views |
| Intermediate | int_orders_enriched, int_customer_stats, int_funnel | Views |
| Marts | fct_orders, dim_customers, mart_product_performance, mart_cohort_retention, mart_funnel | Tables |

---

## Dashboard

| Page | What It Shows |
|------|---------------|
| Sales & Revenue | Revenue trend, US state breakdown, traffic source, age/gender split |
| Customer Analytics | RFM segments, cohort retention heatmap, return rate by segment |
| Product Performance | Category revenue, margin vs avg price by category, top brands |
| Web Funnel | Sessions → Product → Cart → Purchase conversion rates |
| AI Insights | Executive summaries, anomaly detection, segment recommendations, CSV upload |

---

## Technologies Used

| Layer | Technology |
|-------|-----------|
| Data Warehouse | Google BigQuery |
| Live Data Source | `bigquery-public-data.thelook_ecommerce` |
| Transformation | dbt Core + dbt-bigquery |
| CI/CD | GitHub Actions |
| Visualization | Streamlit + Plotly |
| AI Layer | Llama3-70B via Groq API |
| Language | Python, SQL |

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- Google Cloud account with BigQuery enabled
- GCP service account key with BigQuery Admin role
- Free Groq API key — [console.groq.com](https://console.groq.com)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/mridula237/e-commerce_analysis.git
cd e-commerce_analysis

# 2. Add your GCP service account key
# Download from GCP Console → IAM → Service Accounts → Keys
# Save as: credentials.json (in project root)

# 3. Install dependencies
make setup

# 4. Run the pipeline (reads live data — no downloads needed)
make pipeline
# This runs: dbt run → dbt test

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
├── dbt_project/
│   ├── models/
│   │   ├── staging/              # Clean + type-cast live source data
│   │   ├── intermediate/         # Business logic (RFM, funnel, enrichment)
│   │   └── marts/                # Final BI-ready tables
│   ├── macros/
│   │   └── generate_schema_name.sql
│   ├── schema.yml                # Data quality tests
│   └── dbt_project.yml
├── dashboard/
│   ├── app.py                    # Main 4-page dashboard
│   └── pages/
│       └── 5_AI_Insights.py      # AI insights page
├── Makefile                      # One-command pipeline runner
└── README.md
```
