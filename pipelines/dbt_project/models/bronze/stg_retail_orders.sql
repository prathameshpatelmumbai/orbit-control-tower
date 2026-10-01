-- Bronze: Staging Retail Orders
SELECT
    order_id,
    TRY_CAST(timestamp AS TIMESTAMP) AS order_timestamp,
    customer_id,
    warehouse_id,
    product_category,
    sku,
    TRY_CAST(quantity AS INTEGER) AS quantity,
    TRY_CAST(unit_price AS DOUBLE) AS unit_price,
    TRY_CAST(discount_applied AS DOUBLE) AS discount_applied,
    TRY_CAST(total_amount AS DOUBLE) AS total_amount,
    payment_method,
    order_status,
    TRY_CAST(inventory_remaining AS INTEGER) AS inventory_remaining
FROM bronze_retail_orders
