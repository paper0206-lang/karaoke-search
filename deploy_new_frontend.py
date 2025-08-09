#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署新前端到 GitHub 和 Vercel
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd, description):
    """執行命令並顯示結果"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ {description} 成功")
            if result.stdout.strip():
                print(f"   📝 {result.stdout.strip()}")
        else:
            print(f"   ❌ {description} 失敗")
            if result.stderr.strip():
                print(f"   💥 {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"   💥 執行失敗: {e}")
        return False

def main():
    """主部署程序"""
    print("🚀 部署新前端系統到 GitHub")
    print("=" * 50)
    
    # 檢查是否在正確的目錄
    if not os.path.exists('.git'):
        print("❌ 不在 Git 倉庫中，請確認目錄正確")
        return False
    
    # 添加新檔案到 Git
    print("📦 準備新前端檔案...")
    files_to_add = [
        "new_frontend.html",
        "enhanced_api.py", 
        "start_new_system.py",
        "test_new_system.py"
    ]
    
    for file in files_to_add:
        if os.path.exists(file):
            success = run_command(f"git add {file}", f"添加 {file}")
            if not success:
                print(f"⚠️ 無法添加 {file}，但繼續執行...")
        else:
            print(f"⚠️ 檔案 {file} 不存在")
    
    # 添加其他重要檔案
    other_files = [
        "DATABASE_ARCHITECTURE_ANALYSIS.md",
        "enhanced_singer_scraper.py",
        "database_unifier.py",
        "unified_scraper.py"
    ]
    
    for file in other_files:
        if os.path.exists(file):
            run_command(f"git add {file}", f"添加 {file}")
    
    # 檢查是否有檔案要提交
    result = subprocess.run("git diff --cached --name-only", shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        print("⚠️ 沒有檔案需要提交")
        return False
    
    print(f"\n📋 準備提交的檔案:")
    for file in result.stdout.strip().split('\n'):
        print(f"   • {file}")
    
    # 創建提交訊息
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_message = f"""🎵 新增智能搜尋系統 v2.0

✨ 主要新功能:
- 🧠 多資料源智能搜尋引擎
- 🎯 模糊匹配與信心度評分  
- 🎨 全新響應式前端介面
- 📊 整合本地+線上資料庫
- ⚡ 大幅提升搜尋準確率

📁 新增檔案:
- new_frontend.html (全新前端)
- enhanced_api.py (增強版API)  
- start_new_system.py (一鍵啟動)
- test_new_system.py (完整測試)

🔧 Generated with Claude Code
"""
    
    # 提交變更
    success = run_command(f'git commit -m "{commit_message}"', "提交變更")
    if not success:
        print("❌ 提交失敗")
        return False
    
    # 推送到 GitHub
    success = run_command("git push origin main", "推送到 GitHub")
    if not success:
        print("❌ 推送失敗")
        return False
    
    print("\n🎉 部署成功！")
    print("=" * 50)
    print("✅ 新前端系統已成功推送到 GitHub")
    print()
    print("📡 GitHub 網址:")
    print("   https://github.com/[your-username]/karaoke-search")
    print()
    print("🌐 如果有設定 Vercel 自動部署，")
    print("   新版本將會在幾分鐘內自動更新到:")
    print("   https://karaoke-search-theta.vercel.app/")
    print()
    print("💡 測試新功能:")
    print("   1. 等待 Vercel 部署完成")
    print("   2. 開啟線上網址測試新搜尋功能")
    print("   3. 本地測試: python3 start_new_system.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 部署完成，可以開始使用新系統了！")
    else:
        print("\n❌ 部署過程中遇到問題，請檢查錯誤訊息")