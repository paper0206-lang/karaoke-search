#!/bin/bash

echo "🛑 正在停止卡拉OK爬蟲..."

# 查找並終止所有相關進程
PIDS=$(ps aux | grep -E "(advanced_scraper|AdvancedKaraokeScraper)" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "❌ 沒有找到運行中的爬蟲進程"
else
    echo "📋 找到以下進程："
    ps aux | grep -E "(advanced_scraper|AdvancedKaraokeScraper)" | grep -v grep
    echo ""
    
    for PID in $PIDS; do
        echo "🔪 終止進程 $PID"
        kill -TERM $PID
        sleep 2
        
        # 如果進程還在運行，強制終止
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚡ 強制終止進程 $PID"
            kill -KILL $PID
        fi
    done
    
    echo "✅ 爬蟲已停止"
fi

# 顯示目前狀態
echo ""
echo "📊 最後狀態:"
if [[ -f "public/songs_simplified.json" ]]; then
    SONG_COUNT=$(python3 -c "import json; print(len(json.load(open('public/songs_simplified.json', 'r'))))" 2>/dev/null || echo "0")
    echo "   目前歌曲數: $SONG_COUNT 首"
fi

if [[ -f "scraper.log" ]]; then
    echo "📝 最後幾行日誌:"
    tail -n 5 scraper.log
fi