-- models/intermediate/int_orders_enriched.sql
WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

items AS (
    SELECT
        order_id,
        COUNT(*)                        AS item_count,
        SUM(sale_price)                 AS gross_revenue,
        SUM(CASE WHEN is_returned
            THEN sale_price ELSE 0 END) AS returned_revenue,
        COUNT(DISTINCT product_id)      AS unique_products,
        SUM(CASE WHEN is_returned
            THEN 1 ELSE 0 END)          AS returned_items
    FROM {{ ref('stg_order_items') }}
    GROUP BY order_id
),

users AS (
    SELECT * FROM {{ ref('stg_users') }}
),

products AS (
    SELECT
        oi.order_id,
        AVG(p.cost)                     AS avg_item_cost,
        AVG(p.retail_price)             AS avg_retail_price,
        -- revenue at cost
        SUM(p.cost)                     AS total_cost
    FROM {{ ref('stg_order_items') }} oi
    JOIN {{ ref('stg_products') }} p
        ON oi.product_id = p.product_id
    GROUP BY oi.order_id
)

SELECT
    o.order_id,
    o.user_id,
    u.state                             AS customer_state,
    u.city                              AS customer_city,
    u.age_group,
    u.gender,
    u.traffic_source,
    o.order_status,
    o.order_date,
    o.order_month,
    o.created_at,
    o.shipped_at,
    o.delivered_at,
    o.returned_at,
    o.fulfillment_days,
    o.is_returned,
    COALESCE(i.item_count, 0)           AS item_count,
    COALESCE(i.gross_revenue, 0)        AS gross_revenue,
    COALESCE(i.returned_revenue, 0)     AS returned_revenue,
    COALESCE(i.gross_revenue, 0)
        - COALESCE(i.returned_revenue, 0) AS net_revenue,
    COALESCE(p.total_cost, 0)           AS total_cost,
    COALESCE(i.gross_revenue, 0)
        - COALESCE(p.total_cost, 0)     AS gross_profit,
    COALESCE(i.unique_products, 0)      AS unique_products,
    -- Order value tier
    CASE
        WHEN COALESCE(i.gross_revenue, 0) < 50   THEN 'Low (<$50)'
        WHEN COALESCE(i.gross_revenue, 0) < 150  THEN 'Mid ($50-150)'
        WHEN COALESCE(i.gross_revenue, 0) < 300  THEN 'High ($150-300)'
        ELSE 'Premium (>$300)'
    END AS order_value_tier
FROM orders o
LEFT JOIN items   i ON o.order_id = i.order_id
LEFT JOIN users   u ON o.user_id  = u.user_id
LEFT JOIN products p ON o.order_id = p.order_id
