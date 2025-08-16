# 🩺 系統健康檢查指南

## 快速檢查腳本

```bash
#!/bin/bash
# 快速系統健康檢查

echo "🔍 卡拉OK搜尋系統健康檢查"
echo "================================"

# 1. 檢查核心檔案
echo "📁 核心檔案檢查:"
files=("package.json" "app.py" "unified_scraper.py" "public/songs_simplified.json" "public/singers_data.json")
for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file 缺失"
    fi
done

# 2. 檢查資料完整性
echo "📊 資料完整性檢查:"
if [[ -f "public/songs_simplified.json" ]]; then
    SONG_COUNT=$(python3 -c "import json; print(len(json.load(open('public/songs_simplified.json'))))" 2>/dev/null || echo "0")
    echo "  🎵 歌曲數量: $SONG_COUNT"
else
    echo "  ❌ 歌曲資料檔案不存在"
fi

if [[ -f "public/singers_data.json" ]]; then
    SINGER_COUNT=$(python3 -c "import json; print(len(json.load(open('public/singers_data.json'))))" 2>/dev/null || echo "0")
    echo "  🎤 歌手數量: $SINGER_COUNT"
else
    echo "  ❌ 歌手資料檔案不存在"
fi

# 3. 檢查 Python 依賴
echo "🐍 Python 依賴檢查:"
deps=("requests" "flask" "selenium")
for dep in "${deps[@]}"; do
    if python3 -c "import $dep" 2>/dev/null; then
        echo "  ✅ $dep"
    else
        echo "  ❌ $dep 未安裝"
    fi
done

# 4. 檢查過期檔案
echo "🧹 過期檔案檢查:"
if ls *.pid 1> /dev/null 2>&1; then
    echo "  ⚠️ 發現 PID 檔案，可能需要清理"
    ls *.pid
else
    echo "  ✅ 無過期 PID 檔案"
fi

# 5. 檢查網站狀態
echo "🌐 網站狀態檢查:"
if curl -s https://karaoke-search-theta.vercel.app/ | grep -q "卡拉OK"; then
    echo "  ✅ 前端網站正常"
else
    echo "  ❌ 前端網站異常"
fi

# 6. 檢查 Git 狀態
echo "📱 Git 狀態:"
if git status --porcelain | grep -q .; then
    echo "  ⚠️ 有未提交的變更"
    git status --short
else
    echo "  ✅ 工作目錄乾淨"
fi

echo "================================"
echo "✅ 健康檢查完成"