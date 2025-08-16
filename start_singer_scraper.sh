#!/bin/bash
# 歌手關鍵字爬蟲啟動腳本

echo "🎵 歌手關鍵字搜尋爬蟲管理工具"
echo "======================================"

# 檢查 Python 環境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安裝"
    exit 1
fi

# 選單
echo "請選擇操作:"
echo "1. 🚀 啟動歌手搜尋爬蟲"
echo "2. 📊 檢查爬蟲狀態"  
echo "3. 🔄 持續監控模式"
echo "4. 🛑 停止正在運行的爬蟲"
echo "5. 📋 檢查進度檔案"
echo "6. 🗑️ 清理暫存檔案"

read -p "請輸入選項 (1-6): " choice

case $choice in
    1)
        echo "🚀 啟動歌手搜尋爬蟲..."
        python3 singer_keyword_scraper.py
        ;;
    2)
        echo "📊 檢查爬蟲狀態..."
        python3 singer_scraper_monitor.py
        ;;
    3)
        echo "🔄 啟動持續監控模式..."
        python3 singer_scraper_monitor.py --monitor
        ;;
    4)
        echo "🛑 停止爬蟲進程..."
        pkill -f "singer_keyword_scraper.py"
        echo "✅ 爬蟲已停止"
        ;;
    5)
        echo "📋 檢查進度檔案..."
        if [ -f "singer_search_progress.json" ]; then
            echo "進度檔案存在"
            cat singer_search_progress.json | python3 -m json.tool
        else
            echo "❌ 進度檔案不存在"
        fi
        ;;
    6)
        echo "🗑️ 清理暫存檔案..."
        rm -f singer_scraper_*.log
        rm -f *.pyc
        echo "✅ 清理完成"
        ;;
    *)
        echo "❌ 無效選項"
        exit 1
        ;;
esac