"""標記品質檢查 — 用訓練好的模型反查可疑標記

用法：
    python check.py
    python check.py --data data/product_labels.json --threshold 0.3
"""

import argparse
import json

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


def check(data_path: str, model_path: str, threshold: float = 0.3):
    print(f"載入模型: {model_path}")
    model = SentenceTransformer(model_path)

    raw = json.load(open(data_path))

    # 去重
    seen = set()
    data = []
    for d in raw:
        key = (d["shopee_name"], d["coupang_name"])
        if key not in seen:
            seen.add(key)
            data.append(d)

    print(f"標記資料: {len(data)} 組（去重前 {len(raw)}）")

    # 批量編碼
    shopee_names = [d["shopee_name"] for d in data]
    coupang_names = [d["coupang_name"] for d in data]

    print("編碼中...")
    shopee_embs = model.encode(shopee_names, show_progress_bar=False)
    coupang_embs = model.encode(coupang_names, show_progress_bar=False)

    # 找可疑標記
    suspicious = []
    for i, d in enumerate(data):
        sim = cos_sim(shopee_embs[i], coupang_embs[i]).item()
        label = d["label"]

        # 標同款但模型覺得很不像
        if label == 1 and sim < (1.0 - threshold):
            suspicious.append({
                "index": i,
                "shopee": d["shopee_name"],
                "coupang": d["coupang_name"],
                "label": "同款",
                "model_score": round(sim, 4),
                "reason": f"標同款但模型只給 {sim:.2f}",
            })

        # 標不同但模型覺得很像
        if label == 0 and sim > threshold:
            suspicious.append({
                "index": i,
                "shopee": d["shopee_name"],
                "coupang": d["coupang_name"],
                "label": "不同",
                "model_score": round(sim, 4),
                "reason": f"標不同但模型給 {sim:.2f}",
            })

    # 按可疑程度排序
    suspicious.sort(key=lambda x: abs(x["model_score"] - (1.0 if x["label"] == "同款" else 0.0)), reverse=True)

    # 報告
    print(f"\n{'='*60}")
    print(f"  標記品質檢查結果")
    print(f"{'='*60}")
    print(f"  總標記: {len(data)} 組")
    print(f"  可疑:   {len(suspicious)} 組（{len(suspicious)/len(data)*100:.1f}%）")
    print(f"  門檻:   同款 < {1.0-threshold:.1f} 或 不同 > {threshold:.1f} 視為可疑")

    if suspicious:
        print(f"\n{'='*60}")
        print(f"  可疑標記（請複查）")
        print(f"{'='*60}")

        for i, s in enumerate(suspicious, 1):
            print(f"\n  #{i}  ⚠️ {s['reason']}")
            print(f"  你的標記: {s['label']}")
            print(f"  模型分數: {s['model_score']}")
            print(f"  蝦皮: {s['shopee'][:50]}")
            print(f"  酷澎: {s['coupang'][:50]}")
    else:
        print(f"\n  ✅ 沒有可疑標記，品質良好！")

    # 統計
    all_sims = [cos_sim(shopee_embs[i], coupang_embs[i]).item() for i in range(len(data))]
    yes_sims = [all_sims[i] for i, d in enumerate(data) if d["label"] == 1]
    no_sims = [all_sims[i] for i, d in enumerate(data) if d["label"] == 0]

    print(f"\n{'='*60}")
    print(f"  分數分布")
    print(f"{'='*60}")
    if yes_sims:
        print(f"  同款（{len(yes_sims)} 組）: avg={sum(yes_sims)/len(yes_sims):.3f}  min={min(yes_sims):.3f}  max={max(yes_sims):.3f}")
    if no_sims:
        print(f"  不同（{len(no_sims)} 組）: avg={sum(no_sims)/len(no_sims):.3f}  min={min(no_sims):.3f}  max={max(no_sims):.3f}")

    if yes_sims and no_sims:
        gap = min(yes_sims) - max(no_sims)
        print(f"\n  分界間距: {gap:.3f}（{'✅ 正向，分得開' if gap > 0 else '⚠️ 有重疊，模型可能需要更多資料'}）")

    return suspicious


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="標記品質檢查")
    parser.add_argument("--data", default="data/product_labels.json")
    parser.add_argument("--model", default="data/product-matcher-model")
    parser.add_argument("--threshold", type=float, default=0.3, help="可疑門檻（預設 0.3）")
    args = parser.parse_args()

    check(args.data, args.model, args.threshold)
