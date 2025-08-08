#!/bin/bash

# 🚀 一鍵執行爬蟲工具
# 使用方法: ./run_scraper.sh [選項]

echo "🎤 一鍵執行卡拉OK爬蟲"
echo "===================="

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
echo "🎯 選擇爬蟲類型:"
echo "1) 🎵 新歌爬蟲 (專攻2024流行音樂) - 預計+200-500首"
echo "2) 🎶 一般爬蟲 (經典+新歌混合) - 預計+500-1000首"  
echo "3) 🎼 大型爬蟲 (全面搜尋) - 預計+1000-3000首"
echo "4) 📊 只查看統計 (不執行爬蟲)"
echo ""

read -p "請選擇 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🎵 執行新歌專用爬蟲..."
        echo "⏱️  預計執行時間: 15-30分鐘"
        echo "🎯 目標: 收集2024年最新流行歌曲"
        echo ""
        read -p "確定要開始嗎? (y/n): " confirm
        if [[ $confirm == "y" || $confirm == "Y" ]]; then
            python3 new_songs_scraper.py
            
            # 自動提交
            echo ""
            echo "🤖 自動提交更新到 GitHub..."
            git add public/songs_simplified.json
            git commit -m "新歌爬蟲更新: 新增2024流行歌曲"
            git push
            echo "✅ 更新已推送，網站將在2-3分鐘內更新"
        fi
        ;;
    2)
        echo ""
        echo "🎶 執行一般混合爬蟲..."
        echo "⏱️  預計執行時間: 30-60分鐘"  
        echo "🎯 目標: 收集經典與新歌混合"
        echo ""
        read -p "確定要開始嗎? (y/n): " confirm
        if [[ $confirm == "y" || $confirm == "Y" ]]; then
            python3 quick_scraper.py
            
            # 自動提交
            echo ""
            echo "🤖 自動提交更新到 GitHub..."
            git add public/songs_simplified.json
            git commit -m "一般爬蟲更新: 新增經典與流行歌曲"
            git push
            echo "✅ 更新已推送，網站將在2-3分鐘內更新"
        fi
        ;;
    3)
        echo ""
        echo "🎼 執行大型全面爬蟲..."
        echo "⏱️  預計執行時間: 1-3小時"
        echo "🎯 目標: 全面收集，目標10,000首歌曲"
        echo ""
        read -p "確定要開始嗎? 這將花費較長時間 (y/n): " confirm
        if [[ $confirm == "y" || $confirm == "Y" ]]; then
            echo "選擇執行方式:"
            echo "1) 前台執行 (可看到進度)"
            echo "2) 背景執行 (在背景運行)"
            read -p "選擇 (1-2): " mode
            
            if [[ $mode == "1" ]]; then
                python3 continuous_scraper.py
            else
                nohup python3 continuous_scraper.py > continuous.log 2>&1 &
                PID=$!
                echo "✅ 背景程序已啟動 (PID: $PID)"
                echo "📋 查看進度: tail -f continuous.log" 
                echo "⏹️  停止程序: kill $PID"
            fi
        fi
        ;;
    4)
        echo ""
        python3 scraper_stats.py
        ;;
    *)
        echo "❌ 無效選擇"
        exit 1
        ;;
esac

echo ""
echo "🌐 網站: https://karaoke-search-theta.vercel.app"
echo "📊 查看統計: ./check_songs.sh"