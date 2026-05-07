-- models/marts/mart_cohort_retention.sql
WITH orders AS (
    SELECT user_id, order_month
    FROM {{ ref('fct_orders') }}
    WHERE order_status = 'Complete'
),

first_order AS (
    SELECT user_id, MIN(order_month) AS cohort_month
    FROM orders
    GROUP BY user_id
),

activity AS (
    SELECT
        f.cohort_month,
        o.order_month                               AS activity_month,
        COUNT(DISTINCT o.user_id)                   AS active_users,
        DATEDIFF('month', f.cohort_month,
            o.order_month)                          AS months_since_first
    FROM orders o
    JOIN first_order f ON o.user_id = f.user_id
    GROUP BY f.cohort_month, o.order_month
),

cohort_sizes AS (
    SELECT cohort_month, active_users AS cohort_size
    FROM activity
    WHERE months_since_first = 0
)

SELECT
    a.cohort_month,
    a.activity_month,
    a.months_since_first,
    a.active_users,
    cs.cohort_size,
    ROUND(a.active_users::DOUBLE
        / cs.cohort_size * 100, 2)                 AS retention_pct
FROM activity a
JOIN cohort_sizes cs ON a.cohort_month = cs.cohort_month
ORDER BY a.cohort_month, a.months_since_first
