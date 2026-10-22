# -*- coding: utf-8 -*-
"""全局配置：路径、口径常量。

口径常量与 sql/ 目录下的 MySQL 脚本逐条对应，改这里即可同步两边口径。
"""
from pathlib import Path

# 项目根目录（src/ 的上一级）
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

# 6 张原始表文件名
TABLE_FILES = {
    "orders": "orders.csv",
    "products": "products.csv",
    "product_features": "product_features.csv",
    "user_behaviors": "user_behaviors.csv",
    "user_features": "user_features.csv",
    "users": "users.csv",
}

# product_features 中文字段名 → 英文（对应 02_cleaning.sql 的 ALTER 规范化）
CN_TO_EN_COLUMNS = {
    "加购_count": "add_to_cart_count",
    "收藏_count": "favorite_count",
    "浏览_count": "view_count",
    "点击_count": "click_count",
}

# 订单状态全集（实测 7 种）
ALL_ORDER_STATUS = ["待付款", "已付款", "已发货", "已收货", "已完成", "已取消", "已退款"]

# RFM 有效订单口径（05_rfm.sql）：已付款/已发货/已收货/已完成 且 delivery_date 非空
RFM_VALID_STATUS = ("已付款", "已发货", "已收货", "已完成")

# 漏斗下单口径（07_behavior_funnel.sql，按原文档保留）：已付款/已发货/已完成
FUNNEL_ORDER_STATUS = ("已付款", "已发货", "已完成")

# 行为类型全集（实测 4 种）
BEHAVIOR_TYPES = ["浏览", "点击", "收藏", "加购"]

# 转化率小样本过滤阈值（06_product_analysis.sql）
MIN_VIEW_FOR_CV = 10
