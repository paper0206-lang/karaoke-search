#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌手關鍵字搜尋爬蟲 - 全新獨立系統
基於989位歌手資料庫進行關鍵字搜尋，創建獨立的歌手搜尋資料庫
"""

import requests
import json
import time
import threading
import random
import os
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlencode
import logging

class SingerKeywordScraper:
    def __init__(self):
        self.base_url = "https://song.corp.com.tw"
        self.search_url = f"{self.base_url}/index.aspx"
        
        # 獨立的歌手搜尋資料庫
        self.singer_search_database = {
            "metadata": {
                "created_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "scraper_version": "1.0.0",
                "database_type": "singer_keyword_search",
                "total_singers_to_search": 0,
                "total_singers_searched": 0,
                "total_songs_found": 0,
                "search_progress": {}
            },
            "songs_by_singer": {},
            "search_statistics": {
                "successful_singers": [],
                "failed_singers": [],
                "singers_with_songs": [],
                "singers_without_songs": []
            }
        }
        
        # 爬蟲配置
        self.max_workers = 12  # 12個線程
        self.session_pool = []
        self.progress_file = "singer_search_progress.json"
        self.database_file = f"singer_search_database_{time.strftime('%Y%m%d_%H%M%S')}.json"
        
        # 防封鎖配置
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        # 延遲配置
        self.base_delay = (1.0, 3.0)  # 基礎延遲1-3秒
        self.page_delay = (0.5, 1.5)  # 翻頁延遲0.5-1.5秒
        
        # 錯誤處理
        self.max_retries = 3
        self.error_singers = []
        
        # 設置日誌
        self.setup_logging()
        
        # 線程鎖
        self.save_lock = threading.Lock()
        self.progress_lock = threading.Lock()
        
    def setup_logging(self):
        """設置日誌系統"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'singer_scraper_{time.strftime("%Y%m%d")}.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def create_session(self):
        """創建會話"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        return session
        
    def load_singer_database(self):
        """載入989位歌手資料庫"""
        print("📥 載入歌手資料庫...")
        
        singer_file = "FINAL_singer_database_20250811_200210.json"
        
        if not os.path.exists(singer_file):
            print(f"❌ 找不到歌手資料庫: {singer_file}")
            return []
            
        try:
            with open(singer_file, 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            # 提取所有搜尋關鍵字
            search_keywords = database.get('search_keywords', [])
            
            print(f"✅ 成功載入 {len(search_keywords)} 個搜尋關鍵字")
            self.singer_search_database['metadata']['total_singers_to_search'] = len(search_keywords)
            
            return search_keywords
            
        except Exception as e:
            print(f"❌ 載入歌手資料庫失敗: {e}")
            return []
    
    def load_progress(self):
        """載入搜尋進度"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                print(f"📋 載入進度: 已完成 {len(progress.get('completed_singers', []))} 位歌手")
                return progress
            except:
                pass
        return {"completed_singers": [], "failed_singers": []}
    
    def save_progress(self, completed_singer=None, failed_singer=None):
        """保存搜尋進度"""
        with self.progress_lock:
            progress = self.load_progress()
            
            if completed_singer:
                if completed_singer not in progress["completed_singers"]:
                    progress["completed_singers"].append(completed_singer)
                    
            if failed_singer:
                if failed_singer not in progress["failed_singers"]:
                    progress["failed_singers"].append(failed_singer)
            
            try:
                with open(self.progress_file, 'w', encoding='utf-8') as f:
                    json.dump(progress, f, ensure_ascii=False, indent=2)
            except Exception as e:
                self.logger.error(f"保存進度失敗: {e}")
    
    def save_database(self):
        """實時保存歌手搜尋資料庫"""
        with self.save_lock:
            try:
                # 更新統計資訊
                self.singer_search_database['metadata']['total_singers_searched'] = len(self.singer_search_database['songs_by_singer'])
                total_songs = sum(len(songs) for songs in self.singer_search_database['songs_by_singer'].values())
                self.singer_search_database['metadata']['total_songs_found'] = total_songs
                self.singer_search_database['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                with open(self.database_file, 'w', encoding='utf-8') as f:
                    json.dump(self.singer_search_database, f, ensure_ascii=False, indent=2)
                    
            except Exception as e:
                self.logger.error(f"保存資料庫失敗: {e}")
    
    def process_song_title(self, title):
        """處理歌曲標題 - 將(lv)轉換為(Live版)"""
        if not title:
            return title
            
        # 處理Live版本標記
        title = re.sub(r'\(lv\)', '(Live版)', title, flags=re.IGNORECASE)
        title = re.sub(r'\(LV\)', '(Live版)', title)
        
        # 清理多餘空格
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title
    
    def search_singer_songs(self, singer_keyword, session):
        """搜尋單一歌手的所有歌曲"""
        try:
            self.logger.info(f"🔍 開始搜尋歌手: {singer_keyword}")
            
            # 搜尋第一頁
            search_params = {
                '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$but_sel',
                'ctl00$ContentPlaceHolder1$sel_company': '',  # 空白表示全部公司
                'ctl00$ContentPlaceHolder1$txt_keyword': singer_keyword,
                'ctl00$ContentPlaceHolder1$sel_search_type': 'singer'  # 按歌手搜尋
            }
            
            response = session.post(self.search_url, data=search_params, timeout=30)
            response.raise_for_status()
            
            if "查無資料" in response.text or "沒有找到" in response.text:
                self.logger.info(f"⚪ {singer_keyword}: 無搜尋結果")
                self.singer_search_database['search_statistics']['singers_without_songs'].append(singer_keyword)
                return []
            
            songs = []
            page_num = 1
            
            while True:
                self.logger.info(f"   📄 處理第 {page_num} 頁...")
                
                # 解析當前頁面的歌曲
                page_songs = self.parse_songs_from_page(response.text, singer_keyword)
                
                if not page_songs:
                    self.logger.info(f"   🏁 第 {page_num} 頁無歌曲，搜尋完成")
                    break
                    
                songs.extend(page_songs)
                self.logger.info(f"   ✅ 第 {page_num} 頁找到 {len(page_songs)} 首歌曲")
                
                # 檢查是否有下一頁
                if not self.has_next_page(response.text):
                    self.logger.info(f"   🏁 無下一頁，{singer_keyword} 搜尋完成")
                    break
                
                # 翻到下一頁
                time.sleep(random.uniform(*self.page_delay))
                next_page_response = self.goto_next_page(session, response.text)
                
                if not next_page_response:
                    self.logger.warning(f"   ⚠️ 無法翻到下一頁，結束搜尋")
                    break
                    
                response = next_page_response
                page_num += 1
                
                # 防止無限迴圈
                if page_num > 100:
                    self.logger.warning(f"   ⚠️ 頁數超過100頁，強制結束")
                    break
            
            self.logger.info(f"✅ {singer_keyword}: 總共找到 {len(songs)} 首歌曲")
            
            if songs:
                self.singer_search_database['search_statistics']['singers_with_songs'].append(singer_keyword)
            else:
                self.singer_search_database['search_statistics']['singers_without_songs'].append(singer_keyword)
                
            return songs
            
        except Exception as e:
            self.logger.error(f"❌ 搜尋 {singer_keyword} 失敗: {e}")
            return None
    
    def parse_songs_from_page(self, html_content, singer_keyword):
        """從頁面解析歌曲資訊"""
        songs = []
        
        try:
            # 使用正則表達式找到歌曲資訊
            # 這裡需要根據實際網站結構調整
            song_pattern = r'<tr[^>]*>.*?<td[^>]*>(.*?)</td>.*?<td[^>]*>(.*?)</td>.*?<td[^>]*>(.*?)</td>.*?</tr>'
            matches = re.findall(song_pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                if len(match) >= 3:
                    # 假設第一欄是歌曲編號，第二欄是歌名，第三欄是歌手
                    song_id = match[0].strip()
                    song_name = match[1].strip()
                    singer_name = match[2].strip()
                    
                    # 清理HTML標籤
                    song_id = re.sub(r'<[^>]+>', '', song_id).strip()
                    song_name = re.sub(r'<[^>]+>', '', song_name).strip()
                    singer_name = re.sub(r'<[^>]+>', '', singer_name).strip()
                    
                    if song_name and song_id:
                        # 處理Live版本
                        processed_title = self.process_song_title(song_name)
                        is_live = "(Live版)" in processed_title
                        
                        song_info = {
                            "song_id": song_id,
                            "song_name": processed_title,
                            "singer": singer_name,
                            "search_keyword": singer_keyword,
                            "is_live": is_live,
                            "found_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        songs.append(song_info)
                        
        except Exception as e:
            self.logger.error(f"解析頁面失敗: {e}")
            
        return songs
    
    def has_next_page(self, html_content):
        """檢查是否有下一頁"""
        # 查找下一頁按鈕或連結
        next_patterns = [
            r'下一頁',
            r'next',
            r'&gt;',
            r'__doPostBack.*?Page.*?Next'
        ]
        
        for pattern in next_patterns:
            if re.search(pattern, html_content, re.IGNORECASE):
                return True
                
        return False
    
    def goto_next_page(self, session, html_content):
        """跳轉到下一頁"""
        try:
            # 提取ViewState等必要參數
            viewstate_match = re.search(r'name="__VIEWSTATE".*?value="([^"]*)"', html_content)
            eventvalidation_match = re.search(r'name="__EVENTVALIDATION".*?value="([^"]*)"', html_content)
            
            if not viewstate_match:
                return None
                
            # 構建下一頁請求
            next_page_data = {
                '__VIEWSTATE': viewstate_match.group(1),
                '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$GridView1',
                '__EVENTARGUMENT': 'Page$Next'
            }
            
            if eventvalidation_match:
                next_page_data['__EVENTVALIDATION'] = eventvalidation_match.group(1)
            
            response = session.post(self.search_url, data=next_page_data, timeout=30)
            response.raise_for_status()
            
            return response
            
        except Exception as e:
            self.logger.error(f"翻頁失敗: {e}")
            return None
    
    def process_single_singer(self, singer_keyword):
        """處理單一歌手的搜尋任務"""
        session = self.create_session()
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                # 動態延遲
                delay = random.uniform(*self.base_delay)
                time.sleep(delay)
                
                # 搜尋歌曲
                songs = self.search_singer_songs(singer_keyword, session)
                
                if songs is None:
                    # 發生錯誤，重試
                    retry_count += 1
                    self.logger.warning(f"⚠️ {singer_keyword} 第 {retry_count} 次重試...")
                    time.sleep(retry_count * 2)  # 遞增延遲
                    continue
                
                # 保存結果
                with self.save_lock:
                    self.singer_search_database['songs_by_singer'][singer_keyword] = songs
                    
                # 更新進度
                self.save_progress(completed_singer=singer_keyword)
                
                # 實時保存資料庫
                self.save_database()
                
                self.logger.info(f"🎵 完成歌手 {singer_keyword}: {len(songs)} 首歌曲")
                return True
                
            except Exception as e:
                retry_count += 1
                self.logger.error(f"❌ 處理 {singer_keyword} 第 {retry_count} 次失敗: {e}")
                
                if retry_count < self.max_retries:
                    time.sleep(retry_count * 3)
                else:
                    # 最終失敗
                    self.save_progress(failed_singer=singer_keyword)
                    self.error_singers.append(singer_keyword)
                    self.logger.error(f"💔 歌手 {singer_keyword} 最終處理失敗")
                    return False
                    
        return False
    
    def start_scraping(self):
        """開始爬蟲主流程"""
        print("🚀 歌手關鍵字搜尋爬蟲啟動")
        print("=" * 60)
        
        # 載入歌手資料庫
        singer_keywords = self.load_singer_database()
        if not singer_keywords:
            print("❌ 無法載入歌手資料庫，退出")
            return
            
        # 載入進度
        progress = self.load_progress()
        completed_singers = set(progress.get('completed_singers', []))
        failed_singers = set(progress.get('failed_singers', []))
        
        # 過濾已完成的歌手
        remaining_singers = [s for s in singer_keywords if s not in completed_singers]
        
        print(f"📊 統計資訊:")
        print(f"   🎵 歌手總數: {len(singer_keywords)}")
        print(f"   ✅ 已完成: {len(completed_singers)}")
        print(f"   ❌ 已失敗: {len(failed_singers)}")
        print(f"   ⏳ 待處理: {len(remaining_singers)}")
        print(f"   🧵 線程數: {self.max_workers}")
        
        if not remaining_singers:
            print("🎉 所有歌手已處理完成！")
            return
            
        start_time = time.time()
        
        # 使用線程池處理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.process_single_singer, singer): singer 
                      for singer in remaining_singers}
            
            completed_count = len(completed_singers)
            total_count = len(singer_keywords)
            
            for future in as_completed(futures):
                singer = futures[future]
                
                try:
                    success = future.result()
                    completed_count += 1
                    
                    progress_percent = (completed_count / total_count) * 100
                    elapsed_time = time.time() - start_time
                    
                    if completed_count > len(completed_singers):  # 只有新完成的才計算速度
                        remaining = total_count - completed_count
                        eta_seconds = (elapsed_time / (completed_count - len(completed_singers))) * remaining
                        eta_hours = eta_seconds / 3600
                        
                        print(f"📈 進度: {progress_percent:.1f}% ({completed_count}/{total_count}) "
                              f"剩餘時間: {eta_hours:.1f}小時")
                    
                except Exception as e:
                    self.logger.error(f"處理歌手 {singer} 發生異常: {e}")
        
        # 最終統計
        self.print_final_statistics()
    
    def print_final_statistics(self):
        """打印最終統計"""
        print("\n" + "=" * 60)
        print("📊 爬蟲完成統計")
        print("=" * 60)
        
        metadata = self.singer_search_database['metadata']
        stats = self.singer_search_database['search_statistics']
        
        print(f"🎵 總歌手數: {metadata['total_singers_to_search']}")
        print(f"✅ 已搜尋: {metadata['total_singers_searched']}")
        print(f"🎶 總歌曲數: {metadata['total_songs_found']}")
        print(f"👥 有歌曲歌手: {len(stats['singers_with_songs'])}")
        print(f"⚪ 無歌曲歌手: {len(stats['singers_without_songs'])}")
        print(f"❌ 失敗歌手: {len(self.error_singers)}")
        
        print(f"\n💾 資料庫檔案: {self.database_file}")
        print(f"📋 進度檔案: {self.progress_file}")
        
        if self.error_singers:
            print(f"\n❌ 處理失敗的歌手:")
            for singer in self.error_singers[:10]:
                print(f"   • {singer}")
            if len(self.error_singers) > 10:
                print(f"   ... 還有 {len(self.error_singers) - 10} 位")

def main():
    scraper = SingerKeywordScraper()
    
    try:
        scraper.start_scraping()
    except KeyboardInterrupt:
        print("\n🛑 用戶中斷爬蟲")
        print("📋 進度已保存，可使用同一腳本繼續")
    except Exception as e:
        print(f"❌ 爬蟲發生致命錯誤: {e}")
    finally:
        # 最後保存一次
        scraper.save_database()

if __name__ == "__main__":
    main()