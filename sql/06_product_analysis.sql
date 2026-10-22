-- ============================================================
-- 06_product_analysis.sql  商品分析
-- 6.1 品类  6.2 品牌TOP10  6.3 价格区间  6.4 转化率（含小样本过滤）
-- 依赖：03_dimension_model.sql（product_features 列名已规范化为英文）
-- ============================================================

-- ---------- 6.1 品类分析 ----------
SELECT p.category,
       COUNT(DISTINCT p.product_id)          AS prod_cnt,
       ROUND(SUM(o.actual_payment), 2)       AS revenue,
       ROUND(AVG(o.actual_payment), 2)       AS avg_order,
       ROUND(AVG(pf.conversion_rate), 4)     AS avg_cv
FROM dim_product p
LEFT JOIN fact_orders o
       ON p.product_id = o.product_id AND o.order_status NOT IN ('已取消')
LEFT JOIN product_features pf
       ON p.product_id = pf.product_id
GROUP BY p.category
ORDER BY revenue DESC;

-- ---------- 6.2 品牌 TOP10 ----------
SELECT p.brand,
       COUNT(DISTINCT p.product_id)    AS prod_cnt,
       COUNT(DISTINCT o.order_id)      AS order_cnt,
       ROUND(SUM(o.actual_payment), 2) AS revenue,
       ROUND(AVG(o.actual_payment), 2) AS avg_order
FROM dim_product p
LEFT JOIN fact_orders o
       ON p.product_id = o.product_id AND o.order_status NOT IN ('已取消')
GROUP BY p.brand
ORDER BY revenue DESC
LIMIT 10;

-- ---------- 6.3 价格区间分布 ----------
SELECT CASE WHEN price < 100 THEN '低价(<100)'
            WHEN price BETWEEN 100 AND 500 THEN '中价(100-500)'
            WHEN price BETWEEN 500 AND 1000 THEN '中高价(500-1000)'
            WHEN price BETWEEN 1000 AND 3000 THEN '高价(1000-3000)'
            ELSE '超高价(3000+)' END AS price_range,
       COUNT(*) AS cnt,
       ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 2) AS pct
FROM dim_product
GROUP BY price_range
ORDER BY MIN(price);

-- ---------- 6.4 转化率优化 ----------
-- 6.4.1 转化率整体分布（注意：实测 79% 商品浏览量 <10，小样本会虚高转化率）
SELECT CASE WHEN conversion_rate = 1 THEN '100%'
            WHEN conversion_rate >= 0.5 THEN '50%-100%'
            WHEN conversion_rate >= 0.1 THEN '10%-50%'
            WHEN conversion_rate > 0 THEN '0%-10%'
            ELSE '无数据' END AS rate_range,
       COUNT(*) AS product_count,
       ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM dim_product), 2) AS percentage
FROM dim_product
GROUP BY rate_range
ORDER BY product_count DESC;

-- 6.4.2 分品类转化率：平均转化率 vs 有效转化率（过滤浏览量<10 的小样本）
-- 注：原文档此处仍写中文字段名 `浏览_count`，本文件按 2.4 规范化后的英文名列名编写
SELECT category,
       COUNT(*)                                                        AS 商品数,
       SUM(view_count)                                                 AS 总浏览量,
       SUM(total_sales)                                                AS 总销量,
       ROUND(AVG(conversion_rate), 4)                                  AS 平均转化率,
       ROUND(SUM(CASE WHEN view_count >= 10 THEN total_sales ELSE 0 END) * 1.0 /
             SUM(CASE WHEN view_count >= 10 THEN view_count ELSE 0 END), 4) AS 有效转化率
FROM dim_product
GROUP BY category
ORDER BY 有效转化率 DESC;
