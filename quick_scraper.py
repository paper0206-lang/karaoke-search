# -*- coding: utf-8 -*-
import requests
import json
import time
import random
from urllib.parse import quote

def search_specific_songs():
    """搜尋特定歌曲，包括黑色柳丁"""
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
        print(f"載入現有歌曲: {len(all_songs)} 首")
    except:
        all_songs = {}
        print("從空開始")
    
    # 搜尋關鍵字
    search_terms = [
        "黑色柳丁", "柳丁", "F.I.R", "飛兒樂團", "信樂團", "五月天", 
        "蔡依林", "林俊傑", "王力宏", "陶喆", "張惠妹", "周杰倫",
        "張學友", "劉德華", "郭富城", "黎明", "鄧麗君", "張宇",
        "庾澄慶", "伍佰", "羅大佑", "李宗盛", "齊秦", "張雨生",
        "童安格", "潘瑋柏", "羅志祸", "蘇打綠", "動力火車"
    ]
    
    new_found = 0
    
    for term in search_terms:
        try:
            print(f"搜尋: {term}")
            
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
                    if isinstance(data, list):
                        print(f"找到 {len(data)} 首歌曲")
                        
                        for song in data:
                            song_id = f"{song.get('name', '')}-{song.get('singer', '')}-{song.get('code', '')}"
                            if song_id not in all_songs:
                                all_songs[song_id] = {
                                    '歌名': song.get('name', ''),
                                    '歌手': song.get('singer', ''),
                                    '編號': song.get('code', ''),
                                    '公司': song.get('company', '')
                                }
                                new_found += 1
                        
                        # 即時儲存
                        songs_list = list(all_songs.values())
                        with open('public/songs_simplified.json', 'w', encoding='utf-8') as f:
                            json.dump(songs_list, f, ensure_ascii=False, indent=2)
                        print(f"已儲存，目前總計: {len(songs_list)} 首")
                    else:
                        print("沒有找到結果")
                        
                except json.JSONDecodeError:
                    print("JSON 解析錯誤")
            else:
                print(f"請求失敗: {response.status_code}")
                
        except Exception as e:
            print(f"搜尋 {term} 時發生錯誤: {e}")
        
        # 隨機延遲
        time.sleep(random.uniform(1.5, 3))
    
    print(f"✅ 完成！新增了 {new_found} 首歌曲")
    print(f"總計: {len(all_songs)} 首歌曲")
    
    # 檢查是否找到黑色柳丁
    for song in all_songs.values():
        if '黑色柳丁' in song['歌手'] or '柳丁' in song['歌手']:
            print(f"✅ 找到黑色柳丁歌曲: {song}")

if __name__ == "__main__":
    search_specific_songs()