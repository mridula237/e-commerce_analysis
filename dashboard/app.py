"""
TheLook Ecommerce Analytics Dashboard
US clothing retailer — orders, customers, products, web funnel
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from google.cloud import bigquery
from google.oauth2 import service_account

st.set_page_config(
    page_title="TheLook Analytics",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded",
)

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PROJECT_ID   = os.getenv("GCP_PROJECT", "thelook-pipeline")


@st.cache_resource
def get_client():
    # Streamlit Cloud: credentials stored in st.secrets
    if "gcp_service_account" in st.secrets:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
    else:
        # Local: credentials stored in credentials.json
        creds = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS",
                      os.path.join(PROJECT_ROOT, "credentials.json"))
        )
    return bigquery.Client(project=PROJECT_ID, credentials=creds)


def query(sql: str) -> pd.DataFrame:
    return get_client().query(sql).to_dataframe()


def check_ready() -> bool:
    try:
        n = query("SELECT COUNT(*) AS n FROM marts.fct_orders").iloc[0]["n"]
        return n > 0
    except Exception as e:
        st.write(f"Error: {e}")
        return False


if not check_ready():
    st.title("👗 TheLook Ecommerce Analytics")
    st.error("⚠️ No data found. Run: make pipeline")
    st.stop()


# ── Sidebar ──
st.sidebar.title("👗 TheLook Analytics")
page = st.sidebar.radio("Navigation", [
    "📦 Sales & Revenue",
    "👥 Customer Analytics",
    "🛍️ Product Performance",
    "🔁 Web Funnel",
])

# ══════════════════════════════════════════
# PAGE 1: Sales & Revenue
# ══════════════════════════════════════════
if page == "📦 Sales & Revenue":
    st.title("📦 Sales & Revenue")

    orders = query("SELECT * FROM marts.fct_orders")
    complete = orders[orders["order_status"].str.lower() == "complete"]

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Orders",      f"{len(orders):,}")
    col2.metric("Completed Orders",  f"{len(complete):,}")
    col3.metric("Total Revenue",     f"${complete['gross_revenue'].sum():,.0f}")
    col4.metric("Avg Order Value",   f"${complete['gross_revenue'].mean():,.2f}")
    col5.metric("Return Rate",       f"{orders['is_returned'].mean()*100:.1f}%")

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Monthly Revenue Trend")
        monthly = complete.groupby("order_month").agg(
            revenue=("gross_revenue", "sum"),
            orders=("order_id", "count")
        ).reset_index()
        fig = px.area(monthly, x="order_month", y="revenue",
                      title="Monthly Revenue ($)",
                      labels={"revenue": "Revenue ($)", "order_month": "Month"})
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Order Status Breakdown")
        status = orders["order_status"].value_counts().reset_index()
        status.columns = ["status", "count"]
        fig = px.pie(status, names="status", values="count",
                     title="Orders by Status", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader("Revenue by US State (Top 15)")
        state_rev = complete.groupby("customer_state")["gross_revenue"].sum().reset_index()
        state_rev.columns = ["state", "revenue"]
        fig = px.bar(
            state_rev.sort_values("revenue", ascending=False).head(15),
            x="state", y="revenue",
            title="Revenue by State ($)",
            color="revenue", color_continuous_scale="Blues"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        st.subheader("Revenue by Traffic Source")
        traffic = complete.groupby("traffic_source")["gross_revenue"].sum().reset_index()
        traffic.columns = ["source", "revenue"]
        fig = px.pie(traffic, names="source", values="revenue",
                     title="Revenue by Acquisition Channel", hole=0.35)
        st.plotly_chart(fig, use_container_width=True)

    col_e, col_f = st.columns(2)
    with col_e:
        st.subheader("Orders by Gender")
        gender = complete.groupby("gender")["gross_revenue"].sum().reset_index()
        fig = px.pie(gender, names="gender", values="gross_revenue",
                     title="Revenue Split by Gender", hole=0.35,
                     color_discrete_sequence=["#ff6b9d", "#4a90d9"])
        st.plotly_chart(fig, use_container_width=True)

    with col_f:
        st.subheader("Revenue by Age Group")
        age = complete.groupby("age_group")["gross_revenue"].sum().reset_index()
        age_order = ["Under 18", "18-24", "25-34", "35-44", "45-54", "55+"]
        age["age_group"] = pd.Categorical(age["age_group"], categories=age_order, ordered=True)
        age = age.sort_values("age_group")
        fig = px.bar(age, x="age_group", y="gross_revenue",
                     title="Revenue by Age Group",
                     color="gross_revenue", color_continuous_scale="Purples")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════
# PAGE 2: Customer Analytics
# ══════════════════════════════════════════
elif page == "👥 Customer Analytics":
    st.title("👥 Customer Analytics")

    customers = query("SELECT * FROM marts.dim_customers")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers",   f"{len(customers):,}")
    col2.metric("Champions",         f"{(customers['rfm_segment']=='Champions').sum():,}")
    col3.metric("At Risk",           f"{(customers['rfm_segment']=='At Risk').sum():,}")
    col4.metric("Avg Order Value",   f"${customers['avg_order_value'].mean():,.2f}")

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("RFM Customer Segments")
        seg = customers["rfm_segment"].value_counts().reset_index()
        seg.columns = ["segment", "count"]
        fig = px.pie(seg, names="segment", values="count",
                     title="Customer Distribution by Segment", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Revenue by Segment")
        seg_rev = customers.groupby("rfm_segment")["monetary"].sum().reset_index()
        seg_rev.columns = ["segment", "revenue"]
        fig = px.bar(seg_rev.sort_values("revenue"),
                     x="revenue", y="segment", orientation="h",
                     title="Total Revenue by RFM Segment ($)",
                     color="revenue", color_continuous_scale="RdYlGn")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Cohort Retention Heatmap")
    cohort = query("SELECT * FROM marts.mart_cohort_retention")
    cohort["cohort_month"] = pd.to_datetime(cohort["cohort_month"]).dt.strftime("%Y-%m")
    pivot = cohort.pivot_table(
        index="cohort_month",
        columns="months_since_first",
        values="retention_pct",
        aggfunc="mean"
    ).round(1)
    pivot = pivot[[c for c in pivot.columns if c <= 12]]
    fig = px.imshow(
        pivot,
        title="Monthly Cohort Retention % (0 = First Purchase Month)",
        labels={"x": "Months Since First Purchase",
                "y": "Cohort", "color": "Retention %"},
        color_continuous_scale="YlGn",
        aspect="auto",
        text_auto=True,
    )
    fig.update_layout(height=550)
    st.plotly_chart(fig, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader("Customers by Traffic Source")
        ts = customers["traffic_source"].value_counts().reset_index()
        ts.columns = ["source", "count"]
        fig = px.bar(ts, x="source", y="count",
                     title="Customer Acquisition by Channel",
                     color="count", color_continuous_scale="Teal")
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        st.subheader("Return Rate by Segment")
        rr = customers.groupby("rfm_segment")["return_rate_pct"].mean().reset_index()
        fig = px.bar(rr.sort_values("return_rate_pct", ascending=True),
                     x="return_rate_pct", y="rfm_segment", orientation="h",
                     title="Avg Return Rate by RFM Segment (%)",
                     color="return_rate_pct", color_continuous_scale="Reds")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════
# PAGE 3: Product Performance
# ══════════════════════════════════════════
elif page == "🛍️ Product Performance":
    st.title("🛍️ Product Performance")

    products = query("SELECT * FROM marts.mart_product_performance")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products",    f"{len(products):,}")
    col2.metric("Avg Margin",        f"{products['margin_pct'].mean():.1f}%")
    col3.metric("Avg Return Rate",   f"{products['return_rate_pct'].mean():.1f}%")
    col4.metric("Top Category",
                products.groupby("category")["total_revenue"].sum().idxmax())

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Revenue by Category")
        cat_rev = products.groupby("category")["total_revenue"].sum().reset_index()
        fig = px.bar(
            cat_rev.sort_values("total_revenue", ascending=True).tail(15),
            x="total_revenue", y="category", orientation="h",
            title="Revenue by Category ($)",
            color="total_revenue", color_continuous_scale="Blues"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Category: Margin vs Price")
        cat_summary = products.groupby("category").agg(
            avg_margin=("margin_pct", "mean"),
            avg_price=("avg_sale_price", "mean"),
            total_revenue=("total_revenue", "sum"),
            total_units=("total_units_sold", "sum")
        ).reset_index()
        fig = px.scatter(
            cat_summary,
            x="avg_margin", y="avg_price",
            size="total_revenue",
            color="total_units",
            hover_name="category",
            color_continuous_scale="Blues",
            title="Margin % vs Avg Sale Price by Category (bubble = revenue)",
            labels={
                "avg_margin": "Avg Margin %",
                "avg_price": "Avg Sale Price ($)",
                "total_units": "Units Sold"
            },
        )
        fig.add_vline(x=cat_summary["avg_margin"].mean(),
                      line_dash="dash", line_color="gray",
                      annotation_text="Avg margin")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 20 Products by Revenue")
    st.dataframe(
        products.head(20)[["product_name", "category", "brand", "retail_price",
                           "margin_pct", "total_units_sold", "total_revenue",
                           "avg_discount_pct", "return_rate_pct"]],
        hide_index=True, use_container_width=True,
        column_config={
            "retail_price":     st.column_config.NumberColumn(format="$%.2f"),
            "total_revenue":    st.column_config.NumberColumn(format="$%.0f"),
            "margin_pct":       st.column_config.NumberColumn(format="%.1f%%"),
            "avg_discount_pct": st.column_config.NumberColumn(format="%.1f%%"),
            "return_rate_pct":  st.column_config.NumberColumn(format="%.1f%%"),
        }
    )

    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader("Top 10 Brands by Revenue")
        brand_rev = products.groupby("brand")["total_revenue"].sum().reset_index()
        fig = px.bar(
            brand_rev.sort_values("total_revenue", ascending=False).head(10),
            x="brand", y="total_revenue",
            title="Top 10 Brands ($)",
            color="total_revenue", color_continuous_scale="Blues"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        st.subheader("Department Revenue Split")
        dept = products.groupby("department")["total_revenue"].sum().reset_index()
        fig = px.pie(dept, names="department", values="total_revenue",
                     title="Revenue by Department", hole=0.35)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════
# PAGE 4: Web Funnel
# ══════════════════════════════════════════
elif page == "🔁 Web Funnel":
    st.title("🔁 Web Purchase Funnel")

    funnel = query("SELECT * FROM marts.mart_funnel ORDER BY event_month")

    total = funnel.sum(numeric_only=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Sessions",    f"{int(total['total_sessions']):,}")
    col2.metric("Viewed Product",    f"{int(total['viewed_product']):,}")
    col3.metric("Added to Cart",     f"{int(total['added_to_cart']):,}")
    col4.metric("Purchased",         f"{int(total['purchased']):,}")
    col5.metric("Overall CVR",
                f"{total['purchased']/total['total_sessions']*100:.2f}%")

    st.divider()

    st.subheader("Overall Purchase Funnel")
    funnel_stages = pd.DataFrame({
        "Stage": ["Sessions", "Viewed Product", "Added to Cart", "Purchased"],
        "Count": [
            int(total["total_sessions"]),
            int(total["viewed_product"]),
            int(total["added_to_cart"]),
            int(total["purchased"]),
        ]
    })
    fig = px.funnel(funnel_stages, x="Count", y="Stage",
                    title="Purchase Funnel — All Time",
                    color_discrete_sequence=["#3498db"])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Conversion Rate Trend")
    funnel["event_month"] = pd.to_datetime(funnel["event_month"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=funnel["event_month"],
                             y=funnel["overall_conversion_pct"],
                             name="Overall CVR", line=dict(width=2)))
    fig.add_trace(go.Scatter(x=funnel["event_month"],
                             y=funnel["cart_to_purchase_pct"],
                             name="Cart → Purchase", line=dict(dash="dash")))
    fig.add_trace(go.Scatter(x=funnel["event_month"],
                             y=funnel["product_to_cart_pct"],
                             name="Product → Cart", line=dict(dash="dot")))
    fig.update_layout(title="Conversion Rates Over Time (%)",
                      xaxis_title="Month", yaxis_title="Conversion Rate (%)")
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Monthly Sessions vs Purchases")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=funnel["event_month"],
                             y=funnel["total_sessions"], name="Sessions",
                             opacity=0.6))
        fig.add_trace(go.Bar(x=funnel["event_month"],
                             y=funnel["purchased"], name="Purchases"))
        fig.update_layout(barmode="overlay", title="Sessions vs Purchases")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Funnel Stage Drop-off")
        latest = funnel.tail(3).sum(numeric_only=True)
        dropoff = pd.DataFrame({
            "Stage": ["Browse→Product", "Product→Cart", "Cart→Purchase"],
            "Drop-off %": [
                100 - latest["browse_to_product_pct"] / 3,
                100 - latest["product_to_cart_pct"] / 3,
                100 - latest["cart_to_purchase_pct"] / 3,
            ]
        })
        fig = px.bar(dropoff, x="Stage", y="Drop-off %",
                     title="Recent Drop-off Rate by Funnel Stage (%)",
                     color="Drop-off %", color_continuous_scale="Reds")
        st.plotly_chart(fig, use_container_width=True)
