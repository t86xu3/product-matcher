# product-matcher — 跨平台商品配對模型

判斷蝦皮 vs 酷澎商品是否為同款，用於跨平台比價。

## 技術棧

| 類別 | 技術 |
|------|------|
| Base model | paraphrase-multilingual-MiniLM-L12-v2 |
| Loss | CosineSimilarityLoss |
| 框架 | sentence-transformers |
| 語言 | Python 3.11+ |

## 當前狀態（v0.1.1）

- 標記資料：495 組（130 同款 / 365 不同款）
- Spearman：0.703（eval），Pearson 0.823
- 可疑標記：36 筆（前一輪審 63 筆、修正 6 筆後重訓練）

## 同款定義

- ✅ 同款：完全相同型號，不同賣場/賣家
- ❌ 不同款：同型號不同容量/規格（如 473ml vs 236ml）
- ❌ 不同款：同系列不同型號（如 R50i vs R60i）
- ❌ 不同款：版本差異（一般版 vs 降噪版）

## 最優先待辦

- [ ] 重新審核剩下 36 筆可疑標記（前一輪審完 63 修 6）→ 重訓練
- [ ] 繼續標記到 2000 筆（Spearman 卡在 0.7，需更多樣本突破）

## 常用指令

```bash
# 啟動 http server（在專案根目錄跑，才能 fetch 到 ../data/）
python3 -m http.server 8080

# 標記新資料 → http://localhost:8080/labeler/labeler.html
# 重審可疑標記 → http://localhost:8080/labeler/review.html

# 資料品質檢查（印出可疑標記）
python3 check.py

# 產出可疑標記審核清單（給 review.html 用）
python3 review_gen.py

# 套用重審修正
python3 review_apply.py

# 訓練
python3 train.py

# 推論
python3 predict.py
```

## 核心檔案

| 檔案 | 說明 |
|------|------|
| `train.py` | 訓練腳本 |
| `predict.py` | 推論 |
| `check.py` | 品質檢查，印出可疑標記 |
| `review_gen.py` | 產出可疑標記審核清單（含圖片/價格） |
| `review_apply.py` | 套用 review.html 匯出的修正到 product_labels.json |
| `labeler/labeler.html` | 瀏覽器標記工具（新資料） |
| `labeler/review.html` | 瀏覽器重審工具（可疑標記） |
| `data/product_labels.json` | 標記結果（私有） |
| `data/label_pairs.json` | 候選配對資料（含圖片，私有） |
| `data/suspicious_review.json` | 審核清單（review_gen.py 產出） |
| `data/product-matcher-model/` | 已訓練模型 |
