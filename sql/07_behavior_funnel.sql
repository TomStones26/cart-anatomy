-- ============================================================
-- 07_behavior_funnel.sql  行为漏斗分析
-- 7.1 行为类型分布  7.2 关键转化率  7.3 品类加购率对比
-- 依赖：03_dimension_model.sql
-- ============================================================

-- ---------- 7.1 行为路径概览 ----------
-- 实测：behavior_type 仅 4 种（浏览/点击/收藏/加购），「购买」不在行为表中，下单用户来自 fact_orders
SELECT behavior_type,
       COUNT(*)               AS times,
       COUNT(DISTINCT user_id) AS users,
       ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM fact_behaviors), 1) AS pct
FROM fact_behaviors
GROUP BY behavior_type
ORDER BY FIELD(behavior_type, '浏览','点击','收藏','加购');

-- ---------- 7.2 关键转化率：浏览→点击→收藏→加购→下单 ----------
-- 口径说明：下单用户取 order_status IN ('已付款','已发货','已完成')
--           （与 05_rfm 的四状态口径不同——此处按原文档口径保留）
WITH bf AS (
    SELECT COUNT(DISTINCT user_id) AS total,
           COUNT(DISTINCT CASE WHEN behavior_type = '点击' THEN user_id END) AS clkd,
           COUNT(DISTINCT CASE WHEN behavior_type = '收藏' THEN user_id END) AS fav,
           COUNT(DISTINCT CASE WHEN behavior_type = '加购' THEN user_id END) AS cart
    FROM fact_behaviors
),
ord AS (
    SELECT COUNT(DISTINCT user_id) AS ordered
    FROM fact_orders
    WHERE order_status IN ('已付款','已发货','已完成')
)
SELECT total AS 浏览, clkd AS 点击,
       ROUND(clkd * 100 / total, 2) AS 点击率,
       fav AS 收藏, ROUND(fav * 100 / total, 2) AS 收藏率,
       cart AS 加购, ROUND(cart * 100 / total, 2) AS 加购率,
       ordered AS 下单, ROUND(ordered * 100 / total, 2) AS 下单率
FROM bf, ord;

-- ---------- 7.3 品类转化率对比：浏览用户 → 加购用户 ----------
SELECT p.category,
       COUNT(DISTINCT CASE WHEN b.behavior_type = '浏览' THEN b.user_id END) AS browse_users,
       COUNT(DISTINCT CASE WHEN b.behavior_type = '加购' THEN b.user_id END) AS cart_users,
       ROUND(
           COUNT(DISTINCT CASE WHEN b.behavior_type = '加购' THEN b.user_id END) * 100.0 /
           NULLIF(COUNT(DISTINCT CASE WHEN b.behavior_type = '浏览' THEN b.user_id END), 0),
       2) AS cart_rate
FROM fact_behaviors b
JOIN dim_product p ON b.product_id = p.product_id
GROUP BY p.category
ORDER BY cart_rate DESC;
