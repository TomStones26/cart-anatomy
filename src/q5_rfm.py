# -*- coding: utf-8 -*-
"""Q5 RFM 用户分层。

对应 sql/05_rfm.sql：
  5.1 R/F/M 计算（R 用 delivery_date；有效订单四状态）
  5.2 PERCENT_RANK 分档评分
  5.3 八层用户分层
"""
import pandas as pd

from config import RFM_VALID_STATUS


def _percent_rank(s: pd.Series) -> pd.Series:
    """与 SQL PERCENT_RANK() 完全一致的分位排名：(rank-1)/(n-1)，并列取最小 rank。"""
    r = s.rank(method="min")
    n = len(s)
    return (r - 1) / (n - 1)


def run(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    fo = data["fact_orders"]

    # ---- 5.1 RFM 原始指标 ----
    # recency 严格对齐 MySQL DATEDIFF(CURRENT_DATE(), MAX(delivery_date))：
    # 两侧都归零到日期，只算日期差（若不归零，会因时分秒少算 1 天）
    valid = fo[fo["order_status"].isin(RFM_VALID_STATUS) & fo["delivery_date"].notna()]
    today = pd.Timestamp.now().normalize()
    rfm_raw = (valid.groupby("user_id")
                     .agg(recency=("delivery_date", lambda s: (today - s.max().normalize()).days),
                          frequency=("order_id", "nunique"),
                          monetary=("actual_payment", "sum"))
                     .reset_index())
    rfm_raw["frequency"] = rfm_raw["frequency"].astype(int)
    rfm_raw["monetary"] = rfm_raw["monetary"].round(2)

    # ---- 5.2 R/F/M 评分 ----
    r_pct = _percent_rank(rfm_raw["recency"])
    f_pct = _percent_rank(rfm_raw["frequency"])
    m_pct = _percent_rank(rfm_raw["monetary"])

    def r_score(p):   # recency 越小越好
        return 5 if p <= 0.2 else 4 if p <= 0.4 else 3 if p <= 0.6 else 2 if p <= 0.8 else 1

    def fm_score(p):  # frequency / monetary 越大越好
        return 5 if p >= 0.8 else 4 if p >= 0.6 else 3 if p >= 0.4 else 2 if p >= 0.2 else 1

    rfm_score = rfm_raw.copy()
    rfm_score["r_score"] = r_pct.map(r_score).astype(int)
    rfm_score["f_score"] = f_pct.map(fm_score).astype(int)
    rfm_score["m_score"] = m_pct.map(fm_score).astype(int)

    # ---- 5.3 八层用户分层 ----
    def segment(row):
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "重要价值用户"
        if r >= 4 and f >= 4 and m < 4:
            return "重要发展用户"
        if r >= 4 and f < 4 and m >= 4:
            return "重要保持用户"
        if r >= 4 and f < 4 and m < 4:
            return "新用户"
        if r < 4 and f >= 4 and m >= 4:
            return "重要挽留用户"
        if r < 4 and f >= 4 and m < 4:
            return "一般维持用户"
        if r < 4 and f < 4 and m >= 4:
            return "一般价值用户"
        return "流失用户"

    rfm_segments = rfm_score.copy()
    rfm_segments["user_segment"] = rfm_segments.apply(segment, axis=1)

    seg_summary = (rfm_segments.groupby("user_segment")
                                .agg(cnt=("user_id", "size"), avg_spent=("monetary", "mean"))
                                .reset_index())
    seg_summary["pct"] = (seg_summary["cnt"] * 100 / len(rfm_segments)).round(2)
    seg_summary["avg_spent"] = seg_summary["avg_spent"].round(2)
    seg_summary = seg_summary.sort_values("cnt", ascending=False).reset_index(drop=True)

    data["rfm_segments"] = rfm_segments
    return {
        "05_rfm_raw_head": rfm_raw.sort_values("monetary", ascending=False).head(10).reset_index(drop=True),
        "05_rfm_score_head": rfm_score.head(10).reset_index(drop=True),
        "05_rfm_segments": seg_summary,
    }
