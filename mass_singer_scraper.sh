#!/bin/bash

# 大量歌手爬蟲腳本 - 從發現的121位歌手中批次爬取
echo "🎤 大量歌手爬蟲系統"
echo "從 121 位發現的歌手中批次爬取歌曲"
echo "================================="

# 檢查歌手名單檔案
if [[ ! -f "priority_singers.txt" ]]; then
    echo "❌ 找不到歌手名單檔案，請先執行: python3 singer_discovery.py"
    exit 1
fi

TOTAL_SINGERS=$(wc -l < priority_singers.txt)
echo "📊 發現 $TOTAL_SINGERS 位歌手待爬取"

# 檢查目前已爬取的歌手
CURRENT_SINGERS=0
if [[ -f "public/singers_data.json" ]]; then
    CURRENT_SINGERS=$(python3 -c "import json; data = json.load(open('public/singers_data.json', 'r')); print(len(data))" 2>/dev/null || echo "0")
    echo "📊 目前已有 $CURRENT_SINGERS 位歌手資料"
fi

echo ""
echo "🚀 批次爬蟲選項:"
echo "1. 爬取前20位優先歌手 (天王天后級)"
echo "2. 爬取前50位歌手 (包含新生代)"
echo "3. 爬取全部121位歌手 (完整資料庫)"
echo "4. 從指定位置開始爬取"
echo "5. 只爬取尚未收錄的歌手"
echo "6. 🔄 重新爬取現有歌手 (突破之前的限制)"

read -p "請選擇 (1-6): " choice

case $choice in
    1)
        START_LINE=1
        END_LINE=20
        DESCRIPTION="前20位優先歌手"
        ;;
    2)
        START_LINE=1
        END_LINE=50
        DESCRIPTION="前50位歌手"
        ;;
    3)
        START_LINE=1
        END_LINE=$TOTAL_SINGERS
        DESCRIPTION="全部121位歌手"
        ;;
    4)
        read -p "從第幾位開始 (1-$TOTAL_SINGERS): " START_LINE
        read -p "到第幾位結束 (1-$TOTAL_SINGERS): " END_LINE
        DESCRIPTION="第${START_LINE}到${END_LINE}位歌手"
        ;;
    5)
        echo "🔍 檢查尚未收錄的歌手..."
        # 這個選項需要特殊處理
        START_LINE=1
        END_LINE=$TOTAL_SINGERS
        DESCRIPTION="尚未收錄的歌手"
        SKIP_EXISTING=true
        ;;
    6)
        echo "🔄 啟動現有歌手刷新系統..."
        python3 refresh_singer_scraper.py
        exit 0
        ;;
    *)
        echo "❌ 無效選擇"
        exit 1
        ;;
esac

# 確認執行
echo ""
echo "📋 準備爬取: $DESCRIPTION"
echo "⏱️  預估時間: $((($END_LINE - $START_LINE + 1) * 3)) 分鐘"
read -p "確定開始嗎？(y/n): " confirm

if [[ $confirm != "y" && $confirm != "Y" ]]; then
    echo "❌ 已取消"
    exit 0
fi

# 開始批次爬蟲
echo ""
echo "🚀 開始批次爬蟲..."
START_TIME=$(date)
SUCCESS_COUNT=0
FAILED_COUNT=0

# 讀取現有歌手列表 (用於跳過已存在的)
EXISTING_SINGERS=""
if [[ -f "public/singers_data.json" && "$SKIP_EXISTING" == "true" ]]; then
    EXISTING_SINGERS=$(python3 -c "
import json
try:
    with open('public/singers_data.json', 'r') as f:
        data = json.load(f)
    print('|'.join(data.keys()))
except:
    print('')
" 2>/dev/null)
fi

# 執行爬蟲
line_num=0
while IFS= read -r singer_name; do
    line_num=$((line_num + 1))
    
    # 檢查是否在指定範圍內
    if [[ $line_num -lt $START_LINE || $line_num -gt $END_LINE ]]; then
        continue
    fi
    
    # 跳過已存在的歌手
    if [[ "$SKIP_EXISTING" == "true" && "$EXISTING_SINGERS" == *"|$singer_name|"* ]]; then
        echo "⏭️  跳過已收錄: $singer_name ($line_num/$TOTAL_SINGERS)"
        continue
    fi
    
    echo ""
    echo "🎤 [$line_num/$TOTAL_SINGERS] 正在爬取: $singer_name"
    echo "開始時間: $(date '+%H:%M:%S')"
    
    # 執行單一歌手爬蟲
    timeout 300 python3 -c "
import sys
sys.path.append('.')
from singer_scraper import SingerScraper

try:
    scraper = SingerScraper(max_workers=2)
    songs = scraper.search_singer_comprehensive('$singer_name')
    if scraper.save_singer_data('$singer_name', songs):
        print(f'✅ $singer_name 完成: {len(songs)} 首歌曲')
    else:
        print(f'❌ $singer_name 儲存失敗')
        sys.exit(1)
except Exception as e:
    print(f'💥 $singer_name 爬取失敗: {e}')
    sys.exit(1)
"
    
    if [[ $? -eq 0 ]]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo "✅ $singer_name 爬取成功"
    else
        FAILED_COUNT=$((FAILED_COUNT + 1))
        echo "❌ $singer_name 爬取失敗"
    fi
    
    # 進度統計
    PROGRESS=$(($line_num * 100 / $END_LINE))
    echo "📊 進度: $SUCCESS_COUNT 成功, $FAILED_COUNT 失敗 ($PROGRESS%)"
    
    # 每10個歌手休息一下
    if [[ $(($line_num % 10)) -eq 0 ]]; then
        echo "😴 休息 30 秒避免被封鎖..."
        sleep 30
    else
        sleep 5
    fi
    
done < priority_singers.txt

# 完成統計
END_TIME=$(date)
TOTAL_PROCESSED=$((SUCCESS_COUNT + FAILED_COUNT))

echo ""
echo "🎉 批次爬蟲完成！"
echo "================================="
echo "📊 執行統計:"
echo "   處理歌手: $TOTAL_PROCESSED 位"
echo "   成功: $SUCCESS_COUNT 位"
echo "   失敗: $FAILED_COUNT 位"
echo "   成功率: $(($SUCCESS_COUNT * 100 / $TOTAL_PROCESSED))%"
echo ""
echo "⏰ 時間統計:"
echo "   開始時間: $START_TIME"
echo "   結束時間: $END_TIME"
echo ""

# 檢查最終歌手數量
if [[ -f "public/singers_data.json" ]]; then
    FINAL_COUNT=$(python3 -c "import json; data = json.load(open('public/singers_data.json', 'r')); print(len(data))" 2>/dev/null || echo "0")
    FINAL_SONGS=$(python3 -c "import json; data = json.load(open('public/singers_data.json', 'r')); total = sum(len(singer['歌曲清單']) for singer in data.values()); print(total)" 2>/dev/null || echo "0")
    echo "🎤 最終歌手資料庫:"
    echo "   歌手數量: $FINAL_COUNT 位"
    echo "   歌曲總數: $FINAL_SONGS 首"
fi

# 詢問是否自動提交
if [[ $SUCCESS_COUNT -gt 0 ]]; then
    echo ""
    read -p "是否自動提交到GitHub？(y/n, 預設y): " auto_commit
    
    if [[ -z "$auto_commit" || $auto_commit == "y" || $auto_commit == "Y" ]]; then
        echo "🤖 自動提交歌手資料到GitHub..."
        
        git add public/singers_data.json
        git commit -m "大量歌手爬蟲: 新增 $SUCCESS_COUNT 位歌手

📊 批次爬蟲統計:
- 處理歌手: $TOTAL_PROCESSED 位  
- 成功收錄: $SUCCESS_COUNT 位
- 失敗: $FAILED_COUNT 位
- 成功率: $(($SUCCESS_COUNT * 100 / $TOTAL_PROCESSED))%

🎯 爬蟲範圍: $DESCRIPTION
⏰ 執行時間: 從 $START_TIME 開始
📈 最終資料: $FINAL_COUNT 位歌手, $FINAL_SONGS 首歌曲

✨ 使用多策略搜尋突破50首限制
🎵 完整收錄各家KTV編號資訊
🚀 從121位發現的歌手中精選收錄

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
        
        git push
        echo "✅ 歌手資料已推送，網站將在2-3分鐘內更新"
        echo "🌐 查看結果: https://karaoke-search-theta.vercel.app"
    fi
fi

echo ""
echo "💡 後續建議:"
echo "1. 檢查歌手資料: ./check_singers.sh"
echo "2. 查看優先清單: head -20 priority_singers.txt"
echo "3. 繼續爬取: ./mass_singer_scraper.sh"