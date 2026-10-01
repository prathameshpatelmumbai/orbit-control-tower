-- Silver: Fact Retail Orders
-- Deduplicates orders, validates inventory remaining bounds, and computes discounts
WITH deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_timestamp DESC) AS rn
    FROM {{ ref('stg_retail_orders') }}
    WHERE order_id IS NOT NULL
      AND customer_id IS NOT NULL
      AND total_amount IS NOT NULL
      AND total_amount > 0
)
SELECT
    order_id,
    order_timestamp,
    customer_id,
    warehouse_id,
    product_category,
    sku,
    quantity,
    unit_price,
    discount_applied,
    total_amount,
    payment_method,
    order_status,
    GREATEST(0, inventory_remaining) AS inventory_remaining,
    CASE 
        WHEN inventory_remaining <= 10 THEN 'CRITICAL_LOW_STOCK'
        WHEN inventory_remaining <= 50 THEN 'LOW_STOCK'
        ELSE 'OPTIMAL_STOCK'
    END AS stock_health_status
FROM deduplicated
WHERE rn = 1
