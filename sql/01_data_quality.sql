-- ============================================================
-- E-Commerce Intelligence Hub
-- 01 - Data Quality Checks
-- ============================================================

-- 1. Row counts
SELECT 'customers' AS table_name, COUNT(*) AS row_count
FROM customers

UNION ALL

SELECT 'orders', COUNT(*)
FROM orders

UNION ALL

SELECT 'order_items', COUNT(*)
FROM order_items

UNION ALL

SELECT 'products', COUNT(*)
FROM products

UNION ALL

SELECT 'sellers', COUNT(*)
FROM sellers

UNION ALL

SELECT 'payments', COUNT(*)
FROM order_payments

UNION ALL

SELECT 'reviews', COUNT(*)
FROM order_reviews;


-- 2. Check for duplicate customer IDs
SELECT
    customer_id,
    COUNT(*) AS record_count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;


-- 3. Check orders with missing customer IDs
SELECT COUNT(*) AS missing_customer_ids
FROM orders
WHERE customer_id IS NULL;


-- 4. Check order status distribution
SELECT
    order_status,
    COUNT(*) AS order_count
FROM orders
GROUP BY order_status
ORDER BY order_count DESC;


-- 5. Check missing delivery dates
SELECT
    COUNT(*) AS total_orders,
    COUNT(order_delivered_customer_date) AS delivered_orders,
    COUNT(*) - COUNT(order_delivered_customer_date)
        AS missing_delivery_dates
FROM orders;
