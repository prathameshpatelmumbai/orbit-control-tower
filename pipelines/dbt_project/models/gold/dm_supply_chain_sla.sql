-- Gold: Supply Chain SLA & Logistics Performance Mart
SELECT
    carrier_name,
    transport_mode,
    COUNT(*) AS total_shipments,
    AVG(transit_delay_hours) AS avg_delay_hours,
    ROUND(
        (COUNT(CASE WHEN transit_delay_hours = 0 THEN 1 END) * 100.0) / COUNT(*), 
        2
    ) AS on_time_sla_percentage,
    COUNT(CASE WHEN telemetry_alert_level = 'BREACH_COLD_CHAIN' THEN 1 END) AS cold_chain_breaches,
    COUNT(CASE WHEN telemetry_alert_level = 'SEVERE_DELAY' THEN 1 END) AS severe_delays
FROM {{ ref('fct_supply_chain') }}
GROUP BY carrier_name, transport_mode
ORDER BY total_shipments DESC
