#!/bin/bash

# 檢查爬蟲進度
echo "🎵 卡拉OK爬蟲進度檢查"
echo "========================"

# 檢查歌曲數
if [[ -f "public/songs_simplified.json" ]]; then
    SONG_COUNT=$(python3 -c "import json; print(len(json.load(open('public/songs_simplified.json', 'r'))))" 2>/dev/null || echo "0")
    echo "📊 目前歌曲數: $SONG_COUNT 首"
else
    echo "📊 目前歌曲數: 0 首"
fi

# 檢查進程
echo ""
echo "🔄 進程狀態:"
ps aux | grep "advanced_scraper\|AdvancedKaraokeScraper" | grep -v grep | while read line; do
    echo "  ✅ 爬蟲運行中: $(echo $line | awk '{print $2}')"
done

if ! ps aux | grep -q "[A]dvancedKaraokeScraper"; then
    echo "  ❌ 爬蟲未運行"
else
    echo ""
    echo "🛑 要停止爬蟲請執行: ./stop_scraper.sh"
fi

echo ""
echo "📋 最新日誌 (最後10行):"
echo "------------------------"
if [[ -f "scraper.log" ]]; then
    tail -n 10 scraper.log
else
    echo "尚無日誌檔案"
fi