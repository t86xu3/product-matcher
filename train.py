"""訓練商品配對模型

用法：
    python train.py
    python train.py --epochs 5 --batch-size 32
    python train.py --data data/product_labels.json --output data/product-matcher-model
"""

import argparse
import json
import random
import time
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from sentence_transformers import SentenceTransformer, InputExample
from sentence_transformers.losses import CosineSimilarityLoss
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from sentence_transformers.util import cos_sim
from torch.utils.data import DataLoader


def train(data_path: str, output_path: str, epochs: int = 3, batch_size: int = 16, eval_split: float = 0.2):
    # 1. 載入標記資料（自動去重）
    raw = json.load(open(data_path))
    seen = set()
    data = []
    for d in raw:
        key = (d["shopee_name"], d["coupang_name"])
        if key not in seen:
            seen.add(key)
            data.append(d)
    print(f"標記資料: {len(data)} 組（去重前 {len(raw)}，同款 {sum(1 for d in data if d['label']==1)}、不同 {sum(1 for d in data if d['label']==0)}）")

    examples = [
        InputExample(texts=[d["shopee_name"], d["coupang_name"]], label=float(d["label"]))
        for d in data
    ]

    random.seed(42)
    random.shuffle(examples)

    split = int(len(examples) * (1 - eval_split))
    train_ex = examples[:split]
    eval_ex = examples[split:]
    print(f"訓練: {len(train_ex)}, 驗證: {len(eval_ex)}")

    # 2. 載入 base model
    print("載入 base model: paraphrase-multilingual-MiniLM-L12-v2...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    # 3. 訓練
    loader = DataLoader(train_ex, shuffle=True, batch_size=batch_size)
    loss = CosineSimilarityLoss(model)

    evaluator = EmbeddingSimilarityEvaluator(
        [e.texts[0] for e in eval_ex],
        [e.texts[1] for e in eval_ex],
        [e.label for e in eval_ex],
        name="product-match",
    )

    print(f"訓練中（{epochs} epochs, batch_size={batch_size}）...")
    t0 = time.time()

    model.fit(
        train_objectives=[(loader, loss)],
        evaluator=evaluator,
        epochs=epochs,
        warmup_steps=10,
        output_path=output_path,
        show_progress_bar=True,
        evaluation_steps=50,
    )

    print(f"訓練完成（{time.time() - t0:.0f}s）")
    print(f"模型存在: {output_path}")

    # 4. 快速測試
    print("\n快速測試：")
    tests = [
        ("Soundcore R50i NC 主動降噪真無線藍牙耳機", "soundcore R50i NC主動降噪真無線藍牙耳機", True),
        ("CeraVe 溫和泡沫潔膚露 473ml", "CeraVe 適樂膚 溫和泡沫潔膚露 355ml", False),  # 同型號不同容量 = 不同款
        ("Soundcore R50i 真無線藍牙耳機", "Soundcore R60i 真無線藍牙耳機", False),  # 同系列不同型號 = 不同款
        ("Dyson V8 無線吸塵器", "LG PuriCare 空氣清淨機", False),
        ("Canon PGI-750XL 墨水匣", "Canon PGI-750XL+CLI-751XL 原廠墨水匣", True),
        ("Adidas Ultraboost 5 慢跑鞋", "Nike Air Max 270 運動鞋", False),
    ]

    correct = 0
    for a, b, expected in tests:
        emb = model.encode([a, b])
        sim = cos_sim(emb[0], emb[1]).item()
        predicted = sim >= 0.6
        ok = predicted == expected
        correct += ok
        v = "✅" if ok else "❌"
        print(f"  {v} {sim:.4f}  {a[:30]} ↔ {b[:30]}")

    print(f"\n測試準確率: {correct}/{len(tests)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="訓練商品配對模型")
    parser.add_argument("--data", default="data/product_labels.json", help="標記資料路徑")
    parser.add_argument("--output", default="data/product-matcher-model", help="模型輸出路徑")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()

    train(args.data, args.output, args.epochs, args.batch_size)
