#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌手專用爬蟲 - 無上限完整收集單一歌手的所有歌曲
使用方法: python3 singer_scraper.py
"""

import requests
import json
import time
import random
from urllib.parse import quote
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from collections import defaultdict

class SingerScraper:
    def __init__(self, max_workers=2):
        self.max_workers = max_workers
        self.session_pool = []
        self.all_songs = {}
        self.singer_stats = defaultdict(int)
        self.lock = threading.Lock()
        self.base_url = "https://song.corp.com.tw"
        
        # 初始化session池
        for _ in range(max_workers):
            session = requests.Session()
            session.headers.update({
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://song.corp.com.tw/',
                'X-Requested-With': 'XMLHttpRequest',
            })
            self.session_pool.append(session)
    
    def _get_random_user_agent(self):
        """獲取隨機User-Agent"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/605.1.15',
        ]
        return random.choice(agents)
    
    def get_all_companies(self):
        """取得所有卡拉OK公司列表"""
        return ['全部', '錢櫃', '好樂迪', '銀櫃', '音圓', '金嗓', '弘音', '星據點', '音霸', '大東', '點將家']
    
    def search_company_exhaustive(self, company, singer_name):
        """徹底搜尋單一公司的歌手歌曲 - 突破50首限制"""
        print(f"  🔍 搜尋 {company} 的 {singer_name} 歌曲...")
        all_company_results = []
        
        # 策略1: 直接搜尋歌手名
        results1 = self.search_single_method(company, singer_name)
        if results1:
            all_company_results.extend(results1)
            print(f"    📝 策略1: 找到 {len(results1)} 首")
        
        # 策略2: 搜尋歌手名的部分字詞
        if len(singer_name) > 2:
            for i in range(len(singer_name)):
                partial_name = singer_name[i:i+2] if i+2 <= len(singer_name) else singer_name[i:]
                if len(partial_name) >= 2:
                    results2 = self.search_single_method(company, partial_name)
                    if results2:
                        # 過濾出真正是目標歌手的歌曲
                        filtered_results = []
                        for song in results2:
                            song_singer = song.get('singer', '').strip()
                            if singer_name in song_singer or song_singer in singer_name:
                                filtered_results.append(song)
                        
                        if filtered_results:
                            all_company_results.extend(filtered_results)
                            print(f"    📝 策略2({partial_name}): 找到 {len(filtered_results)} 首")
        
        # 策略3: 嘗試不同的搜尋類型
        search_types = ['searchList', 'newSong', 'hotSong']
        for search_type in search_types:
            if search_type != 'searchList':  # searchList已經在策略1用過了
                results3 = self.search_single_method(company, singer_name, search_type)
                if results3:
                    filtered_results = []
                    for song in results3:
                        song_singer = song.get('singer', '').strip()
                        if singer_name in song_singer or song_singer in singer_name:
                            filtered_results.append(song)
                    
                    if filtered_results:
                        all_company_results.extend(filtered_results)
                        print(f"    📝 策略3({search_type}): 找到 {len(filtered_results)} 首")
        
        # 去重
        seen_songs = set()
        unique_results = []
        for song in all_company_results:
            song_key = f"{song.get('name', '')}-{song.get('code', '')}"
            if song_key not in seen_songs:
                seen_songs.add(song_key)
                unique_results.append(song)
        
        total_found = len(unique_results)
        if total_found > 0:
            print(f"    ✅ {company}: 總共找到 {total_found} 首歌曲")
        else:
            print(f"    ❌ {company}: 無相關歌曲")
        
        return unique_results
    
    def search_single_method(self, company, keyword, search_type='searchList'):
        """單一搜尋方法"""
        try:
            session = self.session_pool[0]
            url = f"{self.base_url}/api/song.aspx"
            params = {
                'company': company,
                'cusType': search_type,
                'keyword': keyword
            }
            
            time.sleep(random.uniform(0.8, 1.5))
            response = session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and data:
                    return data
            
            return []
            
        except Exception as e:
            print(f"      💥 搜尋失敗({search_type}): {str(e)}")
            return []
    
    def search_singer_comprehensive(self, singer_name):
        """全面搜尋歌手 - 無上限收集所有歌曲"""
        print(f"\n🎤 開始全面收集歌手: {singer_name}")
        start_time = datetime.now()
        
        companies = self.get_all_companies()
        all_results = []
        
        for company in companies:
            company_results = self.search_company_exhaustive(company, singer_name)
            all_results.extend(company_results)
        
        # 處理和去重所有結果
        unique_songs = self.process_singer_results(singer_name, all_results)
        
        end_time = datetime.now()
        elapsed = end_time - start_time
        
        print(f"\n🎉 {singer_name} 收集完成!")
        print(f"📊 總共找到: {len(unique_songs)} 首歌曲")
        print(f"⏱️  耗時: {elapsed}")
        
        return unique_songs
    
    def process_singer_results(self, singer_name, all_results):
        """處理歌手搜尋結果並去重"""
        seen_songs = {}  # 用於去重和合併不同編號
        
        for song in all_results:
            song_name = song.get('name', '').strip()
            song_singer = song.get('singer', '').strip()
            song_code = song.get('code', '').strip()
            song_company = song.get('company', '').strip()
            song_lang = song.get('lang', '').strip()
            
            if not song_name or not song_singer:
                continue
            
            # 使用歌名+歌手作為唯一識別
            song_key = f"{song_name}--{song_singer}"
            
            if song_key not in seen_songs:
                seen_songs[song_key] = {
                    '歌名': song_name,
                    '歌手': song_singer,
                    '語言': song_lang,
                    '編號資訊': []  # 存放不同公司的編號
                }
            
            # 添加編號資訊
            if song_code and song_company:
                code_info = {
                    '公司': song_company,
                    '編號': song_code
                }
                
                # 檢查是否已存在相同的公司編號
                existing = False
                for existing_code in seen_songs[song_key]['編號資訊']:
                    if existing_code['公司'] == song_company and existing_code['編號'] == song_code:
                        existing = True
                        break
                
                if not existing:
                    seen_songs[song_key]['編號資訊'].append(code_info)
        
        # 排序編號資訊（錢櫃、好樂迪、銀櫃優先）
        priority_companies = ['錢櫃', '好樂迪', '銀櫃', '音圓', '金嗓', '弘音', '星據點', '音霸', '大東', '點將家']
        
        for song_data in seen_songs.values():
            song_data['編號資訊'].sort(key=lambda x: (
                priority_companies.index(x['公司']) if x['公司'] in priority_companies else 999,
                x['公司'],
                x['編號']
            ))
        
        return list(seen_songs.values())
    
    def save_singer_data(self, singer_name, songs_data):
        """儲存歌手資料"""
        try:
            # 載入現有的歌手資料庫
            try:
                with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                    all_singers_data = json.load(f)
            except:
                all_singers_data = {}
            
            # 更新該歌手的資料
            all_singers_data[singer_name] = {
                '歌手名稱': singer_name,
                '歌曲數量': len(songs_data),
                '更新時間': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '歌曲清單': songs_data
            }
            
            # 儲存
            with open('public/singers_data.json', 'w', encoding='utf-8') as f:
                json.dump(all_singers_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 {singer_name} 的資料已儲存 ({len(songs_data)} 首歌曲)")
            return True
            
        except Exception as e:
            print(f"❌ 儲存失敗: {e}")
            return False
    
    def search_multiple_singers(self, singer_list):
        """批次搜尋多個歌手"""
        print(f"🎤 開始批次收集 {len(singer_list)} 位歌手的資料")
        
        total_songs = 0
        successful_singers = 0
        
        for i, singer in enumerate(singer_list, 1):
            print(f"\n{'='*60}")
            print(f"進度 [{i}/{len(singer_list)}]: {singer}")
            
            try:
                songs = self.search_singer_comprehensive(singer)
                if self.save_singer_data(singer, songs):
                    total_songs += len(songs)
                    successful_singers += 1
                
                # 每個歌手之間休息
                if i < len(singer_list):
                    time.sleep(random.uniform(3, 8))
                    
            except Exception as e:
                print(f"❌ {singer} 收集失敗: {e}")
        
        print(f"\n🎉 批次收集完成!")
        print(f"✅ 成功: {successful_singers}/{len(singer_list)} 位歌手")
        print(f"📊 總歌曲數: {total_songs} 首")

def main():
    print("🎤 歌手專用爬蟲 - 無上限完整收集")
    print("="*60)
    
    scraper = SingerScraper(max_workers=2)
    
    while True:
        print("\n📋 選擇模式:")
        print("1. 搜尋單一歌手")
        print("2. 批次搜尋多位歌手")
        print("3. 使用熱門歌手清單")
        print("4. 退出")
        
        choice = input("\n請選擇 (1-4): ").strip()
        
        if choice == '1':
            singer_name = input("請輸入歌手名稱: ").strip()
            if singer_name:
                songs = scraper.search_singer_comprehensive(singer_name)
                scraper.save_singer_data(singer_name, songs)
            
        elif choice == '2':
            print("請輸入歌手名稱，一行一個，輸入空行結束:")
            singers = []
            while True:
                singer = input().strip()
                if not singer:
                    break
                singers.append(singer)
            
            if singers:
                scraper.search_multiple_singers(singers)
        
        elif choice == '3':
            # 預設熱門歌手清單
            hot_singers = [
                "周杰倫", "蔡依林", "林俊傑", "張惠妹", "五月天", "鄧紫棋", "林宥嘉",
                "田馥甄", "楊丞琳", "孫燕姿", "梁靜茹", "告五人", "茄子蛋", "持修",
                "張學友", "劉德華", "鄧麗君", "蔡琴", "李宗盛", "伍佰", "張宇"
            ]
            
            print(f"🔥 將搜尋 {len(hot_singers)} 位熱門歌手:")
            for i, singer in enumerate(hot_singers, 1):
                print(f"  {i:2d}. {singer}")
            
            confirm = input(f"\n確定開始? (y/n): ").strip().lower()
            if confirm == 'y':
                scraper.search_multiple_singers(hot_singers)
        
        elif choice == '4':
            print("👋 再見!")
            break
        
        else:
            print("❌ 無效選擇，請重試")

if __name__ == "__main__":
    main()