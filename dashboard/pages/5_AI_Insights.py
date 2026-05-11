"""
AI Insights Page — TheLook Analytics
Two modes:
1. Auto-generated insights from TheLook mart tables
2. Upload your own CSV and get AI-powered insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import requests
from google.cloud import bigquery
from google.oauth2 import service_account

st.set_page_config(page_title="AI Insights", page_icon="🤖", layout="wide")

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
PROJECT_ID   = os.getenv("GCP_PROJECT", "thelook-pipeline")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
MODEL        = "llama-3.3-70b-versatile"


@st.cache_resource
def get_client():
    if "gcp_service_account" in st.secrets:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
    else:
        creds = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS",
                      os.path.join(PROJECT_ROOT, "credentials.json"))
        )
    return bigquery.Client(project=PROJECT_ID, credentials=creds)


def query(sql: str) -> pd.DataFrame:
    return get_client().query(sql).to_dataframe()


def call_groq(prompt: str, system: str = "You are a senior data analyst and business intelligence expert. Be concise, specific, and actionable.") -> str:
    if not GROQ_API_KEY:
        return "⚠️ GROQ_API_KEY not set. Run: export GROQ_API_KEY=your_key"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "max_tokens": 1024,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt},
        ],
    }
    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


st.title("🤖 AI-Powered Business Insights")
st.caption("Powered by Llama3-70B via Groq")

mode = st.tabs(["📊 TheLook Auto-Insights", "📁 Analyze Your Own CSV"])

# ══════════════════════════════════════════
# MODE 1: TheLook Auto Insights
# ══════════════════════════════════════════
with mode[0]:
    st.subheader("Automated Business Intelligence from TheLook Data")
    st.info("Click any button below to generate AI-powered insights from your pipeline data.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📋 Executive Summary")
        if st.button("Generate Weekly Executive Summary", use_container_width=True):
            with st.spinner("Analyzing data and generating summary..."):
                try:
                    orders    = query("SELECT * FROM marts.fct_orders")
                    complete  = orders[orders["order_status"].str.lower() == "complete"]
                    customers = query("SELECT * FROM marts.dim_customers")
                    monthly   = complete.groupby("order_month").agg(
                        revenue=("gross_revenue", "sum"),
                        orders=("order_id", "count")
                    ).reset_index().tail(6)
                    seg_counts = customers["rfm_segment"].value_counts().to_dict()
                    top_states = complete.groupby("customer_state")["gross_revenue"].sum().nlargest(5).to_dict()

                    prompt = f"""
You are writing a weekly executive summary for TheLook, a US e-commerce clothing retailer.

KEY METRICS:
- Total orders: {len(orders):,}
- Completed orders: {len(complete):,}
- Total revenue: ${complete['gross_revenue'].sum():,.0f}
- Average order value: ${complete['gross_revenue'].mean():,.2f}
- Return rate: {orders['is_returned'].mean()*100:.1f}%
- Total customers: {len(customers):,}

LAST 6 MONTHS REVENUE TREND:
{monthly[['order_month','revenue','orders']].to_string(index=False)}

CUSTOMER SEGMENTS:
{json.dumps(seg_counts, indent=2)}

TOP 5 STATES BY REVENUE:
{json.dumps({k: f'${v:,.0f}' for k,v in top_states.items()}, indent=2)}

Write a concise executive summary (3-4 paragraphs) covering:
1. Overall business performance
2. Key trends and what's driving them
3. Customer health (segment analysis)
4. Top 3 actionable recommendations for next week
"""
                    st.markdown(call_groq(prompt))
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        st.markdown("### 🔍 Anomaly Detection")
        if st.button("Detect Revenue Anomalies", use_container_width=True):
            with st.spinner("Scanning for anomalies..."):
                try:
                    orders   = query("SELECT * FROM marts.fct_orders")
                    complete = orders[orders["order_status"].str.lower() == "complete"]
                    monthly  = complete.groupby("order_month").agg(
                        revenue=("gross_revenue", "sum"),
                        orders=("order_id", "count"),
                    ).reset_index()
                    monthly["revenue_mom_pct"] = monthly["revenue"].pct_change() * 100
                    mean_rev = monthly["revenue_mom_pct"].mean()
                    std_rev  = monthly["revenue_mom_pct"].std()
                    monthly["is_anomaly"] = monthly["revenue_mom_pct"].abs() > mean_rev + 2 * std_rev

                    fig = px.bar(monthly, x="order_month", y="revenue_mom_pct",
                                 color="is_anomaly",
                                 color_discrete_map={True: "#e74c3c", False: "#3498db"},
                                 title="Month-over-Month Revenue Change % (Red = Anomaly)")
                    st.plotly_chart(fig, use_container_width=True)

                    anomalies = monthly[monthly["is_anomaly"]]
                    prompt = f"""
Analyze these revenue anomalies for TheLook e-commerce:

MONTHLY DATA:
{monthly[['order_month','revenue','revenue_mom_pct']].to_string(index=False)}

FLAGGED ANOMALIES:
{anomalies[['order_month','revenue','revenue_mom_pct']].to_string(index=False) if len(anomalies) > 0 else 'No major anomalies detected'}

For each anomaly provide: likely explanation, whether concerning, recommended action. Under 200 words.
"""
                    st.markdown("**AI Analysis:**")
                    st.markdown(call_groq(prompt))
                except Exception as e:
                    st.error(f"Error: {e}")

    st.divider()

    st.markdown("### 🎯 Customer Segment Action Plan")
    if st.button("Generate Segment Recommendations", use_container_width=True):
        with st.spinner("Analyzing segments..."):
            try:
                customers = query("""
                    SELECT rfm_segment,
                           COUNT(*) as customer_count,
                           ROUND(AVG(monetary),2) as avg_revenue,
                           ROUND(AVG(recency_days),0) as avg_recency_days,
                           ROUND(AVG(frequency),2) as avg_orders
                    FROM marts.dim_customers
                    GROUP BY rfm_segment ORDER BY avg_revenue DESC
                """)
                prompt = f"""
TheLook customer segments:
{customers.to_string(index=False)}

For EACH segment give:
1. One-sentence description
2. #1 marketing action RIGHT NOW
3. Expected impact
Under 400 words total.
"""
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    fig = px.bar(customers, x="rfm_segment", y="customer_count",
                                 color="avg_revenue", color_continuous_scale="RdYlGn",
                                 title="Customers per Segment")
                    fig.update_layout(xaxis_tickangle=-30)
                    st.plotly_chart(fig, use_container_width=True)
                with col_b:
                    st.markdown("**AI Recommendations:**")
                    st.markdown(call_groq(prompt))
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("### ⚡ Funnel Optimization")
    if st.button("Analyze Conversion Funnel", use_container_width=True):
        with st.spinner("Analyzing funnel..."):
            try:
                funnel = query("SELECT * FROM marts.mart_funnel ORDER BY event_month")
                total  = funnel.sum(numeric_only=True)
                prompt = f"""
TheLook funnel (all time):
Sessions:       {int(total['total_sessions']):,}
Viewed Product: {int(total['viewed_product']):,} ({total['viewed_product']/total['total_sessions']*100:.1f}%)
Added to Cart:  {int(total['added_to_cart']):,} ({total['added_to_cart']/total['viewed_product']*100:.1f}% of viewers)
Purchased:      {int(total['purchased']):,} ({total['purchased']/total['added_to_cart']*100:.1f}% of cart adders)
Overall CVR:    {total['purchased']/total['total_sessions']*100:.2f}%

Industry benchmarks: CVR 2-4%, cart abandonment 70%, product-to-cart 10-15%

Provide: performance vs benchmarks, biggest drop-off and why, top 3 tactics with expected lift, which stage to prioritize. Under 300 words.
"""
                st.markdown(call_groq(prompt))
            except Exception as e:
                st.error(f"Error: {e}")


# ══════════════════════════════════════════
# MODE 2: Upload Your Own CSV
# ══════════════════════════════════════════
with mode[1]:
    st.subheader("📁 Upload Any CSV — Get Instant AI Insights")
    st.info("Upload your own sales, customer, or product data and get instant AI-powered business insights.")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df):,} rows × {len(df.columns)} columns")

            with st.expander("📋 Data Preview", expanded=True):
                st.dataframe(df.head(10), use_container_width=True)
                c1, c2, c3 = st.columns(3)
                c1.metric("Rows", f"{len(df):,}")
                c2.metric("Columns", len(df.columns))
                c3.metric("Missing Values", df.isnull().sum().sum())

            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            cat_cols     = df.select_dtypes(include="object").columns.tolist()

            st.divider()
            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("### 🔍 Auto-Generate Insights")
                if st.button("Analyze My Data", use_container_width=True):
                    with st.spinner("AI is analyzing your data..."):
                        prompt = f"""
Business CSV dataset profile:
- Columns: {list(df.columns)}
- Shape: {df.shape[0]:,} rows × {df.shape[1]} columns
- Numeric columns: {numeric_cols}
- Categorical columns: {cat_cols}

Sample (first 5 rows):
{df.head(5).to_string(index=False)}

Statistical summary:
{df.describe().round(2).to_string()}

Missing values: {df.isnull().sum()[df.isnull().sum()>0].to_string() or 'None'}

Provide:
1. What this dataset is about (2 sentences)
2. 5 key insights (with specific numbers)
3. 3 data quality issues to watch
4. 3 business questions this data can answer
5. Top recommendation for what to analyze first
"""
                        st.markdown(call_groq(prompt))

            with col_b:
                st.markdown("### 📈 Quick Visualization")
                if numeric_cols:
                    x_col      = st.selectbox("X axis", df.columns.tolist())
                    y_col      = st.selectbox("Y axis", numeric_cols)
                    chart_type = st.selectbox("Chart type", ["Bar", "Line", "Scatter", "Histogram"])
                    if st.button("Generate Chart", use_container_width=True):
                        if chart_type == "Bar":
                            fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                        elif chart_type == "Line":
                            fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over {x_col}")
                        elif chart_type == "Scatter":
                            fig = px.scatter(df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
                        else:
                            fig = px.histogram(df, x=y_col, title=f"Distribution of {y_col}")
                        st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.markdown("### 💬 Ask a Question About Your Data")
            user_question = st.text_input(
                "Ask anything...",
                placeholder="e.g. What are the top 5 products by revenue? Which month had highest sales?"
            )
            if st.button("Get Answer", use_container_width=True) and user_question:
                with st.spinner("Thinking..."):
                    prompt = f"""
Dataset: columns={list(df.columns)}, shape={df.shape}
Sample:
{df.head(10).to_string(index=False)}
Stats:
{df.describe().round(2).to_string()}

Question: {user_question}

Answer specifically using the data. Use exact values where possible. Under 200 words.
"""
                    st.markdown(f"**Answer:** {call_groq(prompt)}")

            if numeric_cols:
                st.divider()
                st.markdown("### 🚨 Detect Anomalies")
                anomaly_col = st.selectbox("Column to scan", numeric_cols)
                if st.button("Find Anomalies", use_container_width=True):
                    with st.spinner("Scanning..."):
                        mean = df[anomaly_col].mean()
                        std  = df[anomaly_col].std()
                        df["is_anomaly"] = (df[anomaly_col] - mean).abs() > 2 * std
                        anomalies = df[df["is_anomaly"]]
                        fig = px.scatter(df, y=anomaly_col, color="is_anomaly",
                                         color_discrete_map={True: "#e74c3c", False: "#3498db"},
                                         title=f"Anomaly Detection: {anomaly_col}")
                        st.plotly_chart(fig, use_container_width=True)
                        st.metric("Anomalies Found", f"{len(anomalies):,} of {len(df):,} rows")
                        if len(anomalies) > 0:
                            st.dataframe(anomalies.drop(columns=["is_anomaly"]).head(10), use_container_width=True)
                            prompt = f"""
Anomaly detection for '{anomaly_col}':
Mean: {mean:.2f}, Std: {std:.2f}
Anomalies: {len(anomalies)} of {len(df)} rows ({len(anomalies)/len(df)*100:.1f}%)
Values: {anomalies[anomaly_col].tolist()[:10]}

In 3-4 sentences: what these anomalies likely represent, whether concerning, recommended action.
"""
                            st.markdown(f"**AI Explanation:** {call_groq(prompt)}")

        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.markdown("""
        **What you can upload:**
        - 📦 Sales data (orders, revenue, products)
        - 👥 Customer data (demographics, purchase history)
        - 📊 Marketing data (campaign performance, conversions)
        - 🏪 Inventory data (stock levels, SKUs)

        **What you'll get:**
        - 🔍 Automatic data profiling and key insights
        - 🚨 Anomaly detection with AI explanation
        - 💬 Natural language Q&A about your data
        - 📈 Instant visualizations
        """)
