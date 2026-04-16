# Changelog

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
