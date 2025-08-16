#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試盧廣仲搜索結果
檢查為什麼台灣點歌網只找到42筆而不是更多
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import json

def debug_lu_search():
    """調試盧廣仲搜索"""
    
    base_url = "https://song.corp.com.tw"
    singer_name = "盧廣仲"
    
    # 檢查我們資料庫中的盧廣仲
    print("📊 我們資料庫中的盧廣仲:")
    try:
        with open('public/singers_data.json', 'r', encoding='utf-8') as f:
            singers_data = json.load(f)
        
        if singer_name in singers_data:
            lu_info = singers_data[singer_name]
            songs = lu_info.get('歌曲清單', [])
            
            print(f"   歌曲數: {len(songs)} 首")
            
            # 統計KTV編號
            total_entries = 0
            companies = set()
            
            for song in songs:
                entries = song.get('編號資訊', [])
                total_entries += len(entries)
                for entry in entries:
                    companies.add(entry.get('公司', ''))
            
            print(f"   KTV編號: {total_entries} 筆")
            print(f"   KTV公司: {len(companies)} 家")
            print(f"   公司列表: {', '.join(sorted(companies))}")
            
            # 顯示前幾首歌
            print(f"\n🎵 歌曲列表:")
            for i, song in enumerate(songs[:5]):
                song_name = song.get('歌名', '')
                entries = song.get('編號資訊', [])
                print(f"   {i+1}. {song_name} - {len(entries)}個編號")
    
    except Exception as e:
        print(f"❌ 讀取失敗: {e}")
    
    # 測試台灣點歌網搜索
    print(f"\n🔍 台灣點歌網搜索測試:")
    
    # 測試幾個主要KTV公司
    test_companies = ["錢櫃", "好樂迪", "金嗓"]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    for company in test_companies:
        try:
            search_url = f"{base_url}/songs.aspx?company={quote(company)}&singer={quote(singer_name)}"
            print(f"\n🎯 測試 {company}:")
            print(f"   URL: {search_url}")
            
            response = session.get(search_url, timeout=15)
            response.encoding = "utf-8"
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # 檢查頁面內容
                print(f"   狀態: {response.status_code} OK")
                print(f"   頁面大小: {len(response.text)} 字符")
                
                # 尋找歌曲連結
                song_links = soup.select('a[href^="mv.aspx?id="]')
                print(f"   找到連結: {len(song_links)} 個")
                
                # 顯示前幾個結果
                for i, link in enumerate(song_links[:3]):
                    try:
                        raw_text = link.get_text().strip()
                        parts = raw_text.split('\n')
                        
                        if len(parts) >= 2:
                            number = parts[0].strip()
                            song_name = parts[1].strip()
                            print(f"     {i+1}. {number} - {song_name}")
                        else:
                            print(f"     {i+1}. 格式異常: {raw_text}")
                    except:
                        print(f"     {i+1}. 解析失敗")
                
                # 檢查是否有其他格式的歌曲資訊
                all_links = soup.find_all('a')
                mv_links = [link for link in all_links if 'mv.aspx' in str(link.get('href', ''))]
                print(f"   總mv.aspx連結: {len(mv_links)} 個")
                
                # 檢查頁面是否有"沒有找到"之類的訊息
                page_text = soup.get_text()
                if "沒有" in page_text or "not found" in page_text.lower():
                    print(f"   ⚠️ 頁面包含'沒有找到'訊息")
                
            else:
                print(f"   ❌ HTTP錯誤: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 搜索失敗: {e}")
    
    print(f"\n💡 分析結論:")
    print(f"   如果台灣點歌網結果明顯少於我們的數據，")
    print(f"   可能原因：")
    print(f"   1. 網站搜索算法變化")
    print(f"   2. 歌手名稱匹配問題")
    print(f"   3. 頁面結構改變")
    print(f"   4. 分頁或限制顯示數量")

if __name__ == "__main__":
    debug_lu_search()