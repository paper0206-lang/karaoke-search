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
    
    # 搜尋關鍵字 - 包含新歌和經典歌曲
    search_terms = [
        # 2023-2024 熱門新歌手/關鍵字
        "告五人", "ØZI", "吳卓源", "9m88", "持修", "血肉果汁機", "康士坦的變化球",
        "理想混蛋", "Crispy脆樂團", "deca joins", "傷心欲絕", "高爾宣", "LEO王",
        "壞特", "孫盛希", "陳零九", "顏人中", "宋念宇", "新歌", "熱門", "最新",
        
        # 2024流行關鍵字
        "Taipei", "台北", "夏天", "海邊", "夜市", "熱浪", "療癒", "chill", "vibe",
        "社群", "限動", "直播", "網紅", "youtuber", "TikTok", "抖音",
        
        # 經典歌手持續更新
        "林憶蓮", "彭佳慧", "張韶涵", "楊丞琳", "田馥甄", "梁靜茹",
        "孫燕姿", "蕭亞軒", "容祖兒", "謝霆鋒", "古巨基", "陳奕迅",
        "黃品源", "黃小琥", "辛曉琪", "萬芳", "姜育恆", "費玉清",
        "鳳飛飛", "蔡琴", "齊豫", "潘越雲", "黃鶯鶯", "蘇芮",
        
        # 樂團（包含新團）
        "Mayday", "sodagreen", "1976", "八三夭", "茄子蛋", "滅火器",
        "董事長樂團", "脫拉庫", "四分衛", "閃靈", "Chthonic", "草東沒有派對",
        "老王樂隊", "原子邦妮", "漂流出口", "落日飛車", "透明雜誌",
        
        # 新世代關鍵字
        "社恐", "焦慮", "療癒", "放鬆", "正能量", "負能量", "emo", "治癒系",
        "下班", "週末", "假日", "旅行", "散步", "運動", "健身", "瑜伽",
        
        # 傳統情感詞彙
        "思念", "回憶", "青春", "校園", "畢業", "離別", "重逢",
        "下雨", "晴天", "星空", "藍天", "大海", "河流", "山峰",
        "咖啡", "酒", "菸", "花", "樹", "鳥", "貓", "狗"
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