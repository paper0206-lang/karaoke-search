#!/bin/bash

# 歌手專用爬蟲執行腳本
echo "🎤 歌手專用爬蟲 - 無上限收集"
echo "======================================="

# 檢查現有資料
if [[ -f "public/singers_data.json" ]]; then
    SINGER_COUNT=$(python3 -c "import json; data = json.load(open('public/singers_data.json', 'r')); print(len(data))" 2>/dev/null || echo "0")
    echo "📊 目前已收錄歌手: $SINGER_COUNT 位"
else
    echo "📊 目前已收錄歌手: 0 位 (新建資料庫)"
fi

echo ""
echo "🎯 歌手爬蟲特色:"
echo "   ✅ 突破50首限制 - 多策略搜尋收集完整歌曲"
echo "   ✅ 搜尋所有卡拉OK公司 (錢櫃、好樂迪、銀櫃等)"
echo "   ✅ 三重搜尋策略 - 歌手名/部分字詞/不同類型"
echo "   ✅ 自動整理相同歌曲的不同編號"
echo "   ✅ 公司排序優先 (錢櫃→好樂迪→銀櫃→其他)"
echo ""

echo "📋 執行選項:"
echo "1. 互動模式 (手動選擇歌手)"
echo "2. 背景模式 (熱門歌手清單)"
echo "3. 單一歌手快速模式"
echo "4. 測試50首限制突破效果"

read -p "請選擇模式 (1/2/3/4): " mode

if [[ $mode == "1" ]]; then
    echo "🔧 啟動互動模式..."
    python3 singer_scraper.py
    
elif [[ $mode == "2" ]]; then
    echo "🚀 背景執行熱門歌手清單..."
    
    # 背景執行熱門歌手
    nohup python3 -c "
import sys
sys.path.append('.')
from singer_scraper import SingerScraper

# 熱門歌手清單
hot_singers = [
    '周杰倫', '蔡依林', '林俊傑', '張惠妹', '五月天', '鄧紫棋', 
    '林宥嘉', '田馥甄', '楊丞琳', '孫燕姿', '告五人', '茄子蛋',
    '持修', 'ØZI', '高爾宣', '張學友', '劉德華', '鄧麗君', 
    '蔡琴', '李宗盛', '伍佰', '張宇'
]

print('🎤 開始收集熱門歌手資料...')
scraper = SingerScraper(max_workers=2)
scraper.search_multiple_singers(hot_singers)
print('✅ 熱門歌手收集完成!')
" > singer_scraper.log 2>&1 &

    PID=$!
    echo "✅ 歌手爬蟲已在背景執行"
    echo "📋 進程ID: $PID"
    echo "📁 日誌檔案: singer_scraper.log"
    echo ""
    echo "🔍 監控指令:"
    echo "  查看進度: tail -f singer_scraper.log"
    echo "  停止爬蟲: kill $PID"

elif [[ $mode == "3" ]]; then
    read -p "請輸入歌手名稱: " singer_name
    if [[ -n "$singer_name" ]]; then
        echo "🎤 開始收集「$singer_name」的歌曲..."
        python3 -c "
import sys
sys.path.append('.')
from singer_scraper import SingerScraper

scraper = SingerScraper(max_workers=2)
songs = scraper.search_singer_comprehensive('$singer_name')
scraper.save_singer_data('$singer_name', songs)
print(f'✅ $singer_name 收集完成!')
"
    else
        echo "❌ 請輸入有效的歌手名稱"
    fi

elif [[ $mode == "4" ]]; then
    echo "🧪 執行50首限制突破測試..."
    python3 test_singer_limit.py
    
else
    echo "❌ 無效選擇"
fi

echo ""
echo "🌐 完成後可在歌手專區查看: https://karaoke-search-theta.vercel.app"