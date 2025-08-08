#!/bin/bash

# 🔍 爬蟲監控工具
# 使用方法: ./monitor_scraper.sh

# 顏色定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🎤 卡拉OK爬蟲監控面板"
echo "==================="

# 檢查爬蟲是否在運行
echo ""
echo "📊 系統狀態:"
if pgrep -f "auto_update_database.sh\|quick_scraper.py\|continuous_scraper.py" > /dev/null; then
    echo -e "${GREEN}✅ 爬蟲程式正在運行中${NC}"
    echo "🆔 程序 PID: $(pgrep -f "auto_update_database.sh\|quick_scraper.py\|continuous_scraper.py")"
else
    echo -e "${RED}❌ 爬蟲程式未在運行${NC}"
fi

# 顯示歌曲數量
echo ""
echo "🎵 資料庫統計:"
if [[ -f "public/songs_simplified.json" ]]; then
    SONG_COUNT=$(python3 -c "import json; print(len(json.load(open('public/songs_simplified.json', 'r'))))" 2>/dev/null || echo "無法讀取")
    echo -e "${BLUE}📈 目前歌曲總數: ${SONG_COUNT} 首${NC}"
    
    # 計算檔案大小
    FILE_SIZE=$(ls -lh public/songs_simplified.json | awk '{print $5}')
    echo "💾 資料庫大小: $FILE_SIZE"
    
    # 最後更新時間
    LAST_MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" public/songs_simplified.json 2>/dev/null || stat -c "%y" public/songs_simplified.json 2>/dev/null | cut -d. -f1)
    echo "🕐 最後更新: $LAST_MODIFIED"
else
    echo -e "${RED}❌ 找不到歌曲資料檔案${NC}"
fi

# 顯示最新日誌
echo ""
echo "📋 最新活動 (最近 10 行):"
if [[ -f "auto_update.log" ]]; then
    echo -e "${YELLOW}$(tail -n 10 auto_update.log)${NC}"
else
    echo "沒有找到日誌檔案"
fi

# 顯示操作選項
echo ""
echo "🛠️  可用操作:"
echo "1) 查看完整日誌: tail -f auto_update.log"
echo "2) 查看歌曲數量: python3 -c \"import json; print('歌曲數:', len(json.load(open('public/songs_simplified.json', 'r'))))\""
echo "3) 停止爬蟲: pkill -f auto_update_database"
echo "4) 重啟爬蟲: ./start_auto_scraper.sh"
echo "5) 查看 Git 狀態: git status"

echo ""
echo "🌐 網站: https://karaoke-search-theta.vercel.app"