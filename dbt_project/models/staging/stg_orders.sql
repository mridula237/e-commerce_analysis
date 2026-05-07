-- models/staging/stg_orders.sql
WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_orders') }}
)

SELECT
    CAST(order_id AS VARCHAR)                                    AS order_id,
    CAST(user_id AS VARCHAR)                                     AS user_id,
    status                                                       AS order_status,
    gender,
    CAST(num_of_item AS INTEGER)                                 AS num_items,
    CAST(created_at AS TIMESTAMP)                                AS created_at,
    CAST(returned_at AS TIMESTAMP)                               AS returned_at,
    CAST(shipped_at AS TIMESTAMP)                                AS shipped_at,
    CAST(delivered_at AS TIMESTAMP)                              AS delivered_at,
    DATE_TRUNC('day',   CAST(created_at AS TIMESTAMP))           AS order_date,
    DATE_TRUNC('month', CAST(created_at AS TIMESTAMP))           AS order_month,
    -- Delivery metrics
    CASE
        WHEN delivered_at IS NOT NULL AND shipped_at IS NOT NULL
        THEN DATEDIFF('day',
                CAST(shipped_at AS TIMESTAMP),
                CAST(delivered_at AS TIMESTAMP))
    END AS days_to_deliver,
    CASE
        WHEN delivered_at IS NOT NULL AND created_at IS NOT NULL
        THEN DATEDIFF('day',
                CAST(created_at AS TIMESTAMP),
                CAST(delivered_at AS TIMESTAMP))
    END AS fulfillment_days,
    CASE
        WHEN returned_at IS NOT NULL THEN TRUE ELSE FALSE
    END AS is_returned
FROM source
WHERE order_id IS NOT NULL
