#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最佳化多線程台灣KTV爬蟲
- 分批保存避免記憶體問題
- 智能重試和錯誤恢復
- 實時進度監控
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os
from datetime import datetime
from urllib.parse import quote
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import signal
import sys

class OptimizedTaiwanScraper:
    def __init__(self, max_workers=5, batch_size=1000):
        self.companies = ["音圓", "弘音", "金嗓", "音圓原廠", "瑞影", "點將家", "嘉揚"]
        self.max_workers = max_workers
        self.batch_size = batch_size  # 每批保存的歌曲數
        
        # 會話管理
        self.sessions = {}
        self.session_lock = threading.Lock()
        
        # 數據管理  
        self.batch_data = []
        self.data_lock = threading.Lock()
        self.total_saved = 0
        self.batch_count = 0
        
        # 控制信號
        self.shutdown_event = threading.Event()
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # 輸出目錄
        os.makedirs('batches', exist_ok=True)
        os.makedirs('progress', exist_ok=True)
    
    def _signal_handler(self, signum, frame):
        print("\n🚨 收到停止信號，正在安全關閉...")
        self.shutdown_event.set()
    
    def _get_session(self, thread_id):
        """獲取線程專用會話"""
        with self.session_lock:
            if thread_id not in self.sessions:
                session = requests.Session()
                session.headers.update({
                    'User-Agent': self._random_user_agent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
                })
                self.sessions[thread_id] = session
            return self.sessions[thread_id]
    
    def _random_user_agent(self):
        """擴展的User-Agent池，更好的偽裝"""
        agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0'
        ]
        return random.choice(agents)
    
    def _smart_delay(self, thread_id, retry_count=0):
        """智能安全延遲機制"""
        base_delay = random.uniform(1.5, 4.0)  # 基礎隨機延遲
        
        # 根據重試次數增加延遲（指數退避）
        if retry_count > 0:
            backoff_delay = min(2 ** retry_count, 30)  # 最多30秒
            base_delay += backoff_delay
            
        # 線程間錯開延遲，避免同時請求
        thread_offset = (thread_id % 1000) * 0.1
        
        # 隨機抖動，模擬人類行為
        jitter = random.uniform(-0.5, 0.5)
        
        final_delay = base_delay + thread_offset + jitter
        final_delay = max(1.0, final_delay)  # 最小1秒
        
        if retry_count > 0:
            print(f"🧵 {thread_id}: 重試延遲 {final_delay:.1f}秒 (重試#{retry_count})")
        
        time.sleep(final_delay)
        
        # 每10次請求更換User-Agent
        if random.random() < 0.1:
            session = self._get_session(thread_id)
            session.headers['User-Agent'] = self._random_user_agent()
    
    def _save_batch(self):
        """保存當前批次數據"""
        if not self.batch_data:
            return
            
        self.batch_count += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batches/batch_{self.batch_count:04d}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.batch_data, f, ensure_ascii=False, indent=2)
            
            self.total_saved += len(self.batch_data)
            print(f"💾 批次{self.batch_count} 已保存: {len(self.batch_data)} 首歌 (總計: {self.total_saved})")
            print(f"   檔案: {filename}")
            
            self.batch_data.clear()
            
        except Exception as e:
            print(f"❌ 保存批次失敗: {e}")
    
    def scrape_page_range(self, company, start_page, end_page):
        """爬取指定頁面範圍"""
        thread_id = threading.get_ident()
        session = self._get_session(thread_id)
        
        page_data = []
        
        print(f"🧵 線程{thread_id}: 開始爬取 {company} 第{start_page}-{end_page}頁")
        
        for page in range(start_page, end_page + 1):
            if self.shutdown_event.is_set():
                break
                
            retry_count = 0
            max_retries = 3
            page_success = False
            
            while retry_count <= max_retries and not page_success:
                try:
                    # 智能安全延遲
                    self._smart_delay(thread_id, retry_count)
                    
                    url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
                    response = session.get(url, timeout=15)
                    response.encoding = "utf-8"
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        song_links = soup.select('a[href^="mv.aspx?id="]')
                        
                        if len(song_links) == 0:
                            print(f"🧵 {thread_id}: {company} 第{page}頁 無數據，可能已結束")
                            return page_data  # 結束爬取
                        
                        page_songs = 0
                        for link in song_links:
                            try:
                                link_text = link.get_text().strip()
                                parts = link_text.split()
                                
                                if len(parts) >= 4:
                                    song_data = {
                                        '公司': company,
                                        '編號': parts[0],
                                        '歌名': parts[1],
                                        '期別': parts[2], 
                                        '歌手': ' '.join(parts[3:]),
                                        '語言': '',
                                        'scraped_at': datetime.now().isoformat(),
                                        'thread_id': thread_id,
                                        'page_number': page
                                    }
                                    page_data.append(song_data)
                                    page_songs += 1
                            except:
                                continue
                        
                        if page % 50 == 0:
                            print(f"✅ 🧵 {thread_id}: {company} 第{page}頁: {page_songs} 首歌")
                        
                        page_success = True  # 成功，跳出重試循環
                        
                    else:
                        print(f"🧵 {thread_id}: 第{page}頁 HTTP {response.status_code}")
                        retry_count += 1
                        
                except Exception as e:
                    print(f"❌ 🧵 {thread_id}: {company} 第{page}頁錯誤: {e}")
                    retry_count += 1
            
            if not page_success:
                print(f"⚠️ 🧵 {thread_id}: 第{page}頁重試{max_retries}次後仍失敗，跳過")
        
        return page_data
    
    def scrape_company_batched(self, company, total_pages_estimate=15000):
        """分批爬取單一公司"""
        print(f"🎯 開始分批爬取: {company}")
        print(f"   估算總頁數: {total_pages_estimate}")
        print(f"   線程數: {self.max_workers}")
        print(f"   批次大小: {self.batch_size} 首歌")
        
        # 將頁面分配給線程
        pages_per_thread = 200  # 每個線程處理200頁
        page_ranges = []
        
        for start_page in range(1, total_pages_estimate + 1, pages_per_thread):
            end_page = min(start_page + pages_per_thread - 1, total_pages_estimate)
            page_ranges.append((start_page, end_page))
        
        print(f"📊 分配策略: {len(page_ranges)} 個任務，每任務最多{pages_per_thread}頁")
        
        completed_tasks = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交任務
            future_to_range = {
                executor.submit(self.scrape_page_range, company, start, end): (start, end)
                for start, end in page_ranges
            }
            
            for future in as_completed(future_to_range):
                if self.shutdown_event.is_set():
                    break
                    
                start, end = future_to_range[future]
                
                try:
                    page_data = future.result()
                    
                    # 添加到批次數據
                    with self.data_lock:
                        self.batch_data.extend(page_data)
                        
                        # 檢查是否需要保存批次
                        if len(self.batch_data) >= self.batch_size:
                            self._save_batch()
                    
                    completed_tasks += 1
                    print(f"🎉 任務完成 {completed_tasks}/{len(page_ranges)}: 第{start}-{end}頁 ({len(page_data)} 首歌)")
                    
                except Exception as e:
                    print(f"❌ 任務失敗 第{start}-{end}頁: {e}")
        
        # 保存剩餘數據
        with self.data_lock:
            if self.batch_data:
                self._save_batch()
        
        print(f"🎉 {company} 爬取完成！總共保存: {self.total_saved} 首歌")
    
    def merge_batches(self):
        """合併所有批次文件"""
        print("\n🔗 合併批次文件...")
        
        all_data = []
        batch_files = [f for f in os.listdir('batches') if f.endswith('.json')]
        batch_files.sort()
        
        for batch_file in batch_files:
            try:
                with open(f'batches/{batch_file}', 'r', encoding='utf-8') as f:
                    batch_data = json.load(f)
                    all_data.extend(batch_data)
                    print(f"✅ 合併 {batch_file}: {len(batch_data)} 首歌")
            except Exception as e:
                print(f"❌ 合併 {batch_file} 失敗: {e}")
        
        # 保存合併結果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        merged_file = f"merged_taiwan_songs_{timestamp}.json"
        
        try:
            with open(merged_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            print(f"🎉 合併完成: {merged_file}")
            print(f"📊 總歌曲數: {len(all_data)}")
            
            return merged_file
        except Exception as e:
            print(f"❌ 保存合併文件失敗: {e}")
            return None

def main():
    """主程序"""
    print("🎵 最佳化多線程台灣KTV爬蟲 v2.0")
    print("🚀 增強安全性版本 - 5線程 + 智能延遲")
    print("=" * 60)
    
    # 設置參數
    max_workers = 5
    batch_size = 1000
    
    print(f"⚙️ 設置:")
    print(f"   線程數: {max_workers}")
    print(f"   批次大小: {batch_size} 首歌")
    
    scraper = OptimizedTaiwanScraper(max_workers, batch_size)
    
    try:
        # 先爬取音圓公司
        scraper.scrape_company_batched("音圓", total_pages_estimate=15000)
        
        # 合併批次文件
        merged_file = scraper.merge_batches()
        
        if merged_file:
            print(f"\n✅ 爬蟲任務完成！")
            print(f"📁 合併文件: {merged_file}")
            print(f"📊 總歌曲數: {scraper.total_saved}")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用戶中斷")
    except Exception as e:
        print(f"\n❌ 爬蟲執行失敗: {e}")
    finally:
        # 清理會話
        for session in scraper.sessions.values():
            session.close()
        
        print("\n📊 最終統計:")
        print(f"   保存批次數: {scraper.batch_count}")
        print(f"   總歌曲數: {scraper.total_saved}")

if __name__ == "__main__":
    main()