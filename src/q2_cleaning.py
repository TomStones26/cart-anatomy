# -*- coding: utf-8 -*-
"""Q2 数据清洗。

对应 sql/02_cleaning.sql：
  2.1 按订单状态确认缺失的业务含义 → 未评价标记
  2.2 异常值检测
  2.3 数据类型检查
  2.4 字段名规范化（中文字段名 → 英文）
"""
import pandas as pd

from config import ALL_ORDER_STATUS, CN_TO_EN_COLUMNS


def run(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    o = data["orders"].copy()

    # ---- 2.1 缺失的业务含义：按订单状态交叉 ----
    status_missing = (o.groupby("order_status")
                        .agg(订单数=("order_id", "size"),
                             无发货日期=("delivery_date", lambda s: s.isna().sum()),
                             无收货日期=("receive_date", lambda s: s.isna().sum()),
                             无评分=("review_score", lambda s: s.isna().sum()),
                             无评价内容=("review_content", lambda s: s.isna().sum()))
                        .reindex([s for s in ALL_ORDER_STATUS if s in set(o["order_status"])])
                        .reset_index())

    # ---- 2.1 执行清洗：review_score 空 → 0（未评价）；review_content 空 → '未评价' ----
    # 口径：0 表示「未评价」而非 0 分差评，后续按评分过滤时需排除 0
    o["review_score"] = o["review_score"].fillna(0)
    o["review_content"] = o["review_content"].fillna("未评价")

    clean_summary = pd.DataFrame([{
        "总订单数": len(o),
        "未评分订单数": int((o["review_score"] == 0).sum()),
        "未评分占比": round((o["review_score"] == 0).mean(), 4),
        "无评价内容数": int((o["review_content"] == "未评价").sum()),
    }])

    # ---- 2.2 异常值：非正的价格/数量/金额 ----
    bad = o[(o["quantity"] <= 0) | (o["unit_price"] <= 0) |
            (o["total_amount"] <= 0) | (o["actual_payment"] <= 0)]
    outlier_check = pd.DataFrame([{
        "非正数量": int((o["quantity"] <= 0).sum()),
        "非正单价": int((o["unit_price"] <= 0).sum()),
        "非正总金额": int((o["total_amount"] <= 0).sum()),
        "非正实付": int((o["actual_payment"] <= 0).sum()),
        "异常订单数": len(bad),
    }])

    # ---- 2.3 数据类型检查（对应 DESCRIBE orders / products / users） ----
    dtype_rows = []
    for tname in ["orders", "products", "users"]:
        for col, dt in data[tname].dtypes.items():
            dtype_rows.append({"表": tname, "字段": col, "pandas类型": str(dt)})
    dtype_check = pd.DataFrame(dtype_rows)

    # ---- 2.4 字段名规范化：product_features 中文列名 → 英文 ----
    pf = data["product_features"]
    cn_cols = [c for c in pf.columns if c in CN_TO_EN_COLUMNS]
    rename_map = pd.DataFrame([{"原字段名": c, "规范后字段名": CN_TO_EN_COLUMNS[c]}
                               for c in cn_cols])
    data["product_features"] = pf.rename(columns=CN_TO_EN_COLUMNS)

    data["orders"] = o  # 清洗结果写回，供后续分析使用
    return {
        "02_status_missing": status_missing,
        "02_clean_summary": clean_summary,
        "02_outlier_check": outlier_check,
        "02_dtype_check": dtype_check,
        "02_rename_map": rename_map,
    }
