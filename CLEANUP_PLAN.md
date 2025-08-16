# 🧹 專案清理計劃

## 清理目標
1. 移除冗餘和過期文件
2. 整理備份文件
3. 清理測試和調試文件
4. 整理日誌和輸出目錄

## 文件分類分析

### 🟢 保留的核心文件 (Active Core Files)
- `fixed_background_scraper.py` - 修正版背景爬蟲 (運行中)
- `monitor_fixed.py` - 修正版監控工具
- `start_fixed_scraper.sh` - 啟動腳本
- `stop_fixed_scraper.sh` - 停止腳本
- `app.py` - 前端應用
- `enhanced_api.py` - API後端

### 🟡 移動到備份目錄 (Move to Backup)
- `background_mass_scraper.py` - 舊版背景爬蟲
- `monitor_background.py` - 舊版監控
- `lu_benchmark_mass_scraper.py` - 基準爬蟲

### 🔴 建議移除的文件 (Recommended for Removal)

#### 測試文件 (Test Files)
- `test_singer_scraper.py`
- `debug_singer_scraper.py`  
- `test_connection.py`
- `quick_test_scraper.py`
- `test_other_companies.py`
- `quick_company_test.py`
- `test_jay_search.py`
- `test_new_system.py`
- `test_singer_limit.py`
- `independent_singer_test.py`

#### 分析工具 (Analysis Tools)
- `analysis_report.py`
- `tools_analysis_report.py`
- `website_search_analyzer.py`
- `viewstate_analyzer.py`
- `viewstate_decoder.py`
- `ajax_analyzer.py`
- `real_search_analyzer.py`
- `threading_analysis.py`
- `company_analyzer.py`

#### 實驗性爬蟲 (Experimental Scrapers)
- `ultimate_scraper.py`
- `browser_scraper.py`
- `taiwan_songking_api_crawler.py`
- `selective_scraper.py`
- `optimized_scraper.py`
- `multi_company_detector.py`
- `common_ktv_detector.py`

### 📁 JSON文件清理

#### 保留
- `public/singers_data.json` - 主資料庫
- `package.json`, `vercel.json` - 配置文件

#### 移動到備份
- `FINAL_singer_database_20250811_200210.json`
- `singers_data_before_cleaning_20250816_200044.json`
- `singers_data_backup_20250816_200211.json`
- 各種分析報告JSON

## 清理執行步驟

1. 創建 `archive/` 目錄存放歷史文件
2. 移動過期文件到歸檔
3. 刪除純測試文件
4. 清理臨時JSON文件
5. 整理目錄結構

## 清理後的目錄結構

```
karaoke-search/
├── 核心系統/
│   ├── fixed_background_scraper.py
│   ├── monitor_fixed.py
│   ├── app.py
│   └── enhanced_api.py
├── 工具腳本/
│   ├── start_fixed_scraper.sh
│   ├── stop_fixed_scraper.sh
│   └── data_growth_estimation.py
├── 資料/
│   └── public/singers_data.json
├── 備份/ (backup_old_data/)
└── 歸檔/ (archive/)
```