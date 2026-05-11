WITH source AS (
    SELECT * FROM {{ source('thelook', 'products') }}
)

SELECT
    CAST(id AS STRING)                          AS product_id,
    name                                        AS product_name,
    category,
    brand,
    department,
    sku,
    CAST(cost AS FLOAT64)                       AS cost,
    CAST(retail_price AS FLOAT64)               AS retail_price,
    CAST(retail_price - cost AS FLOAT64)        AS gross_margin,
    CASE
        WHEN cost > 0
        THEN ROUND((retail_price - cost) / cost * 100, 2)
        ELSE NULL
    END                                         AS margin_pct,
    CAST(distribution_center_id AS STRING)      AS distribution_center_id
FROM source
WHERE id IS NOT NULL
  AND retail_price > 0
