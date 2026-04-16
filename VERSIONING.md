# 版本規則

每次訓練完模型並部署到 Cloud Run 時，必須更新版本號。

## 格式

```
MAJOR.MINOR.PATCH
```

| 類型 | 何時升 | 範例 |
|------|--------|------|
| PATCH | 重新訓練（更多標記資料、修正標記錯誤） | 0.1.0 → 0.1.1 |
| MINOR | 改訓練方式（換 base model、改 loss function、加新特徵） | 0.1.1 → 0.2.0 |
| MAJOR | 架構大改（換模型類型、改推論介面） | 0.2.0 → 1.0.0 |

## 部署 Checklist

1. [ ] 更新 `VERSION` 檔案
2. [ ] 更新 `CHANGELOG.md`
3. [ ] 將 `data/product-matcher-model/` 複製到 `price-compare/data/`
4. [ ] Cloud Run 重新部署
5. [ ] 驗證線上配對精度
