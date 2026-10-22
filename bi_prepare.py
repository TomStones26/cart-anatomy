# -*- coding: utf-8 -*-
"""为 PowerBI 看板生成聚合数据（同时也用于 HTML 高保真预览）。

数据来源：data/ 原始 CSV + outputs/ 已有结果，全部实算，不写死任何数字。
输出：bi/dashboard_data.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import pandas as pd

from data_loader import load_all
import q2_cleaning
import q3_dimension_model
import q5_rfm

BASE = Path(__file__).resolve().parent
OUT = BASE / "bi"
OUT.mkdir(exist_ok=True)

data = load_all()
q2_cleaning.run(data)
q3_dimension_model.run(data)
q5_rfm.run(data)

fo, du = data["fact_orders"], data["dim_user"]
fb, dp = data["fact_behaviors"], data["dim_product"]

# ---------- KPI ----------
valid = fo[fo["order_status"] != "已取消"]
gmv = float(valid["actual_payment"].sum())
orders = int(len(valid))
users_ordered = int(fo["user_id"].nunique())
kpi = {
    "gmv": round(gmv, 2),
    "orders": orders,
    "users_ordered": users_ordered,
    "aov": round(gmv / orders, 2),
    "arpu": round(gmv / users_ordered, 2),
    "products": int(len(dp)),
}

# ---------- 月度销售额（按 order_date，排除已取消） ----------
m = valid.assign(ym=valid["order_date"].dt.to_period("M").astype(str))
monthly = (m.groupby("ym").agg(gmv=("actual_payment", "sum"),
                               orders=("order_id", "nunique"),
                               last_day=("order_date", "max"))
             .reset_index().rename(columns={"ym": "month"}))
monthly["gmv"] = monthly["gmv"].round(2)
# 标记残月：该月最后一天的日期 < 月末，说明数据不完整（如 2026-03 只到 3/5）
import calendar
monthly["partial"] = monthly.apply(
    lambda r: r["last_day"].day < calendar.monthrange(r["last_day"].year, r["last_day"].month)[1],
    axis=1)
monthly["cut"] = monthly["last_day"].dt.strftime("%m-%d")
monthly = monthly.drop(columns=["last_day"])

# ---------- 订单状态 ----------
status = (fo.groupby("order_status").size().rename("n").reset_index()
            .sort_values("n", ascending=False))

# ---------- 品类 GMV ----------
cat = (dp.merge(valid[["product_id", "actual_payment"]], on="product_id", how="left")
         .groupby("category").agg(gmv=("actual_payment", "sum"),
                                  prod=("product_id", "nunique"))
         .reset_index().sort_values("gmv", ascending=False))
cat["gmv"] = cat["gmv"].round(2)

# ---------- 用户画像 ----------
age_order = ["20岁以下", "20-29岁", "30-39岁", "40-49岁", "50岁及以上"]


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


age = (du["age"].map(age_group).value_counts().reindex(age_order)
         .rename("n").reset_index())
age.columns = ["group", "n"]

gender = du.groupby("gender").agg(n=("user_id", "size")).reset_index()

member = (du.groupby("member_level")
            .agg(users=("user_id", "size"), spent=("total_spent", "sum"),
                 avg_spent=("total_spent", "mean"))
            .reset_index().sort_values("spent", ascending=False))
member["spent"] = member["spent"].round(2)
member["avg_spent"] = member["avg_spent"].round(2)

city = (du.groupby("city").agg(n=("user_id", "size"), spent=("total_spent", "sum"))
          .reset_index().sort_values("n", ascending=False).head(15))
city["spent"] = city["spent"].round(2)

# ---------- RFM ----------
seg = data["rfm_segments"]
seg_stat = (seg.groupby("user_segment")
               .agg(users=("user_id", "size"), avg_m=("monetary", "mean"),
                    total_m=("monetary", "sum"), avg_r=("recency", "mean"),
                    avg_f=("frequency", "mean"))
               .reset_index().sort_values("users", ascending=False))
for c in ["avg_m", "total_m", "avg_r", "avg_f"]:
    seg_stat[c] = seg_stat[c].round(2)
# 散点：全量 4472 点太多，等距抽样到 1200 以内，保证形状不失真
sc = seg if len(seg) <= 1200 else seg.iloc[:: max(1, len(seg) // 1200)]
scatter = [{"r": int(r.recency), "f": int(r.frequency), "m": round(float(r.monetary), 2),
            "s": r.user_segment}
           for r in sc.itertuples()]

# ---------- 行为漏斗（次数口径，与行为表一致） ----------
step_order = ["浏览", "点击", "收藏", "加购"]
funnel = (fb.groupby("behavior_type").size().reindex(step_order)
            .rename("n").reset_index())
funnel.columns = ["step", "n"]

# ---------- 品类转化率（来自 outputs，已按小样本过滤口径算好） ----------
cat_cv = pd.read_csv(BASE / "outputs" / "06_category_conversion.csv")

payload = {
    "kpi": kpi,
    "monthly": monthly.to_dict("records"),
    "status": status.to_dict("records"),
    "category": cat.to_dict("records"),
    "age": age.to_dict("records"),
    "gender": gender.to_dict("records"),
    "member": member.to_dict("records"),
    "city": city.to_dict("records"),
    "rfm_segments": seg_stat.to_dict("records"),
    "rfm_scatter": scatter,
    "funnel": funnel.to_dict("records"),
    "cat_cv": cat_cv.to_dict("records"),
    "meta": {
        "gmv_total": round(float(cat["gmv"].sum()), 2),
        "rfm_users": int(seg["user_id"].nunique()),
        "behavior_total": int(len(fb)),
    },
}

(OUT / "dashboard_data.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

print("KPI:", kpi)
print("月度:", len(monthly), "| 状态:", len(status), "| 品类:", len(cat))
print("RFM 分层:", len(seg_stat), "人:", kpi["users_ordered"], "| 散点采样:", len(scatter))
print("漏斗:", funnel.to_dict("records"))
print("写入:", OUT / "dashboard_data.json")
