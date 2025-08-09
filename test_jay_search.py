#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試周杰倫搜尋功能
"""

import requests
import json

def test_search_apis():
    """測試所有搜尋API"""
    base_url = "http://127.0.0.1:5000"
    
    search_terms = ["周杰倫", "青花瓷", "稻香", "告白氣球"]
    
    for keyword in search_terms:
        print(f"\n🔍 測試搜尋: {keyword}")
        
        # 測試一般搜尋API
        try:
            response = requests.get(f"{base_url}/api/search?keyword={keyword}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    print(f"   📊 一般搜尋: 找到 {len(data['data'])} 首歌")
                else:
                    print(f"   ❌ 一般搜尋: 無結果")
            else:
                print(f"   ❌ 一般搜尋API錯誤: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 一般搜尋失敗: {e}")
        
        # 測試台灣KTV API
        try:
            response = requests.get(f"{base_url}/api/taiwan-ktv?keyword={keyword}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    print(f"   🎤 台灣KTV: 找到 {len(data['data'])} 首歌")
                    # 顯示前3首
                    for i, song in enumerate(data['data'][:3], 1):
                        print(f"      {i}. {song.get('name', 'N/A')} - {song.get('singer', 'N/A')} ({song.get('company', 'N/A')})")
                else:
                    print(f"   ❌ 台灣KTV: 無結果")
            else:
                print(f"   ❌ 台灣KTV API錯誤: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 台灣KTV搜尋失敗: {e}")

def check_local_database():
    """檢查本地資料庫中的周杰倫資料"""
    print("\n📚 檢查本地資料庫...")
    
    # 檢查歌手資料庫
    try:
        with open('public/singers_data.json', 'r', encoding='utf-8') as f:
            singers_data = json.load(f)
        
        if "周杰倫" in singers_data:
            jay_data = singers_data["周杰倫"]
            song_count = len(jay_data.get("歌曲清單", []))
            print(f"   🎤 歌手資料庫: 周杰倫有 {song_count} 首歌")
            
            # 顯示前5首
            songs = jay_data.get("歌曲清單", [])[:5]
            for i, song in enumerate(songs, 1):
                print(f"      {i}. {song.get('歌名', 'N/A')}")
        else:
            print("   ❌ 歌手資料庫中沒有周杰倫")
    except Exception as e:
        print(f"   ❌ 讀取歌手資料庫失敗: {e}")
    
    # 檢查一般歌曲資料庫
    try:
        with open('public/songs_simplified.json', 'r', encoding='utf-8') as f:
            songs_data = json.load(f)
        
        jay_songs = [song for song in songs_data if "周杰倫" in song.get("歌手", "")]
        print(f"   🎵 一般資料庫: 找到 {len(jay_songs)} 首周杰倫的歌")
        
        # 顯示前5首
        for i, song in enumerate(jay_songs[:5], 1):
            print(f"      {i}. {song.get('歌名', 'N/A')} - {song.get('公司', 'N/A')}")
            
    except Exception as e:
        print(f"   ❌ 讀取一般資料庫失敗: {e}")

if __name__ == "__main__":
    print("🔧 開始診斷周杰倫搜尋問題...")
    check_local_database()
    test_search_apis()