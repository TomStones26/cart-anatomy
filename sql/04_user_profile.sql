-- ============================================================
-- 04_user_profile.sql  用户画像分析
-- 4.1 年龄分布  4.2 性别  4.3 会员等级  4.4 地域TOP10  4.5 消费能力
-- 依赖：03_dimension_model.sql
-- ============================================================

-- ---------- 4.1 年龄分层 ----------
SELECT CASE WHEN age < 20 THEN '20岁以下'
            WHEN age BETWEEN 20 AND 29 THEN '20-29岁'
            WHEN age BETWEEN 30 AND 39 THEN '30-39岁'
            WHEN age BETWEEN 40 AND 49 THEN '40-49岁'
            ELSE '50岁及以上' END AS age_group,
       COUNT(*) AS cnt,
       ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 2) AS pct
FROM dim_user
GROUP BY age_group
ORDER BY MIN(age);

-- ---------- 4.2 性别分布 ----------
SELECT gender,
       COUNT(*) AS cnt,
       ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 2) AS pct,
       ROUND(AVG(total_spent), 2) AS avg_spent
FROM dim_user
GROUP BY gender;

-- ---------- 4.3 会员等级 ----------
SELECT member_level AS lvl,
       COUNT(DISTINCT user_id) AS cnt,
       ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM dim_user), 2) AS pct,
       ROUND(AVG(total_spent), 2) AS avg_spent
FROM dim_user
GROUP BY member_level
ORDER BY FIELD(member_level, '普通会员','铜牌会员','银牌会员','金牌会员','钻石会员');

-- ---------- 4.4 地域 TOP10（按用户数） ----------
SELECT province,
       COUNT(*) AS cnt,
       ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM dim_user), 1) AS pct
FROM dim_user
GROUP BY province
ORDER BY cnt DESC
LIMIT 10;

-- ---------- 4.5 消费能力 ----------
SELECT consumption_level,
       COUNT(*) AS cnt,
       ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM dim_user), 1) AS pct,
       ROUND(AVG(total_spent), 2) AS avg_spent
FROM dim_user
GROUP BY consumption_level
ORDER BY FIELD(consumption_level, '低','中','高');
