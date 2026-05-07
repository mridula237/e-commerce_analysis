-- models/staging/stg_order_items.sql
WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_order_items') }}
)

SELECT
    CAST(id AS VARCHAR)                         AS order_item_id,
    CAST(order_id AS VARCHAR)                   AS order_id,
    CAST(user_id AS VARCHAR)                    AS user_id,
    CAST(product_id AS VARCHAR)                 AS product_id,
    CAST(inventory_item_id AS VARCHAR)          AS inventory_item_id,
    status                                      AS item_status,
    CAST(created_at AS TIMESTAMP)               AS created_at,
    CAST(shipped_at AS TIMESTAMP)               AS shipped_at,
    CAST(delivered_at AS TIMESTAMP)             AS delivered_at,
    CAST(returned_at AS TIMESTAMP)              AS returned_at,
    CAST(sale_price AS DOUBLE)                  AS sale_price,
    CASE WHEN status = 'Returned' OR returned_at IS NOT NULL
         THEN TRUE ELSE FALSE END               AS is_returned
FROM source
WHERE order_id IS NOT NULL
