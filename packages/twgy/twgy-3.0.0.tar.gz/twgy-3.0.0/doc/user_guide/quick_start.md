# TWGY_V3 快速開始指南

## 安裝

### 1. 系統需求

- Python 3.8+
- 4GB+ RAM (建議)
- 1GB 磁碟空間

### 2. 安裝依賴

```bash
# 克隆專案
git clone <repository-url> TWGY_V3
cd TWGY_V3

# 安裝依賴
pip install -r requirements.txt

# 初始化資料
python scripts/setup_data.py
```

### 3. 驗證安裝

```bash
# 檢查系統資訊
python -m src.cli system-info

# 驗證資料檔案
python -m src.cli validate-data
```

## 基本使用

### 命令列介面

#### 1. 計算兩個詞彙的相似度

```bash
python -m src.cli similarity "知道" "資道"
```

輸出：
```json
{
  "word1": "知道",
  "word2": "資道", 
  "similarity": 0.75,
  "method": "phonetic"
}
```

#### 2. 批量處理

準備輸入檔案 `pairs.csv`：
```csv
知道,資道
吃飯,次飯
是的,四的
```

執行批量處理：
```bash
python -m src.cli batch-process --input pairs.csv --output results.json
```

#### 3. 查找相似詞

```bash
python -m src.cli find-similar "知道" --top-k 5 --threshold 0.7
```

### Python API

#### 基本使用

```python
from src.core.phonetic_system import PhoneticSimilaritySystem

# 初始化系統
system = PhoneticSimilaritySystem()

# 計算相似度
similarity = system.calculate_similarity("知道", "資道")
print(f"相似度: {similarity:.3f}")

# 批量計算
pairs = [("知道", "資道"), ("吃飯", "次飯")]
similarities = system.batch_calculate_similarity(pairs)

# 查找相似詞
similar_words = system.find_similar_words("知道", top_k=5)
```

#### 高級配置

```python
from src.core.config import SystemConfig
from src.core.phonetic_system import PhoneticSimilaritySystem

# 自定義配置
config = SystemConfig()
config.similarity.default_threshold = 0.8
config.performance.device = "mps"  # 使用 Apple Silicon 加速

# 使用自定義配置初始化
system = PhoneticSimilaritySystem(config=config)
```

## 配置

### 配置檔案

建立 `config.yaml`：

```yaml
phonetic:
  use_bopomofo: true
  use_pinyin: true
  tone_weight: 0.3
  initial_weight: 0.4
  final_weight: 0.3

similarity:
  default_threshold: 0.7
  first_char_weight: 0.4
  last_char_weight: 0.4
  middle_chars_weight: 0.2

performance:
  device: "auto"  # auto, cpu, cuda, mps
  batch_size: 32
  cache_size: 10000
  enable_cache: true

data:
  data_dir: "data"
  dictionaries_dir: "data/dictionaries"
  phonetic_tables_dir: "data/phonetic_tables"
```

使用配置檔案：

```bash
python -m src.cli --config config.yaml similarity "知道" "資道"
```

### 環境變數

```bash
export TWGY_DEVICE=mps
export TWGY_THRESHOLD=0.8
export TWGY_LOG_LEVEL=DEBUG

python -m src.cli similarity "知道" "資道"
```

## 資料管理

### 字典檔案

錯誤修正字典格式 (`data/dictionaries/error_candidates_ok.csv`)：

```csv
平油,貧鈾
熊二,雄二
海瑪斯,海馬士
```

### 語音學表格

語音學分類表格 (`data/phonetic_tables/bopomofo_classification.yaml`)：

```yaml
initials:
  row_1_bilabial:
    name: "雙唇音"
    phonemes: ["ㄅ", "ㄆ", "ㄇ", "ㄈ"]
    similarity_within_row: 0.8
```

## 性能優化

### 硬體加速

```python
# 自動選擇最佳設備
system = PhoneticSimilaritySystem(device="auto")

# 指定設備
system = PhoneticSimilaritySystem(device="mps")  # Apple Silicon
system = PhoneticSimilaritySystem(device="cuda") # NVIDIA GPU
system = PhoneticSimilaritySystem(device="cpu")  # CPU only
```

### 批量處理

```python
# 大批量處理
large_pairs = [("詞1", "詞2")] * 10000

# 分批處理
batch_size = 1000
results = []

for i in range(0, len(large_pairs), batch_size):
    batch = large_pairs[i:i+batch_size]
    batch_results = system.batch_calculate_similarity(batch)
    results.extend(batch_results)
```

### 緩存優化

```python
# 啟用緩存
system = PhoneticSimilaritySystem(enable_cache=True, cache_size=20000)

# 清除緩存
system.clear_cache()

# 獲取緩存資訊
cache_info = system.get_cache_info()
```

## 故障排除

### 常見問題

#### 1. 記憶體不足

```bash
# 減少批量大小
export TWGY_BATCH_SIZE=16

# 減少緩存大小
export TWGY_CACHE_SIZE=5000

# 使用 CPU
export TWGY_DEVICE=cpu
```

#### 2. 資料檔案缺失

```bash
# 檢查資料狀態
python -m src.cli validate-data

# 重新設置資料
python scripts/setup_data.py
```

#### 3. 依賴問題

```bash
# 重新安裝依賴
pip install -r requirements.txt --force-reinstall

# 檢查 PyTorch 安裝
python -c "import torch; print(torch.__version__)"
```

### 除錯模式

```bash
# 啟用除錯日誌
python -m src.cli --log-level DEBUG similarity "知道" "資道"

# 詳細系統資訊
python -m src.cli system-info --output system_info.json
```

## 進階使用

### 自定義比對策略

```python
from src.comparison.strategies import ComparisonStrategy

# 自定義策略
class CustomStrategy(ComparisonStrategy):
    def calculate_similarity(self, word1, word2):
        # 自定義相似度計算邏輯
        return 0.5

# 註冊策略
system.register_strategy("custom", CustomStrategy())
```

### 擴展語音學分類

```yaml
# 新增自定義分類
initials:
  custom_group:
    name: "自定義分組"
    phonemes: ["ㄅ", "ㄆ"]
    similarity_within_row: 0.9
```

### 整合其他系統

```python
# 與 ASR 系統整合
def correct_asr_output(asr_text):
    system = PhoneticSimilaritySystem()
    # 實現 ASR 錯誤修正邏輯
    return corrected_text

# 與搜索引擎整合
def expand_search_query(query):
    system = PhoneticSimilaritySystem()
    similar_terms = system.find_similar_words(query)
    return [term["word"] for term in similar_terms]
```

## 下一步

- 閱讀 [API 文檔](../api/api_documentation.md)
- 查看 [技術文檔](../technical/architecture.md)
- 瀏覽 [範例程式](../examples/)
- 參與 [開發指南](../technical/development_guide.md)