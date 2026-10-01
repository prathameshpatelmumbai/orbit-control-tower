-- Silver: Fact Customer Sessions
-- Aggregates raw clicks into session-level KPIs: error count, average latency, total actions
SELECT
    session_id,
    customer_id,
    MIN(event_timestamp) AS session_start_time,
    MAX(event_timestamp) AS session_end_time,
    COUNT(*) AS total_interactions,
    AVG(client_latency_ms) AS avg_client_latency_ms,
    COUNT(CASE WHEN status_code >= 400 THEN 1 END) AS error_count,
    MAX(CASE WHEN action = 'checkout_step' THEN 1 ELSE 0 END) AS has_checkout
FROM {{ ref('stg_customer_events') }}
WHERE session_id IS NOT NULL
GROUP BY session_id, customer_id
