# -*- coding: utf-8 -*-
"""Q3 星型模型构建。

对应 sql/03_dimension_model.sql：
  dim_user = users LEFT JOIN user_features
  dim_product = products LEFT JOIN product_features
  fact_orders / fact_behaviors 直接取事实表
"""
import pandas as pd


def run(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    u, uf = data["users"], data["user_features"]
    p, pf = data["products"], data["product_features"]
    o, b = data["orders"], data["user_behaviors"]

    # ---- 3.1 用户维度表 ----
    # 字段严格按原文档 3.1 的 SELECT 清单（19 列），
    # 不取 user_features 的 days_since_last_order / order_frequency /
    # repurchase_indicator / purchase_intent（原文档未纳入 dim_user）
    dim_user_cols = [
        "user_id", "age", "gender", "province", "city",
        "registration_date", "member_level", "account_balance", "credit_score",
        "total_spent", "order_count", "completed_orders", "avg_order_amount",
        "browse_count", "click_count", "favorite_count", "cart_count",
        "consumption_level", "member_level_score",
    ]
    dim_user = u.merge(uf, on="user_id", how="left")[dim_user_cols]

    # ---- 3.2 商品维度表 ----
    dim_product_cols = [
        "product_id", "product_name", "category", "brand", "price", "sales_count",
        "total_revenue", "total_sales", "completed_count", "cancel_count",
        "add_to_cart_count", "favorite_count", "view_count", "click_count",
        "conversion_rate", "avg_review_score", "popularity_score",
    ]
    dim_product = p.merge(pf, on="product_id", how="left")[dim_product_cols]

    # ---- 3.3 / 3.4 事实表 ----
    fact_orders = o.copy()
    fact_behaviors = b.copy()

    data["dim_user"] = dim_user
    data["dim_product"] = dim_product
    data["fact_orders"] = fact_orders
    data["fact_behaviors"] = fact_behaviors

    # ---- 3.5 星型模型总览 ----
    model_overview = pd.DataFrame([
        {"表": "dim_user", "行数": len(dim_user), "角色": "维度表（用户属性 + 消费特征）"},
        {"表": "dim_product", "行数": len(dim_product), "角色": "维度表（商品属性 + 经营特征）"},
        {"表": "fact_orders", "行数": len(fact_orders), "角色": "事实表（订单）"},
        {"表": "fact_behaviors", "行数": len(fact_behaviors), "角色": "事实表（用户行为）"},
    ])

    return {"03_model_overview": model_overview}
