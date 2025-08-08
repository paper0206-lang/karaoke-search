# -*- coding: utf-8 -*-
"""
新歌專用爬蟲 - 專門搜尋最新流行歌曲
使用方法: python3 new_songs_scraper.py
"""

import requests
import json
import time
import random
from urllib.parse import quote

def search_new_songs():
    """專門搜尋新歌和流行歌曲"""
    base_url = "https://song.corp.com.tw"
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://song.corp.com.tw/',
    }
    
    # 載入現有歌曲
    try:
        with open('public/songs_simplified.json', 'r', encoding='utf-8') as f:
            existing_songs = json.load(f)
        all_songs = {f"{s['歌名']}-{s['歌手']}-{s['編號']}": s for s in existing_songs}
        print(f"🎵 載入現有歌曲: {len(all_songs)} 首")
    except:
        all_songs = {}
        print("🎵 從空開始建立資料庫")
    
    # 專注於新歌的搜尋策略
    new_music_categories = {
        "2024熱門新歌手": [
            "告五人", "ØZI", "吳卓源", "9m88", "持修", "壞特", "孫盛希",
            "高爾宣", "LEO王", "陳零九", "顏人中", "宋念宇", "血肉果汁機"
        ],
        "新世代獨立樂團": [
            "草東沒有派對", "老王樂隊", "原子邦妮", "漂流出口", "落日飛車", 
            "透明雜誌", "理想混蛋", "Crispy脆樂團", "康士坦的變化球",
            "傷心欲絕", "巨獸搖滾", "麵包車", "拍謝少年"
        ],
        "新歌關鍵字": [
            "新歌", "熱門", "最新", "2024", "2023", "流行", "排行榜",
            "抖音", "TikTok", "viral", "爆紅", "翻唱", "remix"
        ],
        "時下流行詞": [
            "療癒", "chill", "vibe", "emo", "治癒系", "正能量", "負能量",
            "社恐", "焦慮", "放鬆", "躺平", "內捲", "佛系", "小確幸"
        ],
        "新世代生活": [
            "台北", "Taipei", "夏天", "海邊", "夜市", "熱浪", "咖啡廳",
            "下班", "週末", "假日", "旅行", "散步", "運動", "健身",
            "社群", "限動", "直播", "網紅", "youtuber"
        ],
        "網路流行語": [
            "很可以", "超讚", "絕了", "神曲", "洗腦", "單曲循環",
            "mood", "feel", "amazing", "awesome", "perfect"
        ]
    }
    
    print("🎵 開始搜尋新歌和流行歌曲...")
    new_found = 0
    total_searched = 0
    
    for category, terms in new_music_categories.items():
        print(f"\n🎯 搜尋類別: {category}")
        
        for term in terms:
            try:
                print(f"🔍 搜尋: {term}")
                total_searched += 1
                
                url = f"{base_url}/api/song.aspx"
                params = {
                    'company': '全部',
                    'cusType': 'searchList', 
                    'keyword': term
                }
                
                response = session.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list) and len(data) > 0:
                            category_new = 0
                            for song in data:
                                song_id = f"{song.get('name', '')}-{song.get('singer', '')}-{song.get('code', '')}"
                                if song_id not in all_songs:
                                    song_info = {
                                        '歌名': song.get('name', ''),
                                        '歌手': song.get('singer', ''),
                                        '編號': song.get('code', ''),
                                        '公司': song.get('company', '')
                                    }
                                    all_songs[song_id] = song_info
                                    category_new += 1
                                    new_found += 1
                            
                            if category_new > 0:
                                print(f"✅ 新增 {category_new} 首，目前總計: {len(all_songs)} 首")
                            else:
                                print(f"ℹ️  找到 {len(data)} 首，但都已存在")
                        else:
                            print("⚠️  無搜尋結果")
                    except json.JSONDecodeError:
                        print("❌ JSON 解析錯誤")
                else:
                    print(f"❌ HTTP 錯誤: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 搜尋 '{term}' 時發生錯誤: {e}")
            
            # 隨機延遲避免被封鎖
            time.sleep(random.uniform(1.5, 3))
            
            # 每10首新歌儲存一次
            if new_found > 0 and new_found % 10 == 0:
                save_songs(all_songs)
    
    # 最終儲存
    final_count = save_songs(all_songs)
    
    print(f"\n🎉 新歌搜尋完成！")
    print(f"🔍 總搜尋次數: {total_searched}")
    print(f"🆕 新增歌曲: {new_found} 首")
    print(f"📈 資料庫總計: {final_count} 首")
    print(f"🌐 網站: https://karaoke-search-theta.vercel.app")

def save_songs(all_songs):
    """儲存歌曲到檔案"""
    try:
        songs_list = list(all_songs.values())
        with open('public/songs_simplified.json', 'w', encoding='utf-8') as f:
            json.dump(songs_list, f, ensure_ascii=False, indent=2)
        
        print(f"💾 已儲存 {len(songs_list)} 首歌曲")
        return len(songs_list)
    except Exception as e:
        print(f"❌ 儲存失敗: {e}")
        return 0

if __name__ == "__main__":
    print("🎵 新歌專用爬蟲")
    print("=" * 30)
    search_new_songs()