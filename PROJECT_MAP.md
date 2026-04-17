# product-matcher PROJECT MAP

最後更新：2026-04-17（v0.1.2）

## 專案目標

微調 sentence-transformers 模型，判斷蝦皮 vs 酷澎商品是否為同款，用於跨平台比價。

---

## 🔴 最優先待辦

- [ ] **繼續擴充到 2000 筆**（現在 994，分界間距 -0.693 是主要瓶頸）
  - 啟動：`python3 gen_pairs.py && python3 -m http.server 8080`
  - 瀏覽：http://localhost:8080/labeler/batch.html
  - 審完下載 `batch_labels.json` → `python3 merge_batch.py` → `python3 train.py`
- [ ] 下批有意識補充「同系列不同型號」案例（R50i vs R60i 測試仍失敗）

---

## 當前狀態

| 項目 | 數值 |
|------|------|
| 標記資料量 | 994 組（193 同款 / 801 不同款） |
| Spearman 相關係數 | 0.640（eval，199 筆 split） |
| Pearson 相關係數 | 0.831（eval，歷史最佳） |
| 可疑標記數 | 94 筆（9.5%） |
| 目標 Spearman | 0.85+ |
| 同款分數分布 | avg 0.776（min 0.041、max 0.982） |
| 不同分數分布 | avg 0.057（min -0.213、max 0.734） |
| 分界間距 | -0.693（有重疊，需更多資料） |

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
| `gen_pairs.py` | 從 price-compare DB 抽新一批候選配對 |
| `merge_batch.py` | 合併批次標記到主資料集（自動備份） |
| `labeler/labeler.html` | 瀏覽器標記工具（初版） |
| `labeler/review.html` | 瀏覽器重審工具（可疑標記） |
| `labeler/batch.html` | 瀏覽器批次標記工具（新一批） |
| `data/label_pairs.json` | 候選配對（私有） |
| `data/product_labels.json` | 標記結果（私有） |
| `data/suspicious_review.json` | 審核清單（臨時） |
| `data/review_corrections.json` | 審核修正（臨時） |
| `data/product-matcher-model/` | 已訓練模型 |
| `checkpoints/` | 訓練 checkpoint |

---

## 下一步路線圖

1. 🔴 繼續擴充到 2000 筆（現在 994，分界間距 -0.693 是瓶頸）
2. 下批補充「同系列不同型號」案例（R50i vs R60i 仍誤判）
3. 資料量 2000+ 後再做一輪重審 + 重訓練
4. Spearman 穩定 0.80+ 後，整合進 shopee-compare / price-compare 比價流程
