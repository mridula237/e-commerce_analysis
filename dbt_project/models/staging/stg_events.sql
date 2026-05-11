WITH source AS (
    SELECT * FROM {{ source('thelook', 'events') }}
)

SELECT
    CAST(id AS STRING)                               AS event_id,
    CAST(user_id AS STRING)                          AS user_id,
    sequence_number,
    session_id,
    CAST(created_at AS TIMESTAMP)                    AS event_at,
    DATE(created_at)                                 AS event_date,
    ip_address,
    city,
    state,
    postal_code                                      AS zip,
    browser,
    traffic_source,
    uri,
    event_type
FROM source
WHERE id IS NOT NULL
  AND event_type IN ('home', 'category', 'brand', 'product',
                     'cart', 'purchase', 'cancel')
