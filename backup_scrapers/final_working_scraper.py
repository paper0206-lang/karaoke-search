#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終工作版10線程爬蟲 - 完成音圓數據收集
基於測試成功的代碼，確保立即工作
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

class FinalWorkingScraper:
    def __init__(self):
        self.company = "音圓"
        self.start_page = 6920
        self.threads = 10
        self.total_pages = 20000
        
        # 創建輸出目錄
        os.makedirs("final_results", exist_ok=True)
        
        # 統計
        self.total_songs = 0
        self.completed_pages = 0
        self.stats_lock = threading.Lock()
        
        print(f"🚀 啟動最終工作版10線程爬蟲")
        print(f"   公司: {self.company}")
        print(f"   起始頁: {self.start_page}")
        print(f"   線程數: {self.threads}")
        print("=" * 50)
    
    def scrape_page_batch(self, thread_id, pages):
        """每個線程處理一批頁面"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        batch_data = []
        thread_songs = 0
        
        print(f"🧵 線程{thread_id}: 開始處理 {len(pages)} 頁 (第{pages[0]}-{pages[-1]}頁)")
        
        for page_num in pages:
            try:
                # 延遲策略：基礎延遲 + 線程偏移 + 隨機抖動
                base_delay = random.uniform(2.0, 4.0)
                thread_offset = (thread_id % 10) * 0.2
                jitter = random.uniform(-0.3, 0.3)
                delay = max(1.0, base_delay + thread_offset + jitter)
                time.sleep(delay)
                
                url = f"https://song.corp.com.tw/songs.aspx?company={quote(self.company)}&page={page_num}"
                response = session.get(url, timeout=15)
                response.encoding = "utf-8"
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    song_links = soup.select('a[href^="mv.aspx?id="]')
                    
                    if not song_links:
                        print(f"🧵 {thread_id}: 第{page_num}頁無數據，到達終點")
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
                    
                    # 每10頁報告一次進度
                    if page_num % 10 == 0:
                        print(f"✅ 🧵 {thread_id}: 第{page_num}頁完成 ({page_songs}首歌)")
                    
                    # 每200首歌保存一次（防止數據丟失）
                    if len(batch_data) >= 200:
                        self.save_batch_data(thread_id, batch_data.copy())
                        batch_data = []
                    
                else:
                    print(f"❌ 🧵 {thread_id}: 第{page_num}頁 HTTP {response.status_code}")
                
            except Exception as e:
                print(f"❌ 🧵 {thread_id}: 第{page_num}頁錯誤: {e}")
                # 遇到錯誤時稍微等待一下
                time.sleep(2)
        
        # 保存剩餘數據
        if batch_data:
            self.save_batch_data(thread_id, batch_data)
        
        with self.stats_lock:
            self.total_songs += thread_songs
            self.completed_pages += len([p for p in pages if p <= page_num])
        
        session.close()
        print(f"🎉 🧵 {thread_id}: 線程完成！收集 {thread_songs} 首歌")
        return thread_songs
    
    def save_batch_data(self, thread_id, data):
        """保存批次數據"""
        if not data:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"final_results/thread{thread_id:02d}_batch_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 🧵 {thread_id}: 保存 {len(data)} 首歌到 {os.path.basename(filename)}")
        except Exception as e:
            print(f"❌ 🧵 {thread_id}: 保存失敗: {e}")
    
    def run(self):
        """開始運行"""
        # 計算頁面分配 - 每個線程處理連續的頁面範圍
        remaining_pages = self.total_pages - self.start_page + 1
        pages_per_thread = remaining_pages // self.threads
        
        page_assignments = []
        current_page = self.start_page
        
        for i in range(self.threads):
            if i == self.threads - 1:  # 最後一個線程處理剩餘頁面
                end_page = self.total_pages
            else:
                end_page = current_page + pages_per_thread - 1
            
            thread_pages = list(range(current_page, min(end_page + 1, self.total_pages + 1)))
            page_assignments.append((i + 1, thread_pages))
            current_page = end_page + 1
        
        print(f"📊 頁面分配:")
        total_assigned = 0
        for thread_id, pages in page_assignments:
            print(f"   線程{thread_id:2d}: {len(pages):4d}頁 (第{pages[0]:5d}-{pages[-1]:5d}頁)")
            total_assigned += len(pages)
        print(f"   總計:   {total_assigned:4d}頁")
        
        print(f"\n🚀 開始10線程並行爬取...")
        print(f"⚡ 預估完成時間: {(total_assigned * 3) / (60 * 10):.1f} 小時 (基於3秒/頁)")
        start_time = datetime.now()
        
        # 執行多線程爬取
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for thread_id, pages in page_assignments:
                future = executor.submit(self.scrape_page_batch, thread_id, pages)
                futures.append((future, thread_id))
            
            # 等待所有線程完成並收集結果
            total_collected = 0
            completed_threads = 0
            for future, thread_id in futures:
                try:
                    songs_count = future.result()
                    total_collected += songs_count
                    completed_threads += 1
                    print(f"✅ 線程{thread_id} 完成，收集 {songs_count} 首歌 ({completed_threads}/{self.threads})")
                except Exception as e:
                    print(f"❌ 線程{thread_id} 執行失敗: {e}")
        
        # 最終統計
        elapsed = datetime.now() - start_time
        hours = elapsed.total_seconds() / 3600
        
        print(f"\n🎉 爬取完成！")
        print("=" * 60)
        print(f"處理頁面: {self.completed_pages:,} 頁")
        print(f"收集歌曲: {self.total_songs:,} 首")
        print(f"總耗時: {elapsed}")
        if hours > 0:
            pages_per_hour = self.completed_pages / hours
            songs_per_hour = self.total_songs / hours
            print(f"平均速度: {pages_per_hour:,.1f} 頁/小時, {songs_per_hour:,.0f} 首歌/小時")
        
        # 合併所有結果文件
        self.merge_results()
    
    def merge_results(self):
        """合併結果文件"""
        try:
            import glob
            result_files = sorted(glob.glob("final_results/*.json"))
            
            if not result_files:
                print("❌ 沒有找到結果文件")
                return
            
            print(f"📁 找到 {len(result_files)} 個結果文件，開始合併...")
            
            all_songs = []
            for file in result_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_songs.extend(data)
                        print(f"   ✅ {os.path.basename(file)}: {len(data)} 首歌")
                except Exception as e:
                    print(f"   ❌ {os.path.basename(file)}: 讀取失敗 - {e}")
            
            # 按頁面編號排序
            all_songs.sort(key=lambda x: (x.get('page', 0), x.get('編號', '')))
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_file = f"taiwan_{self.company}_complete_{timestamp}.json"
            
            with open(final_file, 'w', encoding='utf-8') as f:
                json.dump(all_songs, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ 最終合併文件: {final_file}")
            print(f"📊 總歌曲數: {len(all_songs):,} 首")
            
            # 統計信息
            if all_songs:
                pages = sorted(set(song.get('page', 0) for song in all_songs))
                print(f"📄 覆蓋頁面: 第{pages[0]}-{pages[-1]}頁 (共 {len(pages)} 頁)")
                
                # 歌手統計
                singers = set(song.get('歌手', '') for song in all_songs)
                print(f"🎤 涉及歌手: {len(singers)} 位")
                
                # 樣本展示
                print(f"📝 樣本歌曲:")
                for i, song in enumerate(all_songs[:5]):
                    print(f"   {i+1}. {song.get('歌名', '')} - {song.get('歌手', '')} ({song.get('編號', '')})")
            
        except Exception as e:
            print(f"❌ 合併失敗: {e}")
            import traceback
            traceback.print_exc()

def main():
    scraper = FinalWorkingScraper()
    
    try:
        print("🎯 準備開始爬取...")
        print("⚠️  按 Ctrl+C 可隨時安全中斷")
        input("按 Enter 繼續，或 Ctrl+C 取消...")
        
        scraper.run()
        
        print(f"\n🎊 任務完成！音圓數據收集已完成")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用戶中斷爬蟲")
        print("💾 已保存的數據在 final_results/ 文件夾中")
    except Exception as e:
        print(f"\n❌ 運行錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()