"""使用訓練好的模型做商品配對推論

用法：
    python predict.py "Soundcore R50i 耳機" "soundcore R50i NC 藍牙耳機"
    python predict.py --batch pairs.json
"""

import argparse
import json

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


def predict_pair(model, text_a: str, text_b: str, threshold: float = 0.6) -> dict:
    emb = model.encode([text_a, text_b])
    sim = cos_sim(emb[0], emb[1]).item()
    return {
        "text_a": text_a,
        "text_b": text_b,
        "similarity": round(sim, 4),
        "is_match": sim >= threshold,
    }


def predict_batch(model, pairs: list[dict], threshold: float = 0.6) -> list[dict]:
    results = []
    for p in pairs:
        r = predict_pair(model, p["shopee_name"], p["coupang_name"], threshold)
        results.append(r)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="商品配對推論")
    parser.add_argument("text_a", nargs="?", help="商品名 A")
    parser.add_argument("text_b", nargs="?", help="商品名 B")
    parser.add_argument("--model", default="data/product-matcher-model")
    parser.add_argument("--threshold", type=float, default=0.6)
    parser.add_argument("--batch", help="批量推論 JSON 檔案")
    args = parser.parse_args()

    print(f"載入模型: {args.model}")
    model = SentenceTransformer(args.model)

    if args.batch:
        pairs = json.load(open(args.batch))
        results = predict_batch(model, pairs, args.threshold)
        matched = [r for r in results if r["is_match"]]
        print(f"\n{len(matched)}/{len(results)} 組配對成功")
        for r in matched:
            print(f"  ✅ {r['similarity']:.4f}  {r['text_a'][:30]} ↔ {r['text_b'][:30]}")
    elif args.text_a and args.text_b:
        r = predict_pair(model, args.text_a, args.text_b, args.threshold)
        v = "✅ 同款" if r["is_match"] else "❌ 不同"
        print(f"\n{v}（相似度: {r['similarity']:.4f}）")
        print(f"  A: {r['text_a']}")
        print(f"  B: {r['text_b']}")
    else:
        parser.print_help()
