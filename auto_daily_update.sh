#!/bin/bash

# 每日自動更新爬蟲腳本
echo "🤖 每日自動更新開始 - $(date)"
echo "=================================="

# 記錄開始時間
START_TIME=$(date)
LOG_FILE="auto_update_$(date +%Y%m%d).log"

# 重定向所有輸出到日誌檔案
exec 1> >(tee -a "$LOG_FILE")
exec 2>&1

# 檢查當前歌曲數
CURRENT_COUNT=0
if [[ -f "public/songs_simplified.json" ]]; then
    CURRENT_COUNT=$(python3 -c "import json; print(len(json.load(open('public/songs_simplified.json', 'r'))))" 2>/dev/null || echo "0")
    echo "📊 目前歌曲數: $CURRENT_COUNT 首"
else
    echo "📊 目前歌曲數: 0 首 (新建資料庫)"
fi

# 檢查是否有網路連接
if ! ping -c 1 song.corp.com.tw &> /dev/null; then
    echo "❌ 無法連接到台灣點歌王，跳過此次更新"
    exit 1
fi

echo "✅ 網路連接正常，開始自動爬蟲..."

# 自動執行爬蟲 (使用建議設定)
echo "🚀 執行自動爬蟲 (3線程, 目標15000首)..."
timeout 7200 python3 -c "
import sys
sys.path.append('.')
from advanced_scraper import AdvancedKaraokeScraper

print('🎤 自動爬蟲開始...')
scraper = AdvancedKaraokeScraper(max_workers=3, max_songs=15000)
scraper.run_scraper()
print('✅ 自動爬蟲完成!')
" || echo "⚠️ 爬蟲可能因超時而中斷 (2小時限制)"

# 檢查新的歌曲數
NEW_COUNT=0
if [[ -f "public/songs_simplified.json" ]]; then
    NEW_COUNT=$(python3 -c "import json; print(len(json.load(open('public/songs_simplified.json', 'r'))))" 2>/dev/null || echo "0")
fi

ADDED_COUNT=$((NEW_COUNT - CURRENT_COUNT))

echo ""
echo "📊 更新統計:"
echo "   原有歌曲: $CURRENT_COUNT 首"
echo "   更新後: $NEW_COUNT 首" 
echo "   新增: $ADDED_COUNT 首"

# 自動提交更新 (如果有新歌曲)
if [[ $ADDED_COUNT -gt 0 ]]; then
    echo "🤖 發現新歌曲，自動提交到GitHub..."
    
    # 檢查 git 狀態
    if git status --porcelain | grep -q "public/songs_simplified.json"; then
        git add public/songs_simplified.json
        
        git commit -m "每日自動更新: 新增 $ADDED_COUNT 首歌曲

📊 統計資訊:
- 原有歌曲: $CURRENT_COUNT 首
- 更新後歌曲: $NEW_COUNT 首  
- 新增歌曲: $ADDED_COUNT 首

🕐 更新時間: $(date '+%Y-%m-%d %H:%M:%S')
🤖 自動爬蟲執行時間: 從 $START_TIME 開始

✨ 使用智能關鍵字生成策略
🔄 多線程並行搜尋 (3線程)
🎯 2025年新歌優先收錄

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
        
        # 推送到遠端
        if git push; then
            echo "✅ 成功推送到GitHub，網站將在2-3分鐘內更新"
            
            # 發送更新通知 (可選)
            echo "🌐 網站更新: https://karaoke-search-theta.vercel.app"
            echo "📊 新增歌曲: $ADDED_COUNT 首"
        else
            echo "❌ 推送失敗，請檢查網路連接或權限設定"
        fi
    else
        echo "ℹ️ 歌曲檔案沒有變更，跳過 git 提交"
    fi
else
    echo "ℹ️ 沒有發現新歌曲 ($ADDED_COUNT)，跳過 git 提交"
fi

# 清理舊日誌檔案 (保留最近7天)
find . -name "auto_update_*.log" -mtime +7 -delete 2>/dev/null

echo ""
echo "🎉 每日自動更新完成 - $(date)"
echo "📋 詳細日誌: $LOG_FILE"