# Changelog

## [0.1.2] — 2026-04-17

資料量從 495 翻倍到 994 筆，Pearson 創新高 0.831。

### 工具
- `gen_pairs.py`: 從 price-compare DB 抽 N 筆新配對（避開 label_pairs.json 已有組合，支援 --limit / --per-keyword）
- `merge_batch.py`: 合併批次標記到主資料集（自動備份 label_pairs.json 與 product_labels.json）
- `labeler/batch.html`: 批次標記介面（獨立 localStorage key、頂部同款定義提醒）

### 資料
- 新增 499 筆人工標記（68 同款、431 不同），id 範圍 724–1222
- 標記分布：130/365 → 193/801（同款率 26% → 20%）

### 指標
- eval Pearson: 0.823 → **0.831**（歷史最佳）
- eval Spearman: 0.703 → 0.640（199 筆 split 擴大後含更多新 case）
- 不同分數 max: 0.821 → 0.734（分類更肯定）
- R50i vs R60i 測試仍失敗（0.75）— 訓練資料「同系列不同型號」樣本不足

### 結論
擴增資料是突破 0.8 Spearman 的必經之路，當前瓶頸是樣本量（994 → 2000+），不是審核品質。

## [0.1.1] — 2026-04-17

重審工具鏈 + 6 筆標記修正 + 訓練測試貼齊新定義。

### 工具
- `review_gen.py`: 產出可疑標記審核清單（join label_pairs.json 拿圖片/價格）
- `review_apply.py`: 套用審核修正到 product_labels.json（自動備份）
- `labeler/review.html`: 重審介面（顯示原標 + 模型分數、翻面/維持原標/上一步）

### 修正
- 翻面 6 筆標記（5 筆 CeraVe 容量差異、1 筆 Laneige 氣墊 Neo 版本差異）
- `train.py` 測試 case 貼齊新同款定義：CeraVe 不同容量 = 不同款、新增 R50i vs R60i 同系列不同型號 case
- CLAUDE.md / README.md 的 http.server 啟動指令（原本 `--directory labeler` 會導致 `fetch('../data/...')` 404）

### 指標
- 可疑標記：63 → 36（-43%）
- eval Spearman: 0.71 → 0.703（小樣本修正對 99 筆 eval split 影響有限）
- eval Pearson: 0.80 → 0.823
- 標記分布：141/355 同/不同 → 130/365（翻 6 筆後）

## [0.1.0] — 2026-04-16

首版模型 + 完整工具鏈。

### 模型
- Base model: paraphrase-multilingual-MiniLM-L12-v2
- 訓練資料: 496 組人工標記（141 同款、355 不同）
- Spearman: 0.71
- 測試準確率: 5/5

### 工具
- labeler.html: 標記工具（圖片並排、快捷鍵、上一步）
- labeler-admin.html: 管理員審核頁面
- train.py: 訓練腳本（自動去重）
- predict.py: 推論工具（單對/批量）
- check.py: 標記品質檢查（模型反查可疑標記）
- workflow.png: 迭代流程圖
