#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
啟動新的智能搜尋系統
"""

import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path

def check_dependencies():
    """檢查必要的依賴套件"""
    required_packages = ['flask', 'flask_cors', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少必要套件: {', '.join(missing_packages)}")
        print("🔧 請執行: pip install flask flask-cors requests")
        return False
    
    return True

def start_enhanced_api():
    """啟動增強版API服務"""
    try:
        print("🚀 啟動增強版API服務...")
        process = subprocess.Popen([
            sys.executable, 'enhanced_api.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服務啟動
        time.sleep(3)
        
        if process.poll() is None:  # 程序仍在運行
            print("✅ 增強版API服務已啟動 (端口: 5001)")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ API服務啟動失敗")
            print(f"錯誤: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ 啟動API服務時出錯: {e}")
        return None

def open_frontend():
    """開啟前端頁面"""
    try:
        frontend_path = Path('new_frontend.html').absolute()
        frontend_url = f"file://{frontend_path}"
        
        print(f"🌐 開啟前端頁面: {frontend_url}")
        webbrowser.open(frontend_url)
        return True
        
    except Exception as e:
        print(f"❌ 開啟前端頁面失敗: {e}")
        return False

def show_instructions():
    """顯示使用說明"""
    print("\n" + "="*60)
    print("🎵 智能卡拉OK搜尋系統 v2.0")
    print("="*60)
    print()
    print("✅ 系統已成功啟動！")
    print()
    print("📋 使用說明:")
    print("   1. 前端頁面會自動開啟")
    print("   2. 如果沒有自動開啟，請手動打開 'new_frontend.html'")
    print("   3. API 服務運行在: http://localhost:5001")
    print()
    print("🔍 搜尋功能:")
    print("   • 🧠 綜合搜尋: 整合所有資料源的智能搜尋")
    print("   • 🎤 歌手專搜: 專門搜尋特定歌手的完整作品")
    print()
    print("✨ 新功能亮點:")
    print("   • 多資料源整合 (本地+線上)")
    print("   • 智能模糊匹配")
    print("   • 信心度評分")
    print("   • 自動去重和合併")
    print("   • 優化的搜尋演算法")
    print()
    print("🎯 測試建議:")
    print("   • 試試搜尋 '周杰倫' - 應該會找到大量歌曲")
    print("   • 試試搜尋 '青花瓷' - 測試歌曲名稱搜尋")
    print("   • 試試搜尋 '愛情' - 測試關鍵字搜尋")
    print()
    print("⚠️  停止系統: 按 Ctrl+C")
    print("="*60)

def main():
    """主程序"""
    print("🔧 檢查系統環境...")
    
    # 檢查依賴
    if not check_dependencies():
        return
    
    # 檢查檔案
    if not os.path.exists('enhanced_api.py'):
        print("❌ 找不到 enhanced_api.py 檔案")
        return
    
    if not os.path.exists('new_frontend.html'):
        print("❌ 找不到 new_frontend.html 檔案")
        return
    
    print("✅ 環境檢查通過")
    
    # 啟動API服務
    api_process = start_enhanced_api()
    if not api_process:
        return
    
    # 開啟前端
    open_frontend()
    
    # 顯示說明
    show_instructions()
    
    try:
        # 保持程序運行
        while True:
            time.sleep(1)
            
            # 檢查API進程是否還在運行
            if api_process.poll() is not None:
                print("❌ API服務意外停止")
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止系統...")
        
        # 終止API進程
        if api_process and api_process.poll() is None:
            api_process.terminate()
            api_process.wait()
        
        print("✅ 系統已停止")

if __name__ == "__main__":
    main()