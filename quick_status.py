#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速狀態檢查工具 - 一行輸出當前進度
"""

import os
import json
import glob
import subprocess

def quick_status():
    # 檢查進程
    try:
        result = subprocess.run(['pgrep', '-f', 'auto_scraper.py'], 
                              capture_output=True, text=True)
        running = "🟢" if result.returncode == 0 else "🔴"
    except:
        running = "❓"
    
    # 統計文件和歌曲
    if os.path.exists('auto_results'):
        batch_files = glob.glob('auto_results/T*.json')
        total_files = len(batch_files)
        
        total_songs = 0
        max_pages = []
        
        for file in batch_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_songs += len(data)
                    if data:
                        max_page = max(song.get('page', 0) for song in data)
                        max_pages.append(max_page)
            except:
                continue
        
        if max_pages:
            avg_page = sum(max_pages) / len(max_pages)
            progress = (avg_page / 25000) * 100
            remaining_hours = ((25000 - avg_page) * 50) / 74413
            
            print(f"{running} 進度:{progress:5.1f}% 第{avg_page:,.0f}頁 歌曲:{total_songs:,}首 剩餘:{remaining_hours:.1f}h")
        else:
            print(f"{running} 初始化中... 文件:{total_files}個")
    else:
        print(f"{running} 無數據目錄")

if __name__ == "__main__":
    quick_status()