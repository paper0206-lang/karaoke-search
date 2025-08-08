#!/bin/bash

# 🤖 一鍵啟動自動爬蟲腳本
# 使用方法: ./start_auto_scraper.sh

echo "🎤 卡拉OK歌曲資料庫自動更新工具"
echo "=================================="

# 給腳本執行權限
chmod +x auto_update_database.sh

echo ""
echo "選擇執行模式:"
echo "1) 前台執行 (可看到即時輸出)"
echo "2) 背景執行 (在背景持續運行)"
echo "3) 定時執行 (設定每日自動執行)"
echo ""

read -p "請選擇 (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🚀 前台執行中，請勿關閉終端..."
        ./auto_update_database.sh
        ;;
    2)
        echo ""
        echo "🚀 啟動背景執行..."
        nohup ./auto_update_database.sh > auto_update.log 2>&1 &
        PID=$!
        echo "✅ 背景程序已啟動 (PID: $PID)"
        echo "📋 查看即時日誌: tail -f auto_update.log"
        echo "⏹️  停止程序: kill $PID"
        echo ""
        echo "等待 5 秒後顯示初始日誌..."
        sleep 5
        tail -n 10 auto_update.log
        ;;
    3)
        echo ""
        echo "📅 設定定時執行..."
        echo "將每天凌晨 2:00 自動執行爬蟲"
        
        # 獲取當前路徑
        CURRENT_PATH=$(pwd)
        CRON_JOB="0 2 * * * cd $CURRENT_PATH && ./auto_update_database.sh >> auto_update_cron.log 2>&1"
        
        # 檢查是否已經存在相同的 cron job
        if crontab -l 2>/dev/null | grep -q "$CURRENT_PATH.*auto_update_database.sh"; then
            echo "⚠️  定時任務已存在"
        else
            # 添加 cron job
            (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
            echo "✅ 定時任務設定完成！"
            echo "📋 查看所有定時任務: crontab -l"
            echo "🗑️  移除定時任務: crontab -e (然後刪除相關行)"
        fi
        
        echo ""
        echo "是否立即執行一次？ (y/n)"
        read -p "> " run_now
        if [[ $run_now == "y" || $run_now == "Y" ]]; then
            echo "🚀 立即執行中..."
            ./auto_update_database.sh
        fi
        ;;
    *)
        echo "❌ 無效選擇"
        exit 1
        ;;
esac

echo ""
echo "🎵 完成！你的卡拉OK資料庫將自動持續更新"
echo "🌐 網站: https://karaoke-search-theta.vercel.app"