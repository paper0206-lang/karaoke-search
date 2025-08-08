#!/bin/bash

# 🎤 卡拉OK資料庫自動更新腳本
# 使用方法: ./auto_update_database.sh
# 背景執行: nohup ./auto_update_database.sh > auto_update.log 2>&1 &

set -e  # 遇到錯誤立即退出

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日誌函數
log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# 主函數
main() {
    log_info "🚀 開始自動更新卡拉OK歌曲資料庫"
    
    # 檢查目前目錄
    if [[ ! -f "package.json" ]]; then
        log_error "請在 karaoke-search 項目目錄中執行此腳本"
        exit 1
    fi
    
    # 記錄開始時的歌曲數量
    if [[ -f "public/songs_simplified.json" ]]; then
        INITIAL_COUNT=$(python3 -c "import json; print(len(json.load(open('public/songs_simplified.json', 'r'))))" 2>/dev/null || echo "0")
        log_info "目前資料庫有 $INITIAL_COUNT 首歌曲"
    else
        INITIAL_COUNT=0
        log_info "資料庫為空，從頭開始建立"
    fi
    
    # 執行爬蟲程式
    log_info "🔍 開始執行爬蟲程式..."
    if python3 quick_scraper.py; then
        log_success "爬蟲程式執行完成"
    else
        log_warning "爬蟲程式執行時遇到一些問題，繼續下一步"
    fi
    
    # 檢查是否有新歌曲
    if [[ -f "public/songs_simplified.json" ]]; then
        NEW_COUNT=$(python3 -c "import json; print(len(json.load(open('public/songs_simplified.json', 'r'))))" 2>/dev/null || echo "0")
        ADDED_COUNT=$((NEW_COUNT - INITIAL_COUNT))
        
        if [[ $ADDED_COUNT -gt 0 ]]; then
            log_success "新增了 $ADDED_COUNT 首歌曲！總計: $NEW_COUNT 首"
            
            # 自動提交到 Git
            log_info "📤 自動提交更新到 GitHub..."
            git add public/songs_simplified.json
            
            COMMIT_MESSAGE="自動更新歌曲資料庫: +$ADDED_COUNT 首歌曲 (總計: $NEW_COUNT 首)

更新時間: $(date '+%Y-%m-%d %H:%M:%S')
新增歌曲: $ADDED_COUNT 首
資料庫總計: $NEW_COUNT 首

🤖 由自動化腳本更新"
            
            if git commit -m "$COMMIT_MESSAGE"; then
                log_success "Git 提交成功"
                
                # 推送到 GitHub
                log_info "🚀 推送到 GitHub..."
                if git push; then
                    log_success "推送到 GitHub 成功！"
                    log_info "🌐 Vercel 將在 2-3 分鐘內自動部署更新"
                    log_info "📱 網站: https://karaoke-search-theta.vercel.app"
                else
                    log_error "推送到 GitHub 失敗"
                    exit 1
                fi
            else
                log_warning "沒有新變更需要提交"
            fi
        else
            log_info "沒有新增歌曲，跳過 Git 提交"
        fi
    else
        log_error "找不到歌曲資料檔案"
        exit 1
    fi
    
    # 顯示最終結果
    log_success "✅ 自動更新流程完成！"
    echo ""
    echo "📊 更新總結:"
    echo "   初始歌曲數: $INITIAL_COUNT 首"
    echo "   最終歌曲數: $NEW_COUNT 首"
    echo "   新增歌曲: $ADDED_COUNT 首"
    echo ""
    echo "🌐 網站將在幾分鐘內更新: https://karaoke-search-theta.vercel.app"
}

# 捕獲中斷信號
trap 'log_error "腳本被中斷"; exit 1' INT TERM

# 執行主函數
main "$@"