#!/bin/bash

# 爬蟲進度檢查腳本
echo "📊 統一資料庫進度檢查"
echo "======================="

# 檢查統一資料庫
if [[ -f "public/unified_karaoke_db.json" ]]; then
    echo "📈 統一資料庫狀態:"
    python3 -c "
import json
from datetime import datetime

try:
    with open('public/unified_karaoke_db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f'   📚 總歌曲數: {data[\"metadata\"][\"total_songs\"]:,}')
    print(f'   🎤 總歌手數: {data[\"metadata\"][\"total_singers\"]:,}')
    print(f'   🏢 KTV公司: {len(data[\"metadata\"][\"companies\"])} 家')
    print(f'   📅 建立時間: {data[\"metadata\"].get(\"created\", \"未知\")}')
    print(f'   🔄 更新時間: {data[\"metadata\"].get(\"last_updated\", \"未知\")}')
    print(f'   💾 檔案大小: {len(json.dumps(data))/1024/1024:.2f} MB')
    
    # 顯示歌手排行榜
    print(f'\\n🏆 歌曲數排行榜 (前10位):')
    singer_counts = [(singer, len(songs)) for singer, songs in data['indexes']['by_singer'].items()]
    singer_counts.sort(key=lambda x: x[1], reverse=True)
    for i, (singer, count) in enumerate(singer_counts[:10], 1):
        print(f'   {i:2d}. {singer:10s}: {count:3d} 首')
    
    # 顯示公司分布
    print(f'\\n🏢 KTV公司分布:')
    company_counts = [(company, len(songs)) for company, songs in data['indexes']['by_company'].items()]
    company_counts.sort(key=lambda x: x[1], reverse=True)
    for company, count in company_counts[:8]:
        print(f'   {company:8s}: {count:,} 首')
        
except Exception as e:
    print(f'   ❌ 讀取失敗: {e}')
"
else
    echo "❌ 統一資料庫不存在"
fi

echo ""

# 檢查相容性檔案
echo "📋 相容性檔案狀態:"
for file in "public/songs_simplified.json" "public/singers_data.json"; do
    if [[ -f "$file" ]]; then
        SIZE=$(ls -lh "$file" | awk '{print $5}')
        COUNT=$(python3 -c "import json; data=json.load(open('$file')); print(len(data))" 2>/dev/null || echo "?")
        echo "   ✅ $(basename $file): $SIZE ($COUNT 筆記錄)"
    else
        echo "   ❌ $(basename $file): 不存在"
    fi
done

echo ""

# 檢查爬蟲進程
echo "🔄 爬蟲進程檢查:"
SCRAPER_PROCESSES=$(ps aux | grep -E "(unified_scraper|advanced_scraper|singer_scraper)" | grep -v grep | wc -l)
if [[ $SCRAPER_PROCESSES -gt 0 ]]; then
    echo "   🟢 發現 $SCRAPER_PROCESSES 個爬蟲進程正在運行"
    ps aux | grep -E "(unified_scraper|advanced_scraper|singer_scraper)" | grep -v grep | while read line; do
        echo "   👉 $line"
    done
else
    echo "   🔴 沒有爬蟲進程正在運行"
fi

echo ""

# 檢查日誌檔案
echo "📝 日誌檔案:"
for log_file in "scraper.log" "scraper_*.log" "*.log"; do
    if ls $log_file 1> /dev/null 2>&1; then
        for file in $log_file; do
            if [[ -f "$file" ]]; then
                SIZE=$(ls -lh "$file" | awk '{print $5}')
                LINES=$(wc -l < "$file")
                echo "   📄 $file: $SIZE ($LINES 行)"
            fi
        done
        break
    fi
done

# 如果沒有日誌檔案
if ! ls *.log 1> /dev/null 2>&1; then
    echo "   ℹ️  沒有找到日誌檔案"
fi

echo ""
echo "💡 常用指令:"
echo "   即時監控: watch -n 5 ./check_progress.sh"
echo "   查看日誌: tail -f scraper.log"
echo "   執行爬蟲: ./auto_scraper.sh"
echo "   停止爬蟲: pkill -f unified_scraper"