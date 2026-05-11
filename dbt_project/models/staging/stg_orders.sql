WITH source AS (
    SELECT * FROM {{ source('thelook', 'orders') }}
)

SELECT
    CAST(order_id AS STRING)                                     AS order_id,
    CAST(user_id AS STRING)                                      AS user_id,
    status                                                       AS order_status,
    gender,
    CAST(num_of_item AS INT64)                                   AS num_items,
    CAST(created_at AS TIMESTAMP)                                AS created_at,
    CAST(returned_at AS TIMESTAMP)                               AS returned_at,
    CAST(shipped_at AS TIMESTAMP)                                AS shipped_at,
    CAST(delivered_at AS TIMESTAMP)                              AS delivered_at,
    DATE(created_at)                                             AS order_date,
    DATE_TRUNC(DATE(created_at), MONTH)                          AS order_month,
    CASE
        WHEN delivered_at IS NOT NULL AND shipped_at IS NOT NULL
        THEN DATE_DIFF(DATE(delivered_at), DATE(shipped_at), DAY)
    END AS days_to_deliver,
    CASE
        WHEN delivered_at IS NOT NULL AND created_at IS NOT NULL
        THEN DATE_DIFF(DATE(delivered_at), DATE(created_at), DAY)
    END AS fulfillment_days,
    CASE
        WHEN returned_at IS NOT NULL THEN TRUE ELSE FALSE
    END AS is_returned
FROM source
WHERE order_id IS NOT NULL
