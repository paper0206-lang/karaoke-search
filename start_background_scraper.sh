#!/bin/bash

# 背景爬蟲啟動腳本
# 使用 nohup 確保背景運行，即使終端關閉也能繼續

echo "🚀 啟動背景大規模爬蟲系統"
echo "=========================="

# 檢查Python環境
if ! command -v python3 &> /dev/null; then
    echo "❌ 找不到 python3"
    exit 1
fi

# 創建日誌目錄
mkdir -p background_logs
mkdir -p mass_scraping_results

# 獲取當前時間戳
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 設置日誌文件
LOG_FILE="background_logs/nohup_${TIMESTAMP}.log"
PID_FILE="background_scraper.pid"

# 檢查是否已有進程在運行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  已有背景爬蟲在運行 (PID: $OLD_PID)"
        echo "請先停止現有進程: ./stop_background_scraper.sh"
        exit 1
    else
        echo "🧹 清理舊的PID文件"
        rm -f "$PID_FILE"
    fi
fi

# 啟動背景進程
echo "📁 日誌文件: $LOG_FILE"
echo "🔄 啟動中..."

nohup python3 background_mass_scraper.py > "$LOG_FILE" 2>&1 &
SCRAPER_PID=$!

# 保存PID
echo $SCRAPER_PID > "$PID_FILE"

echo "✅ 背景爬蟲已啟動"
echo "📊 進程 PID: $SCRAPER_PID"
echo "📄 日誌追蹤: tail -f $LOG_FILE"
echo "🛑 停止命令: ./stop_background_scraper.sh"
echo ""
echo "🎯 實用指令:"
echo "   監控進度: python3 monitor_background.py"
echo "   查看日誌: tail -f $LOG_FILE"
echo "   檢查狀態: ps -p $SCRAPER_PID"
echo ""
echo "⚠️  注意: 此進程將在背景持續運行，即使關閉終端也不會停止"