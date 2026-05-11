WITH source AS (
    SELECT * FROM {{ source('thelook', 'users') }}
)

SELECT
    CAST(id AS STRING)                          AS user_id,
    first_name,
    last_name,
    email,
    age,
    gender,
    state,
    city,
    postal_code                                 AS zip,
    country,
    latitude,
    longitude,
    traffic_source,
    CAST(created_at AS TIMESTAMP)               AS created_at,
    CASE
        WHEN age < 18              THEN 'Under 18'
        WHEN age BETWEEN 18 AND 24 THEN '18-24'
        WHEN age BETWEEN 25 AND 34 THEN '25-34'
        WHEN age BETWEEN 35 AND 44 THEN '35-44'
        WHEN age BETWEEN 45 AND 54 THEN '45-54'
        WHEN age >= 55             THEN '55+'
        ELSE 'Unknown'
    END AS age_group
FROM source
WHERE id IS NOT NULL
  AND country = 'United States'
