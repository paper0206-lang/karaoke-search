#!/bin/bash

# 背景執行高級爬蟲 - 2025年優化版
echo "🚀 啟動2025年優化背景爬蟲..."
echo "🎵 優先搜尋2025年新歌和熱門藝人"

# 使用 nohup 在背景執行，輸出到 log 檔案
nohup python3 -c "
import sys
sys.path.append('.')
from advanced_scraper import AdvancedKaraokeScraper

print('🎤 背景爬蟲啟動...')
scraper = AdvancedKaraokeScraper(max_workers=3, max_songs=15000)
scraper.run_scraper()
print('✅ 背景爬蟲完成!')
" > scraper.log 2>&1 &

PID=$!
echo "✅ 爬蟲已在背景執行"
echo "📋 進程ID: $PID"
echo "📁 日誌檔案: scraper.log"
echo ""
echo "🔍 監控指令:"
echo "  查看進度: tail -f scraper.log"
echo "  查看歌曲數: python3 -c \"import json; print(f'目前歌曲數: {len(json.load(open(\"public/songs_simplified.json\")))}')\" 2>/dev/null || echo '讀取中...'"
echo "  停止爬蟲: kill $PID"
echo ""
echo "🌐 完成後網站將自動更新: https://karaoke-search-theta.vercel.app"