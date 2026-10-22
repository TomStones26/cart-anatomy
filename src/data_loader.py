# -*- coding: utf-8 -*-
"""数据加载：读 6 张 CSV，统一日期类型。

对应 sql/00_create_and_load.sql。
注意：本模块**不做**字段名规范化——原文档在「第 2 章数据清洗」才把
product_features 的中文字段名改成英文（见 q2_cleaning.run），此处保留原始列名。
"""
import pandas as pd

from config import DATA_DIR, TABLE_FILES

DATE_COLUMNS = {
    "orders": ["order_date", "delivery_date", "receive_date"],
    "user_behaviors": ["behavior_time"],
    "users": ["registration_date"],
}


def load_all() -> dict[str, pd.DataFrame]:
    """读取全部原始表，返回 {表名: DataFrame}（列名保持原始状态）。"""
    data = {}
    for name, fname in TABLE_FILES.items():
        df = pd.read_csv(DATA_DIR / fname, encoding="utf-8-sig")
        for col in DATE_COLUMNS.get(name, []):
            df[col] = pd.to_datetime(df[col], errors="coerce")
        data[name] = df
    return data
