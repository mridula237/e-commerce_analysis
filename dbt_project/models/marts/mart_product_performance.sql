WITH items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
),

products AS (
    SELECT * FROM {{ ref('stg_products') }}
),

orders AS (
    SELECT order_id, order_status, order_month
    FROM {{ ref('fct_orders') }}
    WHERE order_status = 'Complete'
)

SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    p.department,
    p.retail_price,
    p.cost,
    p.margin_pct,
    COUNT(DISTINCT oi.order_id)             AS total_orders,
    COUNT(oi.order_item_id)                 AS total_units_sold,
    SUM(oi.sale_price)                      AS total_revenue,
    AVG(oi.sale_price)                      AS avg_sale_price,
    ROUND((1 - AVG(oi.sale_price)
        / NULLIF(p.retail_price, 0)) * 100, 2) AS avg_discount_pct,
    SUM(CASE WHEN oi.is_returned
        THEN 1 ELSE 0 END)                  AS returned_units,
    ROUND(CAST(SUM(CASE WHEN oi.is_returned
        THEN 1 ELSE 0 END) AS FLOAT64)
        / NULLIF(COUNT(oi.order_item_id), 0) * 100, 2)
                                            AS return_rate_pct
FROM items oi
JOIN products p  ON oi.product_id = p.product_id
JOIN orders   o  ON oi.order_id   = o.order_id
GROUP BY
    p.product_id, p.product_name, p.category,
    p.brand, p.department, p.retail_price, p.cost, p.margin_pct
HAVING total_orders >= 5
ORDER BY total_revenue DESC
