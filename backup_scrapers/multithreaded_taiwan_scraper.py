#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多線程增強版台灣點歌王爬蟲
基於你的原始程式碼優化：進度記錄 + 多線程 + 智能限速 + 錯誤恢復
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os
import csv
from datetime import datetime
from urllib.parse import quote
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue
import signal
import sys

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multithreaded_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class MultiThreadedTaiwanScraper:
    def __init__(self, max_workers=3):
        self.companies = [
            "音圓", "弘音", "金嗓", "音圓原廠", "瑞影", "點將家", "嘉揚", "音遊",
            "音影", "美華", "金影", "金嗓/投幣", "一級棒", "錢櫃", "好樂迪", "星據點",
            "銀櫃", "享溫馨", "大唐", "MV", "金嗓/家庭"
        ]
        
        self.max_workers = max_workers
        self.sessions = {}  # 每個線程一個session
        self.all_data = []
        self.data_lock = threading.Lock()
        
        # 進度管理
        self.progress_file = 'multithreaded_progress.json'
        self.progress = self._load_progress()
        self.progress_lock = threading.Lock()
        
        # 輸出文件
        self.output_files = {
            'csv': 'taiwan_multithreaded_all.csv',
            'json': 'public/taiwan_songs_raw.json',
            'unified': 'public/songs_simplified.json'
        }
        
        # 智能限速
        self.request_times = Queue()
        self.rate_limit_lock = threading.Lock()
        
        # 優雅關閉
        self.shutdown_event = threading.Event()
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """處理中斷信號"""
        logging.info("🚨 接收到中斷信號，正在安全關閉...")
        self.shutdown_event.set()
    
    def _get_session(self, thread_id):
        """為每個線程獲取獨立的session"""
        if thread_id not in self.sessions:
            session = requests.Session()
            headers = {
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            session.headers.update(headers)
            self.sessions[thread_id] = session
            
        return self.sessions[thread_id]
    
    def _get_random_user_agent(self):
        """隨機User-Agent"""
        agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        return random.choice(agents)
    
    def _load_progress(self):
        """載入爬取進度"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                logging.info(f"載入進度: 已完成 {len(progress.get('completed_companies', []))} 家公司")
                return progress
            except Exception as e:
                logging.error(f"載入進度失敗: {e}")
        return {'completed_companies': [], 'company_progress': {}, 'total_songs': 0, 'last_update': None}
    
    def _save_progress(self):
        """保存爬取進度"""
        with self.progress_lock:
            self.progress['last_update'] = datetime.now().isoformat()
            try:
                with open(self.progress_file, 'w', encoding='utf-8') as f:
                    json.dump(self.progress, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logging.error(f"保存進度失敗: {e}")
    
    def _smart_delay(self):
        """智能延遲 - 根據請求頻率動態調整"""
        with self.rate_limit_lock:
            now = time.time()
            
            # 清理舊的請求時間記錄
            while not self.request_times.empty():
                req_time = self.request_times.queue[0]
                if now - req_time > 60:  # 只保留最近1分鐘的記錄
                    self.request_times.get()
                else:
                    break
            
            # 計算當前請求頻率
            current_requests = self.request_times.qsize()
            
            # 動態調整延遲
            if current_requests >= 30:  # 高頻率
                delay = random.uniform(3.0, 5.0)
            elif current_requests >= 20:  # 中等頻率
                delay = random.uniform(2.0, 3.5)
            else:  # 低頻率
                delay = random.uniform(1.0, 2.5)
            
            self.request_times.put(now)
        
        time.sleep(delay)
    
    def scrape_company_pages(self, company, start_page=1, max_pages=None):
        """爬取單一公司的指定頁面範圍"""
        thread_id = threading.get_ident()
        session = self._get_session(thread_id)
        
        company_data = []
        page = start_page
        consecutive_failures = 0
        max_failures = 3
        
        logging.info(f"🧵 線程 {thread_id}: 開始爬取 {company} 從第{start_page}頁")
        
        while not self.shutdown_event.is_set():
            if max_pages and page > max_pages:
                break
                
            try:
                # 智能延遲
                self._smart_delay()
                
                url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
                
                # 定期更換User-Agent
                if page % 10 == 0:
                    session.headers['User-Agent'] = self._get_random_user_agent()
                
                response = session.get(url, timeout=15)
                response.encoding = "utf-8"
                
                if response.status_code != 200:
                    logging.warning(f"🧵 {thread_id}: {company} 第{page}頁 HTTP {response.status_code}")
                    consecutive_failures += 1
                    if consecutive_failures >= max_failures:
                        break
                    continue
                
                soup = BeautifulSoup(response.text, "html.parser")
                song_links = soup.select('a[href^="mv.aspx?id="]')
                
                if len(song_links) == 0:
                    logging.info(f"🧵 {thread_id}: {company} 第{page}頁 無更多資料，完成")
                    break
                
                page_songs = 0
                for link in song_links:
                    if self.shutdown_event.is_set():
                        break
                        
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
                                'link_url': link.get('href', ''),
                                'scraped_at': datetime.now().isoformat(),
                                'thread_id': thread_id
                            }
                            
                            company_data.append(song_data)
                            page_songs += 1
                    except Exception as e:
                        logging.debug(f"解析歌曲連結失敗: {e}")
                
                if page_songs == 0:
                    consecutive_failures += 1
                    if consecutive_failures >= max_failures:
                        logging.warning(f"🧵 {thread_id}: {company} 連續失敗，停止")
                        break
                else:
                    consecutive_failures = 0
                    logging.info(f"✅ 🧵 {thread_id}: {company} 第{page}頁: {page_songs} 首歌")
                
                # 更新進度
                with self.progress_lock:
                    if company not in self.progress['company_progress']:
                        self.progress['company_progress'][company] = {}
                    self.progress['company_progress'][company]['last_page'] = page
                    self.progress['company_progress'][company]['songs_count'] = len(company_data)
                
                page += 1
                
            except Exception as e:
                logging.error(f"🧵 {thread_id}: {company} 第{page}頁 錯誤: {e}")
                consecutive_failures += 1
                if consecutive_failures >= max_failures:
                    logging.error(f"🧵 {thread_id}: {company} 連續失敗 {max_failures} 次，跳過")
                    break
                
        return company_data
    
    def scrape_all_multithreaded(self):
        """多線程爬取所有公司"""
        logging.info(f"🚀 開始多線程爬取 (線程數: {self.max_workers})")
        start_time = time.time()
        
        # 載入現有資料
        if os.path.exists(self.output_files['json']):
            try:
                with open(self.output_files['json'], 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                with self.data_lock:
                    self.all_data.extend(existing_data)
                logging.info(f"載入現有資料: {len(existing_data)} 首歌")
            except Exception as e:
                logging.warning(f"載入現有資料失敗: {e}")
        
        # 準備任務列表
        tasks = []
        for company in self.companies:
            if company not in self.progress.get('completed_companies', []):
                tasks.append(company)
            else:
                logging.info(f"跳過已完成的公司: {company}")
        
        # 執行多線程爬取
        with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="Scraper") as executor:
            future_to_company = {
                executor.submit(self.scrape_company_pages, company): company 
                for company in tasks
            }
            
            for future in as_completed(future_to_company):
                if self.shutdown_event.is_set():
                    break
                    
                company = future_to_company[future]
                try:
                    company_data = future.result()
                    
                    # 合併資料
                    with self.data_lock:
                        self.all_data.extend(company_data)
                    
                    # 標記公司完成
                    with self.progress_lock:
                        if company not in self.progress['completed_companies']:
                            self.progress['completed_companies'].append(company)
                        self.progress['total_songs'] = len(self.all_data)
                    
                    logging.info(f"🎉 {company} 完成: {len(company_data)} 首歌 (總計: {len(self.all_data)})")
                    
                    # 每完成一家公司就保存
                    self._save_intermediate_results()
                    self._save_progress()
                    
                except Exception as e:
                    logging.error(f"❌ {company} 爬取失敗: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        logging.info(f"🎉 多線程爬取完成！")
        logging.info(f"⏱️  總耗時: {duration:.2f} 秒")
        logging.info(f"📊 總歌曲: {len(self.all_data)} 首")
        logging.info(f"🏢 完成公司: {len(self.progress['completed_companies'])} 家")
        logging.info(f"📈 平均速度: {len(self.all_data)/duration:.1f} 首/秒")
        
        return self.all_data
    
    def _save_intermediate_results(self):
        """保存中間結果"""
        try:
            with self.data_lock:
                data_copy = self.all_data.copy()
            
            # 保存JSON格式
            with open(self.output_files['json'], 'w', encoding='utf-8') as f:
                json.dump(data_copy, f, ensure_ascii=False, indent=2)
            
            logging.info(f"中間結果已保存: {len(data_copy)} 首歌")
        except Exception as e:
            logging.error(f"保存中間結果失敗: {e}")
    
    def save_results(self):
        """保存最終結果"""
        if not self.all_data:
            logging.warning("沒有資料可保存")
            return False
        
        try:
            # 1. 保存CSV格式
            with open(self.output_files['csv'], 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['公司', '編號', '歌名', '歌手', '期別', '語言', 'scraped_at'])
                
                for song in self.all_data:
                    writer.writerow([
                        song.get('公司', ''),
                        song.get('編號', ''),
                        song.get('歌名', ''),
                        song.get('歌手', ''),
                        song.get('期別', ''),
                        song.get('語言', ''),
                        song.get('scraped_at', '')
                    ])
            
            logging.info(f"CSV檔案已保存: {self.output_files['csv']}")
            
            # 2. 保存JSON格式
            with open(self.output_files['json'], 'w', encoding='utf-8') as f:
                json.dump(self.all_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"JSON檔案已保存: {self.output_files['json']}")
            
            # 3. 轉換為統一格式
            unified_data = self._convert_to_unified_format()
            
            # 載入現有統一資料
            existing_unified = []
            if os.path.exists(self.output_files['unified']):
                try:
                    with open(self.output_files['unified'], 'r', encoding='utf-8') as f:
                        existing_unified = json.load(f)
                except:
                    pass
            
            # 合併資料並去重
            all_unified = existing_unified + unified_data
            unique_songs = self._deduplicate_songs(all_unified)
            
            with open(self.output_files['unified'], 'w', encoding='utf-8') as f:
                json.dump(unique_songs, f, ensure_ascii=False, indent=2)
            
            logging.info(f"統一格式已保存: {self.output_files['unified']} ({len(unique_songs)} 首)")
            
            return True
            
        except Exception as e:
            logging.error(f"保存結果失敗: {e}")
            return False
    
    def _convert_to_unified_format(self):
        """轉換為統一格式"""
        unified_data = []
        
        for song in self.all_data:
            if song.get('歌名') and song.get('歌手'):
                unified_song = {
                    '歌名': song.get('歌名', '').strip(),
                    '歌手': song.get('歌手', '').strip(),
                    '編號': song.get('編號', '').strip(),
                    '公司': song.get('公司', '').strip(),
                    '語言': song.get('語言', '').strip()
                }
                unified_data.append(unified_song)
        
        return unified_data
    
    def _deduplicate_songs(self, songs):
        """去除重複歌曲"""
        seen = set()
        unique_songs = []
        
        for song in songs:
            key = f"{song.get('歌名', '')}_{song.get('歌手', '')}_{song.get('公司', '')}_{song.get('編號', '')}"
            if key not in seen:
                seen.add(key)
                unique_songs.append(song)
        
        return unique_songs

def main():
    """主程序"""
    print("🎵 多線程增強版台灣點歌王爬蟲")
    print("=" * 60)
    
    # 詢問線程數
    while True:
        try:
            max_workers = input(f"請輸入線程數 (建議2-4，預設3): ").strip()
            if not max_workers:
                max_workers = 3
            else:
                max_workers = int(max_workers)
            
            if max_workers < 1 or max_workers > 8:
                print("線程數應該在1-8之間")
                continue
            break
        except ValueError:
            print("請輸入有效數字")
    
    print(f"⚙️ 設定線程數: {max_workers}")
    print("🔄 按 Ctrl+C 可安全停止爬蟲")
    
    scraper = MultiThreadedTaiwanScraper(max_workers=max_workers)
    
    try:
        # 爬取資料
        data = scraper.scrape_all_multithreaded()
        
        if data and not scraper.shutdown_event.is_set():
            # 保存結果
            if scraper.save_results():
                print(f"✅ 資料保存成功: {len(data)} 首歌")
            else:
                print("❌ 資料保存失敗")
        elif scraper.shutdown_event.is_set():
            print("⚠️ 爬蟲被中斷，但已保存中間結果")
            scraper.save_results()
        else:
            print("❌ 沒有爬取到資料")
    
    except KeyboardInterrupt:
        print("\n⚠️ 使用者中斷，正在安全關閉...")
        scraper.shutdown_event.set()
        scraper._save_intermediate_results()
        scraper._save_progress()
    except Exception as e:
        print(f"❌ 爬蟲執行失敗: {e}")
        logging.error(f"主程序錯誤: {e}")
    finally:
        # 清理session
        for session in scraper.sessions.values():
            session.close()

if __name__ == "__main__":
    main()