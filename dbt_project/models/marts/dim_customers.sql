-- models/marts/dim_customers.sql
SELECT
    user_id,
    frequency,
    monetary,
    avg_order_value,
    recency_days,
    last_order_date,
    first_order_date,
    return_rate_pct,
    returned_orders,
    r_score,
    f_score,
    m_score,
    rfm_segment,
    age_group,
    gender,
    state,
    traffic_source
FROM {{ ref('int_customer_stats') }}
