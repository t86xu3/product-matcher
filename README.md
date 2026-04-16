# Product Matcher — 跨平台電商商品配對訓練工具

用人工標記 + sentence-transformers 微調，訓練出能判斷「蝦皮的 A 商品」和「酷澎的 B 商品」是否為同款的模型。

## 為什麼需要這個？

跨平台比價的核心問題是：**怎麼判斷兩個平台上的商品是同一個東西？**

- 蝦皮叫「Soundcore R50i NC 主動降噪真無線藍牙耳機」
- 酷澎叫「soundcore R50i NC主動降噪真無線藍牙耳機 原廠保固」
- 規則式比對（品牌+型號）能配到一部分，但很多商品沒有型號、命名格式不同

這個專案用 **人工標記** + **微調語言模型** 來解決這個問題。

## 運作方式

```
1. 從你的商品 DB 產生候選配對
2. 用標記工具（瀏覽器）人工判斷是否同款
3. 用標記資料微調 sentence-transformers 模型
4. 模型學會跨平台商品名的語意匹配
```

## 快速開始

### 1. 安裝

```bash
pip install sentence-transformers datasets accelerate
```

### 2. 準備標記資料

建立 `data/label_pairs.json`，格式：

```json
[
  {
    "id": 0,
    "keyword": "藍牙耳機",
    "shopee": {
      "name": "Soundcore R50i NC 主動降噪真無線藍牙耳機",
      "price": 1290,
      "image": "https://example.com/image.jpg"
    },
    "coupang": {
      "name": "soundcore R50i NC主動降噪真無線藍牙耳機 原廠保固",
      "price": 1190,
      "image": "https://example.com/image2.jpg"
    }
  }
]
```

### 3. 標記

```bash
# 啟動任何 HTTP server
python -m http.server 8080 --directory labeler

# 打開瀏覽器
open http://localhost:8080/labeler.html
```

快捷鍵：
| 按鍵 | 動作 |
|------|------|
| Y / 1 | 同款 |
| N / 0 | 不同 |
| 空白 | 跳過 |
| Z / Backspace | 上一步 |

標完後匯出 `product_labels.json`，放到 `data/` 目錄。

### 4. 訓練

```bash
python train.py
```

訓練完成後模型存在 `data/product-matcher-model/`。

### 5. 使用模型

```python
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

model = SentenceTransformer("data/product-matcher-model")

emb = model.encode(["Soundcore R50i 耳機", "soundcore R50i NC 藍牙耳機"])
similarity = cos_sim(emb[0], emb[1]).item()

if similarity >= 0.6:
    print("同款商品")
else:
    print("不同商品")
```

## 專案結構

```
product-matcher/
├── labeler/
│   └── labeler.html          標記工具（瀏覽器）
├── train.py                  訓練腳本
├── predict.py                推論工具
├── data/                     資料目錄（.gitignore）
│   ├── label_pairs.json      候選配對（私有）
│   ├── product_labels.json   標記結果（私有）
│   └── product-matcher-model/  訓練好的模型（私有）
└── README.md
```

## 技術細節

- **Base model**: `paraphrase-multilingual-MiniLM-L12-v2`（多語言，支援中文）
- **Loss**: CosineSimilarityLoss
- **訓練資料**: 人工標記的跨平台商品配對（同款=1.0, 不同=0.0）
- **推論速度**: 毫秒級（CPU）
- **模型大小**: ~470MB

## 適用場景

- 蝦皮 vs 酷澎比價
- 任何跨電商平台的商品配對
- 同平台不同賣家的同款識別

## License

MIT
