#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復版音圓爬蟲 - 解決ASP.NET ViewState問題
支援動態頁面導航和反爬機制
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os
from datetime import datetime
from urllib.parse import quote, urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import signal
import sys
import re

class FixedAutoScraper:
    def __init__(self):
        self.company = "音圓"
        self.start_page = 1
        self.threads = 5  # 降低線程數避免被檢測
        self.max_test_pages = 10  # 先測試10頁
        
        # 設置信號處理
        signal.signal(signal.SIGINT, self._signal_handler)
        self.shutdown_requested = False
        
        # 創建輸出目錄
        os.makedirs("fixed_results", exist_ok=True)
        
        # 統計
        self.total_songs = 0
        self.completed_pages = 0
        self.stats_lock = threading.Lock()
        
        print(f"🔧 修復版音圓爬蟲啟動")
        print(f"   公司: {self.company}")
        print(f"   測試頁數: {self.max_test_pages}")
        print(f"   線程數: {self.threads}")
        print("=" * 50)
    
    def _signal_handler(self, signum, frame):
        print(f"\\n⚠️ 接收到中斷信號 ({signum})，正在安全關閉...")
        self.shutdown_requested = True
    
    def get_viewstate_and_validation(self, session, url):
        """獲取ASP.NET ViewState和EventValidation"""
        try:
            response = session.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                viewstate_generator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
                event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})
                
                return {
                    'viewstate': viewstate['value'] if viewstate else '',
                    'viewstate_generator': viewstate_generator['value'] if viewstate_generator else '',
                    'event_validation': event_validation['value'] if event_validation else ''
                }
        except Exception as e:
            print(f"獲取ViewState失敗: {e}")
            
        return None
    
    def scrape_page_with_postback(self, session, page_num):
        """使用ASP.NET PostBack機制抓取頁面"""
        try:
            base_url = "https://song.corp.com.tw/songs.aspx"
            initial_url = f"{base_url}?company={quote(self.company)}"
            
            # 獲取初始ViewState
            viewstate_data = self.get_viewstate_and_validation(session, initial_url)
            if not viewstate_data:
                return None
            
            # 如果是第1頁，直接使用GET請求
            if page_num == 1:
                response = session.get(f"{initial_url}&page=1", timeout=15)
            else:
                # 對於其他頁面，嘗試POST請求模擬翻頁
                post_data = {
                    '__VIEWSTATE': viewstate_data['viewstate'],
                    '__VIEWSTATEGENERATOR': viewstate_data['viewstate_generator'],
                    '__EVENTVALIDATION': viewstate_data['event_validation'],
                    '__EVENTTARGET': '',
                    '__EVENTARGUMENT': '',
                    'page': str(page_num),
                    'company': self.company
                }
                
                response = session.post(base_url, data=post_data, timeout=15)
            
            if response.status_code == 200:
                response.encoding = "utf-8"
                soup = BeautifulSoup(response.text, 'html.parser')
                song_links = soup.select('a[href^="mv.aspx?id="]')
                
                songs_data = []
                if song_links:
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
                                    'page': page_num,
                                    'scraped_at': datetime.now().isoformat()
                                }
                                songs_data.append(song_data)
                        except:
                            continue
                
                return songs_data
            else:
                print(f"第{page_num}頁請求失敗: {response.status_code}")
                
        except Exception as e:
            print(f"第{page_num}頁抓取錯誤: {e}")
            
        return None
    
    def scrape_page_batch(self, thread_id, pages):
        """每個線程處理一批頁面"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.{random.randint(1000,9999)}.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        batch_data = []
        thread_songs = 0
        successful_pages = 0
        
        print(f"🧵 線程{thread_id:2d}: 開始處理 {len(pages)} 頁")
        
        for page_num in pages:
            if self.shutdown_requested:
                break
                
            try:
                # 智能延遲
                delay = random.uniform(3, 8)  # 增加延遲避免檢測
                time.sleep(delay)
                
                songs_data = self.scrape_page_with_postback(session, page_num)
                
                if songs_data:
                    batch_data.extend(songs_data)
                    thread_songs += len(songs_data)
                    successful_pages += 1
                    
                    # 檢查數據唯一性
                    unique_ids = set(song['編號'] for song in songs_data)
                    print(f"✅ 🧵 {thread_id:2d}: 第{page_num:3d}頁 ({len(songs_data):2d}首，{len(unique_ids)}個唯一ID)")
                    
                    # 如果所有歌曲ID都相同，說明仍有問題
                    if len(unique_ids) == 1 and len(songs_data) > 1:
                        print(f"⚠️ 🧵 {thread_id:2d}: 第{page_num}頁所有歌曲ID相同，可能仍有反爬問題")
                        
                else:
                    print(f"❌ 🧵 {thread_id:2d}: 第{page_num}頁無數據")
                
                # 每50首歌保存一次
                if len(batch_data) >= 50:
                    self.save_batch_data(thread_id, batch_data.copy())
                    batch_data = []
                    
            except Exception as e:
                print(f"❌ 🧵 {thread_id:2d}: 第{page_num}頁錯誤: {e}")
                time.sleep(2)
        
        # 保存剩餘數據
        if batch_data:
            self.save_batch_data(thread_id, batch_data)
        
        with self.stats_lock:
            self.total_songs += thread_songs
            self.completed_pages += successful_pages
        
        session.close()
        print(f"🎉 🧵 {thread_id:2d}: 完成！處理 {successful_pages} 頁，收集 {thread_songs} 首歌")
        return thread_songs, successful_pages
    
    def save_batch_data(self, thread_id, data):
        """保存批次數據"""
        if not data:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"fixed_results/T{thread_id:02d}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 🧵 {thread_id:2d}: 保存 {len(data)} 首歌到 {filename}")
        except Exception as e:
            print(f"❌ 🧵 {thread_id:2d}: 保存失敗: {e}")
    
    def run_test(self):
        """運行測試版本"""
        print(f"🧪 開始測試前{self.max_test_pages}頁...")
        
        # 頁面分配
        pages_per_thread = max(1, self.max_test_pages // self.threads)
        page_assignments = []
        
        current_page = self.start_page
        for i in range(self.threads):
            end_page = min(current_page + pages_per_thread - 1, self.max_test_pages)
            if current_page <= end_page:
                thread_pages = list(range(current_page, end_page + 1))
                page_assignments.append((i + 1, thread_pages))
                current_page = end_page + 1
        
        start_time = datetime.now()
        
        # 執行測試
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for thread_id, pages in page_assignments:
                future = executor.submit(self.scrape_page_batch, thread_id, pages)
                futures.append((future, thread_id))
            
            total_collected = 0
            total_pages_processed = 0
            
            for future, thread_id in futures:
                try:
                    songs_count, pages_processed = future.result()
                    total_collected += songs_count
                    total_pages_processed += pages_processed
                    
                except Exception as e:
                    print(f"❌ 線程{thread_id} 執行失敗: {e}")
        
        # 測試結果統計
        elapsed = datetime.now() - start_time
        
        print(f"\\n🧪 測試結果報告")
        print("=" * 50)
        print(f"測試頁面: {self.max_test_pages} 頁")
        print(f"處理頁面: {total_pages_processed} 頁")
        print(f"收集歌曲: {total_collected} 首")
        print(f"總耗時: {elapsed}")
        
        if total_collected > 0:
            # 分析數據唯一性
            self.analyze_test_results()
            return True
        else:
            print("❌ 測試失敗，未收集到任何歌曲")
            return False
    
    def analyze_test_results(self):
        """分析測試結果"""
        try:
            import glob
            result_files = sorted(glob.glob("fixed_results/*.json"))
            
            if not result_files:
                print("沒有找到測試結果文件")
                return
            
            all_songs = []
            for file in result_files:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_songs.extend(data)
            
            if all_songs:
                unique_ids = set(song['編號'] for song in all_songs)
                unique_names = set(f"{song['歌名']}_{song['歌手']}" for song in all_songs)
                
                print(f"\\n📊 測試數據分析:")
                print(f"總記錄數: {len(all_songs)}")
                print(f"唯一歌曲ID: {len(unique_ids)}")
                print(f"唯一歌名+歌手: {len(unique_names)}")
                
                if len(unique_ids) > len(all_songs) * 0.8:  # 80%以上是唯一的
                    print("✅ 修復成功！數據唯一性良好")
                elif len(unique_ids) > 10:  # 至少有10首不同的歌
                    print("⚠️ 部分修復！有一定唯一性但仍需改進")
                else:
                    print("❌ 修復失敗！仍存在大量重複")
                
                # 顯示樣本
                print(f"\\n🎵 歌曲樣本:")
                sample_ids = list(unique_ids)[:5]
                for song in all_songs:
                    if song['編號'] in sample_ids:
                        print(f"  {song['編號']} - {song['歌名']} - {song['歌手']} (第{song['page']}頁)")
                        sample_ids.remove(song['編號'])
                        if not sample_ids:
                            break
        
        except Exception as e:
            print(f"分析結果時出錯: {e}")

def main():
    scraper = FixedAutoScraper()
    
    try:
        if scraper.run_test():
            print(f"\\n🎊 測試完成！可以開始大規模爬取")
        else:
            print(f"\\n❌ 測試失敗，需要進一步修復")
        
    except KeyboardInterrupt:
        print(f"\\n⚠️ 用戶中斷測試")
        
    except Exception as e:
        print(f"\\n❌ 運行錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()