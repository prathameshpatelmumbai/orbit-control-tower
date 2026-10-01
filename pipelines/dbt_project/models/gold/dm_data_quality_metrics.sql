-- Gold: Operations Control Tower Quality Summary Mart
SELECT
    'banking_transactions' AS pipeline_name,
    COUNT(*) AS total_processed_records,
    ROUND(AVG(risk_score), 2) AS avg_health_or_risk_metric,
    COUNT(CASE WHEN is_high_risk THEN 1 END) AS flagged_anomaly_count,
    ROUND((COUNT(CASE WHEN NOT is_high_risk THEN 1 END) * 100.0) / COUNT(*), 2) AS data_quality_sla_pct
FROM {{ ref('fct_banking_transactions') }}

UNION ALL

SELECT
    'retail_orders' AS pipeline_name,
    COUNT(*) AS total_processed_records,
    ROUND(AVG(unit_price), 2) AS avg_health_or_risk_metric,
    COUNT(CASE WHEN stock_health_status = 'CRITICAL_LOW_STOCK' THEN 1 END) AS flagged_anomaly_count,
    ROUND((COUNT(CASE WHEN stock_health_status != 'CRITICAL_LOW_STOCK' THEN 1 END) * 100.0) / COUNT(*), 2) AS data_quality_sla_pct
FROM {{ ref('fct_retail_orders') }}

UNION ALL

SELECT
    'supply_chain' AS pipeline_name,
    COUNT(*) AS total_processed_records,
    ROUND(AVG(transit_delay_hours), 2) AS avg_health_or_risk_metric,
    COUNT(CASE WHEN telemetry_alert_level IN ('BREACH_COLD_CHAIN', 'SEVERE_DELAY') THEN 1 END) AS flagged_anomaly_count,
    ROUND((COUNT(CASE WHEN telemetry_alert_level = 'ON_SCHEDULE' THEN 1 END) * 100.0) / COUNT(*), 2) AS data_quality_sla_pct
FROM {{ ref('fct_supply_chain') }}
