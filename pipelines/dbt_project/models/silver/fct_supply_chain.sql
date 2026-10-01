-- Silver: Fact Supply Chain Shipments
-- Evaluates IoT cold-chain temperature thresholds, identifies transit delays, cleans coordinates
WITH deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY shipment_id ORDER BY telemetry_timestamp DESC) AS rn
    FROM {{ ref('stg_supply_chain') }}
    WHERE shipment_id IS NOT NULL
      AND current_latitude BETWEEN -90.0 AND 90.0
      AND current_longitude BETWEEN -180.0 AND 180.0
)
SELECT
    shipment_id,
    telemetry_timestamp,
    order_id,
    carrier_name,
    transport_mode,
    origin_hub,
    destination_hub,
    current_latitude,
    current_longitude,
    status,
    estimated_arrival,
    is_cold_chain,
    cargo_temp_celsius,
    transit_delay_hours,
    CASE
        WHEN is_cold_chain AND cargo_temp_celsius > -10.0 THEN 'BREACH_COLD_CHAIN'
        WHEN transit_delay_hours >= 24 THEN 'SEVERE_DELAY'
        WHEN transit_delay_hours > 0 THEN 'MODERATE_DELAY'
        ELSE 'ON_SCHEDULE'
    END AS telemetry_alert_level
FROM deduplicated
WHERE rn = 1
