WITH events AS (
    SELECT * FROM {{ ref('stg_events') }}
),

session_funnel AS (
    SELECT
        session_id,
        DATE_TRUNC(DATE(MIN(event_at)), MONTH)          AS event_month,
        MAX(CASE WHEN event_type = 'home'
            THEN 1 ELSE 0 END)                          AS visited_home,
        MAX(CASE WHEN event_type IN ('category','brand')
            THEN 1 ELSE 0 END)                          AS browsed_category,
        MAX(CASE WHEN event_type = 'product'
            THEN 1 ELSE 0 END)                          AS viewed_product,
        MAX(CASE WHEN event_type = 'cart'
            THEN 1 ELSE 0 END)                          AS added_to_cart,
        MAX(CASE WHEN event_type = 'purchase'
            THEN 1 ELSE 0 END)                          AS purchased,
        COUNT(*)                                        AS total_events,
        MAX(traffic_source)                             AS traffic_source,
        MAX(browser)                                    AS browser
    FROM events
    GROUP BY session_id
)

SELECT
    event_month,
    COUNT(*)                                            AS total_sessions,
    SUM(visited_home)                                   AS visited_home,
    SUM(browsed_category)                               AS browsed_category,
    SUM(viewed_product)                                 AS viewed_product,
    SUM(added_to_cart)                                  AS added_to_cart,
    SUM(purchased)                                      AS purchased,
    ROUND(CAST(SUM(browsed_category) AS FLOAT64)
        / NULLIF(COUNT(*), 0) * 100, 2)                AS home_to_browse_pct,
    ROUND(CAST(SUM(viewed_product) AS FLOAT64)
        / NULLIF(SUM(browsed_category), 0) * 100, 2)  AS browse_to_product_pct,
    ROUND(CAST(SUM(added_to_cart) AS FLOAT64)
        / NULLIF(SUM(viewed_product), 0) * 100, 2)    AS product_to_cart_pct,
    ROUND(CAST(SUM(purchased) AS FLOAT64)
        / NULLIF(SUM(added_to_cart), 0) * 100, 2)     AS cart_to_purchase_pct,
    ROUND(CAST(SUM(purchased) AS FLOAT64)
        / NULLIF(COUNT(*), 0) * 100, 2)               AS overall_conversion_pct
FROM session_funnel
GROUP BY event_month
ORDER BY event_month
