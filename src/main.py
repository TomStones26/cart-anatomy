# -*- coding: utf-8 -*-
"""主入口：串起 数据质量 → 清洗 → 星型模型 → 用户画像 → RFM → 商品分析 → 行为漏斗。

运行方式（PyCharm）：右键本文件 → Run 'main'
命令行：python src/main.py
所有结果表同时打印到控制台并保存到 outputs/*.csv（utf-8-sig，Excel 可直接打开）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

from config import OUTPUT_DIR
from data_loader import load_all
import q1_data_quality
import q2_cleaning
import q3_dimension_model
import q4_user_profile
import q5_rfm
import q6_product_analysis
import q7_behavior_funnel

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
pd.set_option("display.unicode.east_asian_width", True)

STEPS = [
    ("Q1 数据探索与质量检查", q1_data_quality),
    ("Q2 数据清洗", q2_cleaning),
    ("Q3 星型模型构建", q3_dimension_model),
    ("Q4 用户画像分析", q4_user_profile),
    ("Q5 RFM 用户分层", q5_rfm),
    ("Q6 商品分析", q6_product_analysis),
    ("Q7 行为漏斗分析", q7_behavior_funnel),
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data = load_all()
    print(f"[load] 6 张表读取完成：{ {k: len(v) for k, v in data.items()} }")

    for title, module in STEPS:
        print("\n" + "=" * 72)
        print(f"== {title} ==")
        print("=" * 72)
        results = module.run(data)
        for name, df in results.items():
            print(f"\n--- {name} ---")
            print(df.to_string(index=False))
            df.to_csv(OUTPUT_DIR / f"{name}.csv", index=False, encoding="utf-8-sig")

    print("\n" + "=" * 72)
    print(f"[done] 全部完成，结果文件已写入：{OUTPUT_DIR}")
    print("=" * 72)


if __name__ == "__main__":
    main()
