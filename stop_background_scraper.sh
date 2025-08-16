#!/bin/bash

# 背景爬蟲停止腳本

echo "🛑 停止背景爬蟲系統"
echo "==================="

PID_FILE="background_scraper.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ 沒有找到PID文件，可能沒有背景進程在運行"
    exit 1
fi

SCRAPER_PID=$(cat "$PID_FILE")

if ! ps -p "$SCRAPER_PID" > /dev/null 2>&1; then
    echo "❌ 進程 $SCRAPER_PID 不存在"
    rm -f "$PID_FILE"
    exit 1
fi

echo "📊 找到背景進程 PID: $SCRAPER_PID"
echo "🔄 發送SIGINT信號..."

# 發送SIGINT信號讓程序優雅關閉
kill -INT "$SCRAPER_PID"

# 等待程序關閉
echo "⏳ 等待程序安全關閉..."
for i in {1..30}; do
    if ! ps -p "$SCRAPER_PID" > /dev/null 2>&1; then
        echo "✅ 程序已安全關閉"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
    echo -n "."
done

echo ""
echo "⚠️  程序沒有在30秒內關閉，發送SIGTERM..."
kill -TERM "$SCRAPER_PID"

# 再等待10秒
for i in {1..10}; do
    if ! ps -p "$SCRAPER_PID" > /dev/null 2>&1; then
        echo "✅ 程序已關閉"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
    echo -n "."
done

echo ""
echo "❌ 程序仍在運行，使用強制終止..."
kill -KILL "$SCRAPER_PID"

rm -f "$PID_FILE"
echo "🔚 強制終止完成"