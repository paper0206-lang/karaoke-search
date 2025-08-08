#!/bin/bash

# 🎵 快速查詢歌曲總量工具
# 使用方法: ./check_songs.sh

echo "🎤 卡拉OK資料庫快速查詢"
echo "======================"

if [[ -f "public/songs_simplified.json" ]]; then
    # 顯示歌曲總數
    SONG_COUNT=$(python3 -c "import json; print(len(json.load(open('public/songs_simplified.json', 'r'))))" 2>/dev/null)
    echo "🎵 目前歌曲總數: $SONG_COUNT 首"
    
    # 顯示檔案大小
    FILE_SIZE=$(ls -lh public/songs_simplified.json | awk '{print $5}')
    echo "💾 資料庫大小: $FILE_SIZE"
    
    # 顯示最後更新時間
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        LAST_MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" public/songs_simplified.json 2>/dev/null)
    else
        # Linux
        LAST_MODIFIED=$(stat -c "%y" public/songs_simplified.json 2>/dev/null | cut -d. -f1)
    fi
    echo "🕐 最後更新: $LAST_MODIFIED"
    
    # 顯示增長目標
    TARGET=10000
    REMAINING=$((TARGET - SONG_COUNT))
    PROGRESS=$((SONG_COUNT * 100 / TARGET))
    
    echo ""
    echo "📊 進度統計:"
    echo "   目標歌曲: $TARGET 首"
    echo "   已收集: $SONG_COUNT 首"
    echo "   剩餘: $REMAINING 首"
    echo "   完成度: $PROGRESS%"
    
    # 進度條
    FILLED=$((PROGRESS / 2))
    BAR=""
    for i in $(seq 1 $FILLED); do BAR="$BAR█"; done
    for i in $(seq $FILLED 49); do BAR="$BAR░"; done
    echo "   [$BAR] $PROGRESS%"
    
else
    echo "❌ 找不到歌曲資料檔案"
    echo "請先執行爬蟲程式建立資料庫"
fi

echo ""
echo "🛠️  可用操作:"
echo "1) 執行爬蟲: ./start_auto_scraper.sh"
echo "2) 詳細統計: python3 scraper_stats.py"  
echo "3) 系統監控: ./monitor_scraper.sh"
echo "4) 查看網站: https://karaoke-search-theta.vercel.app"