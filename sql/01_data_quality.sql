-- ============================================================
-- 01_data_quality.sql  数据探索与质量检查
-- 1.1 数据总览 → 1.2 缺失值 → 1.3 异常值 → 1.4 重复值 → 1.5 外键一致性
-- ============================================================

-- ---------- 1.1 数据总览：6 张表记录数 ----------
SELECT 'orders' AS 表名, COUNT(*) AS 记录数 FROM orders
UNION ALL SELECT 'product_features', COUNT(*) FROM product_features
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'user_behaviors', COUNT(*) FROM user_behaviors
UNION ALL SELECT 'user_features', COUNT(*) FROM user_features
UNION ALL SELECT 'users', COUNT(*) FROM users;

-- ---------- 1.2 缺失值：orders 全字段 ----------
SELECT
    COUNT(CASE WHEN order_id IS NULL THEN 1 END)       AS missing_order_id,
    COUNT(CASE WHEN user_id IS NULL THEN 1 END)        AS missing_user_id,
    COUNT(CASE WHEN product_id IS NULL THEN 1 END)     AS missing_product_id,
    COUNT(CASE WHEN quantity IS NULL THEN 1 END)       AS missing_quantity,
    COUNT(CASE WHEN order_date IS NULL THEN 1 END)     AS missing_order_date,
    COUNT(CASE WHEN order_status IS NULL THEN 1 END)   AS missing_order_status,
    COUNT(CASE WHEN payment_method IS NULL THEN 1 END) AS missing_payment_method,
    COUNT(CASE WHEN unit_price IS NULL THEN 1 END)     AS missing_unit_price,
    COUNT(CASE WHEN total_amount IS NULL THEN 1 END)   AS missing_total_amount,
    COUNT(CASE WHEN discount IS NULL THEN 1 END)       AS missing_discount,
    COUNT(CASE WHEN actual_payment IS NULL THEN 1 END) AS missing_actual_payment,
    COUNT(CASE WHEN delivery_date IS NULL THEN 1 END)  AS missing_delivery_date,
    COUNT(CASE WHEN receive_date IS NULL THEN 1 END)   AS missing_receive_date,
    COUNT(CASE WHEN review_score IS NULL THEN 1 END)   AS missing_review_score,
    COUNT(CASE WHEN review_content IS NULL THEN 1 END) AS missing_review_content
FROM orders;

-- ---------- 1.2 缺失值：其余 5 表关键字段 ----------
SELECT 'products' AS 表名, COUNT(*) AS 总数,
       SUM(CASE WHEN product_name IS NULL THEN 1 ELSE 0 END) AS name_null,
       SUM(CASE WHEN category IS NULL THEN 1 ELSE 0 END)     AS category_null,
       SUM(CASE WHEN brand IS NULL THEN 1 ELSE 0 END)        AS brand_null
FROM products
UNION ALL
SELECT 'users', COUNT(*),
       SUM(CASE WHEN age IS NULL THEN 1 ELSE 0 END),
       SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END),
       SUM(CASE WHEN province IS NULL THEN 1 ELSE 0 END)
FROM users
UNION ALL
SELECT 'user_features', COUNT(*),
       SUM(CASE WHEN total_spent IS NULL THEN 1 ELSE 0 END),
       SUM(CASE WHEN order_count IS NULL THEN 1 ELSE 0 END),
       SUM(CASE WHEN consumption_level IS NULL THEN 1 ELSE 0 END)
FROM user_features
UNION ALL
SELECT 'product_features', COUNT(*),
       SUM(CASE WHEN total_revenue IS NULL THEN 1 ELSE 0 END),
       SUM(CASE WHEN conversion_rate IS NULL THEN 1 ELSE 0 END),
       SUM(CASE WHEN avg_review_score IS NULL THEN 1 ELSE 0 END)
FROM product_features
UNION ALL
SELECT 'user_behaviors', COUNT(*),
       SUM(CASE WHEN user_id IS NULL THEN 1 ELSE 0 END),
       SUM(CASE WHEN behavior_type IS NULL THEN 1 ELSE 0 END),
       SUM(CASE WHEN behavior_time IS NULL THEN 1 ELSE 0 END)
FROM user_behaviors;

-- ---------- 1.3 异常值：数值字段 MIN/MAX ----------
SELECT MIN(quantity) q_min, MAX(quantity) q_max,
       MIN(unit_price) p_min, MAX(unit_price) p_max,
       MIN(actual_payment) amt_min, MAX(actual_payment) amt_max
FROM orders;

SELECT MIN(age) a_min, MAX(age) a_max,
       MIN(account_balance) b_min, MAX(account_balance) b_max
FROM users;

SELECT MIN(price) p_min, MAX(price) p_max,
       MIN(sales_count) s_min, MAX(sales_count) s_max
FROM products;

SELECT MIN(behavior_time) time_min, MAX(behavior_time) time_max,
       MIN(duration_seconds) d_min, MAX(duration_seconds) d_max
FROM user_behaviors;

-- ---------- 1.4 重复值：主键唯一性 ----------
SELECT 'orders' AS 表名, COUNT(*) AS 总数, COUNT(DISTINCT order_id) AS 唯一数 FROM orders
UNION ALL SELECT 'products', COUNT(*), COUNT(DISTINCT product_id) FROM products
UNION ALL SELECT 'product_features', COUNT(*), COUNT(DISTINCT product_id) FROM product_features
UNION ALL SELECT 'users', COUNT(*), COUNT(DISTINCT user_id) FROM users
UNION ALL SELECT 'user_features', COUNT(*), COUNT(DISTINCT user_id) FROM user_features
UNION ALL SELECT 'user_behaviors', COUNT(*), COUNT(DISTINCT behavior_id) FROM user_behaviors;

-- ---------- 1.5 表间关联一致性 ----------
SELECT (SELECT COUNT(DISTINCT user_id) FROM orders)                                        AS o_user,
       (SELECT COUNT(*) FROM users)                                                        AS u_tot,
       (SELECT COUNT(*) FROM orders WHERE user_id IN (SELECT user_id FROM users))          AS matched_user,
       (SELECT COUNT(*) FROM orders WHERE product_id IN (SELECT product_id FROM products)) AS matched_product;
