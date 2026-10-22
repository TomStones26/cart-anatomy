# -*- coding: utf-8 -*-
"""Q1 数据探索与质量检查。

对应 sql/01_data_quality.sql：
  1.1 数据总览 → 1.2 缺失值 → 1.3 异常值 → 1.4 重复值 → 1.5 外键一致性
"""
import pandas as pd


def run(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    o, u, p = data["orders"], data["users"], data["products"]
    b, uf, pf = data["user_behaviors"], data["user_features"], data["product_features"]

    # ---- 1.1 数据总览 ----
    overview = pd.DataFrame(
        [{"表名": n, "记录数": len(df)} for n, df in
         [("orders", o), ("product_features", pf), ("products", p),
          ("user_behaviors", b), ("user_features", uf), ("users", u)]]
    )

    # ---- 1.2 缺失值：orders 全字段 ----
    missing_orders = pd.DataFrame([{
        f"missing_{c}": int(o[c].isna().sum()) for c in o.columns
    }])

    # ---- 1.2 缺失值：其余表关键字段（列名与原文档 SQL 输出一致） ----
    missing_others = pd.DataFrame([
        {"表名": "products", "总数": len(p),
         "name_null": int(p["product_name"].isna().sum()),
         "category_null": int(p["category"].isna().sum()),
         "brand_null": int(p["brand"].isna().sum())},
        {"表名": "users", "总数": len(u),
         "age_null": int(u["age"].isna().sum()),
         "gender_null": int(u["gender"].isna().sum()),
         "province_null": int(u["province"].isna().sum())},
        {"表名": "user_features", "总数": len(uf),
         "total_spent_null": int(uf["total_spent"].isna().sum()),
         "order_count_null": int(uf["order_count"].isna().sum()),
         "consumption_level_null": int(uf["consumption_level"].isna().sum())},
        {"表名": "product_features", "总数": len(pf),
         "total_revenue_null": int(pf["total_revenue"].isna().sum()),
         "conversion_rate_null": int(pf["conversion_rate"].isna().sum()),
         "avg_review_score_null": int(pf["avg_review_score"].isna().sum())},
        {"表名": "user_behaviors", "总数": len(b),
         "user_id_null": int(b["user_id"].isna().sum()),
         "behavior_type_null": int(b["behavior_type"].isna().sum()),
         "behavior_time_null": int(b["behavior_time"].isna().sum())},
    ])

    # ---- 1.3 异常值：数值字段 min/max ----
    outliers = pd.DataFrame([
        {"表": "orders", "字段": "quantity", "min": o["quantity"].min(), "max": o["quantity"].max()},
        {"表": "orders", "字段": "unit_price", "min": o["unit_price"].min(), "max": o["unit_price"].max()},
        {"表": "orders", "字段": "actual_payment", "min": o["actual_payment"].min(), "max": o["actual_payment"].max()},
        {"表": "users", "字段": "age", "min": u["age"].min(), "max": u["age"].max()},
        {"表": "users", "字段": "account_balance", "min": u["account_balance"].min(), "max": u["account_balance"].max()},
        {"表": "products", "字段": "price", "min": p["price"].min(), "max": p["price"].max()},
        {"表": "products", "字段": "sales_count", "min": p["sales_count"].min(), "max": p["sales_count"].max()},
        {"表": "user_behaviors", "字段": "duration_seconds", "min": b["duration_seconds"].min(), "max": b["duration_seconds"].max()},
    ])

    # ---- 1.4 重复值：主键唯一性 ----
    duplicates = pd.DataFrame([
        {"表名": "orders", "主键": "order_id", "总数": len(o), "唯一数": o["order_id"].nunique()},
        {"表名": "products", "主键": "product_id", "总数": len(p), "唯一数": p["product_id"].nunique()},
        {"表名": "product_features", "主键": "product_id", "总数": len(pf), "唯一数": pf["product_id"].nunique()},
        {"表名": "users", "主键": "user_id", "总数": len(u), "唯一数": u["user_id"].nunique()},
        {"表名": "user_features", "主键": "user_id", "总数": len(uf), "唯一数": uf["user_id"].nunique()},
        {"表名": "user_behaviors", "主键": "behavior_id", "总数": len(b), "唯一数": b["behavior_id"].nunique()},
    ])
    duplicates["重复数"] = duplicates["总数"] - duplicates["唯一数"]

    # ---- 1.5 外键一致性 ----
    fk = pd.DataFrame([{
        "orders_用户数": o["user_id"].nunique(),
        "users_总数": len(u),
        "user_id匹配数": int(o["user_id"].isin(u["user_id"]).sum()),
        "user_id匹配率": round(o["user_id"].isin(u["user_id"]).mean(), 4),
        "product_id匹配数": int(o["product_id"].isin(p["product_id"]).sum()),
        "product_id匹配率": round(o["product_id"].isin(p["product_id"]).mean(), 4),
    }])

    return {
        "01_overview": overview,
        "01_missing_orders": missing_orders,
        "01_missing_others": missing_others,
        "01_outliers": outliers,
        "01_duplicates": duplicates,
        "01_foreign_keys": fk,
    }
