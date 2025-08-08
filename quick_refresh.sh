#!/bin/bash

# 快速刷新 - 自動刷新歌曲數偏少的歌手
echo "⚡ 快速刷新系統"
echo "自動識別並刷新歌曲數偏少的歌手"
echo "================================"

# 檢查是否有歌手資料
if [[ ! -f "public/singers_data.json" ]]; then
    echo "❌ 找不到歌手資料檔案"
    exit 1
fi

echo "📊 分析現有歌手資料..."

# 分析歌手資料，找出需要刷新的歌手
python3 -c "
import json
import sys

try:
    with open('public/singers_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    needs_refresh = []
    famous_singers = ['周杰倫', '蔡依林', '林俊傑', '張惠妹', '五月天', '孫燕姿', '梁靜茹', '王力宏', '陶喆', '鄧紫棋']
    
    for singer_name, singer_data in data.items():
        song_count = len(singer_data.get('歌曲清單', []))
        
        # 判斷是否需要刷新
        should_refresh = False
        
        if singer_name in famous_singers and song_count < 100:
            should_refresh = True
        elif song_count < 30:
            should_refresh = True
        
        if should_refresh:
            needs_refresh.append((singer_name, song_count))
    
    # 按歌曲數排序
    needs_refresh.sort(key=lambda x: x[1])
    
    print(f'發現 {len(needs_refresh)} 位歌手需要刷新:')
    for singer, count in needs_refresh:
        print(f'  {singer}: {count} 首')
    
    # 輸出到檔案供 bash 讀取
    with open('temp_refresh_list.txt', 'w', encoding='utf-8') as f:
        for singer, count in needs_refresh:
            f.write(f'{singer}\n')
            
except Exception as e:
    print(f'❌ 分析失敗: {e}')
    sys.exit(1)
"

if [[ $? -ne 0 ]]; then
    echo "❌ 歌手分析失敗"
    exit 1
fi

# 檢查是否有需要刷新的歌手
if [[ ! -f "temp_refresh_list.txt" ]]; then
    echo "✅ 所有歌手資料都很完整，無需刷新"
    exit 0
fi

REFRESH_COUNT=$(wc -l < temp_refresh_list.txt)

if [[ $REFRESH_COUNT -eq 0 ]]; then
    echo "✅ 所有歌手資料都很完整，無需刷新"
    rm -f temp_refresh_list.txt
    exit 0
fi

echo ""
echo "🔄 發現 $REFRESH_COUNT 位歌手需要刷新"
echo "⏱️  預估時間: $((REFRESH_COUNT * 2)) 分鐘"

read -p "是否立即開始刷新？(y/n): " confirm

if [[ $confirm != "y" && $confirm != "Y" ]]; then
    echo "❌ 已取消"
    rm -f temp_refresh_list.txt
    exit 0
fi

echo ""
echo "🚀 開始快速刷新..."
START_TIME=$(date)
SUCCESS_COUNT=0
FAILED_COUNT=0
TOTAL_ADDED=0

# 逐個刷新歌手
line_num=0
while IFS= read -r singer_name; do
    line_num=$((line_num + 1))
    
    echo ""
    echo "🔄 [$line_num/$REFRESH_COUNT] 刷新: $singer_name"
    echo "開始時間: $(date '+%H:%M:%S')"
    
    # 記錄原有歌曲數
    OLD_COUNT=$(python3 -c "
import json
try:
    with open('public/singers_data.json', 'r') as f:
        data = json.load(f)
    print(len(data.get('$singer_name', {}).get('歌曲清單', [])))
except:
    print(0)
" 2>/dev/null)
    
    echo "   原有歌曲: $OLD_COUNT 首"
    
    # 執行刷新
    timeout 300 python3 -c "
import sys
sys.path.append('.')
from singer_scraper import SingerScraper

try:
    scraper = SingerScraper(max_workers=2)
    songs = scraper.search_singer_comprehensive('$singer_name')
    new_count = len(songs)
    
    # 只有在新數量 >= 原數量時才儲存
    if new_count >= $OLD_COUNT:
        if scraper.save_singer_data('$singer_name', songs):
            print(f'✅ $singer_name 完成: {new_count} 首 (+{new_count - $OLD_COUNT})')
            sys.exit(0)
        else:
            print(f'❌ $singer_name 儲存失敗')
            sys.exit(1)
    else:
        print(f'⚠️ $singer_name 新數量較少: {new_count} < $OLD_COUNT，保持原資料')
        sys.exit(0)
        
except Exception as e:
    print(f'💥 $singer_name 刷新失敗: {e}')
    sys.exit(1)
"
    
    if [[ $? -eq 0 ]]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        
        # 計算實際新增數量
        NEW_COUNT=$(python3 -c "
import json
try:
    with open('public/singers_data.json', 'r') as f:
        data = json.load(f)
    print(len(data.get('$singer_name', {}).get('歌曲清單', [])))
except:
    print(0)
" 2>/dev/null)
        
        ADDED=$((NEW_COUNT - OLD_COUNT))
        if [[ $ADDED -gt 0 ]]; then
            TOTAL_ADDED=$((TOTAL_ADDED + ADDED))
            echo "   📈 新增 $ADDED 首，現有 $NEW_COUNT 首"
        else
            echo "   ✅ 資料已是最新"
        fi
    else
        FAILED_COUNT=$((FAILED_COUNT + 1))
        echo "   ❌ 刷新失敗"
    fi
    
    # 進度統計
    echo "📊 進度: $SUCCESS_COUNT 成功, $FAILED_COUNT 失敗, 累計新增 $TOTAL_ADDED 首"
    
    # 休息避免被封鎖
    if [[ $line_num -lt $REFRESH_COUNT ]]; then
        echo "😴 休息 5 秒..."
        sleep 5
    fi
    
done < temp_refresh_list.txt

# 清理暫存檔案
rm -f temp_refresh_list.txt

# 完成統計
END_TIME=$(date)

echo ""
echo "🎉 快速刷新完成！"
echo "================================="
echo "📊 執行結果:"
echo "   處理歌手: $((SUCCESS_COUNT + FAILED_COUNT)) 位"
echo "   成功: $SUCCESS_COUNT 位"
echo "   失敗: $FAILED_COUNT 位"
echo "   新增歌曲: $TOTAL_ADDED 首"
echo ""
echo "⏰ 時間統計:"
echo "   開始時間: $START_TIME"
echo "   結束時間: $END_TIME"

# 顯示最新統計
if [[ -f "public/singers_data.json" ]]; then
    FINAL_COUNT=$(python3 -c "import json; data = json.load(open('public/singers_data.json', 'r')); print(len(data))" 2>/dev/null || echo "0")
    FINAL_SONGS=$(python3 -c "import json; data = json.load(open('public/singers_data.json', 'r')); total = sum(len(singer['歌曲清單']) for singer in data.values()); print(total)" 2>/dev/null || echo "0")
    echo ""
    echo "🎤 最新歌手資料庫:"
    echo "   歌手數量: $FINAL_COUNT 位"
    echo "   歌曲總數: $FINAL_SONGS 首"
fi

# 詢問是否提交
if [[ $TOTAL_ADDED -gt 0 ]]; then
    echo ""
    read -p "是否自動提交更新到GitHub？(y/n, 預設y): " auto_commit
    
    if [[ -z "$auto_commit" || $auto_commit == "y" || $auto_commit == "Y" ]]; then
        echo "🤖 自動提交歌手資料到GitHub..."
        
        git add public/singers_data.json
        git commit -m "快速刷新: 優化 $SUCCESS_COUNT 位歌手資料

📊 刷新統計:
- 處理歌手: $((SUCCESS_COUNT + FAILED_COUNT)) 位
- 成功優化: $SUCCESS_COUNT 位  
- 新增歌曲: $TOTAL_ADDED 首

🎯 主要改進:
- 突破之前的50首限制
- 使用新的多策略搜尋
- 自動識別歌曲數偏少的歌手

⏰ 執行時間: 從 $START_TIME 開始
📈 最終資料: $FINAL_COUNT 位歌手, $FINAL_SONGS 首歌曲

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
        
        git push
        echo "✅ 歌手資料已推送，網站將在2-3分鐘內更新"
        echo "🌐 查看結果: https://karaoke-search-theta.vercel.app"
    fi
fi

echo ""
echo "💡 建議:"
echo "1. 檢查刷新結果: ./check_singers.sh"  
echo "2. 繼續爬取新歌手: ./mass_singer_scraper.sh"
echo "3. 再次快速刷新: ./quick_refresh.sh"