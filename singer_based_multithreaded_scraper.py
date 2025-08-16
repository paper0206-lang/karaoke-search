#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基於歌手分配的多線程爬蟲系統
每個線程處理一位歌手的完整資料，效率最大化
"""

import json
import os
import sys
import time
import logging
import signal
import threading
import random
import queue
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import subprocess
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# 導入改進的台灣比較器
from improved_taiwan_comparator import ImprovedTaiwanComparator

class SingerBasedMultithreadedScraper:
    def __init__(self):
        self.setup_logging()
        self.comparator = ImprovedTaiwanComparator()
        self.running = True
        self.max_threads = 10
        
        # 線程安全組件
        self.data_lock = threading.Lock()
        self.progress_lock = threading.Lock()
        self.checkpoint_lock = threading.Lock()
        self.singer_queue = queue.Queue()
        
        # 信號處理
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # 統計數據
        self.stats = {
            'singers_queued': 0,
            'singers_completed': 0,
            'singers_scraped': 0,
            'singers_skipped': 0,
            'total_songs_found': 0,
            'active_threads': 0,
            'start_time': datetime.now()
        }
        
        # 檔案路徑
        self.checkpoint_file = "singer_based_checkpoint.json"
        self.results_file = "singer_based_results.json"
        self.singers_data_file = "public/singers_data.json"
        
        self.logger.info("🚀 基於歌手分配的多線程爬蟲系統已初始化")
        self.logger.info(f"   最大線程數: {self.max_threads}")
        self.logger.info(f"   架構: 每線程處理一位歌手完整資料")
    
    def setup_logging(self):
        """設置日誌系統"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('singer_based_scraper.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SingerBasedScraper')
    
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
    
    def intelligent_delay(self, thread_id, page_num=0, is_error=False):
        """智能延遲策略 - 針對歌手分配優化"""
        # 基礎隨機延遲
        base_delay = random.uniform(2.0, 4.0)  # 歌手間延遲可以稍長
        
        # 線程錯開延遲（更重要了）
        thread_delay = thread_id * random.uniform(0.3, 0.6)
        
        # 每10頁額外延遲
        page_delay = random.uniform(0.3, 0.8) if page_num > 0 and page_num % 10 == 0 else 0
        
        # 錯誤後指數退避
        error_delay = random.uniform(8, 15) if is_error else 0
        
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
    
    def scrape_single_singer_complete(self, singer_name, thread_id):
        """完整爬取單個歌手的所有資料"""
        session = self.create_session(thread_id)
        all_songs = []
        page_content_cache = {}
        consecutive_empty = 0
        max_empty = 3
        page = 1
        
        # 更新活躍線程統計
        with self.progress_lock:
            self.stats['active_threads'] += 1
        
        self.logger.info(f"🧵 線程{thread_id}: 開始完整爬取 {singer_name}")
        start_time = time.time()
        
        try:
            while self.running and consecutive_empty < max_empty:
                try:
                    # 智能延遲 - 線程間錯開
                    self.intelligent_delay(thread_id, page)
                    
                    # 定期更換User-Agent
                    if page % 25 == 0:
                        session.headers['User-Agent'] = self.get_random_user_agent()
                    
                    # 構建歌手搜索URL
                    url = f"https://song.corp.com.tw/songs.aspx?company=全部&keyword={quote(singer_name)}&page={page}"
                    
                    response = session.get(url, timeout=20)
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
                                    lines = raw_text.split('\\n')
                                    
                                    if len(lines) >= 2:
                                        song_name = lines[0].strip()
                                        additional_info = lines[1].strip() if len(lines) > 1 else ""
                                        
                                        # 檢查是否真的包含歌手名稱（避免無關歌曲）
                                        if singer_name in raw_text or singer_name in additional_info:
                                            # 解析KTV編號和公司信息
                                            ktv_info = self.parse_ktv_info(raw_text, additional_info)
                                            
                                            song_data = {
                                                'song_name': song_name,
                                                'singer': singer_name,
                                                'ktv_info': ktv_info,
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
                            if page > 1 and page_content_cache:
                                prev_page = page - 1
                                if prev_page in page_content_cache:
                                    if self.check_content_similarity(page_songs, page_content_cache[prev_page]):
                                        self.logger.info(f"🧵 線程{thread_id}: {singer_name} 第{page}頁內容重複，停止爬取")
                                        break
                            
                            # 緩存頁面內容（只保留最近5頁）
                            page_content_cache[page] = page_songs
                            if len(page_content_cache) > 5:
                                oldest_page = min(page_content_cache.keys())
                                del page_content_cache[oldest_page]
                            
                            all_songs.extend(page_songs)
                            
                            # 只對相關歌曲計數
                            relevant_songs = len(page_songs)
                            if relevant_songs > 0:
                                self.logger.debug(f"🧵 線程{thread_id}: {singer_name} 第{page}頁 {relevant_songs} 首相關歌")
                            
                        else:
                            consecutive_empty += 1
                            self.logger.debug(f"🧵 線程{thread_id}: {singer_name} 第{page}頁 無資料 ({consecutive_empty}/{max_empty})")
                    else:
                        self.logger.warning(f"🧵 線程{thread_id}: {singer_name} 第{page}頁 HTTP {response.status_code}")
                        self.intelligent_delay(thread_id, page, is_error=True)
                        
                    page += 1
                    
                except Exception as e:
                    self.logger.error(f"🧵 線程{thread_id}: {singer_name} 第{page}頁 異常: {e}")
                    self.intelligent_delay(thread_id, page, is_error=True)
                    page += 1
                    continue
            
        finally:
            session.close()
            with self.progress_lock:
                self.stats['active_threads'] -= 1
            
        elapsed_time = time.time() - start_time
        unique_songs = len(set(song['song_name'] for song in all_songs))
        
        self.logger.info(f"🧵 線程{thread_id}: {singer_name} 完成")
        self.logger.info(f"     耗時: {elapsed_time:.1f}秒")
        self.logger.info(f"     頁數: {page-1}頁")
        self.logger.info(f"     歌曲: {unique_songs}首，{len(all_songs)}個KTV編號")
        
        return all_songs
    
    def parse_ktv_info(self, raw_text, additional_info):
        """解析KTV編號和公司信息"""
        ktv_entries = []
        
        # 這裡需要根據實際的頁面格式來解析
        # 暫時使用簡化的解析邏輯
        lines = raw_text.split('\\n')
        
        if len(lines) >= 3:
            # 嘗試解析編號和公司
            number = lines[0].strip()
            company = "全部"  # 從搜索方式推斷
            
            # 語言檢測
            language = "國"  # 預設
            text_to_check = additional_info.lower()
            if any(char in text_to_check for char in ["台語", "閩南語", "台"]):
                language = "台"
            elif any(char in text_to_check for char in ["英文", "english", "英"]):
                language = "英"
            
            ktv_entries.append({
                "公司": company,
                "編號": number,
                "語言": language
            })
        
        return ktv_entries
    
    def worker_thread(self, thread_id):
        """工作線程函數"""
        self.logger.info(f"🧵 線程{thread_id}: 啟動")
        
        while self.running:
            try:
                # 從隊列取得歌手任務
                singer_item = self.singer_queue.get(timeout=5)
                if singer_item is None:  # 結束信號
                    break
                
                singer_name = singer_item['singer']
                
                # 檢查是否需要爬取
                check_result = self.comparator.check_needs_scraping_with_priority(singer_name)
                
                if check_result['needs_scraping']:
                    self.logger.info(f"🧵 線程{thread_id}: ✅ 爬取 {singer_name} (優先級{check_result['priority_score']:.1f}分)")
                    
                    # 完整爬取歌手
                    songs_data = self.scrape_single_singer_complete(singer_name, thread_id)
                    
                    if songs_data:
                        # 整合到資料庫
                        self.integrate_singer_data(singer_name, songs_data)
                        
                        with self.progress_lock:
                            self.stats['singers_scraped'] += 1
                            self.stats['total_songs_found'] += len(songs_data)
                    
                else:
                    self.logger.info(f"🧵 線程{thread_id}: ⏭️ 跳過 {singer_name} ({check_result['reason']})")
                    with self.progress_lock:
                        self.stats['singers_skipped'] += 1
                
                # 標記任務完成
                with self.progress_lock:
                    self.stats['singers_completed'] += 1
                
                self.singer_queue.task_done()
                
            except queue.Empty:
                continue  # 繼續等待新任務
            except Exception as e:
                self.logger.error(f"🧵 線程{thread_id}: 處理失敗: {e}")
                with self.progress_lock:
                    self.stats['singers_completed'] += 1
                self.singer_queue.task_done()
        
        self.logger.info(f"🧵 線程{thread_id}: 結束")
    
    def populate_singer_queue(self):
        """填充歌手隊列"""
        try:
            # 獲取優先級歌手列表
            priority_singers = self.comparator.get_priority_sorted_singers(max_singers=100)
            processed_singers = self.load_checkpoint()
            
            # 過濾已處理的歌手
            remaining_singers = [
                item for item in priority_singers 
                if item['singer'] not in processed_singers
            ]
            
            # 添加到隊列
            for singer_item in remaining_singers:
                self.singer_queue.put(singer_item)
            
            with self.progress_lock:
                self.stats['singers_queued'] = len(remaining_singers)
            
            self.logger.info(f"📋 歌手隊列已填充: {len(remaining_singers)} 位待處理歌手")
            
        except Exception as e:
            self.logger.error(f"填充歌手隊列失敗: {e}")
    
    def run_multithreaded_scraping(self):
        """運行多線程歌手爬取"""
        try:
            self.logger.info("🚀 開始多線程歌手爬取...")
            
            # 填充歌手隊列
            self.populate_singer_queue()
            
            if self.stats['singers_queued'] == 0:
                self.logger.info("✅ 沒有需要處理的歌手")
                return
            
            # 啟動工作線程
            threads = []
            for i in range(self.max_threads):
                thread = threading.Thread(target=self.worker_thread, args=(i,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
            
            self.logger.info(f"🧵 已啟動 {self.max_threads} 個工作線程")
            
            # 監控進度
            last_completed = 0
            while self.running and self.stats['singers_completed'] < self.stats['singers_queued']:
                time.sleep(10)  # 每10秒檢查一次
                
                current_completed = self.stats['singers_completed']
                if current_completed > last_completed:
                    self.logger.info(f"📊 進度: {current_completed}/{self.stats['singers_queued']} 歌手完成")
                    self.logger.info(f"     已爬取: {self.stats['singers_scraped']} 位")
                    self.logger.info(f"     已跳過: {self.stats['singers_skipped']} 位")
                    self.logger.info(f"     活躍線程: {self.stats['active_threads']}")
                    
                    # 定期Git推送
                    if self.stats['singers_scraped'] % 5 == 0 and self.stats['singers_scraped'] > 0:
                        self.git_push_changes()
                    
                    last_completed = current_completed
            
            # 停止所有線程
            for _ in range(self.max_threads):
                self.singer_queue.put(None)  # 發送結束信號
            
            # 等待線程結束
            for thread in threads:
                thread.join(timeout=30)
            
            self.logger.info("🎉 多線程歌手爬取完成")
            
        except Exception as e:
            self.logger.error(f"多線程爬取失敗: {e}")
    
    def integrate_singer_data(self, singer_name, songs_data):
        """整合歌手資料到主資料庫（線程安全）"""
        try:
            with self.data_lock:  # 確保線程安全
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
                    # 展開KTV信息
                    for ktv_entry in song.get('ktv_info', []):
                        songs_dict[song_key].append(ktv_entry)
                
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
    
    def save_checkpoint(self, processed_singers):
        """保存檢查點"""
        try:
            with self.checkpoint_lock:
                checkpoint_data = {
                    "singers_queued": self.stats['singers_queued'],
                    "singers_completed": self.stats['singers_completed'],
                    "singers_scraped": self.stats['singers_scraped'],
                    "singers_skipped": self.stats['singers_skipped'],
                    "last_update": datetime.now().isoformat(),
                    "status": "running",
                    "processed_singers": processed_singers
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
                    
                self.logger.info(f"📊 檢查點已讀取: 已處理{data.get('singers_completed', 0)}位歌手")
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
                
                commit_message = f"🎵 歌手多線程爬取更新: {datetime.now().strftime('%Y%m%d_%H%M%S')}"
                subprocess.run(['git', 'commit', '-m', commit_message], check=True)
                
                subprocess.run(['git', 'push'], check=True)
                
                self.logger.info("✅ Git變更已自動推送")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Git推送失敗: {e}")
            return False

def main():
    """主函數"""
    scraper = SingerBasedMultithreadedScraper()
    
    try:
        # 運行多線程歌手爬取
        scraper.run_multithreaded_scraping()
        
    except KeyboardInterrupt:
        scraper.logger.info("🛑 用戶中斷")
    except Exception as e:
        scraper.logger.error(f"運行失敗: {e}")
    finally:
        scraper.logger.info("🏁 歌手多線程爬蟲已停止")

if __name__ == "__main__":
    main()