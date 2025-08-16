#!/bin/bash

# 檢查最終正確基準爬蟲狀態腳本

echo "📊 檢查最終正確基準爬蟲狀態..."

PID_FILE="final_scraper.pid"

# 檢查進程狀態
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    
    if ps -p $PID > /dev/null; then
        echo "✅ 爬蟲正在運行"
        echo "   PID: $PID"
        
        # 顯示進程信息
        echo "   進程信息:"
        ps -p $PID -o pid,ppid,cmd,etime,pcpu,pmem --no-headers | sed 's/^/     /'
        
    else
        echo "❌ PID文件存在但進程不在運行"
        echo "   過期PID: $PID"
    fi
else
    echo "❌ 沒有找到PID文件"
    
    # 檢查是否有相關進程
    RUNNING_PID=$(pgrep -f "final_correct_scraper.py")
    if [ ! -z "$RUNNING_PID" ]; then
        echo "⚠️ 發現未記錄的進程: $RUNNING_PID"
    fi
fi

echo ""

# 檢查檢查點文件
CHECKPOINT_FILE="final_scraper_checkpoint.json"
if [ -f "$CHECKPOINT_FILE" ]; then
    echo "📋 檢查點狀態:"
    
    # 提取關鍵信息
    if command -v jq > /dev/null; then
        echo "   當前批次: $(jq -r '.current_batch // "未知"' "$CHECKPOINT_FILE")"
        echo "   已爬取歌手: $(jq -r '.scraped_singers // "未知"' "$CHECKPOINT_FILE")"
        echo "   已跳過歌手: $(jq -r '.skipped_singers // "未知"' "$CHECKPOINT_FILE")"
        echo "   最後更新: $(jq -r '.last_update // "未知"' "$CHECKPOINT_FILE")"
        echo "   狀態: $(jq -r '.status // "未知"' "$CHECKPOINT_FILE")"
        
        PROCESSED_COUNT=$(jq -r '.processed_singers | length' "$CHECKPOINT_FILE" 2>/dev/null || echo "未知")
        echo "   已處理歌手總數: $PROCESSED_COUNT"
    else
        echo "   檢查點文件存在，但需要jq工具解析詳細信息"
        echo "   文件大小: $(wc -c < "$CHECKPOINT_FILE") 字節"
        echo "   最後修改: $(stat -f "%Sm" "$CHECKPOINT_FILE")"
    fi
else
    echo "❌ 沒有找到檢查點文件"
fi

echo ""

# 檢查日誌文件
LOG_FILE="final_correct_scraper.log"
if [ -f "$LOG_FILE" ]; then
    echo "📝 日誌狀態:"
    echo "   日誌文件大小: $(wc -c < "$LOG_FILE") 字節"
    echo "   最後修改: $(stat -f "%Sm" "$LOG_FILE")"
    
    echo ""
    echo "🔍 最近10行日誌:"
    tail -10 "$LOG_FILE" | sed 's/^/   /'
else
    echo "❌ 沒有找到日誌文件"
fi

echo ""

# 檢查結果文件
RESULTS_FILE="final_scraper_results.json"
if [ -f "$RESULTS_FILE" ]; then
    echo "📊 結果文件狀態:"
    echo "   結果文件大小: $(wc -c < "$RESULTS_FILE") 字節"
    echo "   最後修改: $(stat -f "%Sm" "$RESULTS_FILE")"
    
    if command -v jq > /dev/null; then
        TOTAL_RESULTS=$(jq '. | length' "$RESULTS_FILE" 2>/dev/null || echo "未知")
        echo "   總結果數: $TOTAL_RESULTS"
        
        SCRAPED_COUNT=$(jq '[.[] | select(.action == "scraped")] | length' "$RESULTS_FILE" 2>/dev/null || echo "未知")
        SKIPPED_COUNT=$(jq '[.[] | select(.action == "skipped")] | length' "$RESULTS_FILE" 2>/dev/null || echo "未知")
        echo "   已爬取: $SCRAPED_COUNT"
        echo "   已跳過: $SKIPPED_COUNT"
    fi
else
    echo "❌ 沒有找到結果文件"
fi

echo ""
echo "🔧 管理命令:"
echo "   啟動爬蟲: ./start_final_scraper.sh"
echo "   停止爬蟲: ./stop_final_scraper.sh"
echo "   查看實時日誌: tail -f final_correct_scraper.log"