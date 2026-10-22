# -*- coding: utf-8 -*-
"""Q7 行为漏斗分析。

对应 sql/07_behavior_funnel.sql：
  7.1 行为类型分布  7.2 关键转化率  7.3 品类浏览→加购转化率
"""
import pandas as pd

from config import BEHAVIOR_TYPES, FUNNEL_ORDER_STATUS


def run(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    fb, fo, dp = data["fact_behaviors"], data["fact_orders"], data["dim_product"]
    total_b = len(fb)

    # ---- 7.1 行为类型分布 ----
    behavior_stats = (fb.groupby("behavior_type")
                        .agg(times=("behavior_id", "size"), users=("user_id", "nunique"))
                        .reindex([t for t in BEHAVIOR_TYPES if t in set(fb["behavior_type"])])
                        .reset_index())
    behavior_stats["pct"] = (behavior_stats["times"] * 100 / total_b).round(1)

    # ---- 7.2 关键转化率：浏览→点击→收藏→加购→下单（按去重用户数） ----
    total_u = fb["user_id"].nunique()
    clkd = fb.loc[fb["behavior_type"] == "点击", "user_id"].nunique()
    fav = fb.loc[fb["behavior_type"] == "收藏", "user_id"].nunique()
    cart = fb.loc[fb["behavior_type"] == "加购", "user_id"].nunique()
    ordered = fo.loc[fo["order_status"].isin(FUNNEL_ORDER_STATUS), "user_id"].nunique()

    funnel = pd.DataFrame([
        {"环节": "浏览", "用户数": total_u, "环节转化率%": 100.0},
        {"环节": "点击", "用户数": clkd, "环节转化率%": round(clkd * 100 / total_u, 2)},
        {"环节": "收藏", "用户数": fav, "环节转化率%": round(fav * 100 / total_u, 2)},
        {"环节": "加购", "用户数": cart, "环节转化率%": round(cart * 100 / total_u, 2)},
        {"环节": "下单", "用户数": ordered, "环节转化率%": round(ordered * 100 / total_u, 2)},
    ])

    # ---- 7.3 品类：浏览用户 → 加购用户 ----
    m = fb.merge(dp[["product_id", "category"]], on="product_id", how="inner")
    cat_funnel = (m.pivot_table(index="category", columns="behavior_type",
                                values="user_id", aggfunc="nunique")
                    .fillna(0)
                    .astype(int)
                    .reset_index())
    for col in ["浏览", "加购"]:
        if col not in cat_funnel.columns:
            cat_funnel[col] = 0
    cat_funnel["cart_rate"] = (cat_funnel["加购"] * 100.0 /
                               cat_funnel["浏览"].replace(0, pd.NA)).round(2)
    cat_funnel = cat_funnel[["category", "浏览", "加购", "cart_rate"]]
    cat_funnel.columns = ["category", "browse_users", "cart_users", "cart_rate"]
    cat_funnel = cat_funnel.sort_values("cart_rate", ascending=False).reset_index(drop=True)

    return {
        "07_behavior_stats": behavior_stats,
        "07_funnel_key_rates": funnel,
        "07_category_cart_rate": cat_funnel,
    }
