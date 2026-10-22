# -*- coding: utf-8 -*-
"""Q6 商品分析。

对应 sql/06_product_analysis.sql：
  6.1 品类  6.2 品牌TOP10  6.3 价格区间  6.4 转化率分布与分品类有效转化率
口径：销售口径排除「已取消」订单（与原文档一致，「已退款」未排除）
"""
import pandas as pd

from config import MIN_VIEW_FOR_CV


def run(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    dp, fo = data["dim_product"], data["fact_orders"]

    valid = fo[fo["order_status"] != "已取消"]

    # ---- 6.1 品类分析 ----
    cat = (dp.merge(valid[["product_id", "actual_payment"]], on="product_id", how="left")
             .groupby("category")
             .agg(prod_cnt=("product_id", "nunique"),
                  revenue=("actual_payment", "sum"),
                  avg_order=("actual_payment", "mean"),
                  avg_cv=("conversion_rate", "mean"))
             .reset_index()
             .sort_values("revenue", ascending=False))
    for c in ["revenue", "avg_order", "avg_cv"]:
        cat[c] = cat[c].round(2 if c != "avg_cv" else 4)
    cat = cat.reset_index(drop=True)

    # ---- 6.2 品牌 TOP10 ----
    brand = (dp.merge(valid[["product_id", "order_id", "actual_payment"]], on="product_id", how="left")
                .groupby("brand")
                .agg(prod_cnt=("product_id", "nunique"),
                     order_cnt=("order_id", "nunique"),
                     revenue=("actual_payment", "sum"),
                     avg_order=("actual_payment", "mean"))
                .reset_index()
                .sort_values("revenue", ascending=False)
                .head(10)
                .reset_index(drop=True))
    for c in ["revenue", "avg_order"]:
        brand[c] = brand[c].round(2)

    # ---- 6.3 价格区间分布 ----
    def price_range(x):
        if x < 100:
            return "低价(<100)"
        if x <= 500:
            return "中价(100-500)"
        if x <= 1000:
            return "中高价(500-1000)"
        if x <= 3000:
            return "高价(1000-3000)"
        return "超高价(3000+)"

    pr_order = ["低价(<100)", "中价(100-500)", "中高价(500-1000)", "高价(1000-3000)", "超高价(3000+)"]
    g = dp["price"].map(price_range)
    price_dist = (g.value_counts().reindex(pr_order).rename("cnt").reset_index())
    price_dist.columns = ["price_range", "cnt"]
    price_dist["pct"] = (price_dist["cnt"] * 100 / len(dp)).round(2)

    # ---- 6.4.1 转化率整体分布 ----
    def cv_range(x):
        if x == 1:
            return "100%"
        if x >= 0.5:
            return "50%-100%"
        if x >= 0.1:
            return "10%-50%"
        if x > 0:
            return "0%-10%"
        return "无数据"

    cv_dist = (dp["conversion_rate"].map(cv_range)
                 .value_counts()
                 .rename("product_count")
                 .reset_index())
    cv_dist.columns = ["rate_range", "product_count"]
    cv_dist["percentage"] = (cv_dist["product_count"] * 100 / len(dp)).round(2)
    cv_dist = cv_dist.sort_values("product_count", ascending=False).reset_index(drop=True)

    # ---- 6.4.2 分品类：平均转化率 vs 有效转化率（过滤浏览量<10 的小样本） ----
    cat_cv = dp.groupby("category").agg(
        商品数=("product_id", "size"),
        总浏览量=("view_count", "sum"),
        总销量=("total_sales", "sum"),
        平均转化率=("conversion_rate", "mean"),
    ).reset_index()
    ok = dp[dp["view_count"] >= MIN_VIEW_FOR_CV]
    eff = (ok.groupby("category")["total_sales"].sum() /
           ok.groupby("category")["view_count"].sum()).round(4)
    cat_cv["有效转化率"] = cat_cv["category"].map(eff)
    cat_cv["平均转化率"] = cat_cv["平均转化率"].round(4)
    cat_cv = cat_cv.sort_values("有效转化率", ascending=False).reset_index(drop=True)

    return {
        "06_category_analysis": cat,
        "06_brand_top10": brand,
        "06_price_range": price_dist,
        "06_cv_distribution": cv_dist,
        "06_category_conversion": cat_cv,
    }
