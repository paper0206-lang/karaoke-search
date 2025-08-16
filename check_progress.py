#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音圓爬蟲進度監控工具
"""

import os
import json
import glob
from datetime import datetime
import subprocess

def check_progress():
    """檢查音圓爬蟲進度"""
    print("🎵 音圓爬蟲進度監控")
    print("=" * 50)
    
    # 檢查進程狀態
    try:
        result = subprocess.run(['pgrep', '-f', 'auto_scraper.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 爬蟲狀態: 正在運行")
            pids = result.stdout.strip().split('\n')
            print(f"📍 進程ID: {', '.join(pids)}")
        else:
            print("❌ 爬蟲狀態: 未運行")
    except:
        print("⚠️ 無法檢查進程狀態")
    
    # 檢查批次文件
    if os.path.exists('auto_results'):
        batch_files = glob.glob('auto_results/T*.json')
        total_files = len(batch_files)
        print(f"📁 批次文件: {total_files} 個")
        
        if batch_files:
            # 計算總歌曲數
            total_songs = 0
            latest_pages = {}
            
            for file in batch_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        total_songs += len(data)
                        
                        # 獲取線程ID和最新頁面
                        if data:
                            thread_id = data[0].get('thread', 0)
                            max_page = max(song.get('page', 0) for song in data)
                            if thread_id not in latest_pages or max_page > latest_pages[thread_id]:
                                latest_pages[thread_id] = max_page
                except:
                    continue
            
            print(f"🎵 總歌曲數: {total_songs:,} 首")
            
            # 顯示各線程進度
            print(f"\n📊 各線程進度:")
            for thread_id in sorted(latest_pages.keys()):
                page = latest_pages[thread_id]
                progress = (page / 2500) * 100  # 每線程2500頁
                print(f"   線程{thread_id:2d}: 第{page:5,}頁 ({progress:5.1f}%)")
            
            # 整體進度
            if latest_pages:
                avg_page = sum(latest_pages.values()) / len(latest_pages)
                total_progress = (avg_page / 25000) * 100
                print(f"\n🎯 整體進度: {total_progress:.1f}% (平均第{avg_page:,.0f}頁)")
                
                # 預估完成時間
                if total_progress > 0:
                    songs_per_hour = 74413  # 基於實際表現
                    remaining_songs = (25000 - avg_page) * 50
                    remaining_hours = remaining_songs / songs_per_hour
                    
                    if remaining_hours > 1:
                        print(f"⏰ 預估剩餘: {remaining_hours:.1f} 小時")
                    else:
                        print(f"⏰ 預估剩餘: {remaining_hours*60:.0f} 分鐘")
    
    # 檢查最終文件
    final_files = glob.glob('音圓完整數據_*.json')
    if final_files:
        latest_file = max(final_files, key=os.path.getmtime)
        file_size = os.path.getsize(latest_file) / (1024*1024)  # MB
        print(f"\n📄 最終文件: {os.path.basename(latest_file)}")
        print(f"💾 文件大小: {file_size:.1f} MB")
        
        # 統計最終文件歌曲數
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                lines = sum(1 for line in f if '"公司"' in line)
                print(f"🎵 已合併歌曲: {lines:,} 首")
        except:
            print("⚠️ 無法讀取最終文件統計")
    
    print(f"\n⏰ 檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    check_progress()