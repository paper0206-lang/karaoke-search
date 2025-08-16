#!/bin/bash

# 優化版背景爬蟲啟動腳本

echo "🚀 啟動優化版背景大規模爬蟲系統"
echo "================================"

# 檢查Python環境
if ! command -v python3 &> /dev/null; then
    echo "❌ 找不到 python3"
    exit 1
fi

# 創建日誌目錄
mkdir -p optimized_logs
mkdir -p optimized_scraping_results

# 獲取當前時間戳
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 設置日誌文件
LOG_FILE="optimized_logs/nohup_${TIMESTAMP}.log"
PID_FILE="optimized_scraper.pid"

# 檢查是否已有進程在運行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  已有優化版爬蟲在運行 (PID: $OLD_PID)"
        echo "請先停止現有進程: ./stop_optimized_scraper.sh"
        exit 1
    else
        echo "🧹 清理舊的PID文件"
        rm -f "$PID_FILE"
    fi
fi

# 檢查Git狀態
echo "🔍 檢查Git狀態..."
if ! git status &> /dev/null; then
    echo "❌ 不在Git倉庫中，無法使用自動推送功能"
    echo "請確認您在正確的Git目錄中"
    exit 1
fi

# 檢查是否有未提交的singers_data.json更改
if git status --porcelain | grep -q "public/singers_data.json"; then
    echo "⚠️  發現public/singers_data.json有未提交的更改"
    echo "建議先手動提交或重置這些更改"
    echo "繼續執行將自動處理這些更改..."
fi

# 啟動背景進程
echo "📁 日誌文件: $LOG_FILE"
echo "🔄 啟動中..."

nohup python3 optimized_background_scraper.py > "$LOG_FILE" 2>&1 &
SCRAPER_PID=$!

# 保存PID
echo $SCRAPER_PID > "$PID_FILE"

echo "✅ 優化版背景爬蟲已啟動"
echo "📊 進程 PID: $SCRAPER_PID"
echo "📄 日誌追蹤: tail -f $LOG_FILE"
echo "🛑 停止命令: ./stop_optimized_scraper.sh"
echo ""
echo "🚀 優化項目:"
echo "   ✅ 並行處理: 2線程同時爬取"
echo "   ✅ 延遲優化: 2.0-4.0秒 (降低50%)"
echo "   ✅ 批次提升: 10位/批次"
echo "   ✅ 會話擴大: 1000位/會話"
echo "   ✅ Git優化: 每50位推送"
echo "   ✅ 智能排序: 按基準分數優先"
echo ""
echo "⚡ 預估效能:"
echo "   速度提升: 2-3倍"
echo "   預估完成: 2.8-4.5天"
echo "   高優先級歌手優先處理"
echo ""
echo "🎯 實用指令:"
echo "   監控進度: python3 monitor_optimized.py"
echo "   查看日誌: tail -f $LOG_FILE"
echo "   檢查狀態: ps -p $SCRAPER_PID"
echo "   Git狀態: git log --oneline -5"
echo ""
echo "⚠️  注意: 此進程將在背景持續運行，即使關閉終端也不會停止"