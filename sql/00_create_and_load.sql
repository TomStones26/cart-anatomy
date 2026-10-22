-- ============================================================
-- 00_create_and_load.sql
-- 淘宝用户消费数据分析 - 建库 / 建表 / 导入数据
-- 适用：MySQL 8.0+（用到了窗口函数 PERCENT_RANK）
-- 说明：CSV 带 UTF-8 BOM，已用 IGNORE 1 ROWS 跳过表头；
--       所有可空列均通过 NULLIF(@col,'') 映射，保证空字段导入为 NULL 而非 0/空串
-- ============================================================

CREATE DATABASE IF NOT EXISTS taobao_sales DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE taobao_sales;

DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS product_features;
DROP TABLE IF EXISTS user_behaviors;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS user_features;

CREATE TABLE users (
    user_id           VARCHAR(10)  NOT NULL PRIMARY KEY,
    age               INT,
    gender            VARCHAR(2),
    province          VARCHAR(20),
    city              VARCHAR(20),
    registration_date DATETIME(6),
    member_level      VARCHAR(10),
    account_balance   DECIMAL(12,2),
    credit_score      INT
) ENGINE=InnoDB;

CREATE TABLE products (
    product_id   VARCHAR(10)  NOT NULL PRIMARY KEY,
    product_name VARCHAR(100),
    category     VARCHAR(20),
    brand        VARCHAR(50),
    price        DECIMAL(10,2),
    sales_count  INT
) ENGINE=InnoDB;

-- 15 字段订单事实表（与原始 CSV 一一对应）
CREATE TABLE orders (
    order_id       VARCHAR(10)  NOT NULL PRIMARY KEY,
    user_id        VARCHAR(10),
    product_id     VARCHAR(10),
    quantity       INT,
    order_date     DATETIME(6),
    order_status   VARCHAR(10),
    payment_method VARCHAR(10),
    unit_price     DECIMAL(10,2),
    total_amount   DECIMAL(12,2),
    discount       DECIMAL(10,2),
    actual_payment DECIMAL(12,2),
    delivery_date  DATETIME(6)  NULL,
    receive_date   DATETIME(6)  NULL,
    review_score   DECIMAL(2,1) NULL,
    review_content TEXT         NULL
) ENGINE=InnoDB;

CREATE TABLE user_behaviors (
    behavior_id      VARCHAR(10) NOT NULL PRIMARY KEY,
    user_id          VARCHAR(10),
    product_id       VARCHAR(10),
    behavior_type    VARCHAR(10),
    behavior_time    DATETIME(6),
    duration_seconds INT
) ENGINE=InnoDB;

CREATE TABLE user_features (
    user_id              VARCHAR(10)  NOT NULL PRIMARY KEY,
    total_spent          DECIMAL(16,2),   -- CSV 含 14 位浮点尾巴，按分存储（Note 1265 属预期）
    order_count          INT,
    completed_orders     INT,
    avg_order_amount     DECIMAL(16,4),   -- 如 1755.1533333333334，保留 4 位
    browse_count         INT,
    click_count          INT,
    favorite_count       INT,
    cart_count           INT,
    days_since_last_order INT,
    order_frequency      INT,
    repurchase_indicator INT,
    purchase_intent      DECIMAL(6,4),
    consumption_level    VARCHAR(2),
    member_level_score   INT
) ENGINE=InnoDB;

-- product_features 保留中文字段名（第 02 节再做规范化，复现原项目流程）
-- 精度说明：avg_review_score 在 CSV 中有 2 位小数（如 4.25），故用 DECIMAL(3,2)；
--          金额列按「分」存储（2 位），CSV 中 total_revenue/total_spent 的
--          14 位小数是浮点尾巴，导入时触发 Note 1265（截断提示，非错误），属预期。
CREATE TABLE product_features (
    product_id       VARCHAR(10)  NOT NULL PRIMARY KEY,
    total_revenue    DECIMAL(16,2),
    total_sales      INT,
    completed_count  INT,
    cancel_count     INT,
    `加购_count`      INT,
    `收藏_count`      INT,
    `浏览_count`      INT,
    `点击_count`      INT,
    conversion_rate  DECIMAL(6,4),
    avg_review_score DECIMAL(3,2),
    popularity_score DECIMAL(4,2)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 导入数据
-- 前提：SHOW VARIABLES LIKE 'local_infile' = ON
--       客户端需允许 LOCAL INFILE（如 mysql --local-infile=1）
-- 路径按本项目 data/ 目录填写，迁移项目时改成实际路径
-- 重要：本数据集 CSV 为 Windows 换行（CRLF），必须用 '\r\n' 分行，
--       否则行尾 \r 会粘在最后一列上（如 credit_score = '611\r'），
--       严格模式下 INT 列直接报 Incorrect integer value。
--       若换成 LF 换行的 CSV，需把下面的 '\r\n' 全部改回 '\n'。
-- ------------------------------------------------------------

LOAD DATA LOCAL INFILE 'C:/Users/ynwas/WorkBuddy/2026-10-19-15-49-03/taobao_sales_analysis/data/users.csv'
INTO TABLE users CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(user_id, age, gender, province, city, registration_date, member_level, account_balance, credit_score);

LOAD DATA LOCAL INFILE 'C:/Users/ynwas/WorkBuddy/2026-10-19-15-49-03/taobao_sales_analysis/data/products.csv'
INTO TABLE products CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(product_id, product_name, category, brand, price, sales_count);

LOAD DATA LOCAL INFILE 'C:/Users/ynwas/WorkBuddy/2026-10-19-15-49-03/taobao_sales_analysis/data/orders.csv'
INTO TABLE orders CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(order_id, user_id, product_id, quantity, order_date, order_status, payment_method,
 unit_price, total_amount, discount, actual_payment,
 @delivery_date, @receive_date, @review_score, @review_content)
SET delivery_date  = NULLIF(@delivery_date, ''),
    receive_date   = NULLIF(@receive_date, ''),
    review_score   = NULLIF(@review_score, ''),
    review_content = NULLIF(@review_content, '');

LOAD DATA LOCAL INFILE 'C:/Users/ynwas/WorkBuddy/2026-10-19-15-49-03/taobao_sales_analysis/data/user_behaviors.csv'
INTO TABLE user_behaviors CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(behavior_id, user_id, product_id, behavior_type, behavior_time, duration_seconds);

LOAD DATA LOCAL INFILE 'C:/Users/ynwas/WorkBuddy/2026-10-19-15-49-03/taobao_sales_analysis/data/user_features.csv'
INTO TABLE user_features CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(user_id, total_spent, order_count, completed_orders, avg_order_amount,
 browse_count, click_count, favorite_count, cart_count,
 days_since_last_order, order_frequency, repurchase_indicator,
 purchase_intent, consumption_level, member_level_score);

LOAD DATA LOCAL INFILE 'C:/Users/ynwas/WorkBuddy/2026-10-19-15-49-03/taobao_sales_analysis/data/product_features.csv'
INTO TABLE product_features CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(product_id, total_revenue, total_sales, completed_count, cancel_count,
 `加购_count`, `收藏_count`, `浏览_count`, `点击_count`,
 conversion_rate, avg_review_score, popularity_score);

-- 导入后校验：6 张表行数应为 15000/2000/2000/30000/5000/5000
SELECT 'orders' AS 表名, COUNT(*) AS 记录数 FROM orders
UNION ALL SELECT 'product_features', COUNT(*) FROM product_features
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'user_behaviors', COUNT(*) FROM user_behaviors
UNION ALL SELECT 'user_features', COUNT(*) FROM user_features
UNION ALL SELECT 'users', COUNT(*) FROM users;
