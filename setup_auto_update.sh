#!/bin/bash

# 設置自動更新定時任務
echo "🤖 設置卡拉OK自動更新系統"
echo "=========================="

# 獲取當前腳本目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTO_UPDATE_SCRIPT="$SCRIPT_DIR/auto_daily_update.sh"

echo "📍 專案位置: $SCRIPT_DIR"
echo "🔧 自動更新腳本: $AUTO_UPDATE_SCRIPT"

# 確保腳本可執行
chmod +x "$AUTO_UPDATE_SCRIPT"
chmod +x "$SCRIPT_DIR"/*.sh

echo ""
echo "⏰ 定時任務選項:"
echo "1. 每日凌晨 2:00 自動更新"
echo "2. 每週日凌晨 3:00 自動更新"  
echo "3. 每3天凌晨 1:00 自動更新"
echo "4. 自訂時間"
echo "5. 手動執行測試"

read -p "請選擇 (1-5): " choice

case $choice in
    1)
        CRON_TIME="0 2 * * *"
        DESCRIPTION="每日凌晨2點"
        ;;
    2)
        CRON_TIME="0 3 * * 0"
        DESCRIPTION="每週日凌晨3點"
        ;;
    3)
        CRON_TIME="0 1 */3 * *"
        DESCRIPTION="每3天凌晨1點"
        ;;
    4)
        echo "請輸入 cron 表達式 (例如: 0 2 * * * 表示每日凌晨2點):"
        read -p "cron 時間: " CRON_TIME
        DESCRIPTION="自訂時間"
        ;;
    5)
        echo "🧪 執行手動測試..."
        cd "$SCRIPT_DIR"
        bash "$AUTO_UPDATE_SCRIPT"
        echo "✅ 測試完成"
        exit 0
        ;;
    *)
        echo "❌ 無效選擇"
        exit 1
        ;;
esac

# 建立 cron 任務
CRON_JOB="$CRON_TIME cd $SCRIPT_DIR && bash $AUTO_UPDATE_SCRIPT"

# 檢查是否已存在相同任務
if crontab -l 2>/dev/null | grep -q "auto_daily_update.sh"; then
    echo "⚠️ 發現現有的自動更新任務"
    read -p "是否要替換現有任務？(y/n): " replace
    
    if [[ $replace == "y" || $replace == "Y" ]]; then
        # 移除舊任務
        crontab -l 2>/dev/null | grep -v "auto_daily_update.sh" | crontab -
        echo "🗑️ 已移除舊任務"
    else
        echo "❌ 取消設置"
        exit 0
    fi
fi

# 新增 cron 任務
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

if [[ $? -eq 0 ]]; then
    echo "✅ 自動更新任務設置成功！"
    echo ""
    echo "📅 執行時間: $DESCRIPTION"
    echo "⏰ Cron 表達式: $CRON_TIME"
    echo "📁 工作目錄: $SCRIPT_DIR"
    echo "📝 日誌位置: $SCRIPT_DIR/auto_update_YYYYMMDD.log"
    echo ""
    echo "🔍 查看目前的定時任務:"
    echo "   crontab -l"
    echo ""
    echo "🗑️ 移除自動更新:"
    echo "   crontab -l | grep -v 'auto_daily_update.sh' | crontab -"
    echo ""
    echo "📊 手動檢查狀態:"
    echo "   ./check_progress.sh"
else
    echo "❌ 設置失敗，請檢查權限或 cron 服務"
fi