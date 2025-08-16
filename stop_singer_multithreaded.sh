#!/bin/bash

# 停止基於歌手分配的多線程爬蟲

echo "🛑 正在停止基於歌手分配的多線程爬蟲..."

PID_FILE="singer_multithreaded.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    echo "📊 找到 PID: $PID"
    
    if ps -p $PID > /dev/null; then
        echo "⏹️ 正在終止進程 $PID..."
        kill -TERM $PID
        
        # 等待最多45秒讓進程正常退出（多線程需要更多時間）
        for i in {1..45}; do
            if ! ps -p $PID > /dev/null; then
                echo "✅ 進程已正常停止"
                rm -f "$PID_FILE"
                exit 0
            fi
            echo "⏳ 等待進程停止... ($i/45)"
            sleep 1
        done
        
        # 強制終止
        echo "⚠️ 正常停止超時，強制終止..."
        kill -KILL $PID
        rm -f "$PID_FILE"
        echo "✅ 進程已強制停止"
    else
        echo "❌ 進程不存在，清理PID文件"
        rm -f "$PID_FILE"
    fi
else
    echo "❌ 沒有找到PID文件"
    # 嘗試找到進程並停止
    PID=$(pgrep -f "singer_based_multithreaded_scraper.py")
    if [ ! -z "$PID" ]; then
        echo "🔍 找到運行中的歌手多線程爬蟲進程: $PID"
        kill -TERM $PID
        echo "✅ 已發送停止信號"
    else
        echo "ℹ️ 沒有找到運行中的歌手多線程爬蟲進程"
    fi
fi

echo "🏁 停止操作完成"