#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌手優先爬蟲 - 突破50首限制的完整歌手資料爬取
專門針對歌手進行深度挖掘，整合到統一資料庫
"""

import requests
import json
import time
import random
from datetime import datetime
from unified_scraper import UnifiedKaraokeScraper
from collections import defaultdict

class SingerFocusedScraper(UnifiedKaraokeScraper):
    def __init__(self, max_workers=2):
        super().__init__(max_workers)
        self.singer_strategies = []
        
    def search_singer_comprehensive(self, singer_name):
        """
        全面搜尋單一歌手 - 突破50首限制
        使用多種策略確保完整收錄
        """
        print(f"\n🎤 深度挖掘歌手: {singer_name}")
        all_songs = []
        seen_songs = set()
        
        # 策略1: 直接搜尋歌手名
        direct_songs = self._search_direct_singer(singer_name)
        self._add_unique_songs(all_songs, direct_songs, seen_songs, "直接搜尋")
        
        # 策略2: 歌手名 + 公司組合搜尋
        company_songs = self._search_singer_by_companies(singer_name)
        self._add_unique_songs(all_songs, company_songs, seen_songs, "分公司搜尋")
        
        # 策略3: 歌手名部分匹配
        partial_songs = self._search_singer_partial(singer_name)
        self._add_unique_songs(all_songs, partial_songs, seen_songs, "部分匹配")
        
        # 策略4: 使用歌手的熱門歌曲反推
        popular_songs = self._search_by_popular_songs(singer_name)
        self._add_unique_songs(all_songs, popular_songs, seen_songs, "熱門歌曲反推")
        
        # 策略5: 多種搜尋類型
        type_songs = self._search_singer_multiple_types(singer_name)
        self._add_unique_songs(all_songs, type_songs, seen_songs, "多類型搜尋")
        
        print(f"   🎯 {singer_name} 總計收錄: {len(all_songs)} 首")
        return all_songs
    
    def _search_direct_singer(self, singer_name):
        """策略1: 直接搜尋歌手名"""
        songs = []
        session = random.choice(self.session_pool)
        
        try:
            # 使用正確的API端點
            search_url = f"{self.base_url}/song_list_json.php"
            params = {
                'song': singer_name.encode('utf-8'),
                'company': '全部',
                'cusType': 'searchList',
                '_': int(time.time() * 1000)
            }
            response = session.get(search_url, params=params, timeout=15)
            
            if response.status_code == 200 and 'json' in response.headers.get('content-type', ''):
                data = response.json()
                songs.extend(self._parse_song_data(data))
                
        except Exception as e:
            print(f"   ⚠️ 直接搜尋失敗: {e}")
            
        return songs
    
    def _search_singer_by_companies(self, singer_name):
        """策略2: 分公司逐一搜尋"""
        all_songs = []
        companies = ['錢櫃', '好樂迪', '銀櫃', '音圓', '金嗓', '弘音', '星據點', '點將家']
        
        for company in companies:
            try:
                session = random.choice(self.session_pool)
                response = session.get(f"{self.base_url}/song_list_json.php", params={
                    'song': singer_name,
                    'company': company,
                    'cusType': 'searchList'
                }, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    songs = self._parse_song_data(data)
                    all_songs.extend(songs)
                    if songs:
                        print(f"   {company}: {len(songs)} 首")
                
                time.sleep(random.uniform(1, 2))  # 避免被封鎖
                
            except Exception as e:
                print(f"   ⚠️ {company} 搜尋失敗: {e}")
                continue
                
        return all_songs
    
    def _search_singer_partial(self, singer_name):
        """策略3: 歌手名部分匹配"""
        songs = []
        
        # 生成部分匹配關鍵字
        partial_keywords = []
        
        if len(singer_name) >= 2:
            # 前兩字
            partial_keywords.append(singer_name[:2])
            # 後兩字
            if len(singer_name) > 2:
                partial_keywords.append(singer_name[-2:])
            # 中間字 (如果是三字以上)
            if len(singer_name) >= 3:
                partial_keywords.append(singer_name[1:-1])
        
        for keyword in partial_keywords:
            try:
                session = random.choice(self.session_pool)
                response = session.get(f"{self.base_url}/song_list_json.php", params={
                    'song': keyword,
                    'company': '全部',
                    'cusType': 'searchList'
                }, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    # 過濾只保留目標歌手的歌
                    filtered_songs = []
                    for item in data:
                        if singer_name in item.get('singer_name', ''):
                            filtered_songs.append(item)
                    
                    songs.extend(self._parse_song_data(filtered_songs))
                    
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                continue
                
        return songs
    
    def _search_by_popular_songs(self, singer_name):
        """策略4: 通過已知熱門歌曲反推"""
        songs = []
        
        # 預設熱門歌曲庫 (可以擴展)
        popular_songs_db = {
            "周杰倫": ["青花瓷", "稻香", "告白氣球", "簡單愛", "夜曲", "雙截棍", "菊花台"],
            "蔡依林": ["日不落", "舞娘", "愛情三十六計", "馬德里不思議", "花蝴蝶"],
            "林俊傑": ["江南", "曹操", "小酒窩", "醉赤壁", "可惜沒如果"],
            "張惠妹": ["姊妹", "聽海", "剪愛", "我可以抱你嗎", "三天三夜"],
            "五月天": ["突然好想你", "擁抱", "倔強", "知足", "溫柔"]
        }
        
        if singer_name in popular_songs_db:
            for song_name in popular_songs_db[singer_name]:
                try:
                    session = random.choice(self.session_pool)
                    response = session.get(f"{self.base_url}/song_list_json.php", params={
                        'song': song_name,
                        'company': '全部',
                        'cusType': 'searchList'
                    }, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        # 只取該歌手的版本
                        for item in data:
                            if singer_name in item.get('singer_name', ''):
                                songs.extend(self._parse_song_data([item]))
                    
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    continue
                    
        return songs
    
    def _search_singer_multiple_types(self, singer_name):
        """策略5: 使用不同搜尋類型"""
        songs = []
        search_types = ['searchList', 'newSong', 'hotSong']
        
        for search_type in search_types:
            try:
                session = random.choice(self.session_pool)
                response = session.get(f"{self.base_url}/song_list_json.php", params={
                    'song': singer_name,
                    'company': '全部',
                    'cusType': search_type
                }, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    songs.extend(self._parse_song_data(data))
                    
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                continue
                
        return songs
    
    def _parse_song_data(self, data):
        """解析歌曲數據"""
        songs = []
        for item in data:
            if isinstance(item, dict):
                song_info = {
                    '歌名': item.get('song_name', '').strip(),
                    '歌手': item.get('singer_name', '').strip(), 
                    '編號': item.get('song_id', '').strip(),
                    '公司': item.get('company_name', '').strip(),
                    '語言': item.get('language', '').strip()
                }
                if song_info['歌名'] and song_info['歌手']:
                    songs.append(song_info)
        return songs
    
    def _add_unique_songs(self, all_songs, new_songs, seen_songs, strategy_name):
        """添加去重歌曲"""
        added_count = 0
        for song in new_songs:
            song_key = f"{song['歌名']}-{song['歌手']}-{song['編號']}-{song['公司']}"
            if song_key not in seen_songs:
                seen_songs.add(song_key)
                all_songs.append(song)
                added_count += 1
        
        if added_count > 0:
            print(f"   📈 {strategy_name}: 新增 {added_count} 首")
    
    def scrape_singers_batch(self, singer_list, save_frequency=5):
        """
        批次爬取歌手列表
        save_frequency: 每幾個歌手保存一次
        """
        print(f"🎤 歌手優先批次爬取")
        print(f"📋 目標歌手: {len(singer_list)} 位")
        print(f"💾 保存頻率: 每 {save_frequency} 位歌手")
        print("=" * 50)
        
        total_added = 0
        processed = 0
        
        for i, singer_name in enumerate(singer_list, 1):
            print(f"\n[{i}/{len(singer_list)}] 處理歌手: {singer_name}")
            
            try:
                # 深度搜尋該歌手
                songs = self.search_singer_comprehensive(singer_name)
                
                if songs:
                    # 加入統一資料庫
                    added = self.add_songs_to_database(songs)
                    total_added += added
                    print(f"   ✅ {singer_name}: 新增 {added} 首到統一資料庫")
                else:
                    print(f"   ⚠️ {singer_name}: 沒有找到歌曲")
                
                processed += 1
                
                # 定期保存
                if processed % save_frequency == 0:
                    if self.save_unified_database():
                        print(f"\n💾 已保存進度: {processed}/{len(singer_list)} 位歌手")
                        print(f"📊 累計新增: {total_added} 首歌曲")
                
                # 避免被封鎖
                if i < len(singer_list):
                    sleep_time = random.uniform(3, 8)
                    print(f"   😴 休息 {sleep_time:.1f} 秒...")
                    time.sleep(sleep_time)
                    
            except Exception as e:
                print(f"   ❌ {singer_name} 處理失敗: {e}")
                continue
        
        # 最終保存
        if self.save_unified_database():
            print(f"\n🎉 歌手批次爬取完成!")
            print(f"📊 最終統計:")
            print(f"   處理歌手: {processed}/{len(singer_list)} 位")
            print(f"   新增歌曲: {total_added} 首")
            print(f"   總歌曲數: {self.unified_db['metadata']['total_songs']:,} 首")
            print(f"   總歌手數: {self.unified_db['metadata']['total_singers']:,} 位")
        
        return total_added

def main():
    # 優先爬取的歌手列表 (已按重要性排序)
    priority_singers = [
        # 天王天后級
        "周杰倫", "蔡依林", "林俊傑", "張惠妹", "五月天",
        "孫燕姿", "梁靜茹", "王力宏", "陶喆", "鄧紫棋",
        
        # 經典歌手
        "張學友", "劉德華", "郭富城", "黎明", "張國榮",
        "梅艷芳", "鄧麗君", "蔡琴", "鳳飛飛", "費玉清",
        
        # 新生代熱門
        "告五人", "茄子蛋", "持修", "ØZI", "高爾宣",
        "LEO王", "9m88", "吳卓源", "血肉果汁機", "理想混蛋",
        
        # 搖滾樂團
        "蘇打綠", "信樂團", "F.I.R", "八三夭", "滅火器",
        "四分衛", "黑色柳丁", "董事長樂團", "脫拉庫",
        
        # 實力派歌手
        "李宗盛", "羅大佑", "伍佰", "張宇", "庾澄慶",
        "齊秦", "張雨生", "黃品源", "黃小琥", "辛曉琪"
    ]
    
    print("🎤 歌手優先爬蟲系統")
    print("突破50首限制，完整收錄歌手作品")
    print("=" * 50)
    
    scraper = SingerFocusedScraper(max_workers=2)
    
    print(f"📋 預設歌手清單: {len(priority_singers)} 位")
    print("前10位:", ", ".join(priority_singers[:10]))
    
    choice = input("\n選擇模式:\n1. 爬取前10位優先歌手\n2. 爬取前20位歌手\n3. 爬取全部歌手\n4. 自訂歌手列表\n請選擇 (1-4): ")
    
    if choice == '1':
        target_singers = priority_singers[:10]
    elif choice == '2':
        target_singers = priority_singers[:20]
    elif choice == '3':
        target_singers = priority_singers
    elif choice == '4':
        custom_input = input("請輸入歌手名稱 (用逗號分隔): ")
        target_singers = [s.strip() for s in custom_input.split(',') if s.strip()]
    else:
        print("❌ 無效選擇")
        return
    
    if not target_singers:
        print("❌ 沒有選擇歌手")
        return
    
    print(f"\n🎯 準備爬取 {len(target_singers)} 位歌手")
    print("目標歌手:", ", ".join(target_singers))
    
    confirm = input(f"\n確定開始嗎？預估時間 {len(target_singers) * 3} 分鐘 (y/n): ")
    if confirm.lower() == 'y':
        scraper.scrape_singers_batch(target_singers)
    else:
        print("❌ 已取消")

if __name__ == "__main__":
    main()