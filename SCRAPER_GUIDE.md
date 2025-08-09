# 🚀 統一爬蟲執行指南

## 📋 快速開始

### 方法1: 自動化執行（推薦新手）
```bash
./auto_scraper.sh
```
**特色**:
- 🎯 4種爬取模式選擇
- 📊 自動顯示進度統計  
- 🔄 可選自動提交GitHub
- 🛡️ 內建錯誤處理

### 方法2: 直接執行統一爬蟲
```bash
python3 unified_scraper.py
```

### 方法3: 自訂參數執行
```bash
python3 -c "
from unified_scraper import UnifiedKaraokeScraper
keywords = ['周杰倫', '蔡依林', '2025新歌', '愛情', '思念']
scraper = UnifiedKaraokeScraper(max_workers=3)
result = scraper.scrape_with_keywords(keywords, max_songs_per_keyword=50)
print(f'✅ 完成！新增 {result} 首歌曲')
"
```

## 🔄 後台執行（長時間爬取）

### 啟動後台爬蟲
```bash
# 後台執行並記錄日誌
nohup python3 unified_scraper.py > scraper.log 2>&1 &

# 記住進程ID
echo $! > scraper.pid
echo "🚀 爬蟲已啟動，進程ID: $(cat scraper.pid)"
```

### 監控後台爬蟲
```bash
# 查看即時日誌
tail -f scraper.log

# 查看進程狀態  
ps -p $(cat scraper.pid)

# 檢查爬蟲是否還在運行
if ps -p $(cat scraper.pid) > /dev/null; then
    echo "🟢 爬蟲正在運行"
else
    echo "🔴 爬蟲已停止"
fi
```

### 停止後台爬蟲
```bash
# 優雅停止
kill $(cat scraper.pid)

# 強制停止
kill -9 $(cat scraper.pid)

# 或者停止所有爬蟲進程
pkill -f unified_scraper
```

## 📊 進度檢視方式

### 1. 基本進度檢查
```bash
./check_progress.sh
```

### 2. 即時監控（每5秒更新）
```bash
watch -n 5 ./check_progress.sh
```

### 3. 詳細統計查看
```bash
python3 -c "
import json
with open('public/unified_karaoke_db.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
print('📊 詳細統計:')
print(f'   總歌曲: {data[\"metadata\"][\"total_songs\"]:,}')
print(f'   總歌手: {data[\"metadata\"][\"total_singers\"]:,}') 
print(f'   公司數: {len(data[\"metadata\"][\"companies\"])}')
print(f'   更新時間: {data[\"metadata\"].get(\"last_updated\", \"未知\")}')

# 最新增加的歌曲
songs = data['songs']
recent_songs = [(id, info) for id, info in songs.items() 
                if '2025-08-09' in info.get('更新時間', '')]
print(f'   今日新增: {len(recent_songs)} 首')
"
```

### 4. 檔案大小監控
```bash
# 監控資料庫檔案大小變化
ls -lh public/*.json | grep -E "(unified_karaoke_db|songs_simplified|singers_data)"
```

## 🎛️ 爬蟲參數設定

### 基本參數
```python
scraper = UnifiedKaraokeScraper(
    max_workers=3        # 並行線程數 (1-5)
)
```

### 關鍵字設定
```python
# 預設智能關鍵字
keywords = [
    # 2025熱門
    "2025", "新歌", "熱門", "最新", 
    
    # 經典歌手  
    "周杰倫", "蔡依林", "林俊傑",
    
    # 情感主題
    "愛情", "思念", "青春", "夢想",
    
    # 音樂類型
    "抒情", "搖滾", "R&B", "民謠"
]

# 自訂爬取
result = scraper.scrape_with_keywords(keywords)
```

## 📈 進度指標說明

### 數據庫狀態
- **📚 總歌曲數**: 統一資料庫中的唯一歌曲數
- **🎤 總歌手數**: 索引中的歌手總數  
- **🏢 KTV公司**: 支援的卡拉OK公司數量
- **💾 檔案大小**: 統一資料庫檔案大小

### 進程監控
- **🟢 進程運行**: 爬蟲正在執行中
- **🔴 進程停止**: 爬蟲已結束
- **📄 日誌檔案**: 記錄爬蟲執行過程

## ⚡ 效能優化建議

### 1. 線程數設定
```bash
# 保守設定 (穩定但較慢)
max_workers=1-2

# 平衡設定 (推薦)
max_workers=3

# 激進設定 (快但可能被封鎖)
max_workers=4-5
```

### 2. 關鍵字策略
```python
# 高效關鍵字 (容易找到歌曲)
effective_keywords = ["愛", "心", "夢", "情", "周杰倫", "蔡依林"]

# 探索性關鍵字 (發現新歌手)  
discovery_keywords = ["2025", "新歌", "indie", "治癒系"]
```

### 3. 執行時機
```bash
# 建議在網路較穩定時執行
# 避免高峰時段 (晚上8-10點)
# 推薦時段: 早上9-11點, 下午2-5點
```

## 🚨 常見問題處理

### 1. 爬蟲卡住不動
```bash
# 檢查網路連線
ping song.corp.com.tw

# 重啟爬蟲
pkill -f unified_scraper
./auto_scraper.sh
```

### 2. 資料庫損壞
```bash
# 檢查檔案完整性
python3 -c "import json; json.load(open('public/unified_karaoke_db.json'))"

# 恢復備份
cp public/unified_karaoke_db.json.backup public/unified_karaoke_db.json
```

### 3. 記憶體不足
```bash
# 檢查記憶體使用
ps aux | grep python3 | head -5

# 降低並行數
max_workers=1
```

## 💡 最佳實踐

### 1. 定期執行
```bash
# 設定每天自動爬取
# 加入 crontab
0 9 * * * cd /path/to/karaoke-search && ./auto_scraper.sh
```

### 2. 備份策略
```bash
# 執行前備份
cp public/unified_karaoke_db.json public/unified_karaoke_db.json.backup

# 定期完整備份
tar -czf backup_$(date +%Y%m%d).tar.gz public/*.json
```

### 3. 監控自動化
```bash
# 設定監控腳本
watch -n 30 './check_progress.sh | tail -20'
```

## 📞 技術支援

遇到問題時的檢查順序:
1. 執行 `./check_progress.sh` 檢查狀態
2. 查看 `tail -f scraper.log` 檢查日誌
3. 確認網路連線 `ping song.corp.com.tw`
4. 檢查磁碟空間 `df -h`
5. 重新執行 `./auto_scraper.sh`