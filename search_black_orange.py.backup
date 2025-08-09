# -*- coding: utf-8 -*-
import requests
import json

def search_black_orange_songs():
    """專門搜尋黑色柳丁的歌曲"""
    base_url = "https://song.corp.com.tw"
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://song.corp.com.tw/',
    }
    
    # 黑色柳丁的知名歌曲
    song_names = [
        "多愛我一天", "愛情逃兵", "男歌女唱", "天天想你", "看透你", 
        "我不會喜歡你", "當我們窩在一起", "想太多", "不是我的",
        "心電感應", "日不落", "愛上你", "回到最初", "OH MY GOD"
    ]
    
    # 載入現有歌曲
    try:
        with open('public/songs_simplified.json', 'r', encoding='utf-8') as f:
            existing_songs = json.load(f)
        all_songs = {f"{s['歌名']}-{s['歌手']}-{s['編號']}": s for s in existing_songs}
        print(f"載入現有歌曲: {len(all_songs)} 首")
    except:
        all_songs = {}
        print("從空開始")
    
    found_songs = []
    
    for song_name in song_names:
        try:
            print(f"搜尋歌曲: {song_name}")
            
            url = f"{base_url}/api/song.aspx"
            params = {
                'company': '全部',
                'cusType': 'searchList', 
                'keyword': song_name
            }
            
            response = session.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        # 找出黑色柳丁的歌曲
                        for song in data:
                            singer = song.get('singer', '').lower()
                            if '黑色柳丁' in singer or 'black orange' in singer or song.get('name') == song_name:
                                song_id = f"{song.get('name', '')}-{song.get('singer', '')}-{song.get('code', '')}"
                                if song_id not in all_songs:
                                    song_info = {
                                        '歌名': song.get('name', ''),
                                        '歌手': song.get('singer', ''),
                                        '編號': song.get('code', ''),
                                        '公司': song.get('company', '')
                                    }
                                    all_songs[song_id] = song_info
                                    found_songs.append(song_info)
                                    print(f"✅ 找到: {song_info}")
                        
                        print(f"搜尋結果: {len(data)} 首")
                    
                except json.JSONDecodeError:
                    print("JSON 解析錯誤")
            else:
                print(f"請求失敗: {response.status_code}")
                
        except Exception as e:
            print(f"搜尋 {song_name} 時發生錯誤: {e}")
        
        import time, random
        time.sleep(random.uniform(1, 2))
    
    # 儲存結果
    if found_songs:
        songs_list = list(all_songs.values())
        with open('public/songs_simplified.json', 'w', encoding='utf-8') as f:
            json.dump(songs_list, f, ensure_ascii=False, indent=2)
        print(f"✅ 儲存完成！總計: {len(songs_list)} 首歌曲")
    
    print(f"\n黑色柳丁相關歌曲:")
    for song in found_songs:
        print(f"- {song['歌名']} by {song['歌手']} ({song['公司']}: {song['編號']})")

if __name__ == "__main__":
    search_black_orange_songs()