# 🛠️ KTV專案工具參考清單

## 🎯 核心爬蟲程式

### 1. **auto_scraper.py** ⭐ 主力爬蟲
- **用途**: 單一公司完整數據爬取
- **特點**: 10線程、智能延遲、實時保存
- **修改方式**: 改變第23-26行的公司名稱和頁數上限

### 2. **selective_scraper.py** 
- **用途**: 多家中小型公司並行爬取
- **特點**: 數據去重、智能檢測

### 3. **common_ktv_detector.py**
- **用途**: 快速檢測KTV公司數據規模  
- **用於**: 策略規劃和頁數估算

### 4. **data_quality_checker.py**
- **用途**: 檢查數據重複和品質

## 📊 核心監控工具

### 1. **quick_status.py** ⭐ 最常用
```bash
python quick_status.py
# 🟢 進度:51.2% 第12,809頁 歌曲:136,500首 剩餘:8.2h
```

### 2. **check_progress.py** 
```bash
python check_progress.py  # 詳細進度報告
```

### 3. **stop_scraper.py**
```bash
python stop_scraper.py    # 安全停止爬蟲
```

## ⚠️ 重要提醒

### 使用前先檢查
1. **爬蟲存在檢查**: `ls *scraper*.py` 確認有哪些可用
2. **監控工具檢查**: `ls *status*.py *progress*.py *check*.py` 避免重複創建
3. **參考指南**: 查看 `MONITORING_GUIDE.md` 和 `CORE_SCRAPERS.md`

### 避免重複創建
- ✅ 先查看現有工具
- ✅ 檢查 MONITORING_GUIDE.md 
- ✅ 使用已驗證的工具
- ❌ 不要創建功能相似的新工具

### 工具使用優先級
1. **快速狀態**: `python quick_status.py`
2. **詳細分析**: `python check_progress.py` 
3. **停止操作**: `python stop_scraper.py`
4. **公司檢測**: `python common_ktv_detector.py`

## 📁 目錄結構參考

```
/karaoke-search/
├── auto_scraper.py              # 主力爬蟲 ⭐
├── quick_status.py              # 快速監控 ⭐  
├── check_progress.py            # 詳細監控 ⭐
├── stop_scraper.py              # 停止工具 ⭐
├── selective_scraper.py         # 多公司爬蟲
├── common_ktv_detector.py       # 公司檢測
├── data_quality_checker.py      # 品質檢查
├── MONITORING_GUIDE.md          # 監控指南
├── CORE_SCRAPERS.md             # 爬蟲指南
├── backup_scrapers/             # 備份的舊工具
└── auto_results/                # 爬蟲輸出目錄
```

最後更新: 2025-08-10