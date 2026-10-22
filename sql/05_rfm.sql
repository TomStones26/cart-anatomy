-- ============================================================
-- 05_rfm.sql  RFM 用户分层
-- 5.1 R/F/M 计算  5.2 评分（PERCENT_RANK 分档）  5.3 八层用户分层
-- 依赖：03_dimension_model.sql
-- 口径：R 用 delivery_date（发货时间为真实业务时间）；
--       有效订单 = 已付款/已发货/已收货/已完成 且 delivery_date 非空
-- ============================================================

-- ---------- 5.1 RFM 原始指标 ----------
DROP TABLE IF EXISTS rfm_raw;
CREATE TABLE rfm_raw AS
SELECT user_id,
       DATEDIFF(CURRENT_DATE(), MAX(delivery_date)) AS recency,
       COUNT(DISTINCT order_id)                     AS frequency,
       ROUND(SUM(actual_payment), 2)                AS monetary
FROM fact_orders
WHERE order_status IN ('已付款','已发货','已收货','已完成')
  AND delivery_date IS NOT NULL
GROUP BY user_id;

SELECT COUNT(*) AS rfm_user_cnt FROM rfm_raw;
SELECT * FROM rfm_raw ORDER BY monetary DESC LIMIT 10;

-- ---------- 5.2 R/F/M 评分 ----------
-- 文档标题写 NTILE(5)，实现用的是 PERCENT_RANK 分档，此处与文档实现保持一致
-- recency 越小越好 → r_pct 低分位给 5 分；frequency / monetary 越大越好 → 高分位给 5 分
DROP TABLE IF EXISTS rfm_score;
CREATE TABLE rfm_score AS
WITH rfm_pct AS (
    SELECT user_id, recency, frequency, monetary,
           PERCENT_RANK() OVER (ORDER BY recency)   AS r_pct,
           PERCENT_RANK() OVER (ORDER BY frequency) AS f_pct,
           PERCENT_RANK() OVER (ORDER BY monetary)  AS m_pct
    FROM rfm_raw
)
SELECT user_id, recency, frequency, monetary,
       CASE WHEN r_pct <= 0.2 THEN 5
            WHEN r_pct <= 0.4 THEN 4
            WHEN r_pct <= 0.6 THEN 3
            WHEN r_pct <= 0.8 THEN 2
            ELSE 1 END AS r_score,
       CASE WHEN f_pct >= 0.8 THEN 5
            WHEN f_pct >= 0.6 THEN 4
            WHEN f_pct >= 0.4 THEN 3
            WHEN f_pct >= 0.2 THEN 2
            ELSE 1 END AS f_score,
       CASE WHEN m_pct >= 0.8 THEN 5
            WHEN m_pct >= 0.6 THEN 4
            WHEN m_pct >= 0.4 THEN 3
            WHEN m_pct >= 0.2 THEN 2
            ELSE 1 END AS m_score
FROM rfm_pct;

-- ---------- 5.3 用户分层（8 类） ----------
DROP TABLE IF EXISTS rfm_segments;
CREATE TABLE rfm_segments AS
SELECT user_id, r_score, f_score, m_score,
       CASE WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN '重要价值用户'
            WHEN r_score >= 4 AND f_score >= 4 AND m_score < 4 THEN '重要发展用户'
            WHEN r_score >= 4 AND f_score < 4 AND m_score >= 4 THEN '重要保持用户'
            WHEN r_score >= 4 AND f_score < 4 AND m_score < 4 THEN '新用户'
            WHEN r_score < 4 AND f_score >= 4 AND m_score >= 4 THEN '重要挽留用户'
            WHEN r_score < 4 AND f_score >= 4 AND m_score < 4 THEN '一般维持用户'
            WHEN r_score < 4 AND f_score < 4 AND m_score >= 4 THEN '一般价值用户'
            ELSE '流失用户' END AS user_segment
FROM rfm_score;

SELECT r.user_segment,
       COUNT(*) AS cnt,
       ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 2) AS pct,
       ROUND(AVG(m.monetary), 2) AS avg_spent
FROM rfm_segments r
JOIN rfm_raw m USING (user_id)
GROUP BY r.user_segment
ORDER BY cnt DESC;
