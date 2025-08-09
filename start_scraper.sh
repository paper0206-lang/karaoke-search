#!/bin/bash

# 歌手優先爬蟲啟動腳本
echo "🎤 歌手優先爬蟲啟動器"
echo "========================"

# 檢查當前狀態
echo "📊 當前資料庫狀態:"
python3 -c "
import json
try:
    with open('public/unified_karaoke_db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'   歌曲數量: {data[\"metadata\"][\"total_songs\"]:,}')
    print(f'   歌手數量: {data[\"metadata\"][\"total_singers\"]:,}')
    print(f'   檔案大小: {len(json.dumps(data))/1024/1024:.1f}MB')
except:
    print('   ❌ 無法讀取統一資料庫')
"

echo ""
echo "🚀 執行選項:"
echo "1. 快速模式 - 前10位天王天后 (約30分鐘)"
echo "2. 標準模式 - 前20位優先歌手 (約60分鐘) [預設]"  
echo "3. 深度模式 - 前40位精選歌手 (約120分鐘)"
echo "4. 背景執行標準模式"
echo ""

if [[ -t 0 ]]; then
    # 互動模式
    read -p "請選擇模式 (1-4，預設2): " mode
    case ${mode:-2} in
        1) MODE="quick" ;;
        3) MODE="deep" ;;
        4) 
            echo "🔄 啟動背景執行..."
            nohup python3 run_singer_scraper.py standard > singer_scraper.log 2>&1 &
            echo $! > singer_scraper.pid
            echo "✅ 背景執行已啟動"
            echo "📊 監控進度: tail -f singer_scraper.log"
            echo "⏹️  停止執行: kill \$(cat singer_scraper.pid)"
            exit 0
            ;;
        *) MODE="standard" ;;
    esac
else
    # 非互動模式，使用標準模式
    MODE="standard"
fi

echo "🎯 執行模式: $MODE"
echo "⏰ 開始時間: $(date)"

# 前台執行
python3 run_singer_scraper.py $MODE

echo ""
echo "⏰ 完成時間: $(date)"
echo "💡 檢查結果: ./check_progress.sh"