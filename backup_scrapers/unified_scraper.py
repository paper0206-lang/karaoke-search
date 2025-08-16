#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統一架構卡拉OK爬蟲 - 直接輸出到統一資料庫格式
適配新的unified_karaoke_db.json架構
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

class UnifiedKaraokeScraper:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.session_pool = []
        self.unified_db = None
        self.lock = threading.Lock()
        self.base_url = "https://song.corp.com.tw"
        
        # 載入現有統一資料庫
        self.load_unified_database()
        
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
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0'
        ]
        return random.choice(agents)
    
    def load_unified_database(self):
        """載入統一資料庫"""
        try:
            with open('public/unified_karaoke_db.json', 'r', encoding='utf-8') as f:
                self.unified_db = json.load(f)
            print(f"📚 載入統一資料庫: {self.unified_db['metadata']['total_songs']:,} 首歌曲")
        except FileNotFoundError:
            print("📚 建立新的統一資料庫")
            self.unified_db = {
                "metadata": {
                    "version": "2.0",
                    "created": datetime.now().isoformat(),
                    "total_songs": 0,
                    "total_singers": 0,
                    "companies": set()
                },
                "songs": {},
                "indexes": {
                    "by_singer": defaultdict(list),
                    "by_company": defaultdict(list),
                    "by_song_name": defaultdict(list),
                    "by_language": defaultdict(list)
                },
                "singer_metadata": {}
            }
    
    def generate_song_id(self, song_name, singer_name):
        """產生唯一的歌曲ID"""
        clean_song = ''.join(c for c in song_name if c.isalnum() or c in '中文')[:20]
        clean_singer = ''.join(c for c in singer_name if c.isalnum() or c in '中文')[:10]
        
        base_id = f"{clean_singer}_{clean_song}".replace(' ', '_')
        
        counter = 1
        song_id = base_id
        while song_id in self.unified_db["songs"]:
            song_id = f"{base_id}_{counter}"
            counter += 1
            
        return song_id
    
    def merge_song_codes(self, song_entries):
        """合併相同歌曲的不同編號"""
        merged_codes = []
        seen_codes = set()
        
        for entry in song_entries:
            company = entry.get('公司', entry.get('company', ''))
            code = entry.get('編號', entry.get('code', ''))
            
            if company and code:
                code_key = f"{company}:{code}"
                if code_key not in seen_codes:
                    merged_codes.append({
                        "公司": company,
                        "編號": code
                    })
                    seen_codes.add(code_key)
        
        # 按公司優先順序排序
        company_priority = ['錢櫃', '好樂迪', '銀櫃', '音圓', '金嗓', '弘音', '星據點', '音霸', '大東', '點將家']
        merged_codes.sort(key=lambda x: (
            company_priority.index(x['公司']) if x['公司'] in company_priority else 999,
            x['公司'],
            x['編號']
        ))
        
        return merged_codes
    
    def search_songs(self, keyword, company='全部', search_type='searchList'):
        """搜尋歌曲"""
        session = random.choice(self.session_pool)
        
        try:
            # 搜尋請求
            search_url = f"{self.base_url}/song_list_json.php"
            params = {
                'song': quote(keyword),
                'company': company,
                'cusType': search_type,
                '_': int(time.time() * 1000)
            }
            
            response = session.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200 and 'json' in response.headers.get('content-type', ''):
                data = response.json()
                songs = []
                
                for item in data:
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
                
        except Exception as e:
            print(f"⚠️ 搜尋 '{keyword}' 時發生錯誤: {e}")
        
        return []
    
    def add_songs_to_database(self, new_songs):
        """將新歌曲加入統一資料庫"""
        added_count = 0
        
        # 按歌名+歌手分組
        song_groups = defaultdict(list)
        
        for song in new_songs:
            song_name = song.get('歌名', '').strip()
            singer_name = song.get('歌手', '').strip()
            
            if song_name and singer_name:
                key = f"{song_name}||{singer_name}"
                song_groups[key].append(song)
        
        for group_key, song_entries in song_groups.items():
            song_name, singer_name = group_key.split('||')
            song_id = self.generate_song_id(song_name, singer_name)
            
            # 合併編號資訊
            merged_codes = self.merge_song_codes(song_entries)
            
            # 檢查是否已存在
            if song_id in self.unified_db["songs"]:
                # 更新現有歌曲的編號資訊
                existing_codes = self.unified_db["songs"][song_id].get('編號資訊', [])
                all_codes = existing_codes + merged_codes
                final_codes = self.merge_song_codes(all_codes)
                
                if len(final_codes) > len(existing_codes):
                    self.unified_db["songs"][song_id]['編號資訊'] = final_codes
                    self.unified_db["songs"][song_id]['更新時間'] = datetime.now().isoformat()
                    added_count += 1
            else:
                # 新增歌曲
                language = ''
                for entry in song_entries:
                    if entry.get('語言'):
                        language = entry['語言']
                        break
                
                self.unified_db["songs"][song_id] = {
                    "歌名": song_name,
                    "歌手": singer_name,
                    "語言": language,
                    "編號資訊": merged_codes,
                    "來源": "統一爬蟲",
                    "創建時間": datetime.now().date().isoformat(),
                    "更新時間": datetime.now().isoformat()
                }
                
                # 更新索引
                self.unified_db["indexes"]["by_singer"][singer_name].append(song_id)
                self.unified_db["indexes"]["by_song_name"][song_name].append(song_id)
                if language:
                    self.unified_db["indexes"]["by_language"][language].append(song_id)
                
                for code_info in merged_codes:
                    company = code_info['公司']
                    self.unified_db["indexes"]["by_company"][company].append(song_id)
                    self.unified_db["metadata"]["companies"].add(company)
                
                added_count += 1
        
        return added_count
    
    def save_unified_database(self):
        """儲存統一資料庫"""
        # 更新統計資料
        self.unified_db["metadata"]["total_songs"] = len(self.unified_db["songs"])
        self.unified_db["metadata"]["total_singers"] = len(self.unified_db["indexes"]["by_singer"])
        self.unified_db["metadata"]["companies"] = sorted(list(self.unified_db["metadata"]["companies"]))
        self.unified_db["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # 清理索引
        for index_type in self.unified_db["indexes"]:
            if isinstance(self.unified_db["indexes"][index_type], defaultdict):
                self.unified_db["indexes"][index_type] = dict(self.unified_db["indexes"][index_type])
        
        try:
            with open('public/unified_karaoke_db.json', 'w', encoding='utf-8') as f:
                json.dump(self.unified_db, f, ensure_ascii=False, indent=2)
            
            # 重新生成相容性檔案
            self.generate_compatibility_files()
            
            return True
        except Exception as e:
            print(f"❌ 儲存失敗: {e}")
            return False
    
    def generate_compatibility_files(self):
        """生成相容性檔案"""
        # 生成 songs_simplified.json
        songs_list = []
        for song_data in self.unified_db["songs"].values():
            for code_info in song_data.get('編號資訊', []):
                songs_list.append({
                    "歌名": song_data["歌名"],
                    "歌手": song_data["歌手"],
                    "編號": code_info["編號"],
                    "公司": code_info["公司"],
                    "語言": song_data.get("語言", "")
                })
        
        with open('public/songs_simplified.json', 'w', encoding='utf-8') as f:
            json.dump(songs_list, f, ensure_ascii=False, indent=2)
        
        # 生成 singers_data.json
        singers_dict = {}
        for singer_name in self.unified_db["indexes"]["by_singer"]:
            song_ids = self.unified_db["indexes"]["by_singer"][singer_name]
            singer_songs = []
            
            for song_id in song_ids:
                song_data = self.unified_db["songs"][song_id]
                singer_songs.append({
                    "歌名": song_data["歌名"],
                    "歌手": song_data["歌手"],
                    "語言": song_data.get("語言", ""),
                    "編號資訊": song_data.get("編號資訊", [])
                })
            
            singers_dict[singer_name] = {
                "歌手名稱": singer_name,
                "歌曲數量": len(singer_songs),
                "更新時間": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "歌曲清單": singer_songs
            }
        
        with open('public/singers_data.json', 'w', encoding='utf-8') as f:
            json.dump(singers_dict, f, ensure_ascii=False, indent=2)
    
    def scrape_with_keywords(self, keywords, max_songs_per_keyword=100):
        """使用關鍵字批次爬取"""
        print(f"🚀 開始批次爬取 {len(keywords)} 個關鍵字")
        
        total_added = 0
        processed = 0
        
        for keyword in keywords:
            print(f"\n🔍 [{processed+1}/{len(keywords)}] 搜尋關鍵字: {keyword}")
            
            # 搜尋多個公司
            companies = ['全部', '錢櫃', '好樂迪', '銀櫃', '音圓', '金嗓']
            keyword_songs = []
            
            for company in companies:
                songs = self.search_songs(keyword, company)
                keyword_songs.extend(songs)
                
                if len(songs) > 0:
                    print(f"   {company}: {len(songs)} 首")
                
                # 避免被封鎖
                time.sleep(random.uniform(1, 3))
            
            if keyword_songs:
                added = self.add_songs_to_database(keyword_songs)
                total_added += added
                print(f"   ✅ 新增 {added} 首歌曲")
                
                # 每100首歌曲保存一次
                if total_added % 100 == 0:
                    self.save_unified_database()
            
            processed += 1
            
            # 每個關鍵字後休息
            if processed < len(keywords):
                time.sleep(random.uniform(3, 8))
        
        # 最終保存
        if self.save_unified_database():
            print(f"\n🎉 爬取完成！")
            print(f"   處理關鍵字: {processed} 個")
            print(f"   新增歌曲: {total_added} 首")
            print(f"   總歌曲數: {self.unified_db['metadata']['total_songs']:,} 首")
            print(f"   總歌手數: {self.unified_db['metadata']['total_singers']:,} 位")
        
        return total_added

def main():
    # 2025年智能關鍵字
    keywords_2025 = [
        # 2025熱門
        "2025", "新歌", "熱門", "最新", "流行",
        
        # 經典歌手
        "周杰倫", "蔡依林", "林俊傑", "張惠妹", "五月天",
        "孫燕姿", "梁靜茹", "王力宏", "陶喆", "鄧紫棋",
        
        # 音樂風格
        "抒情", "搖滾", "民謠", "R&B", "Hip-Hop",
        "國語", "台語", "粵語", "英語",
        
        # 情感主題  
        "愛情", "分手", "思念", "快樂", "傷心",
        "青春", "友情", "家人", "夢想", "希望",
        
        # 常見字詞
        "你", "我", "愛", "心", "夜", "夢", "情", "花"
    ]
    
    scraper = UnifiedKaraokeScraper(max_workers=3)
    scraper.scrape_with_keywords(keywords_2025)

if __name__ == "__main__":
    main()