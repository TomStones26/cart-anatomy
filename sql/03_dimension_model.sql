-- ============================================================
-- 03_dimension_model.sql  星型模型构建
-- dim_user / dim_product（合并相关维度表）+ fact_orders / fact_behaviors
-- 依赖：02_cleaning.sql 已执行（product_features 列名已规范化）
-- ============================================================

-- ---------- 3.1 用户维度表：users + user_features ----------
DROP TABLE IF EXISTS dim_user;
CREATE TABLE dim_user AS
SELECT u.user_id, u.age, u.gender, u.province, u.city,
       u.registration_date, u.member_level, u.account_balance, u.credit_score,
       uf.total_spent, uf.order_count, uf.completed_orders, uf.avg_order_amount,
       uf.browse_count, uf.click_count, uf.favorite_count, uf.cart_count,
       uf.consumption_level, uf.member_level_score
FROM users u
LEFT JOIN user_features uf ON u.user_id = uf.user_id;

SELECT COUNT(*) AS dim_user_cnt FROM dim_user;

-- ---------- 3.2 商品维度表：products + product_features ----------
DROP TABLE IF EXISTS dim_product;
CREATE TABLE dim_product AS
SELECT p.product_id, p.product_name, p.category, p.brand, p.price, p.sales_count,
       pf.total_revenue, pf.total_sales, pf.completed_count, pf.cancel_count,
       pf.add_to_cart_count, pf.favorite_count, pf.view_count, pf.click_count,
       pf.conversion_rate, pf.avg_review_score, pf.popularity_score
FROM products p
LEFT JOIN product_features pf ON p.product_id = pf.product_id;

SELECT COUNT(*) AS dim_product_cnt FROM dim_product;

-- ---------- 3.3 订单事实表 ----------
DROP TABLE IF EXISTS fact_orders;
CREATE TABLE fact_orders AS SELECT * FROM orders;

SELECT COUNT(*) AS fact_orders_cnt FROM fact_orders;

-- ---------- 3.4 行为事实表 ----------
DROP TABLE IF EXISTS fact_behaviors;
CREATE TABLE fact_behaviors AS SELECT * FROM user_behaviors;

SELECT COUNT(*) AS fact_behaviors_cnt FROM fact_behaviors;

-- ---------- 3.5 星型模型总览 ----------
-- 模型结构：
--   fact_orders    (user_id, product_id) → dim_user, dim_product
--   fact_behaviors (user_id, product_id) → dim_user, dim_product
-- 设计价值：PowerBI 中切片器沿关系自动下推；度量值 SUM(actual_payment) 可跨图复用；
--          低基数文本列（品类、会员等级）压缩率高，内存占用低于宽表
SELECT 'dim_user' AS 表, COUNT(*) AS 行数 FROM dim_user
UNION ALL SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL SELECT 'fact_orders', COUNT(*) FROM fact_orders
UNION ALL SELECT 'fact_behaviors', COUNT(*) FROM fact_behaviors;
