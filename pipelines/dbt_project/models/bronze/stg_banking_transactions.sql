-- Bronze: Staging Banking Transactions
-- Raw ingestion pass-through with timestamp casting
SELECT
    event_id,
    TRY_CAST(timestamp AS TIMESTAMP) AS event_timestamp,
    account_id,
    customer_id,
    transaction_type,
    TRY_CAST(amount AS DOUBLE) AS amount,
    currency,
    channel,
    merchant_name,
    merchant_category,
    TRY_CAST(risk_score AS DOUBLE) AS risk_score,
    is_flagged,
    origin_country,
    status
FROM bronze_banking_transactions
