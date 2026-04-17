"""從 price-compare products.db 產生新一批候選配對

避開 label_pairs.json 已有的 (shopee_name, coupang_name) 組合，
每個 keyword 最多取 9 對（3×3），優先取剛爬到且價格接近的商品。

用法：
    python3 gen_pairs.py
    python3 gen_pairs.py --limit 500 --db ~/affiliate/price-compare/data/products.db
"""

import argparse
import json
import sqlite3
from pathlib import Path


def main(db_path: str, existing_pairs_path: str, output_path: str, limit: int, per_keyword: int):
    existing = set()
    next_id = 0
    if Path(existing_pairs_path).exists():
        for p in json.load(open(existing_pairs_path)):
            existing.add((p["shopee"]["name"], p["coupang"]["name"]))
            next_id = max(next_id, p.get("id", 0) + 1)
    print(f"既有配對 {len(existing)} 組，新 id 從 {next_id} 開始")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # 取兩邊都有商品的 keyword
    kws = [r[0] for r in conn.execute("""
        SELECT keyword FROM products
        WHERE image_url != ''
        GROUP BY keyword
        HAVING COUNT(DISTINCT platform) >= 2
    """)]
    print(f"跨平台 keyword {len(kws)} 個")

    new_pairs = []
    per_kw = max(3, per_keyword ** 0.5)

    for kw in kws:
        if len(new_pairs) >= limit:
            break

        shopee = list(conn.execute("""
            SELECT name, price, image_url, brand FROM products
            WHERE platform='shopee' AND keyword=? AND image_url != ''
            ORDER BY price ASC
            LIMIT ?
        """, (kw, int(per_kw))))
        coupang = list(conn.execute("""
            SELECT name, price, image_url, brand FROM products
            WHERE platform='coupang' AND keyword=? AND image_url != ''
            ORDER BY price ASC
            LIMIT ?
        """, (kw, int(per_kw))))

        taken = 0
        for s in shopee:
            for c in coupang:
                if (s["name"], c["name"]) in existing:
                    continue
                existing.add((s["name"], c["name"]))  # 避免同批重複
                new_pairs.append({
                    "id": next_id,
                    "keyword": kw,
                    "shopee": {"name": s["name"], "price": s["price"], "image": s["image_url"]},
                    "coupang": {"name": c["name"], "price": c["price"], "image": c["image_url"]},
                    "shopee_brand": s["brand"] or "",
                    "coupang_brand": c["brand"] or "",
                })
                next_id += 1
                taken += 1
                if taken >= per_keyword:
                    break
                if len(new_pairs) >= limit:
                    break
            if taken >= per_keyword or len(new_pairs) >= limit:
                break

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(new_pairs, f, ensure_ascii=False, indent=2)

    print(f"\n產出 {len(new_pairs)} 組新配對 → {output_path}")
    print(f"id 範圍: {new_pairs[0]['id']} – {new_pairs[-1]['id']}")


if __name__ == "__main__":
    home = str(Path.home())
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=f"{home}/affiliate/price-compare/data/products.db")
    parser.add_argument("--existing", default="data/label_pairs.json")
    parser.add_argument("--output", default="data/new_pairs.json")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--per-keyword", type=int, default=9)
    args = parser.parse_args()

    main(args.db, args.existing, args.output, args.limit, args.per_keyword)
