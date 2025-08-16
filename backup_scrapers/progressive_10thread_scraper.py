#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
漸進式10線程爬蟲
從8線程開始，逐步增加到10線程
包含智能監控和自動降級
"""

import sys
import os
import time
import threading
import random
from datetime import datetime, timedelta

# 匯入優化爬蟲
from optimized_scraper import OptimizedTaiwanScraper

class Progressive10ThreadScraper(OptimizedTaiwanScraper):
    def __init__(self, start_threads=8, target_threads=10, batch_size=1000):
        super().__init__(start_threads, batch_size)
        
        self.start_threads = start_threads
        self.target_threads = target_threads
        self.current_threads = start_threads
        
        # 性能監控
        self.performance_monitor = {
            'request_count': 0,
            'error_count': 0,
            'start_time': None,
            'last_check': None,
            'error_rate': 0.0,
            'requests_per_minute': 0.0
        }
        
        self.monitor_lock = threading.Lock()
        
    def _enhanced_smart_delay(self, thread_id, retry_count=0):
        """增強版智能延遲 - 更保守的設置"""
        base_delay = random.uniform(2.0, 5.0)  # 更保守的延遲
        
        # 根據當前線程數調整延遲
        thread_factor = self.current_threads / 5.0  # 基於5線程的倍數
        adjusted_delay = base_delay * (1 + (thread_factor - 1) * 0.3)
        
        # 根據重試次數增加延遲（指數退避）
        if retry_count > 0:
            backoff_delay = min(2 ** retry_count, 30)
            adjusted_delay += backoff_delay
            
        # 線程間錯開延遲
        thread_offset = (thread_id % 1000) * 0.2
        
        # 隨機抖動
        jitter = random.uniform(-0.5, 0.5)
        
        final_delay = adjusted_delay + thread_offset + jitter
        final_delay = max(2.0, final_delay)  # 最小2秒
        
        if retry_count > 0:
            print(f"🧵 {thread_id}: 重試延遲 {final_delay:.1f}秒 (重試#{retry_count})")
        
        time.sleep(final_delay)
        
        # 更新性能監控
        self._update_performance_monitor()
    
    def _update_performance_monitor(self):
        """更新性能監控數據"""
        with self.monitor_lock:
            self.performance_monitor['request_count'] += 1
            now = datetime.now()
            
            if self.performance_monitor['start_time'] is None:
                self.performance_monitor['start_time'] = now
                self.performance_monitor['last_check'] = now
            
            # 每100次請求檢查一次性能
            if self.performance_monitor['request_count'] % 100 == 0:
                self._check_performance()
    
    def _record_error(self):
        """記錄錯誤"""
        with self.monitor_lock:
            self.performance_monitor['error_count'] += 1
    
    def _check_performance(self):
        """檢查性能並決定是否調整線程數"""
        with self.monitor_lock:
            now = datetime.now()
            total_time = (now - self.performance_monitor['start_time']).total_seconds()
            
            if total_time > 0:
                # 計算錯誤率
                error_rate = self.performance_monitor['error_count'] / self.performance_monitor['request_count']
                
                # 計算請求速率
                requests_per_minute = (self.performance_monitor['request_count'] / total_time) * 60
                
                self.performance_monitor['error_rate'] = error_rate
                self.performance_monitor['requests_per_minute'] = requests_per_minute
                
                print(f"📊 性能監控: 錯誤率 {error_rate:.2%}, 請求速率 {requests_per_minute:.1f}/分鐘")
                
                # 決定是否調整線程數
                self._adjust_threads_based_on_performance(error_rate, requests_per_minute)
    
    def _adjust_threads_based_on_performance(self, error_rate, requests_per_minute):
        """根據性能調整線程數"""
        if self.performance_monitor['request_count'] < 500:
            return  # 數據不足，不調整
        
        # 調整邏輯
        if error_rate > 0.05:  # 錯誤率超過5%
            if self.current_threads > self.start_threads:
                print(f"⚠️ 錯誤率過高 ({error_rate:.2%})，降低線程數")
                self._decrease_threads()
        elif error_rate < 0.02 and self.current_threads < self.target_threads:  # 錯誤率低於2%
            if requests_per_minute > 50:  # 且請求速率良好
                print(f"✅ 性能良好，嘗試增加線程數")
                self._increase_threads()
    
    def _increase_threads(self):
        """增加線程數"""
        if self.current_threads < self.target_threads:
            self.current_threads += 1
            print(f"🚀 線程數增加至: {self.current_threads}")
    
    def _decrease_threads(self):
        """減少線程數"""
        if self.current_threads > 3:  # 最少保持3線程
            self.current_threads -= 1
            print(f"📉 線程數減少至: {self.current_threads}")
    
    def enhanced_scrape_page_range(self, company, start_page, end_page):
        """增強版頁面爬取 - 包含錯誤監控"""
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
                    # 使用增強版延遲
                    self._enhanced_smart_delay(thread_id, retry_count)
                    
                    url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
                    response = session.get(url, timeout=15)
                    response.encoding = "utf-8"
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        song_links = soup.select('a[href^="mv.aspx?id="]')
                        
                        if len(song_links) == 0:
                            print(f"🧵 {thread_id}: {company} 第{page}頁 無數據，可能已結束")
                            return page_data
                        
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
                        
                        page_success = True
                        
                    else:
                        print(f"🧵 {thread_id}: 第{page}頁 HTTP {response.status_code}")
                        self._record_error()
                        retry_count += 1
                        
                except Exception as e:
                    print(f"❌ 🧵 {thread_id}: {company} 第{page}頁錯誤: {e}")
                    self._record_error()
                    retry_count += 1
            
            if not page_success:
                print(f"⚠️ 🧵 {thread_id}: 第{page}頁重試{max_retries}次後仍失敗，跳過")
                self._record_error()
        
        return page_data
    
    def progressive_scrape_company(self, company, start_page, total_pages_estimate=20000):
        """漸進式多線程爬取"""
        print(f"🎯 漸進式多線程爬取: {company}")
        print(f"   起始線程: {self.start_threads}")
        print(f"   目標線程: {self.target_threads}")
        print(f"   從第{start_page}頁開始")
        print("=" * 60)
        
        # 計算剩餘頁面
        remaining_pages = total_pages_estimate - start_page + 1
        pages_per_thread = 150
        page_ranges = []
        
        current_page = start_page
        while current_page <= total_pages_estimate:
            end_page = min(current_page + pages_per_thread - 1, total_pages_estimate)
            page_ranges.append((current_page, end_page))
            current_page = end_page + 1
        
        print(f"📊 分配策略: {len(page_ranges)} 個任務")
        
        # 使用當前線程數執行
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        completed_tasks = 0
        
        with ThreadPoolExecutor(max_workers=self.current_threads) as executor:
            future_to_range = {
                executor.submit(self.enhanced_scrape_page_range, company, start, end): (start, end)
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
                        
                        if len(self.batch_data) >= self.batch_size:
                            self._save_batch()
                    
                    completed_tasks += 1
                    progress = (completed_tasks / len(page_ranges)) * 100
                    print(f"🎉 任務完成 {completed_tasks}/{len(page_ranges)} ({progress:.1f}%): 第{start}-{end}頁 ({len(page_data)} 首歌)")
                    
                except Exception as e:
                    print(f"❌ 任務失敗 第{start}-{end}頁: {e}")
        
        # 保存剩餘數據
        with self.data_lock:
            if self.batch_data:
                self._save_batch()
        
        # 性能總結
        self._print_final_performance()
        
        print(f"🎉 {company} 漸進式爬取完成！總共保存: {self.total_saved} 首歌")
    
    def _print_final_performance(self):
        """打印最終性能報告"""
        with self.monitor_lock:
            total_time = (datetime.now() - self.performance_monitor['start_time']).total_seconds()
            
            print(f"\n📊 最終性能報告:")
            print(f"   總請求數: {self.performance_monitor['request_count']:,}")
            print(f"   總錯誤數: {self.performance_monitor['error_count']}")
            print(f"   錯誤率: {self.performance_monitor['error_rate']:.2%}")
            print(f"   平均請求速率: {self.performance_monitor['requests_per_minute']:.1f}/分鐘")
            print(f"   最終線程數: {self.current_threads}")
            print(f"   總耗時: {total_time/3600:.2f} 小時")

def main():
    """主程序"""
    print("🚀 漸進式10線程台灣KTV爬蟲")
    print("📈 智能性能監控 + 自動線程調整")
    print("=" * 60)
    
    scraper = Progressive10ThreadScraper(
        start_threads=8,
        target_threads=10,
        batch_size=1000
    )
    
    try:
        print("🎯 開始漸進式爬取...")
        print("⚠️ 系統將自動監控性能並調整線程數")
        print("⚠️ 按 Ctrl+C 可隨時安全停止")
        print()
        
        # 繼續音圓從第6920頁
        scraper.progressive_scrape_company("音圓", 6920, 20000)
        
        # 合併批次文件
        merged_file = scraper.merge_batches()
        
        if merged_file:
            print(f"\n✅ 漸進式爬取完成！")
            print(f"📁 合併文件: {merged_file}")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用戶中斷，正在安全關閉...")
        scraper.shutdown_event.set()
        
        with scraper.data_lock:
            if scraper.batch_data:
                scraper._save_batch()
        
        print("✅ 已安全停止")
        
    except Exception as e:
        print(f"\n❌ 爬取失敗: {e}")
    finally:
        for session in scraper.sessions.values():
            session.close()

if __name__ == "__main__":
    main()