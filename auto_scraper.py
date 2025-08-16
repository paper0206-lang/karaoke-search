#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動10線程爬蟲 - 立即開始，無需確認
完成音圓數據收集任務
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os
from datetime import datetime
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import signal
import sys

class AutoScraper:
    def __init__(self):
        self.company = "音圓"
        self.start_page = 1  # 從第1頁開始完整爬取
        self.threads = 10
        self.total_pages = 25000  # 增加上限確保完整
        
        # 設置信號處理
        signal.signal(signal.SIGINT, self._signal_handler)
        self.shutdown_requested = False
        
        # 創建輸出目錄
        os.makedirs("auto_results", exist_ok=True)
        
        # 統計
        self.total_songs = 0
        self.completed_pages = 0
        self.stats_lock = threading.Lock()
        
        print(f"🚀 自動10線程爬蟲啟動")
        print(f"   公司: {self.company}")
        print(f"   起始頁: {self.start_page}")
        print(f"   線程數: {self.threads}")
        print(f"   預估頁面: {self.total_pages - self.start_page + 1:,} 頁")
        print("=" * 50)
    
    def _signal_handler(self, signum, frame):
        print(f"\n⚠️ 接收到中斷信號 ({signum})，正在安全關閉...")
        self.shutdown_requested = True
    
    def scrape_page_batch(self, thread_id, pages):
        """每個線程處理一批頁面"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        batch_data = []
        thread_songs = 0
        successful_pages = 0
        
        print(f"🧵 線程{thread_id:2d}: 開始處理 {len(pages)} 頁 (第{pages[0]}-{pages[-1]}頁)")
        
        for page_num in pages:
            if self.shutdown_requested:
                print(f"🧵 {thread_id}: 接收到關閉信號，停止處理")
                break
                
            try:
                # 智能延遲策略
                base_delay = random.uniform(2.5, 4.5)
                thread_offset = (thread_id % 10) * 0.15
                jitter = random.uniform(-0.3, 0.3)
                delay = max(1.5, base_delay + thread_offset + jitter)
                time.sleep(delay)
                
                url = f"https://song.corp.com.tw/songs.aspx?company={quote(self.company)}&page={page_num}"
                response = session.get(url, timeout=15)
                response.encoding = "utf-8"
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    song_links = soup.select('a[href^="mv.aspx?id="]')
                    
                    if not song_links:
                        print(f"🧵 {thread_id}: 第{page_num}頁無數據，可能到達終點")
                        break
                    
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
                                    'page': page_num,
                                    'thread': thread_id,
                                    'scraped_at': datetime.now().isoformat()
                                }
                                batch_data.append(song_data)
                                page_songs += 1
                        except:
                            continue
                    
                    thread_songs += page_songs
                    successful_pages += 1
                    
                    # 每5頁報告一次進度
                    if page_num % 5 == 0 or len(batch_data) >= 200:
                        print(f"✅ 🧵 {thread_id:2d}: 第{page_num:5d}頁 ({page_songs:2d}首) 累計:{thread_songs:4d}首")
                    
                    # 每150首歌保存一次
                    if len(batch_data) >= 150:
                        self.save_batch_data(thread_id, batch_data.copy())
                        batch_data = []
                    
                else:
                    print(f"❌ 🧵 {thread_id}: 第{page_num}頁 HTTP {response.status_code}")
                
            except Exception as e:
                print(f"❌ 🧵 {thread_id}: 第{page_num}頁錯誤: {e}")
                time.sleep(1)  # 錯誤後短暫等待
        
        # 保存剩餘數據
        if batch_data:
            self.save_batch_data(thread_id, batch_data)
        
        with self.stats_lock:
            self.total_songs += thread_songs
            self.completed_pages += successful_pages
        
        session.close()
        print(f"🎉 🧵 {thread_id:2d}: 線程完成！成功處理 {successful_pages} 頁，收集 {thread_songs} 首歌")
        return thread_songs, successful_pages
    
    def save_batch_data(self, thread_id, data):
        """保存批次數據"""
        if not data:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"auto_results/T{thread_id:02d}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 🧵 {thread_id:2d}: 保存 {len(data)} 首歌")
        except Exception as e:
            print(f"❌ 🧵 {thread_id:2d}: 保存失敗: {e}")
    
    def run(self):
        """開始運行"""
        # 計算頁面分配
        remaining_pages = self.total_pages - self.start_page + 1
        pages_per_thread = remaining_pages // self.threads
        
        page_assignments = []
        current_page = self.start_page
        
        for i in range(self.threads):
            if i == self.threads - 1:
                end_page = self.total_pages
            else:
                end_page = current_page + pages_per_thread - 1
            
            thread_pages = list(range(current_page, min(end_page + 1, self.total_pages + 1)))
            page_assignments.append((i + 1, thread_pages))
            current_page = end_page + 1
        
        print(f"📊 頁面分配策略:")
        total_assigned = 0
        for thread_id, pages in page_assignments:
            print(f"   線程{thread_id:2d}: {len(pages):4d}頁 (第{pages[0]:5d}-{pages[-1]:5d}頁)")
            total_assigned += len(pages)
        print(f"   總計:   {total_assigned:4d}頁")
        
        # 估算完成時間
        estimated_hours = (total_assigned * 3.0) / (60 * 60)  # 假設平均3秒/頁
        print(f"\n⏱️  預估完成時間: {estimated_hours:.1f} 小時")
        print(f"🎯 預估收集歌曲: {total_assigned * 50:,} 首 (每頁50首)")
        
        print(f"\n🚀 立即開始10線程並行爬取...")
        start_time = datetime.now()
        
        # 執行多線程爬取
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for thread_id, pages in page_assignments:
                future = executor.submit(self.scrape_page_batch, thread_id, pages)
                futures.append((future, thread_id))
            
            # 監控進度
            completed_threads = 0
            total_collected = 0
            total_pages_processed = 0
            
            for future, thread_id in futures:
                try:
                    songs_count, pages_processed = future.result()
                    total_collected += songs_count
                    total_pages_processed += pages_processed
                    completed_threads += 1
                    
                    print(f"✅ 線程{thread_id:2d} 完成: {songs_count:4d}首歌, {pages_processed:4d}頁 ({completed_threads}/{self.threads})")
                    
                except Exception as e:
                    print(f"❌ 線程{thread_id:2d} 執行失敗: {e}")
        
        # 最終統計
        elapsed = datetime.now() - start_time
        hours = elapsed.total_seconds() / 3600
        
        print(f"\n🎉 爬取任務完成！")
        print("=" * 60)
        print(f"實際處理頁面: {total_pages_processed:,} 頁")
        print(f"實際收集歌曲: {total_collected:,} 首")
        print(f"總耗時: {elapsed}")
        
        if hours > 0:
            pages_per_hour = total_pages_processed / hours
            songs_per_hour = total_collected / hours
            print(f"實際速度: {pages_per_hour:,.1f} 頁/小時, {songs_per_hour:,.0f} 首歌/小時")
            
            if pages_per_hour > 0:
                remaining_pages_est = max(0, self.total_pages - (self.start_page + total_pages_processed))
                remaining_hours = remaining_pages_est / pages_per_hour
                print(f"剩餘估算: 還需 {remaining_hours:.1f} 小時完成剩餘 {remaining_pages_est:,} 頁")
        
        # 合併結果
        self.merge_results()
    
    def merge_results(self):
        """合併結果文件"""
        try:
            import glob
            result_files = sorted(glob.glob("auto_results/*.json"))
            
            if not result_files:
                print("❌ 沒有找到結果文件")
                return
            
            print(f"\n📁 合併 {len(result_files)} 個結果文件...")
            
            all_songs = []
            for file in result_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_songs.extend(data)
                except Exception as e:
                    print(f"   ❌ 讀取失敗 {os.path.basename(file)}: {e}")
            
            if not all_songs:
                print("❌ 沒有成功讀取任何數據")
                return
            
            # 排序和去重
            all_songs.sort(key=lambda x: (x.get('page', 0), x.get('編號', '')))
            
            # 保存最終結果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_file = f"音圓完整數據_{timestamp}.json"
            
            with open(final_file, 'w', encoding='utf-8') as f:
                json.dump(all_songs, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 最終文件: {final_file}")
            print(f"📊 總歌曲數: {len(all_songs):,} 首")
            
            # 統計分析
            if all_songs:
                pages = sorted(set(song.get('page', 0) for song in all_songs))
                singers = set(song.get('歌手', '') for song in all_songs)
                
                print(f"📄 頁面範圍: 第{pages[0]}-{pages[-1]}頁 (共 {len(pages)} 頁)")
                print(f"🎤 涉及歌手: {len(singers)} 位")
                
                print(f"\n📝 樣本歌曲:")
                sample_songs = random.sample(all_songs, min(5, len(all_songs)))
                for i, song in enumerate(sample_songs, 1):
                    print(f"   {i}. {song.get('歌名', '')} - {song.get('歌手', '')} ({song.get('編號', '')})")
            
            return final_file
            
        except Exception as e:
            print(f"❌ 合併失敗: {e}")
            import traceback
            traceback.print_exc()

def main():
    scraper = AutoScraper()
    
    try:
        scraper.run()
        print(f"\n🎊 音圓數據收集任務完成！")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ 用戶中斷爬蟲")
        print(f"💾 已保存的數據在 auto_results/ 文件夾中")
        
    except Exception as e:
        print(f"\n❌ 運行錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()