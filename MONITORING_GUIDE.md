# 🎯 KTV爬蟲監控工具指南

## 📋 核心監控工具清單

### 1. **quick_status.py** ⭐ 快速狀態檢查
```bash
python quick_status.py
# 輸出: 🟢 進度:52.6% 第13,140頁 歌曲:112,950首 剩餘:8.0h
```
- **用途**: 一行輸出當前進度
- **頻率**: 隨時快速查看
- **輸出**: 狀態圖標 + 進度百分比 + 頁數 + 歌曲數 + 剩餘時間

### 2. **check_progress.py** ⭐ 詳細進度報告
```bash
python check_progress.py
```
- **用途**: 完整的爬蟲狀態分析
- **頻率**: 需要詳細信息時
- **輸出**: 
  - 進程狀態和PID
  - 批次文件統計
  - 各線程詳細進度
  - 整體進度和預估時間
  - 最終文件信息

### 3. **stop_scraper.py** ⭐ 安全停止工具
```bash
python stop_scraper.py
```
- **用途**: 安全停止運行中的爬蟲
- **特點**: 保留已完成的數據

## 🔧 使用場景指南

### 💡 日常監控
```bash
# 快速檢查 (推薦)
python quick_status.py

# 每10分鐘檢查一次
watch -n 600 "python quick_status.py"
```

### 📊 深度分析
```bash
# 詳細進度報告
python check_progress.py

# 檢查批次文件
ls -la auto_results/ | tail -10
```

### 🛑 緊急停止
```bash
# 安全停止爬蟲
python stop_scraper.py
```

### 📁 數據檢查
```bash
# 檢查最終合併文件
ls -la 音圓完整數據_*.json

# 統計歌曲數量
grep -c '"公司"' 音圓完整數據_*.json
```

## 🎯 其他公司爬蟲監控

使用同樣的監控工具，會自動適應：
- `quick_status.py` - 自動檢測任何running的scraper
- `check_progress.py` - 檢測auto_results目錄
- `stop_scraper.py` - 停止任何scraper進程

## ⚠️ 注意事項

1. **避免創建重複工具** - 先檢查這個指南
2. **統一使用Python版本** - 更穩定和跨平台
3. **保持工具簡潔** - 單一職責原則
4. **實時監控使用watch命令** - 而非創建循環腳本

## 📝 工具維護

- ✅ 已清理重複工具
- ✅ 統一命名規範  
- ✅ 單一職責設計
- ✅ 跨平台兼容性