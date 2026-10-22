# -*- coding: utf-8 -*-
"""Q4 用户画像分析。

对应 sql/04_user_profile.sql：
  4.1 年龄分层  4.2 性别  4.3 会员等级  4.4 地域TOP10  4.5 消费能力
"""
import pandas as pd


def run(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    du = data["dim_user"]
    n = len(du)

    # ---- 4.1 年龄分层 ----
    def age_group(a):
        if a < 20:
            return "20岁以下"
        if a <= 29:
            return "20-29岁"
        if a <= 39:
            return "30-39岁"
        if a <= 49:
            return "40-49岁"
        return "50岁及以上"

    order = ["20岁以下", "20-29岁", "30-39岁", "40-49岁", "50岁及以上"]
    g = du["age"].map(age_group)
    age_dist = (g.value_counts().reindex(order).rename("cnt").reset_index())
    age_dist.columns = ["age_group", "cnt"]
    age_dist["pct"] = (age_dist["cnt"] * 100 / n).round(2)

    # ---- 4.2 性别分布 ----
    gender = (du.groupby("gender")
                .agg(cnt=("user_id", "size"), avg_spent=("total_spent", "mean"))
                .reset_index())
    gender["pct"] = (gender["cnt"] * 100 / n).round(2)
    gender["avg_spent"] = gender["avg_spent"].round(2)

    # ---- 4.3 会员等级 ----
    lvl_order = ["普通会员", "铜牌会员", "银牌会员", "金牌会员", "钻石会员"]
    member = (du.groupby("member_level")
                 .agg(cnt=("user_id", "nunique"), avg_spent=("total_spent", "mean"))
                 .reindex([x for x in lvl_order if x in set(du["member_level"])])
                 .reset_index())
    member.columns = ["lvl", "cnt", "avg_spent"]
    member["pct"] = (member["cnt"] * 100 / n).round(2)
    member["avg_spent"] = member["avg_spent"].round(2)

    # ---- 4.4 地域 TOP10 ----
    province = (du.groupby("province")
                  .agg(cnt=("user_id", "size"))
                  .sort_values("cnt", ascending=False)
                  .head(10)
                  .reset_index())
    province["pct"] = (province["cnt"] * 100 / n).round(1)

    # ---- 4.5 消费能力 ----
    clvl_order = ["低", "中", "高"]
    consumption = (du.groupby("consumption_level")
                     .agg(cnt=("user_id", "size"), avg_spent=("total_spent", "mean"))
                     .reindex([x for x in clvl_order if x in set(du["consumption_level"])])
                     .reset_index())
    consumption["pct"] = (consumption["cnt"] * 100 / n).round(1)
    consumption["avg_spent"] = consumption["avg_spent"].round(2)

    return {
        "04_age_distribution": age_dist,
        "04_gender_distribution": gender,
        "04_member_level": member,
        "04_province_top10": province,
        "04_consumption_level": consumption,
    }
