# product-matcher PROJECT MAP

最後更新：2026-04-17（v0.1.3）

## 專案目標

微調 sentence-transformers 模型，判斷蝦皮 vs 酷澎商品是否為同款，用於跨平台比價。

---

## 🔴 最優先待辦

- [ ] **整合進 price-compare 比價流程**（`backend/core/product_matcher.py` 已有 hook，需確認模型檔部署方式）
- [ ] 下次擴充標記時有意識補「同系列不同型號」案例（R50i vs R60i、CeraVe 473/355 測試仍失敗）
- [ ] 3000+ 筆後再做一輪重審（現在 62 筆可疑不急）

---

## 當前狀態

| 項目 | 數值 |
|------|------|
| 標記資料量 | 1992 組（299 同款 / 1693 不同款） |
| 可疑標記數 | **62 筆（3.1%）** — v0.1.0 以來最低 |
| 目標 | 3000+ 筆、可疑 < 2% |
| 同款分數分布 | avg 0.853（min 0.096、max 0.989） |
| 不同分數分布 | avg 0.010（min -0.205、max 0.797） |
| 分界間距 | -0.701（outlier 修正後拉回）|

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
| `labeler/review.html` | 瀏覽器重審工具（可疑標記，逐筆） |
| `labeler/overview.html` | 瀏覽器一覽式重審（全部 render + 篩選 + 批次翻面） |
| `labeler/batch.html` | 瀏覽器批次標記工具（新一批，支援 ?round=N） |
| `data/label_pairs.json` | 候選配對（私有） |
| `data/product_labels.json` | 標記結果（私有） |
| `data/suspicious_review.json` | 審核清單（臨時） |
| `data/review_corrections.json` | 審核修正（臨時） |
| `data/product-matcher-model/` | 已訓練模型 |
| `checkpoints/` | 訓練 checkpoint |

---

## 下一步路線圖

1. 🔴 **整合進 price-compare** — 可疑 3.1%、分界間距 -0.701，已達上線水準
2. 觀察線上實際表現，收集 bad case
3. 資料量 3000+ 時再做一輪重審 + 重訓練
4. 下批擴充時補「同系列不同型號」case
