#!/bin/bash

# 🚀 高級多線程爬蟲執行腳本
# 使用方法: ./run_advanced_scraper.sh

echo "🎤 高級多線程卡拉OK歌曲爬蟲"
echo "======================================"

# 顯示目前狀態
echo "📊 目前狀態:"
if [[ -f "public/songs_simplified.json" ]]; then
    CURRENT_COUNT=$(python3 -c "import json; print(len(json.load(open('public/songs_simplified.json', 'r'))))" 2>/dev/null || echo "0")
    echo "   目前歌曲數: $CURRENT_COUNT 首"
else
    CURRENT_COUNT=0
    echo "   目前歌曲數: 0 首 (新建資料庫)"
fi

echo ""
echo "🎯 高級爬蟲特色:"
echo "   ✅ 智能關鍵字生成 (歌手+主題+組合+常用字)"
echo "   ✅ 多線程並行搜尋 (避免被阻擋)"  
echo "   ✅ 自動進度儲存"
echo "   ✅ 統計分析功能"
echo ""

echo "⚙️ 建議設定:"
echo "   線程數: 3 (平衡速度與穩定性)"
echo "   目標數: 15000 首歌曲"
echo "   預計耗時: 2-4 小時"
echo ""

read -p "是否使用建議設定快速開始？(y/n): " quick_start

if [[ $quick_start == "y" || $quick_start == "Y" ]]; then
    echo ""
    echo "🚀 使用建議設定啟動..."
    echo "   線程數: 3"
    echo "   目標數: 15000"
    echo ""
    
    # 使用建議設定執行
    python3 -c "
import sys
sys.path.append('.')
from advanced_scraper import AdvancedKaraokeScraper

scraper = AdvancedKaraokeScraper(max_workers=3, max_songs=15000)
scraper.run_scraper()
"
else
    echo ""
    echo "🔧 自訂模式啟動..."
    python3 advanced_scraper.py
fi

echo ""
echo "✅ 爬蟲執行完畢!"
echo "📊 查看統計: ./check_songs.sh"
echo "🌐 網站: https://karaoke-search-theta.vercel.app"

# 詢問是否自動提交到GitHub
echo ""
read -p "是否自動提交更新到GitHub？(y/n): " auto_commit

if [[ $auto_commit == "y" || $auto_commit == "Y" ]]; then
    echo "🤖 自動提交到GitHub..."
    
    NEW_COUNT=$(python3 -c "import json; print(len(json.load(open('public/songs_simplified.json', 'r'))))" 2>/dev/null || echo "0")
    ADDED_COUNT=$((NEW_COUNT - CURRENT_COUNT))
    
    git add public/songs_simplified.json
    git commit -m "高級爬蟲更新: 新增 $ADDED_COUNT 首歌曲

- 使用智能關鍵字生成策略
- 多線程並行搜尋
- 目前總計: $NEW_COUNT 首歌曲
- 新增歌曲: $ADDED_COUNT 首

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
    
    git push
    echo "✅ 更新已推送，網站將在2-3分鐘內更新"
fi