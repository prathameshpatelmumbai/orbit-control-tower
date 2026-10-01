-- Silver: Fact Banking Transactions
-- Cleanses, deduplicates, and flags suspicious transactions
WITH deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY event_timestamp DESC) AS rn
    FROM {{ ref('stg_banking_transactions') }}
    WHERE event_id IS NOT NULL
      AND account_id IS NOT NULL
      AND amount IS NOT NULL
      AND amount > 0
)
SELECT
    event_id,
    event_timestamp,
    account_id,
    customer_id,
    transaction_type,
    amount,
    currency,
    channel,
    merchant_name,
    merchant_category,
    risk_score,
    CASE 
        WHEN risk_score >= 80.0 THEN TRUE 
        ELSE FALSE 
    END AS is_high_risk,
    origin_country,
    status
FROM deduplicated
WHERE rn = 1
