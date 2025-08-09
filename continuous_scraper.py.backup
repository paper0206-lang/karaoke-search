# -*- coding: utf-8 -*-
"""
持續爬取腳本 - 自動擴展歌曲資料庫
使用方法: python3 continuous_scraper.py
"""

import requests
import json
import time
import random
from urllib.parse import quote
from datetime import datetime

def continuous_scrape(max_songs=10000):
    """持續爬取直到達到指定歌曲數量"""
    
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
    
    # 更全面的搜尋關鍵字（包含新歌）
    search_categories = {
        "2024新歌手": [
            "告五人", "ØZI", "吳卓源", "9m88", "持修", "血肉果汁機", "康士坦的變化球",
            "理想混蛋", "Crispy脆樂團", "deca joins", "傷心欲絕", "高爾宣", "LEO王",
            "壞特", "孫盛希", "陳零九", "顏人中", "宋念宇", "草東沒有派對", "老王樂隊"
        ],
        "新世代樂團": [
            "原子邦妮", "漂流出口", "落日飛車", "透明雜誌", "血肉果汁機", "理想混蛋",
            "Crispy脆樂團", "康士坦的變化球", "傷心欲絕", "巨獸搖滾", "麵包車"
        ],
        "流行新歌關鍵字": [
            "新歌", "熱門", "最新", "2024", "2023", "Taipei", "台北", "夏天", "海邊",
            "夜市", "熱浪", "療癒", "chill", "vibe", "社群", "限動", "直播"
        ],
        "新世代情感詞": [
            "社恐", "焦慮", "療癒", "放鬆", "正能量", "負能量", "emo", "治癒系",
            "下班", "週末", "假日", "躺平", "內捲", "佛系", "小確幸"
        ],
        "經典歌手": [
            "鄧麗君", "張學友", "劉德華", "郭富城", "黎明", "張國榮",
            "梅艷芳", "蔡琴", "鳳飛飛", "費玉清", "齊豫", "蘇芮"
        ],
        "流行歌手": [
            "周杰倫", "蔡依林", "林俊傑", "張惠妹", "王力宏", "陶喆",
            "孫燕姿", "梁靜茹", "田馥甄", "楊丞琳", "蕭亞軒", "張韶涵"
        ],
        "搖滾樂團": [
            "五月天", "蘇打綠", "信樂團", "動力火車", "F.I.R", "飛兒樂團",
            "八三夭", "茄子蛋", "滅火器", "四分衛", "黑色柳丁", "董事長樂團"
        ],
        "創作歌手": [
            "李宗盛", "羅大佑", "伍佰", "張宇", "庾澄慶", "齊秦",
            "張雨生", "黃品源", "黃小琥", "辛曉琪", "萬芳", "林憶蓮"
        ],
        "情感關鍵字": [
            "愛情", "思念", "想念", "回憶", "青春", "夢想", "希望",
            "孤單", "寂寞", "快樂", "傷心", "幸福", "痛苦", "離別"
        ],
        "生活關鍵字": [
            "朋友", "家人", "媽媽", "爸爸", "故鄉", "家鄉", "學校",
            "工作", "旅行", "下雨", "晴天", "星空", "月亮", "太陽"
        ],
        "常用字詞": [
            "一", "二", "三", "天", "年", "月", "日", "春", "夏", "秋", "冬",
            "東", "南", "西", "北", "大", "小", "新", "老", "好", "美"
        ]
    }
    
    start_time = datetime.now()
    total_searches = 0
    
    print(f"🚀 開始爬取，目標: {max_songs} 首歌曲")
    print(f"📅 開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 依序搜尋各類別
    for category, terms in search_categories.items():
        if len(all_songs) >= max_songs:
            break
            
        print(f"\n🎯 正在搜尋類別: {category}")
        
        for term in terms:
            if len(all_songs) >= max_songs:
                break
                
            try:
                print(f"🔍 搜尋: {term}")
                total_searches += 1
                
                url = f"{base_url}/api/song.aspx"
                params = {
                    'company': '全部',
                    'cusType': 'searchList',
                    'keyword': term
                }
                
                response = session.get(url, params=params, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            new_count = 0
                            for song in data:
                                song_id = f"{song.get('name', '')}-{song.get('singer', '')}-{song.get('code', '')}"
                                if song_id not in all_songs:
                                    all_songs[song_id] = {
                                        '歌名': song.get('name', ''),
                                        '歌手': song.get('singer', ''),
                                        '編號': song.get('code', ''),
                                        '公司': song.get('company', '')
                                    }
                                    new_count += 1
                            
                            if new_count > 0:
                                print(f"✅ 新增 {new_count} 首，目前總計: {len(all_songs)} 首")
                                
                                # 每增加50首歌曲儲存一次
                                if len(all_songs) % 50 == 0:
                                    save_progress(all_songs)
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
            delay = random.uniform(2, 5)
            time.sleep(delay)
            
            # 每10次搜尋顯示進度
            if total_searches % 10 == 0:
                elapsed = datetime.now() - start_time
                print(f"📊 已搜尋 {total_searches} 次，收集 {len(all_songs)} 首歌，耗時 {elapsed}")
    
    # 最終儲存
    final_count = save_progress(all_songs)
    
    end_time = datetime.now()
    elapsed_time = end_time - start_time
    
    print(f"\n🎉 爬取完成！")
    print(f"📈 總歌曲數: {final_count} 首")
    print(f"🔍 總搜尋次數: {total_searches}")
    print(f"⏱️  總耗時: {elapsed_time}")
    print(f"⚡ 平均每首歌耗時: {elapsed_time.total_seconds()/final_count:.2f} 秒")

def save_progress(all_songs):
    """儲存進度到檔案"""
    try:
        songs_list = list(all_songs.values())
        with open('public/songs_simplified.json', 'w', encoding='utf-8') as f:
            json.dump(songs_list, f, ensure_ascii=False, indent=2)
        
        print(f"💾 已儲存 {len(songs_list)} 首歌曲到資料庫")
        return len(songs_list)
    except Exception as e:
        print(f"❌ 儲存失敗: {e}")
        return 0

if __name__ == "__main__":
    print("🎤 卡拉OK 歌曲資料庫擴展工具")
    print("=" * 50)
    
    # 設定目標歌曲數量
    target = input("請輸入目標歌曲數量 (預設: 10000): ").strip()
    if not target.isdigit():
        target = 10000
    else:
        target = int(target)
    
    continuous_scrape(target)