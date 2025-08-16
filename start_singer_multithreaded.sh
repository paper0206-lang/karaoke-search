#!/bin/bash

# 啟動基於歌手分配的多線程爬蟲

echo "🚀 啟動基於歌手分配的多線程爬蟲..."

PID_FILE="singer_multithreaded.pid"

# 檢查是否已經在運行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        echo "⚠️ 爬蟲已在運行 (PID: $PID)"
        echo "請先停止現有爬蟲或使用 ./stop_singer_multithreaded.sh"
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

echo "📋 歌手多線程爬蟲配置:"
echo "   線程架構: 每線程處理一位歌手完整資料"
echo "   最大線程數: 10個並發線程"
echo "   效率提升: 5-10倍（相比按頁分配）"
echo "   基準閾值: 5% (95%覆蓋率)"
echo "   分頁檢測: 無上限 + 重複檢測"
echo "   隨機延遲: 2.0-4.0秒 + 線程錯開"
echo "   自動Git推送: 每5位歌手推送一次"

# 後台啟動爬蟲
nohup python3 singer_based_multithreaded_scraper.py > logs/singer_multithreaded_$(date +%Y%m%d_%H%M%S).log 2>&1 &
SCRAPER_PID=$!

# 保存PID
echo $SCRAPER_PID > "$PID_FILE"

echo "✅ 基於歌手分配的多線程爬蟲已啟動"
echo "   PID: $SCRAPER_PID"
echo "   PID文件: $PID_FILE" 
echo "   日誌文件: logs/singer_multithreaded_$(date +%Y%m%d_%H%M%S).log"

echo ""
echo "📊 監控命令:"
echo "   查看狀態: ./check_singer_multithreaded.sh"
echo "   停止爬蟲: ./stop_singer_multithreaded.sh"
echo "   查看日誌: tail -f singer_based_scraper.log"

echo ""
echo "🎯 新架構優勢:"
echo "   ✅ 效率最大化: 10位歌手同時處理"
echo "   ✅ 動態負載均衡: 完成一位立即處理下一位"
echo "   ✅ 資源充分利用: 沒有閒置線程"
echo "   ✅ 結果更快產出: 不需等待整組完成"
echo "   ✅ 盧廣仲基準 + 優先級排序"
echo "   ✅ 無上限分頁 + 智能重複檢測"