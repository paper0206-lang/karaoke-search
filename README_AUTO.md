# 🤖 自動化卡拉OK資料庫更新系統

## 🚀 一鍵啟動

只需要執行一個命令，系統就會自動完成所有工作：

```bash
./start_auto_scraper.sh
```

## 📋 功能特色

- ✅ **完全自動化**: 爬取 → 儲存 → 提交 → 推送 → 部署
- ✅ **智能重試**: 遇到網路問題自動重試
- ✅ **進度追蹤**: 即時顯示爬取進度和統計
- ✅ **自動部署**: 推送到 GitHub 後 Vercel 自動更新網站
- ✅ **定時執行**: 可設定每日自動更新
- ✅ **日誌記錄**: 完整的操作記錄和錯誤追蹤

## 🎯 使用方式

### 方式一：立即執行
```bash
# 給腳本執行權限
chmod +x start_auto_scraper.sh

# 一鍵啟動
./start_auto_scraper.sh
```

### 方式二：直接背景執行
```bash
chmod +x auto_update_database.sh
nohup ./auto_update_database.sh > auto_update.log 2>&1 &
```

### 方式三：查看執行狀態
```bash
# 查看即時日誌
tail -f auto_update.log

# 檢查歌曲數量
python3 -c "import json; print('目前歌曲數:', len(json.load(open('public/songs_simplified.json', 'r'))))"
```

## 📊 執行流程

1. **檢查環境** → 確認在正確目錄
2. **記錄初始狀態** → 統計現有歌曲數量  
3. **執行爬蟲** → 自動搜尋新歌曲
4. **統計結果** → 計算新增歌曲數量
5. **Git 提交** → 自動提交變更到版本控制
6. **推送更新** → 自動推送到 GitHub
7. **觸發部署** → Vercel 自動更新網站
8. **完成報告** → 顯示詳細統計資訊

## 🔧 自訂設定

### 修改搜尋關鍵字
編輯 `quick_scraper.py` 中的 `search_terms` 列表

### 修改爬取間隔
編輯 `quick_scraper.py` 中的 `time.sleep()` 參數

### 修改提交訊息
編輯 `auto_update_database.sh` 中的 `COMMIT_MESSAGE` 變數

## 📱 監控和管理

### 查看背景程序
```bash
# 查看所有背景程序
ps aux | grep auto_update_database

# 停止特定程序
kill <PID>
```

### 管理定時任務
```bash
# 查看定時任務
crontab -l

# 編輯定時任務
crontab -e
```

## 🎵 預期結果

- **每次執行**: 通常增加 100-500 首新歌曲
- **執行時間**: 約 10-30 分鐘（取決於網路狀況）
- **自動部署**: 推送後 2-3 分鐘網站更新
- **網站更新**: https://karaoke-search-theta.vercel.app

## ⚠️ 注意事項

- 建議在網路穩定時執行
- 避免同時運行多個爬蟲實例
- 定期檢查日誌檔案大小
- 遇到錯誤會自動記錄並繼續執行

## 📞 故障排除

### 如果爬蟲失敗
```bash
# 檢查錯誤日誌
tail -n 50 auto_update.log

# 手動執行爬蟲
python3 quick_scraper.py
```

### 如果 Git 推送失敗
```bash
# 檢查 Git 狀態
git status

# 手動推送
git push
```

---

**🎤 現在你的卡拉OK資料庫會自動持續成長！**