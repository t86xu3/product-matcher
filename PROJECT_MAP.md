# product-matcher PROJECT MAP

最後更新：2026-04-17

## 專案目標

微調 sentence-transformers 模型，判斷蝦皮 vs 酷澎商品是否為同款，用於跨平台比價。

---

## 🔴 最優先待辦

- [ ] **重新審核剩下 36 筆可疑標記**（前一輪 63 → 審完翻 6 筆 → 重訓練後剩 36）
  - 啟動：`python3 review_gen.py && python3 -m http.server 8080`
  - 瀏覽：http://localhost:8080/labeler/review.html
  - 審完下載 `review_corrections.json` → `python3 review_apply.py` → `python3 train.py`

---

## 當前狀態

| 項目 | 數值 |
|------|------|
| 標記資料量 | 495 組（130 同款 / 365 不同款） |
| Spearman 相關係數 | 0.703（eval） |
| Pearson 相關係數 | 0.823（eval） |
| 可疑標記數 | 36 筆（前輪 63 → 修 6 → 重訓練剩 36） |
| 目標 Spearman | 0.85+ |
| 同款分數分布 | avg 0.807（min 0.298、max 0.981） |
| 不同分數分布 | avg 0.045（min -0.177、max 0.821） |

---

## 同款定義（標記標準）

- ✅ 同款：完全相同型號，不同賣場/賣家
- ❌ 不同款：同型號但不同容量/規格（如 473ml vs 236ml）
- ❌ 不同款：同系列但不同型號（如 R50i vs R60i）
- ❌ 不同款：版本差異（一般版 vs NC 降噪版）

---

## 技術棧

| 類別 | 技術 |
|------|------|
| Base model | paraphrase-multilingual-MiniLM-L12-v2 |
| Loss | CosineSimilarityLoss |
| 框架 | sentence-transformers |
| 語言 | Python 3.11+ |
| 推論閾值 | 0.6（同款） |

---

## 核心檔案

| 檔案 | 說明 |
|------|------|
| `train.py` | 訓練腳本 |
| `predict.py` | 推論工具 |
| `check.py` | 資料品質檢查（印出可疑標記） |
| `review_gen.py` | 產出可疑標記審核清單（含圖片） |
| `review_apply.py` | 套用審核修正（自動備份） |
| `labeler/labeler.html` | 瀏覽器標記工具（新資料） |
| `labeler/review.html` | 瀏覽器重審工具（可疑標記） |
| `data/label_pairs.json` | 候選配對（私有） |
| `data/product_labels.json` | 標記結果（私有） |
| `data/suspicious_review.json` | 審核清單（臨時） |
| `data/review_corrections.json` | 審核修正（臨時） |
| `data/product-matcher-model/` | 已訓練模型 |
| `checkpoints/` | 訓練 checkpoint |

---

## 下一步路線圖

1. 🔴 重審剩下 36 筆可疑標記 → 重訓練
2. 繼續標記到 2000 筆（現在 495，分界間距 -0.523 有重疊）
3. 確保各商品類別都有覆蓋（避免 long tail 問題）
4. Spearman 穩定 0.80+ 後，整合進 shopee-compare 比價流程
