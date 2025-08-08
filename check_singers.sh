#!/bin/bash

# 檢查歌手資料庫狀態
echo "🎤 歌手資料庫狀態檢查"
echo "========================"

if [[ -f "public/singers_data.json" ]]; then
    # 統計資料
    SINGER_COUNT=$(python3 -c "import json; data = json.load(open('public/singers_data.json', 'r')); print(len(data))" 2>/dev/null || echo "0")
    TOTAL_SONGS=$(python3 -c "import json; data = json.load(open('public/singers_data.json', 'r')); total = sum(len(singer['歌曲清單']) for singer in data.values()); print(total)" 2>/dev/null || echo "0")
    
    echo "📊 資料庫統計:"
    echo "   歌手數量: $SINGER_COUNT 位"
    echo "   歌曲總數: $TOTAL_SONGS 首"
    echo "   平均每位歌手: $((TOTAL_SONGS / (SINGER_COUNT == 0 ? 1 : SINGER_COUNT))) 首歌"
    
    echo ""
    echo "🎤 已收錄歌手清單:"
    python3 -c "
import json
try:
    with open('public/singers_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    singers = []
    for singer_name, singer_data in data.items():
        song_count = len(singer_data.get('歌曲清單', []))
        update_time = singer_data.get('更新時間', '未知')
        singers.append((singer_name, song_count, update_time))
    
    # 按歌曲數量排序
    singers.sort(key=lambda x: x[1], reverse=True)
    
    for i, (name, count, time) in enumerate(singers, 1):
        print(f'  {i:2d}. {name:8s} - {count:3d} 首 ({time})')
        
except Exception as e:
    print(f'讀取失敗: {e}')
"
else
    echo "❌ 尚未建立歌手資料庫"
    echo "💡 執行以下指令開始收集歌手資料:"
    echo "   ./run_singer_scraper.sh"
fi

echo ""
echo "🔄 進程狀態:"
ps aux | grep "singer_scraper\|SingerScraper" | grep -v grep | while read line; do
    echo "  ✅ 歌手爬蟲運行中: $(echo $line | awk '{print $2}')"
done

if ! ps aux | grep -q "[s]inger_scraper"; then
    echo "  ❌ 歌手爬蟲未運行"
fi

# 檢查日誌
if [[ -f "singer_scraper.log" ]]; then
    echo ""
    echo "📋 最新日誌 (最後5行):"
    echo "------------------------"
    tail -n 5 singer_scraper.log
fi