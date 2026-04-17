"""合併新一批標記結果到主資料集

把 batch_labels.json（用戶在 batch.html 標完匯出的）
和 new_pairs.json 分別 append 到 product_labels.json 和 label_pairs.json。

自動備份舊檔。

用法：
    python3 merge_batch.py
    python3 merge_batch.py --batch-labels data/batch_labels.json
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


def main(labels_path: str, pairs_path: str, batch_labels_path: str, batch_pairs_path: str):
    batch_labels = json.load(open(batch_labels_path))
    batch_pairs = json.load(open(batch_pairs_path))

    labels = json.load(open(labels_path))
    pairs = json.load(open(pairs_path))

    # 備份
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy(labels_path, Path(labels_path).with_name(f"product_labels.backup-{stamp}.json"))
    shutil.copy(pairs_path, Path(pairs_path).with_name(f"label_pairs.backup-{stamp}.json"))
    print(f"已備份 product_labels.json / label_pairs.json (stamp {stamp})")

    # 過濾重複（以 id 為準，理論上不應該有，因為 gen_pairs.py 已避開）
    existing_label_ids = {d["id"] for d in labels}
    existing_pair_ids = {p["id"] for p in pairs}

    new_labels = [b for b in batch_labels if b["id"] not in existing_label_ids]
    new_pairs_to_add = [p for p in batch_pairs if p["id"] not in existing_pair_ids]

    # Append
    labels.extend(new_labels)
    pairs.extend(new_pairs_to_add)

    with open(labels_path, "w", encoding="utf-8") as f:
        json.dump(labels, f, ensure_ascii=False, indent=2)
    with open(pairs_path, "w", encoding="utf-8") as f:
        json.dump(pairs, f, ensure_ascii=False, indent=2)

    same = sum(1 for d in labels if d["label"] == 1)
    diff = sum(1 for d in labels if d["label"] == 0)
    print(f"\n合併完成")
    print(f"  批次新增 labels: {len(new_labels)} 筆（batch 檔 {len(batch_labels)} 筆，去重後 {len(new_labels)}）")
    print(f"  批次新增 pairs:  {len(new_pairs_to_add)} 筆（new_pairs 檔 {len(batch_pairs)} 筆）")
    print(f"  現行 product_labels: {len(labels)} 筆（同款 {same} / 不同 {diff}）")
    print(f"  現行 label_pairs:    {len(pairs)} 筆")
    print(f"\n下一步: python3 train.py && python3 check.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", default="data/product_labels.json")
    parser.add_argument("--pairs", default="data/label_pairs.json")
    parser.add_argument("--batch-labels", default="data/batch_labels.json")
    parser.add_argument("--batch-pairs", default="data/new_pairs.json")
    args = parser.parse_args()

    main(args.labels, args.pairs, args.batch_labels, args.batch_pairs)
