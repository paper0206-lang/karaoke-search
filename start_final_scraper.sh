#!/bin/bash

# 啟動最終正確基準爬蟲腳本

echo "🚀 啟動最終正確基準爬蟲..."

# 檢查是否已經在運行
PID_FILE="final_scraper.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        echo "⚠️ 爬蟲已在運行 (PID: $PID)"
        echo "請先停止現有爬蟲或使用 ./stop_final_scraper.sh"
        exit 1
    else
        echo "🧹 清理過期的PID文件"
        rm -f "$PID_FILE"
    fi
fi

# 檢查Python環境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未找到"
    exit 1
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

echo "📋 爬蟲配置:"
echo "   基準閾值: 5% (95%覆蓋率)"
echo "   優先級排序: 覆蓋率低的歌手優先"
echo "   自動Git推送: 啟用"
echo "   檢查點保存: 啟用"

# 後台啟動爬蟲
nohup python3 final_correct_scraper.py > logs/final_scraper_$(date +%Y%m%d_%H%M%S).log 2>&1 &
SCRAPER_PID=$!

# 保存PID
echo $SCRAPER_PID > "$PID_FILE"

echo "✅ 最終正確基準爬蟲已啟動"
echo "   PID: $SCRAPER_PID"
echo "   PID文件: $PID_FILE"
echo "   日誌文件: logs/final_scraper_$(date +%Y%m%d_%H%M%S).log"

echo ""
echo "📊 監控命令:"
echo "   查看狀態: ./check_final_scraper.sh"
echo "   停止爬蟲: ./stop_final_scraper.sh"
echo "   查看日誌: tail -f final_correct_scraper.log"

echo ""
echo "🎯 爬蟲特點:"
echo "   ✅ 使用HAR文件洞察的正確搜索方式"
echo "   ✅ 實現5%差異閾值檢測"
echo "   ✅ 優先處理覆蓋率低的歌手"
echo "   ✅ 跳過5%以內差異的歌手"
echo "   ✅ 自動Git推送功能"
echo "   ✅ 檢查點容錯恢復"