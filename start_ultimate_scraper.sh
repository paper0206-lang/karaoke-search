#!/bin/bash

# 啟動終極10線程並發爬蟲

echo "🚀 啟動終極10線程並發爬蟲..."

PID_FILE="ultimate_scraper.pid"

# 檢查是否已經在運行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        echo "⚠️ 爬蟲已在運行 (PID: $PID)"
        echo "請先停止現有爬蟲或使用 ./stop_ultimate_scraper.sh"
        exit 1
    else
        echo "🧹 清理過期的PID文件"
        rm -f "$PID_FILE"
    fi
fi

# 檢查依賴文件
if [ ! -f "improved_taiwan_comparator.py" ]; then
    echo "❌ 缺少依賴文件: improved_taiwan_comparator.py"
    exit 1
fi

if [ ! -f "public/singers_data.json" ]; then
    echo "❌ 缺少歌手數據文件: public/singers_data.json"
    exit 1
fi

# 創建日誌目錄
mkdir -p logs

echo "📋 終極爬蟲配置:"
echo "   線程數: 10個並發線程"
echo "   每線程頁數: 200頁"
echo "   基準閾值: 5% (95%覆蓋率)"
echo "   分頁檢測: 無上限 + 重複檢測"
echo "   隨機延遲: 1.5-3.5秒 + 線程錯開"
echo "   自動Git推送: 每5位歌手推送一次"

# 後台啟動爬蟲
nohup python3 ultimate_10thread_scraper.py > logs/ultimate_scraper_$(date +%Y%m%d_%H%M%S).log 2>&1 &
SCRAPER_PID=$!

# 保存PID
echo $SCRAPER_PID > "$PID_FILE"

echo "✅ 終極10線程並發爬蟲已啟動"
echo "   PID: $SCRAPER_PID"
echo "   PID文件: $PID_FILE" 
echo "   日誌文件: logs/ultimate_scraper_$(date +%Y%m%d_%H%M%S).log"

echo ""
echo "📊 監控命令:"
echo "   查看狀態: ./check_ultimate_scraper.sh"
echo "   停止爬蟲: ./stop_ultimate_scraper.sh"
echo "   查看日誌: tail -f ultimate_10thread_scraper.log"

echo ""
echo "🎯 爬蟲特點:"
echo "   ✅ 10線程並發 + 智能任務分配"
echo "   ✅ 無上限分頁 + 重複檢測停止"  
echo "   ✅ 盧廣仲基準 + 優先級排序"
echo "   ✅ 隨機延遲 + 反爬蟲策略"
echo "   ✅ 檢查點恢復 + 自動Git推送"
echo "   ✅ 線程安全 + 資料整合"