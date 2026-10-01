-- Bronze: Staging Customer Behavioral Events
SELECT
    event_id,
    TRY_CAST(timestamp AS TIMESTAMP) AS event_timestamp,
    session_id,
    customer_id,
    action,
    page_url,
    device_type,
    ip_address,
    TRY_CAST(client_latency_ms AS INTEGER) AS client_latency_ms,
    TRY_CAST(status_code AS INTEGER) AS status_code,
    TRY_CAST(payload_bytes AS INTEGER) AS payload_bytes
FROM bronze_customer_events
