# 核心爬蟲程式清單

## 🎯 保留的核心程式

### 1. **auto_scraper.py** ⭐ 主力10線程爬蟲
- 目前運行中，表現優異
- 用途：單一公司完整數據爬取
- 修改方式：改變`self.company`參數

### 2. **selective_scraper.py** ⭐ 多公司選擇性爬蟲
- 用途：多家中小型公司並行爬取
- 特點：數據去重、智能檢測

### 3. **common_ktv_detector.py** ⭐ 公司檢測工具
- 用途：快速檢測KTV公司數據規模
- 策略規劃必需

### 4. **data_quality_checker.py** ⭐ 品質檢查工具
- 用途：檢查數據重複和品質

### 5. **stop_scraper.py** ⭐ 安全停止工具
- 用途：安全停止運行中的爬蟲

## 🗑️ 已備份的冗餘程式
- 所有*.py.backup文件 → backup_scrapers/
- 測試程式 → backup_scrapers/
- 舊版爬蟲 → backup_scrapers/

## 📝 下次使用說明
使用auto_scraper.py爬取其他公司時，只需修改第23-26行：
```python
self.company = "弘音"        # 改成目標公司
self.start_page = 1
self.total_pages = 2000      # 根據檢測結果調整
```

其他設置保持不變即可。