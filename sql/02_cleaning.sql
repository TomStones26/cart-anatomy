-- ============================================================
-- 02_cleaning.sql  数据清洗与规范化
-- 2.1 缺失值（按订单状态确认业务含义后处理）
-- 2.2 异常值检测   2.3 类型检查   2.4 字段名规范化
-- ============================================================

-- ---------- 2.1 先确认缺失的业务含义：空值是否与订单状态对应 ----------
-- 实测口径：本数据集订单状态共 7 种
-- 待付款/已取消/已退款：未发货未收货未评价（全空属正常）
-- 已付款：已下单未发货（delivery/receive 空）
-- 已发货：已发货未签收（receive 空）
-- 已收货/已完成：物流齐全；未评价属正常业务缺失
SELECT order_status,
       COUNT(*)                                                        AS 订单数,
       SUM(CASE WHEN delivery_date IS NULL THEN 1 ELSE 0 END)          AS 无发货日期,
       SUM(CASE WHEN receive_date IS NULL THEN 1 ELSE 0 END)           AS 无收货日期,
       SUM(CASE WHEN review_score IS NULL THEN 1 ELSE 0 END)           AS 无评分,
       SUM(CASE WHEN review_content IS NULL THEN 1 ELSE 0 END)         AS 无评价内容
FROM orders
GROUP BY order_status
ORDER BY FIELD(order_status, '待付款','已付款','已发货','已收货','已完成','已取消','已退款');

-- ---------- 2.1 执行清洗：未评价标记 ----------
-- 口径说明：review_score 填 0 = 「未评价」（非 0 分）；review_content 填「未评价」
UPDATE orders SET review_score = 0 WHERE review_score IS NULL;
UPDATE orders SET review_content = '未评价' WHERE review_content IS NULL;

-- 验证
SELECT COUNT(*) AS 总订单数,
       SUM(CASE WHEN review_score = 0 THEN 1 ELSE 0 END)    AS 未评分订单数,
       SUM(CASE WHEN review_content = '未评价' THEN 1 ELSE 0 END) AS 无评价内容数
FROM orders;

-- ---------- 2.2 异常值：非正的价格/数量/金额 ----------
-- 实测结果：0 条（本数据集数值字段干净，此查询作为例行检查保留）
SELECT order_id, product_id, quantity, unit_price, total_amount
FROM orders
WHERE quantity <= 0 OR unit_price <= 0 OR total_amount <= 0;

-- ---------- 2.3 数据类型检查 ----------
DESCRIBE orders;
DESCRIBE products;
DESCRIBE users;

-- ---------- 2.4 字段名规范化：中文字段名改英文 ----------
-- 注意：原文档此处写成 CHANGE add_to_cart_count `加购_count`，方向反了
--       （CHANGE 是「旧名 新名」），照抄会报 Unknown column 'add_to_cart_count'。
--       原文档正文意图是「中文 → 英文」，且 3.2 节 dim_product 已按英文名引用，
--       故此处按正确方向编写。
ALTER TABLE product_features
    CHANGE `加购_count` add_to_cart_count INT,
    CHANGE `收藏_count` favorite_count   INT,
    CHANGE `浏览_count` view_count       INT,
    CHANGE `点击_count` click_count      INT;

DESCRIBE product_features;
