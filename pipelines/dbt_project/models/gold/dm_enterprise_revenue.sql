-- Gold: Enterprise Daily & Hourly Revenue Mart
-- Combines settled banking transactions and confirmed retail orders into unified executive metrics
WITH banking_rev AS (
    SELECT
        DATE_TRUNC('hour', event_timestamp) AS window_hour,
        SUM(amount) AS banking_volume_usd,
        COUNT(*) AS banking_txn_count,
        SUM(CASE WHEN is_high_risk THEN 1 ELSE 0 END) AS high_risk_txn_count
    FROM {{ ref('fct_banking_transactions') }}
    WHERE status = 'settled'
    GROUP BY 1
),
retail_rev AS (
    SELECT
        DATE_TRUNC('hour', order_timestamp) AS window_hour,
        SUM(total_amount) AS retail_volume_usd,
        COUNT(*) AS retail_order_count
    FROM {{ ref('fct_retail_orders') }}
    GROUP BY 1
)
SELECT
    COALESCE(b.window_hour, r.window_hour) AS metric_hour,
    COALESCE(b.banking_volume_usd, 0.0) AS banking_revenue_usd,
    COALESCE(r.retail_volume_usd, 0.0) AS retail_revenue_usd,
    COALESCE(b.banking_volume_usd, 0.0) + COALESCE(r.retail_volume_usd, 0.0) AS total_enterprise_revenue_usd,
    COALESCE(b.banking_txn_count, 0) AS total_banking_txns,
    COALESCE(r.retail_order_count, 0) AS total_retail_orders,
    COALESCE(b.high_risk_txn_count, 0) AS high_risk_transactions
FROM banking_rev b
FULL OUTER JOIN retail_rev r ON b.window_hour = r.window_hour
ORDER BY metric_hour DESC
