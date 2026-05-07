-- models/marts/mart_funnel.sql
SELECT * FROM {{ ref('int_funnel') }}
