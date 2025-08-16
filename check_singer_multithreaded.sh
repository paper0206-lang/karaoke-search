#!/bin/bash

# 檢查基於歌手分配的多線程爬蟲狀態

echo "📊 檢查基於歌手分配的多線程爬蟲狀態..."

PID_FILE="singer_multithreaded.pid"

# 檢查進程狀態
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    
    if ps -p $PID > /dev/null; then
        echo "✅ 爬蟲正在運行"
        echo "   PID: $PID"
        
        # 顯示進程信息
        echo "   進程信息:"
        ps -p $PID -o pid,ppid,cmd,etime,pcpu,pmem --no-headers | sed 's/^/     /'
        
        # 顯示線程數
        THREAD_COUNT=$(ps -M $PID | wc -l)
        echo "   總線程數: $((THREAD_COUNT - 1))"
        
    else
        echo "❌ PID文件存在但進程不在運行"
        echo "   過期PID: $PID"
    fi
else
    echo "❌ 沒有找到PID文件"
    
    # 檢查是否有相關進程
    RUNNING_PID=$(pgrep -f "singer_based_multithreaded_scraper.py")
    if [ ! -z "$RUNNING_PID" ]; then
        echo "⚠️ 發現未記錄的進程: $RUNNING_PID"
    fi
fi

echo ""

# 檢查檢查點文件
CHECKPOINT_FILE="singer_based_checkpoint.json"
if [ -f "$CHECKPOINT_FILE" ]; then
    echo "📋 檢查點狀態:"
    
    # 提取關鍵信息
    if command -v jq > /dev/null; then
        echo "   隊列歌手: $(jq -r '.singers_queued // "未知"' "$CHECKPOINT_FILE")"
        echo "   已完成歌手: $(jq -r '.singers_completed // "未知"' "$CHECKPOINT_FILE")"
        echo "   已爬取歌手: $(jq -r '.singers_scraped // "未知"' "$CHECKPOINT_FILE")"
        echo "   已跳過歌手: $(jq -r '.singers_skipped // "未知"' "$CHECKPOINT_FILE")"
        echo "   最後更新: $(jq -r '.last_update // "未知"' "$CHECKPOINT_FILE")"
        echo "   狀態: $(jq -r '.status // "未知"' "$CHECKPOINT_FILE")"
        
        PROCESSED_COUNT=$(jq -r '.processed_singers | length' "$CHECKPOINT_FILE" 2>/dev/null || echo "未知")
        echo "   已處理歌手總數: $PROCESSED_COUNT"
        
        # 計算進度百分比
        QUEUED=$(jq -r '.singers_queued // 0' "$CHECKPOINT_FILE")
        COMPLETED=$(jq -r '.singers_completed // 0' "$CHECKPOINT_FILE")
        if [ "$QUEUED" != "0" ] && [ "$QUEUED" != "未知" ]; then
            PROGRESS=$(echo "scale=1; $COMPLETED * 100 / $QUEUED" | bc 2>/dev/null || echo "0")
            echo "   完成進度: ${PROGRESS}%"
        fi
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
LOG_FILE="singer_based_scraper.log"
if [ -f "$LOG_FILE" ]; then
    echo "📝 日誌狀態:"
    echo "   日誌文件大小: $(wc -c < "$LOG_FILE") 字節"
    echo "   最後修改: $(stat -f "%Sm" "$LOG_FILE")"
    
    # 統計線程活動
    THREAD_ACTIVITY=$(grep -c "🧵 線程" "$LOG_FILE" 2>/dev/null || echo "0")
    echo "   線程活動記錄: $THREAD_ACTIVITY 條"
    
    echo ""
    echo "🔍 最近10行日誌:"
    tail -10 "$LOG_FILE" | sed 's/^/   /'
    
    echo ""
    echo "📈 統計信息:"
    
    # 統計各類事件
    SCRAPED_COUNT=$(grep -c "✅ 爬取.*優先級" "$LOG_FILE" 2>/dev/null || echo "0")
    SKIPPED_COUNT=$(grep -c "⏭️ 跳過" "$LOG_FILE" 2>/dev/null || echo "0") 
    COMPLETED_COUNT=$(grep -c "完成.*首歌" "$LOG_FILE" 2>/dev/null || echo "0")
    ERROR_COUNT=$(grep -c "ERROR" "$LOG_FILE" 2>/dev/null || echo "0")
    
    echo "   開始爬取: $SCRAPED_COUNT 位歌手"
    echo "   跳過歌手: $SKIPPED_COUNT 位歌手"
    echo "   完成爬取: $COMPLETED_COUNT 位歌手"
    echo "   錯誤數量: $ERROR_COUNT 個"
    
    # 效率統計
    if [ "$COMPLETED_COUNT" != "0" ]; then
        ACTIVE_THREADS=$(grep "活躍線程:" "$LOG_FILE" | tail -1 | grep -o "[0-9]*" | tail -1 2>/dev/null || echo "0")
        echo "   當前活躍線程: $ACTIVE_THREADS"
    fi
    
else
    echo "❌ 沒有找到日誌文件"
fi

echo ""

# 檢查資料庫更新
SINGERS_DB="public/singers_data.json"
if [ -f "$SINGERS_DB" ]; then
    echo "💾 資料庫狀態:"
    echo "   資料庫大小: $(wc -c < "$SINGERS_DB") 字節"
    echo "   最後修改: $(stat -f "%Sm" "$SINGERS_DB")"
    
    if command -v jq > /dev/null; then
        TOTAL_SINGERS=$(jq '. | length' "$SINGERS_DB" 2>/dev/null || echo "未知")
        echo "   總歌手數: $TOTAL_SINGERS"
    fi
else
    echo "❌ 沒有找到歌手資料庫"
fi

echo ""
echo "🔧 管理命令:"
echo "   啟動爬蟲: ./start_singer_multithreaded.sh"
echo "   停止爬蟲: ./stop_singer_multithreaded.sh"
echo "   查看實時日誌: tail -f singer_based_scraper.log"
echo "   查看線程活動: grep '🧵 線程' singer_based_scraper.log | tail -20"
echo "   查看進度報告: grep '📊 進度' singer_based_scraper.log | tail -10"