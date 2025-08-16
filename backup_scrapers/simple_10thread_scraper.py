#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版10線程台灣KTV爬蟲
直接實現，不依賴複雜繼承
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os
import threading
from datetime import datetime
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
import signal
import sys

class Simple10ThreadScraper:
    def __init__(self):
        self.company = "音圓"
        self.start_page = 6920
        self.max_threads = 10
        self.batch_size = 1000
        self.shutdown_event = threading.Event()
        
        # 創建批次文件夾
        os.makedirs("batches", exist_ok=True)
        
        # 線程會話管理
        self.sessions = {}
        self.session_lock = threading.Lock()
        
        # 數據管理
        self.all_data = []
        self.data_lock = threading.Lock()
        self.batch_counter = 0
        
        # 性能統計
        self.stats = {
            'pages_completed': 0,
            'songs_collected': 0,
            'start_time': datetime.now()
        }
        self.stats_lock = threading.Lock()
        
        # 註冊信號處理
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        print("\n⚠️ 接收到中斷信號，正在安全關閉...")
        self.shutdown_event.set()
    
    def _get_session(self, thread_id):
        """獲取線程專用session"""
        with self.session_lock:
            if thread_id not in self.sessions:
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
                })
                self.sessions[thread_id] = session
            return self.sessions[thread_id]
    
    def _save_batch(self, data):
        """保存批次數據"""
        if not data:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.batch_counter += 1
        filename = f"batches/batch_{self.batch_counter:04d}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 保存批次: {filename} ({len(data)} 首歌)")
        except Exception as e:
            print(f"❌ 保存失敗: {e}")
    
    def _scrape_page_range(self, start_page, end_page):
        """爬取頁面範圍"""
        thread_id = threading.get_ident()
        session = self._get_session(thread_id)
        thread_data = []
        
        print(f"🧵 線程{thread_id}: 開始爬取第{start_page}-{end_page}頁")
        
        for page in range(start_page, end_page + 1):
            if self.shutdown_event.is_set():
                break
                
            retry_count = 0
            max_retries = 3
            page_success = False
            
            while retry_count <= max_retries and not page_success:
                try:
                    # 智能延遲
                    base_delay = random.uniform(2.0, 5.0)
                    thread_offset = (thread_id % 1000) * 0.1
                    jitter = random.uniform(-0.5, 0.5)
                    delay = max(1.0, base_delay + thread_offset + jitter)
                    time.sleep(delay)
                    
                    url = f"https://song.corp.com.tw/songs.aspx?company={quote(self.company)}&page={page}"
                    response = session.get(url, timeout=15)
                    response.encoding = "utf-8"
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        song_links = soup.select('a[href^="mv.aspx?id="]')
                        
                        if len(song_links) == 0:
                            print(f"🧵 {thread_id}: 第{page}頁無數據，可能已到達終點")
                            return thread_data
                        
                        page_songs = 0
                        for link in song_links:
                            try:
                                link_text = link.get_text().strip()
                                parts = link_text.split()
                                
                                if len(parts) >= 4:
                                    song_data = {
                                        '公司': self.company,
                                        '編號': parts[0],
                                        '歌名': parts[1],
                                        '期別': parts[2],
                                        '歌手': ' '.join(parts[3:]),
                                        '語言': '',
                                        'scraped_at': datetime.now().isoformat(),
                                        'thread_id': thread_id,
                                        'page_number': page
                                    }
                                    thread_data.append(song_data)
                                    page_songs += 1
                            except:
                                continue
                        
                        if page % 20 == 0:
                            print(f"✅ 🧵 {thread_id}: 第{page}頁完成 ({page_songs} 首歌)")
                        
                        # 更新統計
                        with self.stats_lock:
                            self.stats['pages_completed'] += 1
                            self.stats['songs_collected'] += page_songs
                        
                        page_success = True
                        
                        # 批次保存
                        if len(thread_data) >= 500:  # 線程級批次保存
                            with self.data_lock:
                                self.all_data.extend(thread_data)
                                if len(self.all_data) >= self.batch_size:
                                    self._save_batch(self.all_data)
                                    self.all_data = []
                            thread_data = []
                            
                    else:
                        print(f"🧵 {thread_id}: 第{page}頁 HTTP {response.status_code}")
                        retry_count += 1
                        
                except Exception as e:
                    print(f"❌ 🧵 {thread_id}: 第{page}頁錯誤: {e}")
                    retry_count += 1
                    
                if retry_count > 0:
                    backoff_delay = min(2 ** retry_count, 10)
                    time.sleep(backoff_delay)
            
            if not page_success:
                print(f"⚠️ 🧵 {thread_id}: 第{page}頁重試{max_retries}次後仍失敗")
        
        return thread_data
    
    def scrape_company(self):
        """開始爬取"""
        print(f"🚀 開始10線程爬取: {self.company}")
        print(f"   起始頁面: 第{self.start_page}頁")
        print(f"   線程數: {self.max_threads}")
        print("=" * 60)
        
        # 計算頁面範圍
        pages_per_thread = 200
        total_estimated_pages = 20000
        remaining_pages = total_estimated_pages - self.start_page + 1
        
        page_ranges = []
        current_page = self.start_page
        
        while current_page <= total_estimated_pages:
            end_page = min(current_page + pages_per_thread - 1, total_estimated_pages)
            page_ranges.append((current_page, end_page))
            current_page = end_page + 1
        
        print(f"📊 任務分配: {len(page_ranges)} 個任務，每個任務 {pages_per_thread} 頁")
        
        # 多線程執行
        completed_tasks = 0
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            future_to_range = {
                executor.submit(self._scrape_page_range, start, end): (start, end)
                for start, end in page_ranges
            }
            
            for future in as_completed(future_to_range):
                if self.shutdown_event.is_set():
                    break
                    
                start, end = future_to_range[future]
                
                try:
                    thread_data = future.result()
                    
                    # 合併數據
                    with self.data_lock:
                        self.all_data.extend(thread_data)
                        if len(self.all_data) >= self.batch_size:
                            self._save_batch(self.all_data)
                            self.all_data = []
                    
                    completed_tasks += 1
                    progress = (completed_tasks / len(page_ranges)) * 100
                    print(f"🎉 任務完成 {completed_tasks}/{len(page_ranges)} ({progress:.1f}%): 第{start}-{end}頁")
                    
                except Exception as e:
                    print(f"❌ 任務失敗 第{start}-{end}頁: {e}")
        
        # 保存剩餘數據
        with self.data_lock:
            if self.all_data:
                self._save_batch(self.all_data)
        
        self._print_final_stats()
    
    def _print_final_stats(self):
        """打印最終統計"""
        elapsed = datetime.now() - self.stats['start_time']
        hours = elapsed.total_seconds() / 3600
        
        print(f"\n🎉 爬取完成！")
        print("=" * 50)
        print(f"完成頁面: {self.stats['pages_completed']:,} 頁")
        print(f"收集歌曲: {self.stats['songs_collected']:,} 首")
        print(f"總耗時: {hours:.2f} 小時")
        if hours > 0:
            print(f"平均速度: {self.stats['songs_collected'] / hours:,.0f} 首歌/小時")
        
        # 合併批次文件
        self._merge_batches()
    
    def _merge_batches(self):
        """合併批次文件"""
        try:
            import glob
            batch_files = sorted(glob.glob("batches/*.json"))
            
            if not batch_files:
                print("❌ 沒有找到批次文件")
                return
            
            all_songs = []
            for batch_file in batch_files:
                with open(batch_file, 'r', encoding='utf-8') as f:
                    batch_data = json.load(f)
                    all_songs.extend(batch_data)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            merged_file = f"taiwan_{self.company}_complete_{timestamp}.json"
            
            with open(merged_file, 'w', encoding='utf-8') as f:
                json.dump(all_songs, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 合併完成: {merged_file}")
            print(f"📊 總歌曲數: {len(all_songs):,} 首")
            
        except Exception as e:
            print(f"❌ 合併失敗: {e}")
    
    def cleanup(self):
        """清理資源"""
        for session in self.sessions.values():
            session.close()

def main():
    """主程序"""
    print("🎵 簡化版10線程台灣KTV爬蟲")
    print("🔥 專為完成音圓數據收集而設計")
    print("=" * 60)
    
    scraper = Simple10ThreadScraper()
    
    try:
        scraper.scrape_company()
    except KeyboardInterrupt:
        print("\n⚠️ 用戶中斷")
    except Exception as e:
        print(f"\n❌ 爬取失敗: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()