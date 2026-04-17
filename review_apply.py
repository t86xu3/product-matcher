"""套用重審修正到 product_labels.json

吃 review.html 匯出的 review_corrections.json，用 id match 更新 product_labels.json。
自動備份舊檔到 data/product_labels.backup-YYYYMMDD-HHMMSS.json。

用法：
    python3 review_apply.py
    python3 review_apply.py --corrections data/review_corrections.json
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


def main(labels_path: str, corrections_path: str):
    labels = json.load(open(labels_path))
    corrections = json.load(open(corrections_path))

    # 備份
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = Path(labels_path).with_name(f"product_labels.backup-{stamp}.json")
    shutil.copy(labels_path, backup)
    print(f"備份舊檔: {backup}")

    # 用 id 建 index（可能有重複 id 對應不同條目，這裡用最後一筆為準）
    label_by_id = {}
    for i, d in enumerate(labels):
        label_by_id[d["id"]] = i

    changed = 0
    missing = 0
    same_value = 0
    for c in corrections:
        idx = label_by_id.get(c["id"])
        if idx is None:
            missing += 1
            print(f"  ⚠️ id={c['id']} 在 labels 找不到，跳過")
            continue
        if labels[idx]["label"] == c["label"]:
            same_value += 1
            continue
        old = labels[idx]["label"]
        labels[idx]["label"] = c["label"]
        changed += 1
        print(f"  id={c['id']}  {old} → {c['label']}  | {labels[idx]['shopee_name'][:30]} ↔ {labels[idx]['coupang_name'][:30]}")

    with open(labels_path, "w", encoding="utf-8") as f:
        json.dump(labels, f, ensure_ascii=False, indent=2)

    same = sum(1 for d in labels if d["label"] == 1)
    diff = sum(1 for d in labels if d["label"] == 0)
    print(f"\n修正套用完成")
    print(f"  實際翻面: {changed} 筆")
    if same_value:
        print(f"  已是此值（跳過）: {same_value} 筆")
    if missing:
        print(f"  找不到: {missing} 筆")
    print(f"  現行標記: {len(labels)} 筆（同款 {same} / 不同 {diff}）")
    print(f"\n下一步: python3 train.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", default="data/product_labels.json")
    parser.add_argument("--corrections", default="data/review_corrections.json")
    args = parser.parse_args()

    main(args.labels, args.corrections)
