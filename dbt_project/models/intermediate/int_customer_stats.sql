-- models/intermediate/int_customer_stats.sql
WITH orders AS (
    SELECT * FROM {{ ref('int_orders_enriched') }}
    WHERE order_status = 'Complete'
),

ref_date AS (
    SELECT MAX(order_date) AS max_date FROM orders
),

rfm_raw AS (
    SELECT
        user_id,
        COUNT(DISTINCT order_id)                AS frequency,
        SUM(net_revenue)                        AS monetary,
        MAX(order_date)                         AS last_order_date,
        MIN(order_date)                         AS first_order_date,
        DATEDIFF('day', MAX(order_date),
            (SELECT max_date FROM ref_date))    AS recency_days,
        AVG(net_revenue)                        AS avg_order_value,
        MAX(age_group)                          AS age_group,
        MAX(gender)                             AS gender,
        MAX(customer_state)                     AS state,
        MAX(traffic_source)                     AS traffic_source,
        SUM(CASE WHEN is_returned
            THEN 1 ELSE 0 END)                  AS returned_orders,
        ROUND(SUM(CASE WHEN is_returned
            THEN 1 ELSE 0 END)::DOUBLE
            / NULLIF(COUNT(DISTINCT order_id), 0) * 100, 1)
                                                AS return_rate_pct
    FROM orders
    GROUP BY user_id
),

rfm_scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days DESC)  AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC)      AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC)       AS m_score
    FROM rfm_raw
)

SELECT *,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3                   THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2                   THEN 'New Customers'
        WHEN r_score >= 3 AND m_score >= 3                   THEN 'Potential Loyalists'
        WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3  THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2                   THEN 'Hibernating'
        ELSE 'Needs Attention'
    END AS rfm_segment
FROM rfm_scored
