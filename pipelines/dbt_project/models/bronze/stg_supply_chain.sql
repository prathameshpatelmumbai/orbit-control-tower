-- Bronze: Staging Supply Chain Shipments
SELECT
    shipment_id,
    TRY_CAST(timestamp AS TIMESTAMP) AS telemetry_timestamp,
    order_id,
    carrier_name,
    transport_mode,
    origin_hub,
    destination_hub,
    TRY_CAST(current_latitude AS DOUBLE) AS current_latitude,
    TRY_CAST(current_longitude AS DOUBLE) AS current_longitude,
    status,
    TRY_CAST(estimated_arrival AS TIMESTAMP) AS estimated_arrival,
    is_cold_chain,
    TRY_CAST(cargo_temp_celsius AS DOUBLE) AS cargo_temp_celsius,
    TRY_CAST(transit_delay_hours AS INTEGER) AS transit_delay_hours
FROM bronze_supply_chain
