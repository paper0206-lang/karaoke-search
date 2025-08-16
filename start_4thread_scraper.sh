#!/bin/bash

# 啟動4線程優化版背景爬蟲

echo "🚀 啟動4線程優化版背景爬蟲"
echo "📊 配置: 4並行線程, 2-4秒延遲, 95%基準"

# 檢查是否有運行中的進程
if [ -f "optimized_scraper.pid" ]; then
    PID=$(cat optimized_scraper.pid)
    if ps -p $PID > /dev/null; then
        echo "⚠️ 發現運行中的爬蟲 (PID: $PID)"
        echo "請先執行: ./stop_optimized_scraper.sh"
        exit 1
    else
        rm -f optimized_scraper.pid
    fi
fi

# 確保日誌目錄存在
mkdir -p optimized_logs

# 生成唯一的日誌文件名
LOG_FILE="optimized_logs/4thread_$(date +%Y%m%d_%H%M%S).log"

echo "📝 日誌將保存到: $LOG_FILE"

# 啟動背景進程
nohup python3 optimized_background_scraper.py > "$LOG_FILE" 2>&1 &

# 保存PID
echo $! > optimized_scraper.pid

echo "✅ 4線程爬蟲已啟動"
echo "📊 進程 PID: $(cat optimized_scraper.pid)"
echo ""
echo "💡 監控命令:"
echo "   查看狀態: python3 monitor_optimized.py"
echo "   實時日誌: tail -f $LOG_FILE"
echo "   停止爬蟲: ./stop_optimized_scraper.sh"
echo ""
echo "⚡ 4線程配置預期性能:"
echo "   處理速度: ~300+ 位歌手/小時"
echo "   歌曲產出: ~2000+ 首歌/小時"
echo "   預計完成時間: 1-2小時"