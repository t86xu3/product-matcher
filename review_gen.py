"""產出可疑標記審核清單

把 check.py 找出來的可疑標記，用 id join 回 label_pairs.json 拿圖片/價格，
輸出 data/suspicious_review.json 供 review.html 使用。

用法：
    python3 review_gen.py
    python3 review_gen.py --threshold 0.3
"""

import argparse
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


def main(labels_path: str, pairs_path: str, model_path: str, output_path: str, threshold: float):
    print(f"載入模型: {model_path}")
    model = SentenceTransformer(model_path)

    labels = json.load(open(labels_path))
    pairs = json.load(open(pairs_path))
    pairs_by_id = {p["id"]: p for p in pairs}

    # 去重（同 check.py 邏輯）
    seen = set()
    data = []
    for d in labels:
        key = (d["shopee_name"], d["coupang_name"])
        if key not in seen:
            seen.add(key)
            data.append(d)

    print(f"標記資料: {len(data)} 組（去重前 {len(labels)}）")
    print("編碼中...")
    s_embs = model.encode([d["shopee_name"] for d in data], show_progress_bar=False)
    c_embs = model.encode([d["coupang_name"] for d in data], show_progress_bar=False)

    suspicious = []
    for i, d in enumerate(data):
        sim = cos_sim(s_embs[i], c_embs[i]).item()
        label = d["label"]
        reason = None

        if label == 1 and sim < (1.0 - threshold):
            reason = f"標同款但模型只給 {sim:.2f}"
        elif label == 0 and sim > threshold:
            reason = f"標不同但模型給 {sim:.2f}"
        else:
            continue

        pair = pairs_by_id.get(d["id"])
        if not pair:
            print(f"  ⚠️ id={d['id']} 在 label_pairs.json 找不到，跳過")
            continue

        suspicious.append({
            "id": d["id"],
            "keyword": pair.get("keyword"),
            "shopee": pair["shopee"],
            "coupang": pair["coupang"],
            "shopee_brand": pair.get("shopee_brand"),
            "coupang_brand": pair.get("coupang_brand"),
            "original_label": label,
            "model_score": round(sim, 4),
            "reason": reason,
        })

    # 按可疑程度排序（越矛盾越前面）
    suspicious.sort(
        key=lambda x: abs(x["model_score"] - (1.0 if x["original_label"] == 1 else 0.0)),
        reverse=True,
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(suspicious, f, ensure_ascii=False, indent=2)

    same = sum(1 for s in suspicious if s["original_label"] == 1)
    diff = sum(1 for s in suspicious if s["original_label"] == 0)
    print(f"\n可疑 {len(suspicious)} 組  →  {output_path}")
    print(f"  原標「同款」模型覺得不像: {same} 筆")
    print(f"  原標「不同」模型覺得很像: {diff} 筆")
    print(f"\n下一步：")
    print(f"  python3 -m http.server 8080 --directory labeler")
    print(f"  開啟 http://localhost:8080/review.html")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", default="data/product_labels.json")
    parser.add_argument("--pairs", default="data/label_pairs.json")
    parser.add_argument("--model", default="data/product-matcher-model")
    parser.add_argument("--output", default="data/suspicious_review.json")
    parser.add_argument("--threshold", type=float, default=0.3)
    args = parser.parse_args()

    main(args.labels, args.pairs, args.model, args.output, args.threshold)
