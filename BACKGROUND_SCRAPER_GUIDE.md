# 🔄 背景大規模爬蟲系統使用指南

## 📊 系統狀態

✅ **背景爬蟲已啟動並運行中**  
📊 **進程 PID**: 28009  
📁 **日誌文件**: `background_logs/nohup_20250816_221726.log`  
🎯 **處理目標**: 112位需要改進的歌手，分23批次處理

## 🎮 主要指令

### 基本控制
```bash
# 啟動背景爬蟲
./start_background_scraper.sh

# 停止背景爬蟲
./stop_background_scraper.sh

# 檢查背景爬蟲狀態
python3 monitor_background.py

# 連續監控模式 (每30秒更新)
python3 monitor_background.py --continuous
```

### 日誌查看
```bash
# 實時查看日誌
tail -f background_logs/nohup_20250816_221726.log

# 查看最新日誌文件
tail -f background_logs/*.log

# 檢查進程狀態
ps -p 28009
```

## 📊 當前進展

### 系統狀態
- **篩選階段**: ✅ 已完成 - 從200位歌手中找出112位需要改進
- **處理階段**: 🔄 進行中 - 第1/23批次
- **批次配置**: 每批5位歌手，批次間休息45秒
- **預估時間**: 約23 × 5分鐘 = 1.5-2小時完成

### 處理策略
1. **智能篩選**: 自動檢測需要改進的歌手（未達盧廣仲基準）
2. **批次處理**: 小批次避免長時間阻塞，每批次間休息
3. **檢查點保存**: 每處理5位歌手自動保存進度
4. **錯誤恢復**: 自動重試和優雅錯誤處理

## 🎯 監控要點

### 正常運行指標
- **進程狀態**: 顯示"運行中"
- **日誌活動**: 每3-5分鐘有新的處理記錄
- **檢查點更新**: 定期更新 `background_checkpoint.json`
- **批次進展**: 在 `mass_scraping_results/` 中生成批次報告

### 異常處理
- **進程停止**: 使用 `./start_background_scraper.sh` 重啟
- **網路問題**: 系統會自動重試，延長延遲時間
- **檢查點錯誤**: 已修復JSON序列化問題
- **記憶體不足**: 系統使用小批次和定期清理

## 📁 輸出文件結構

```
background_logs/          # 日誌文件
├── nohup_*.log          # 主日誌文件
└── background_scraper_*.log  # 詳細日誌

mass_scraping_results/    # 爬取結果
├── batch_*_progress.json # 批次進度報告
├── *_*.json             # 個別歌手結果
└── final_report_*.json  # 最終完成報告

background_checkpoint.json # 進度檢查點
background_scraper.pid    # 進程PID文件
```

## 🔧 高級操作

### 恢復和重啟
```bash
# 從檢查點恢復（預設）
./start_background_scraper.sh

# 重新開始（忽略檢查點）
python3 background_mass_scraper.py --fresh
```

### 自訂配置
編輯 `background_mass_scraper.py` 中的配置：
- `max_singers_per_session`: 每次會話處理上限（預設200）
- `batch_size`: 批次大小（預設5）
- `longer_delays`: 延遲時間（預設4-7秒）

### 進度分析
```bash
# 生成詳細進度報告
python3 progress_summary.py

# 檢查特定歌手狀態
python3 quick_benchmark_analyzer.py
```

## 🎉 預期成果

### 量化目標
- **處理歌手**: 112位歌手
- **預期改進**: 30-50位歌手達到盧廣仲基準
- **新增歌曲**: 估計500-1000首
- **基準達成率**: 目標40-60%

### 品質保證
- **盧廣仲基準**: 12首歌、16家KTV覆蓋
- **語言多樣性**: 國語、台語雙語平衡
- **數據完整性**: 自動去重和格式驗證

## ⚠️ 注意事項

### 系統要求
- **網路穩定**: 需要穩定的網路連線
- **磁碟空間**: 預留500MB存儲空間
- **執行時間**: 預計1.5-2小時完成

### 安全考慮
- **延遲控制**: 4-7秒延遲避免對目標網站造成壓力
- **錯誤處理**: 自動處理網路錯誤和連線問題
- **優雅關閉**: 支援SIGINT信號安全關閉

### 維護建議
- **定期檢查**: 每30分鐘檢查一次進度
- **日誌備份**: 重要日誌建議備份
- **結果驗證**: 完成後驗證資料庫更新

## 📞 故障排除

### 常見問題
1. **進程意外停止**: 檢查日誌，重新啟動
2. **網路連線問題**: 系統會自動重試
3. **記憶體不足**: 重啟系統並調小批次大小
4. **檢查點損壞**: 使用 `--fresh` 重新開始

### 緊急停止
```bash
# 優雅停止
./stop_background_scraper.sh

# 強制停止
kill -9 28009
rm -f background_scraper.pid
```

---

**背景爬蟲現已成功啟動並開始工作！**  
您可以安全地關閉終端，系統將在背景持續運行直到完成所有任務。

**建議**: 使用 `python3 monitor_background.py --continuous` 進行連續監控。