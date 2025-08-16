#!/bin/bash

# 啟動正確基準爬蟲

echo "🎯 啟動正確基準爬蟲系統"
echo "📊 特色: 5%差異閾值 + 逐筆重複檢查 + 台灣點歌網動態比較"

# 檢查是否有運行中的進程
if [ -f "correct_scraper.pid" ]; then
    PID=$(cat correct_scraper.pid)
    if ps -p $PID > /dev/null; then
        echo "⚠️ 發現運行中的正確基準爬蟲 (PID: $PID)"
        echo "請先執行: ./stop_correct_scraper.sh"
        exit 1
    else
        rm -f correct_scraper.pid
    fi
fi

# 停止其他爬蟲
echo "🛑 停止其他爬蟲進程..."
if [ -f "optimized_scraper.pid" ]; then
    ./stop_optimized_scraper.sh
fi

# 確保日誌目錄存在
mkdir -p correct_logs

# 生成唯一的日誌文件名
LOG_FILE="correct_logs/correct_$(date +%Y%m%d_%H%M%S).log"

echo "📝 日誌將保存到: $LOG_FILE"
echo ""
echo "🎯 正確基準機制說明:"
echo "   1. 查詢台灣點歌網某歌手的KTV編號總數"
echo "   2. 與我們資料庫的KTV編號數量對比"
echo "   3. 如果覆蓋率 < 95%就開始爬資料"
echo "   4. 逐筆比對確保不重複添加KTV編號"
echo ""
echo "✅ 這就是您原始需求的正確實現！"
echo ""

# 啟動背景進程
nohup python3 correct_benchmark_scraper.py > "$LOG_FILE" 2>&1 &

# 保存PID
echo $! > correct_scraper.pid

echo "✅ 正確基準爬蟲已啟動"
echo "📊 進程 PID: $(cat correct_scraper.pid)"
echo ""
echo "💡 監控命令:"
echo "   查看狀態: python3 monitor_correct.py"
echo "   實時日誌: tail -f $LOG_FILE"
echo "   停止爬蟲: ./stop_correct_scraper.sh"
echo ""
echo "🎉 正確基準機制特色:"
echo "   ⚡ 動態比較台灣點歌網實際數據"
echo "   🎯 5%差異閾值智能判斷"
echo "   🔍 逐筆重複檢查避免重複"
echo "   📊 精確的增量更新機制"