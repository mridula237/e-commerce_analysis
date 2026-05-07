-- models/staging/stg_products.sql
WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_products') }}
)

SELECT
    CAST(id AS VARCHAR)                         AS product_id,
    name                                        AS product_name,
    category,
    brand,
    department,
    sku,
    CAST(cost AS DOUBLE)                        AS cost,
    CAST(retail_price AS DOUBLE)                AS retail_price,
    CAST(retail_price - cost AS DOUBLE)         AS gross_margin,
    CASE
        WHEN cost > 0
        THEN ROUND((retail_price - cost) / cost * 100, 2)
        ELSE NULL
    END                                         AS margin_pct,
    CAST(distribution_center_id AS VARCHAR)     AS distribution_center_id
FROM source
WHERE id IS NOT NULL
  AND retail_price > 0
