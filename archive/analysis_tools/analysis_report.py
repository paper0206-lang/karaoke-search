#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣KTV爬蟲完成時間和資源評估
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import quote
from datetime import datetime, timedelta

def estimate_completion():
    """評估爬蟲完成時間"""
    print("🔍 評估音圓公司總頁數...")
    
    # 測試最後頁數的方法：二分搜尋
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    company = "音圓"
    current_known = 6750  # 當前已知頁數
    
    # 嘗試找到最後一頁
    test_pages = [7000, 8000, 10000, 12000, 15000]
    
    last_valid_page = current_known
    
    for test_page in test_pages:
        try:
            print(f"測試第 {test_page} 頁...")
            url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={test_page}"
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                song_links = soup.select('a[href^="mv.aspx?id="]')
                
                if len(song_links) > 0:
                    last_valid_page = test_page
                    print(f"✅ 第 {test_page} 頁有數據 ({len(song_links)} 首歌)")
                else:
                    print(f"❌ 第 {test_page} 頁無數據")
                    break
            else:
                print(f"❌ 第 {test_page} 頁 HTTP {response.status_code}")
                break
                
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ 測試第 {test_page} 頁失敗: {e}")
            break
    
    return last_valid_page

def calculate_estimates():
    """計算各種估算"""
    
    # 當前狀態
    current_page = 6750
    songs_per_page = 50
    current_speed_pages_per_min = 23.9
    
    print("📊 當前爬取狀態:")
    print(f"   目前頁數: {current_page:,}")
    print(f"   每頁歌曲: {songs_per_page}")
    print(f"   目前總歌曲: {current_page * songs_per_page:,}")
    print(f"   爬取速度: {current_speed_pages_per_min:.1f} 頁/分鐘")
    print()
    
    # 嘗試估算總頁數
    print("🔍 估算音圓公司總頁數...")
    try:
        estimated_total_pages = estimate_completion()
        print(f"✅ 估算音圓公司總頁數: {estimated_total_pages:,} 頁")
        
        # 計算剩餘時間
        remaining_pages = estimated_total_pages - current_page
        remaining_minutes = remaining_pages / current_speed_pages_per_min
        remaining_hours = remaining_minutes / 60
        
        print(f"\n⏰ 音圓公司完成時間估算:")
        print(f"   剩餘頁數: {remaining_pages:,} 頁")
        print(f"   剩餘時間: {remaining_hours:.1f} 小時 ({remaining_minutes:.0f} 分鐘)")
        
        completion_time = datetime.now() + timedelta(minutes=remaining_minutes)
        print(f"   預計完成: {completion_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 計算總數據量
        total_songs_yinyuan = estimated_total_pages * songs_per_page
        print(f"\n🎵 音圓公司總歌曲估算: {total_songs_yinyuan:,} 首")
        
        # 21家公司的估算
        companies = [
            "音圓", "弘音", "金嗓", "音圓原廠", "瑞影", "點將家", "嘉揚", "音遊",
            "音影", "美華", "金影", "金嗓/投幣", "一級棒", "錢櫃", "好樂迪", "星據點",
            "銀櫃", "享溫馨", "大唐", "MV", "金嗓/家庭"
        ]
        
        # 假設其他公司平均有音圓的1/3數據量 (保守估算)
        avg_other_company_songs = total_songs_yinyuan // 3
        total_all_companies = total_songs_yinyuan + (len(companies) - 1) * avg_other_company_songs
        
        print(f"\n🏢 全部21家公司估算:")
        print(f"   假設其他公司平均: {avg_other_company_songs:,} 首/家")
        print(f"   總歌曲數估算: {total_all_companies:,} 首")
        
        # 完成全部公司需要的時間
        total_pages_all = total_all_companies // songs_per_page
        total_time_minutes = total_pages_all / current_speed_pages_per_min
        total_time_hours = total_time_minutes / 60
        total_time_days = total_time_hours / 24
        
        print(f"   總頁數估算: {total_pages_all:,} 頁")
        print(f"   完成全部需要: {total_time_days:.1f} 天 ({total_time_hours:.0f} 小時)")
        
        # 資源評估
        print(f"\n💾 資源需求估算:")
        
        # JSON文件大小估算 (每首歌約200-300字節)
        avg_bytes_per_song = 250
        total_json_size_mb = (total_all_companies * avg_bytes_per_song) / (1024 * 1024)
        
        print(f"   JSON文件大小: {total_json_size_mb:.1f} MB")
        print(f"   CSV文件大小: {total_json_size_mb * 0.8:.1f} MB (估算)")
        print(f"   總存儲需求: {total_json_size_mb * 2:.1f} MB")
        
        # 記憶體需求
        memory_per_song = 400  # 字節 (包含Python物件開銷)
        total_memory_mb = (total_all_companies * memory_per_song) / (1024 * 1024)
        
        print(f"   記憶體需求: {total_memory_mb:.1f} MB")
        
        if total_memory_mb > 1024:
            print(f"   ⚠️ 記憶體需求超過1GB，建議分批保存")
        
    except Exception as e:
        print(f"❌ 估算過程發生錯誤: {e}")
        
        # 基於當前速度的簡單估算
        print(f"\n📊 基於當前狀態的保守估算:")
        print(f"   如果音圓有10,000頁 (50萬首歌):")
        remaining_simple = 10000 - current_page
        time_simple = remaining_simple / current_speed_pages_per_min / 60
        print(f"   剩餘時間: {time_simple:.1f} 小時")
        
        print(f"\n   如果音圓有15,000頁 (75萬首歌):")
        remaining_simple = 15000 - current_page
        time_simple = remaining_simple / current_speed_pages_per_min / 60
        print(f"   剩餘時間: {time_simple:.1f} 小時")

if __name__ == "__main__":
    calculate_estimates()