#!/bin/bash

# 自動爬蟲腳本 - 使用統一資料庫架構
echo "🚀 統一架構自動爬蟲系統"
echo "自動使用新的unified_scraper.py進行爬取"
echo "======================================="

# 檢查統一資料庫是否存在
if [[ ! -f "public/unified_karaoke_db.json" ]]; then
    echo "❌ 統一資料庫不存在，請先執行 python3 database_unifier.py"
    exit 1
fi

echo "📊 當前資料庫狀態:"
python3 -c "
import json
try:
    with open('public/unified_karaoke_db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'   歌曲數量: {data[\"metadata\"][\"total_songs\"]:,}')
    print(f'   歌手數量: {data[\"metadata\"][\"total_singers\"]:,}')
    print(f'   KTV公司: {len(data[\"metadata\"][\"companies\"])}家')
    print(f'   上次更新: {data[\"metadata\"].get(\"last_updated\", \"未知\")}')
except Exception as e:
    print(f'   ❌ 讀取失敗: {e}')
"

echo ""
echo "🎯 爬蟲選項 (歌手優先策略):"
echo "1. 快速歌手爬取 (前10位天王天后，突破50首限制)"
echo "2. 標準歌手爬取 (前20位優先歌手，完整作品收錄)" 
echo "3. 深度歌手爬取 (40位精選歌手，全面覆蓋)"
echo "4. 傳統關鍵字爬取 (使用關鍵字搜尋)"
echo "5. 自訂歌手爬取"
echo "0. 退出"

read -p "請選擇 (0-5): " choice

case $choice in
    1)
        SCRAPER_MODE="singer"
        SINGER_COUNT=10
        DESCRIPTION="快速歌手爬取 (前10位)"
        ;;
    2)
        SCRAPER_MODE="singer"
        SINGER_COUNT=20
        DESCRIPTION="標準歌手爬取 (前20位)"
        ;;
    3)
        SCRAPER_MODE="singer"
        SINGER_COUNT=40
        DESCRIPTION="深度歌手爬取 (前40位)"
        ;;
    4)
        SCRAPER_MODE="keyword"
        KEYWORDS_COUNT=200
        DESCRIPTION="傳統關鍵字爬取"
        ;;
    5)
        SCRAPER_MODE="custom_singer"
        read -p "請輸入歌手名稱 (用逗號分隔): " custom_singers
        DESCRIPTION="自訂歌手爬取"
        ;;
    0)
        echo "👋 已退出"
        exit 0
        ;;
    *)
        echo "❌ 無效選擇"
        exit 1
        ;;
esac

echo ""
echo "📋 準備執行: $DESCRIPTION"
if [[ $SCRAPER_MODE == "singer" ]]; then
    echo "⏱️  預估時間: $((SINGER_COUNT * 3)) 分鐘"
    echo "🎯 突破50首限制: 使用5種策略深度挖掘每位歌手"
elif [[ $SCRAPER_MODE == "keyword" ]]; then
    echo "⏱️  預估時間: $((KEYWORDS_COUNT / 20)) 分鐘"
elif [[ $SCRAPER_MODE == "custom_singer" ]]; then
    echo "⏱️  預估時間: 視歌手數量而定 (約每位3分鐘)"
fi

read -p "確定開始嗎？(y/n): " confirm

if [[ $confirm != "y" && $confirm != "Y" ]]; then
    echo "❌ 已取消"
    exit 0
fi

echo ""
echo "🚀 開始自動爬取..."
START_TIME=$(date)

# 執行對應的爬蟲
if [[ $SCRAPER_MODE == "singer" ]]; then
    # 歌手優先爬取
    python3 -c "
from singer_focused_scraper import SingerFocusedScraper

# 優先歌手列表
priority_singers = [
    '周杰倫', '蔡依林', '林俊傑', '張惠妹', '五月天',
    '孫燕姿', '梁靜茹', '王力宏', '陶喆', '鄧紫棋',
    '張學友', '劉德華', '郭富城', '黎明', '張國榮',
    '梅艷芳', '鄧麗君', '蔡琴', '鳳飛飛', '費玉清',
    '告五人', '茄子蛋', '持修', 'ØZI', '高爾宣',
    'LEO王', '9m88', '吳卓源', '血肉果汁機', '理想混蛋',
    '蘇打綠', '信樂團', 'F.I.R', '八三夭', '滅火器',
    '四分衛', '黑色柳丁', '董事長樂團', '脫拉庫', '1976'
]

target_singers = priority_singers[:$SINGER_COUNT]
scraper = SingerFocusedScraper(max_workers=2)
result = scraper.scrape_singers_batch(target_singers, save_frequency=3)
print(f'\\n🎉 $DESCRIPTION 完成，新增 {result} 首歌曲')
"

elif [[ $SCRAPER_MODE == "custom_singer" ]]; then
    # 自訂歌手爬取
    python3 -c "
from singer_focused_scraper import SingerFocusedScraper
singers = [s.strip() for s in '$custom_singers'.split(',') if s.strip()]
scraper = SingerFocusedScraper(max_workers=2)
result = scraper.scrape_singers_batch(singers, save_frequency=2)
print(f'\\n🎉 自訂歌手爬取完成，新增 {result} 首歌曲')
"

elif [[ $SCRAPER_MODE == "keyword" ]]; then
    # 傳統關鍵字爬取
    python3 -c "
from unified_scraper import UnifiedKaraokeScraper

keywords_2025 = [
    '2025', '新歌', '熱門', '最新', '流行',
    '周杰倫', '蔡依林', '林俊傑', '張惠妹', '五月天',
    '愛情', '思念', '青春', '夢想', '快樂', '傷心',
    '你', '我', '愛', '心', '夜', '夢', '情', '花',
    '抒情', '搖滾', '民謠', 'R&B', '國語', '台語'
]

import random
all_keywords = keywords_2025 * 8
random.shuffle(all_keywords)
selected_keywords = all_keywords[:$KEYWORDS_COUNT]

scraper = UnifiedKaraokeScraper(max_workers=3)
result = scraper.scrape_with_keywords(selected_keywords)
print(f'\\n🎉 傳統關鍵字爬取完成，新增 {result} 首歌曲')
"
fi

END_TIME=$(date)

echo ""
echo "🎉 爬取完成!"
echo "================================"
echo "⏰ 時間統計:"
echo "   開始時間: $START_TIME"
echo "   結束時間: $END_TIME"

# 顯示最新統計
echo ""
echo "📊 最新資料庫狀態:"
python3 -c "
import json
try:
    with open('public/unified_karaoke_db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'   歌曲數量: {data[\"metadata\"][\"total_songs\"]:,}')
    print(f'   歌手數量: {data[\"metadata\"][\"total_singers\"]:,}')
    print(f'   KTV公司: {len(data[\"metadata\"][\"companies\"])}家')
    print(f'   檔案大小: {len(json.dumps(data))/1024/1024:.1f}MB')
except Exception as e:
    print(f'   ❌ 讀取失敗: {e}')
"

echo ""
echo "💡 建議操作:"
echo "1. 檢查資料: ls -lh public/*.json"
echo "2. 測試前端: 打開網站確認搜尋功能"
echo "3. 提交更新: git add . && git commit -m '統一爬蟲更新'"

# 詢問是否自動提交
read -p "是否自動提交到GitHub？(y/n, 預設n): " auto_commit

if [[ $auto_commit == "y" || $auto_commit == "Y" ]]; then
    echo "🤖 自動提交資料到GitHub..."
    
    git add public/unified_karaoke_db.json public/songs_simplified.json public/singers_data.json
    git commit -m "統一架構爬蟲更新: $DESCRIPTION

📊 爬取統計:
- 爬取類型: $DESCRIPTION
- 執行時間: 從 $START_TIME 開始

🎯 架構優勢:
- 統一資料庫管理
- 消除資料重複
- 多重索引支援
- 完整相容性檔案

⏰ 執行時間: $END_TIME

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
    
    git push
    echo "✅ 資料已推送，網站將在2-3分鐘內更新"
    echo "🌐 查看結果: https://karaoke-search-theta.vercel.app"
fi

echo ""
echo "✨ 統一架構爬蟲系統執行完成！"