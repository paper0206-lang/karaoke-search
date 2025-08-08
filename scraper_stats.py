#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
爬蟲統計工具 - 分析歌曲資料庫
使用方法: python3 scraper_stats.py
"""

import json
import os
from datetime import datetime
from collections import Counter

def analyze_database():
    """分析歌曲資料庫"""
    
    print("🎤 卡拉OK資料庫統計分析")
    print("=" * 40)
    
    # 檢查檔案是否存在
    if not os.path.exists('public/songs_simplified.json'):
        print("❌ 找不到歌曲資料檔案")
        return
    
    try:
        with open('public/songs_simplified.json', 'r', encoding='utf-8') as f:
            songs = json.load(f)
        
        print(f"\n📊 基本統計:")
        print(f"   總歌曲數量: {len(songs):,} 首")
        
        # 按公司統計
        companies = Counter(song.get('公司', '未知') for song in songs)
        print(f"   涵蓋公司: {len(companies)} 家")
        
        # 按歌手統計
        singers = Counter(song.get('歌手', '未知') for song in songs)
        print(f"   收錄歌手: {len(singers)} 位")
        
        # 檔案資訊
        file_size = os.path.getsize('public/songs_simplified.json')
        file_size_mb = file_size / (1024 * 1024)
        print(f"   檔案大小: {file_size_mb:.2f} MB")
        
        # 最後修改時間
        mtime = os.path.getmtime('public/songs_simplified.json')
        last_modified = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"   最後更新: {last_modified}")
        
        print(f"\n🏢 各公司歌曲數量 (前10名):")
        for company, count in companies.most_common(10):
            print(f"   {company}: {count:,} 首")
        
        print(f"\n🎙️ 熱門歌手 (前10名):")
        for singer, count in singers.most_common(10):
            print(f"   {singer}: {count} 首")
        
        # 檢查重複
        song_titles = [song.get('歌名', '') for song in songs]
        unique_titles = len(set(song_titles))
        duplicate_titles = len(song_titles) - unique_titles
        
        print(f"\n🔍 資料品質:")
        print(f"   獨特歌名: {unique_titles:,}")
        print(f"   重複歌名: {duplicate_titles:,}")
        print(f"   重複率: {duplicate_titles/len(songs)*100:.1f}%")
        
        # 搜尋建議
        print(f"\n💡 熱門搜尋建議:")
        popular_words = []
        for song in songs[:100]:  # 分析前100首歌
            title = song.get('歌名', '')
            for char in title:
                if '\u4e00' <= char <= '\u9fff':  # 中文字符
                    popular_words.append(char)
        
        word_counter = Counter(popular_words)
        print("   常見字詞: " + " ".join([f"{word}({count})" for word, count in word_counter.most_common(10)]))
        
        # 增長趨勢（如果有歷史記錄）
        if os.path.exists('auto_update.log'):
            print(f"\n📈 增長趨勢:")
            try:
                with open('auto_update.log', 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    if '目前總計:' in log_content:
                        import re
                        counts = re.findall(r'目前總計: (\d+) 首', log_content)
                        if len(counts) >= 2:
                            start_count = int(counts[0])
                            end_count = int(counts[-1])
                            growth = end_count - start_count
                            print(f"   本次增長: +{growth:,} 首")
                        else:
                            print("   增長數據不足")
                    else:
                        print("   沒有增長記錄")
            except Exception as e:
                print(f"   無法讀取增長數據: {e}")
        
    except Exception as e:
        print(f"❌ 分析失敗: {e}")

def check_scraper_status():
    """檢查爬蟲運行狀態"""
    import subprocess
    
    print(f"\n🤖 爬蟲狀態:")
    try:
        # 檢查是否有爬蟲程序在運行
        result = subprocess.run(['pgrep', '-f', 'auto_update_database.sh|quick_scraper.py'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            print("   ✅ 爬蟲程序正在運行")
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                print(f"      PID: {pid}")
        else:
            print("   ⏹️  爬蟲程序未運行")
    except Exception as e:
        print(f"   ❓ 無法檢查狀態: {e}")

if __name__ == "__main__":
    analyze_database()
    check_scraper_status()
    
    print(f"\n🌐 網站: https://karaoke-search-theta.vercel.app")
    print(f"📋 監控命令: ./monitor_scraper.sh")
    print(f"🔄 重新統計: python3 scraper_stats.py")