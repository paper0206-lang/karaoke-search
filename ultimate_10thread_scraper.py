#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
終極10線程並發爬蟲系統
實現所有用戶要求的核心功能
"""

import json
import os
import sys
import time
import logging
import signal
import threading
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import subprocess
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# 導入改進的台灣比較器
from improved_taiwan_comparator import ImprovedTaiwanComparator

class Ultimate10ThreadScraper:
    def __init__(self):
        self.setup_logging()
        self.comparator = ImprovedTaiwanComparator()
        self.running = True
        self.max_threads = 10
        self.pages_per_thread = 200
        
        # 線程安全鎖
        self.data_lock = threading.Lock()
        self.progress_lock = threading.Lock()
        self.checkpoint_lock = threading.Lock()
        
        # 信號處理
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # 統計數據
        self.stats = {
            'singers_processed': 0,
            'singers_scraped': 0,
            'singers_skipped': 0,
            'total_songs_found': 0,
            'threads_active': 0,
            'start_time': datetime.now()
        }
        
        # KTV公司清單
        self.companies = [
            "音圓", "弘音", "金嗓", "瑞影", "點將家", "嘉揚", "音遊", "音影", 
            "美華", "金影", "錢櫃", "好樂迪", "星據點", "銀櫃", "享溫馨", "大唐", "MV"
        ]
        
        # 檔案路徑
        self.checkpoint_file = "ultimate_scraper_checkpoint.json"
        self.results_file = "ultimate_scraper_results.json"
        self.singers_data_file = "public/singers_data.json"
        
        self.logger.info("🚀 終極10線程並發爬蟲系統已初始化")
        self.logger.info(f"   線程數: {self.max_threads}")
        self.logger.info(f"   每線程頁數: {self.pages_per_thread}")
        self.logger.info(f"   KTV公司: {len(self.companies)} 家")
    
    def setup_logging(self):
        """設置日誌系統"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ultimate_10thread_scraper.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Ultimate10ThreadScraper')
    
    def signal_handler(self, signum, frame):
        """信號處理器"""
        self.logger.info(f"🛑 收到停止信號 {signum}")
        self.running = False
    
    def get_random_user_agent(self):
        """隨機User-Agent"""
        agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        return random.choice(agents)
    
    def create_session(self, thread_id):
        """為每個線程創建獨立的Session"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        return session
    
    def intelligent_delay(self, thread_id, page_num, is_error=False):
        """智能延遲策略"""
        # 基礎隨機延遲
        base_delay = random.uniform(1.5, 3.5)
        
        # 線程錯開延遲
        thread_delay = thread_id * 0.2
        
        # 每10頁額外延遲
        page_delay = 0.5 if page_num % 10 == 0 else 0
        
        # 錯誤後指數退避
        error_delay = random.uniform(5, 10) if is_error else 0
        
        total_delay = base_delay + thread_delay + page_delay + error_delay
        time.sleep(total_delay)
    
    def check_content_similarity(self, songs1, songs2, threshold=0.8):
        """檢查兩個頁面的內容相似度"""
        if not songs1 or not songs2:
            return False
        
        # 比較前3首歌曲的標題
        sample1 = [song.get('song_name', '')[:20] for song in songs1[:3]]
        sample2 = [song.get('song_name', '')[:20] for song in songs2[:3]]
        
        if not sample1 or not sample2:
            return False
        
        # 計算相似度
        common = len(set(sample1) & set(sample2))
        similarity = common / min(len(sample1), len(sample2), 3)
        
        return similarity >= threshold
    
    def scrape_page_range_for_singer(self, singer_name, company, start_page, end_page, thread_id):
        """單個線程爬取指定頁面範圍"""
        session = self.create_session(thread_id)
        thread_data = []
        page_content_cache = {}  # 用於重複檢測
        consecutive_empty = 0
        max_empty = 3
        
        self.logger.info(f"🧵 線程{thread_id}: 開始爬取 {singer_name}({company}) 第{start_page}-{end_page}頁")
        
        try:
            for page in range(start_page, end_page + 1):
                if not self.running:
                    break
                
                try:
                    # 智能延遲
                    self.intelligent_delay(thread_id, page)
                    
                    # 定期更換User-Agent
                    if page % 20 == 0:
                        session.headers['User-Agent'] = self.get_random_user_agent()
                    
                    # 構建URL
                    if singer_name:
                        # 歌手搜索模式
                        url = f"https://song.corp.com.tw/songs.aspx?company=全部&keyword={quote(singer_name)}&page={page}"
                    else:
                        # 公司爬取模式
                        url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
                    
                    response = session.get(url, timeout=15)
                    response.encoding = "utf-8"
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        song_links = soup.select('a[href^="mv.aspx?id="]')
                        
                        if song_links:
                            consecutive_empty = 0
                            page_songs = []
                            
                            for link in song_links:
                                try:
                                    raw_text = link.get_text().strip()
                                    lines = raw_text.split('\n')
                                    
                                    if len(lines) >= 3:
                                        number = lines[0].strip()
                                        song_name = lines[1].strip()
                                        singer_info = lines[2].strip()
                                        
                                        # 語言檢測
                                        language = "國"  # 預設
                                        if any(char in singer_info for char in "台語閩南語"):
                                            language = "台"
                                        elif any(char in singer_info for char in "英文English"):
                                            language = "英"
                                        
                                        song_data = {
                                            'company': company,
                                            'number': number,
                                            'song_name': song_name,
                                            'singer': singer_info,
                                            'language': language,
                                            'page': page,
                                            'thread_id': thread_id,
                                            'scraped_at': datetime.now().isoformat(),
                                            'raw_text': raw_text
                                        }
                                        
                                        page_songs.append(song_data)
                                        
                                except Exception as e:
                                    self.logger.debug(f"線程{thread_id}: 解析歌曲失敗: {e}")
                                    continue
                            
                            # 重複檢測
                            if page > start_page and page_content_cache:
                                prev_page = page - 1
                                if prev_page in page_content_cache:
                                    if self.check_content_similarity(page_songs, page_content_cache[prev_page]):
                                        self.logger.info(f"🧵 線程{thread_id}: 第{page}頁內容重複，停止爬取")
                                        break
                            
                            # 緩存頁面內容（只保留最近5頁）
                            page_content_cache[page] = page_songs
                            if len(page_content_cache) > 5:
                                oldest_page = min(page_content_cache.keys())
                                del page_content_cache[oldest_page]
                            
                            thread_data.extend(page_songs)
                            self.logger.debug(f"🧵 線程{thread_id}: 第{page}頁 {len(page_songs)} 首歌")
                            
                        else:
                            consecutive_empty += 1
                            self.logger.debug(f"🧵 線程{thread_id}: 第{page}頁 無資料 ({consecutive_empty}/{max_empty})")
                            
                            if consecutive_empty >= max_empty:
                                self.logger.info(f"🧵 線程{thread_id}: 連續{max_empty}頁無資料，停止爬取")
                                break
                    else:
                        self.logger.warning(f"🧵 線程{thread_id}: 第{page}頁 HTTP {response.status_code}")
                        self.intelligent_delay(thread_id, page, is_error=True)
                        
                except Exception as e:
                    self.logger.error(f"🧵 線程{thread_id}: 第{page}頁 異常: {e}")
                    self.intelligent_delay(thread_id, page, is_error=True)
                    continue
            
        finally:
            session.close()
            
        self.logger.info(f"🧵 線程{thread_id}: 完成，共爬取 {len(thread_data)} 首歌")
        return thread_data
    
    def scrape_singer_with_multithreading(self, singer_name, max_pages=2000):
        """使用10線程並發爬取單個歌手"""
        self.logger.info(f"🎵 開始10線程並發爬取: {singer_name}")
        
        all_songs = []
        
        # 計算線程範圍
        page_ranges = []
        for i in range(self.max_threads):
            start_page = i * self.pages_per_thread + 1
            end_page = min((i + 1) * self.pages_per_thread, max_pages)
            if start_page <= max_pages:
                page_ranges.append((start_page, end_page))
        
        self.logger.info(f"📊 任務分配: {len(page_ranges)} 個線程，每線程最多{self.pages_per_thread}頁")
        
        # 並發執行
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {
                executor.submit(
                    self.scrape_page_range_for_singer, 
                    singer_name, "全部", start, end, i
                ): (start, end, i) 
                for i, (start, end) in enumerate(page_ranges)
            }
            
            for future in as_completed(futures):
                if not self.running:
                    break
                    
                start, end, thread_id = futures[future]
                try:
                    thread_data = future.result(timeout=300)  # 5分鐘超時
                    all_songs.extend(thread_data)
                    
                    with self.stats_lock:
                        self.stats['threads_completed'] = self.stats.get('threads_completed', 0) + 1
                    
                    self.logger.info(f"✅ 線程{thread_id} 完成: 第{start}-{end}頁，{len(thread_data)}首歌")
                    
                except Exception as e:
                    self.logger.error(f"❌ 線程{thread_id} 失敗: {e}")
        
        # 統計結果
        unique_songs = len(set((song['song_name'], song['singer']) for song in all_songs))
        
        self.logger.info(f"🎉 {singer_name} 爬取完成:")
        self.logger.info(f"   總歌曲數: {len(all_songs)}")
        self.logger.info(f"   獨特歌曲: {unique_songs}")
        
        return all_songs
    
    def save_checkpoint(self, data):
        """保存檢查點"""
        try:
            with self.checkpoint_lock:
                checkpoint_data = {
                    "singers_processed": data.get("singers_processed", 0),
                    "singers_scraped": data.get("singers_scraped", 0),
                    "singers_skipped": data.get("singers_skipped", 0),
                    "last_update": datetime.now().isoformat(),
                    "status": data.get("status", "running"),
                    "processed_singers": data.get("processed_singers", [])
                }
                
                with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                    json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
                    
        except Exception as e:
            self.logger.error(f"保存檢查點失敗: {e}")
    
    def load_checkpoint(self):
        """讀取檢查點"""
        try:
            if os.path.exists(self.checkpoint_file):
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self.logger.info(f"📊 檢查點已讀取: 已處理{data.get('singers_processed', 0)}位歌手")
                return data.get("processed_singers", [])
        except Exception as e:
            self.logger.error(f"讀取檢查點失敗: {e}")
        
        return []
    
    def git_push_changes(self):
        """自動推送Git變更"""
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip():
                self.logger.info("📤 發現Git變更，準備推送...")
                
                subprocess.run(['git', 'add', '.'], check=True)
                
                commit_message = f"🎵 終極爬蟲更新: {datetime.now().strftime('%Y%m%d_%H%M%S')}"
                subprocess.run(['git', 'commit', '-m', commit_message], check=True)
                
                subprocess.run(['git', 'push'], check=True)
                
                self.logger.info("✅ Git變更已自動推送")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Git推送失敗: {e}")
            return False
    
    def run_singer_based_scraping(self):
        """運行基於歌手的智能爬取"""
        try:
            self.logger.info("🚀 開始基於歌手的智能爬取...")
            
            # 獲取優先級歌手列表
            priority_singers = self.comparator.get_priority_sorted_singers(max_singers=50)
            processed_singers = self.load_checkpoint()
            
            # 過濾已處理的歌手
            remaining_singers = [
                item for item in priority_singers 
                if item['singer'] not in processed_singers
            ]
            
            self.logger.info(f"📋 待處理歌手: {len(remaining_singers)} 位")
            
            for i, singer_item in enumerate(remaining_singers):
                if not self.running:
                    break
                
                singer_name = singer_item['singer']
                
                self.logger.info(f"🎯 處理 {i+1}/{len(remaining_singers)}: {singer_name}")
                
                # 檢查是否需要爬取
                check_result = self.comparator.check_needs_scraping_with_priority(singer_name)
                
                if check_result['needs_scraping']:
                    self.logger.info(f"✅ 需要爬取 {singer_name}: 優先級{check_result['priority_score']:.1f}分")
                    
                    # 使用10線程並發爬取
                    songs_data = self.scrape_singer_with_multithreading(singer_name)
                    
                    if songs_data:
                        # 整合到資料庫
                        self.integrate_singer_data(singer_name, songs_data)
                        
                        with self.data_lock:
                            self.stats['singers_scraped'] += 1
                            self.stats['total_songs_found'] += len(songs_data)
                    
                else:
                    self.logger.info(f"⏭️ 跳過 {singer_name}: {check_result['reason']}")
                    with self.data_lock:
                        self.stats['singers_skipped'] += 1
                
                # 更新進度
                processed_singers.append(singer_name)
                with self.data_lock:
                    self.stats['singers_processed'] += 1
                
                # 保存檢查點
                self.save_checkpoint({
                    "singers_processed": self.stats['singers_processed'],
                    "singers_scraped": self.stats['singers_scraped'], 
                    "singers_skipped": self.stats['singers_skipped'],
                    "status": "running",
                    "processed_singers": processed_singers
                })
                
                # 定期Git推送
                if self.stats['singers_scraped'] % 5 == 0 and self.stats['singers_scraped'] > 0:
                    self.git_push_changes()
            
            self.logger.info("🎉 基於歌手的智能爬取完成")
            
        except Exception as e:
            self.logger.error(f"智能爬取失敗: {e}")
    
    def integrate_singer_data(self, singer_name, songs_data):
        """整合歌手資料到主資料庫"""
        try:
            # 讀取現有資料庫
            singers_data = {}
            if os.path.exists(self.singers_data_file):
                with open(self.singers_data_file, 'r', encoding='utf-8') as f:
                    singers_data = json.load(f)
            
            # 組織歌曲資料
            if singer_name not in singers_data:
                singers_data[singer_name] = {
                    "基本資訊": {
                        "歌手名稱": singer_name,
                        "語言類型": [],
                        "歌曲總數": 0,
                        "KTV編號總數": 0
                    },
                    "歌曲清單": []
                }
            
            # 按歌曲組織KTV編號
            songs_dict = defaultdict(list)
            for song in songs_data:
                song_key = song['song_name']
                songs_dict[song_key].append({
                    "公司": song['company'],
                    "編號": song['number'],
                    "語言": song['language']
                })
            
            # 更新歌曲清單
            existing_songs = {song['歌名']: song for song in singers_data[singer_name]['歌曲清單']}
            
            for song_name, ktv_entries in songs_dict.items():
                if song_name in existing_songs:
                    # 合併KTV編號
                    existing_entries = {f"{e['公司']}:{e['編號']}" for e in existing_songs[song_name]['編號資訊']}
                    for entry in ktv_entries:
                        entry_key = f"{entry['公司']}:{entry['編號']}"
                        if entry_key not in existing_entries:
                            existing_songs[song_name]['編號資訊'].append(entry)
                else:
                    # 新歌曲
                    existing_songs[song_name] = {
                        "歌名": song_name,
                        "編號資訊": ktv_entries
                    }
            
            # 更新歌曲清單
            singers_data[singer_name]['歌曲清單'] = list(existing_songs.values())
            
            # 更新統計資訊
            total_ktv_entries = sum(len(song['編號資訊']) for song in singers_data[singer_name]['歌曲清單'])
            languages = set()
            for song in singers_data[singer_name]['歌曲清單']:
                for entry in song['編號資訊']:
                    languages.add(entry['語言'])
            
            singers_data[singer_name]['基本資訊'].update({
                "歌曲總數": len(singers_data[singer_name]['歌曲清單']),
                "KTV編號總數": total_ktv_entries,
                "語言類型": sorted(list(languages))
            })
            
            # 保存資料庫
            with open(self.singers_data_file, 'w', encoding='utf-8') as f:
                json.dump(singers_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"💾 {singer_name} 資料已整合: {len(songs_dict)}首歌，{len(songs_data)}個KTV編號")
            
        except Exception as e:
            self.logger.error(f"整合 {singer_name} 資料失敗: {e}")

def main():
    """主函數"""
    scraper = Ultimate10ThreadScraper()
    
    try:
        # 設置統計資訊鎖
        scraper.stats_lock = threading.Lock()
        
        # 運行智能爬取
        scraper.run_singer_based_scraping()
        
    except KeyboardInterrupt:
        scraper.logger.info("🛑 用戶中斷")
    except Exception as e:
        scraper.logger.error(f"運行失敗: {e}")
    finally:
        scraper.logger.info("🏁 終極爬蟲已停止")

if __name__ == "__main__":
    main()