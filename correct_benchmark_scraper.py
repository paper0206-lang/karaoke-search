#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正確基準爬蟲系統
基於台灣點歌網動態比較的智能爬蟲
實現用戶原始需求：5%差異閾值 + 逐筆重複檢查
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import random
import signal
import logging
import subprocess
from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from taiwan_ktv_comparator import TaiwanKTVComparator

class CorrectBenchmarkScraper:
    def __init__(self, resume_from_checkpoint=True):
        # 設置日誌
        self.setup_logging()
        self.logger = logging.getLogger('CorrectBenchmarkScraper')
        
        self.base_url = "https://song.corp.com.tw"
        
        # 正確的基準配置
        self.threshold_percentage = 0.05  # 5%差異閾值
        self.comparator = TaiwanKTVComparator()
        
        # KTV公司清單
        self.companies_to_check = [
            "音圓", "錢櫃", "好樂迪", "銀櫃", "金嗓", "弘音", 
            "點將家", "星據點", "享溫馨", "大唐", "瑞影", "MV",
            "金影", "音影", "嘉揚", "音遊", "美華"
        ]
        
        # 配置參數
        self.resume_from_checkpoint = resume_from_checkpoint
        self.checkpoint_file = "correct_benchmark_checkpoint.json"
        self.max_singers_per_session = 1000
        self.batch_size = 5  # 降低批次大小以提高準確性
        self.delay_range = (3.0, 6.0)  # 增加延遲確保網站查詢準確
        self.parallel_threads = 2  # 減少並行度確保查詢品質
        
        # Git自動推送配置
        self.auto_git_push = True
        self.git_push_interval = 25  # 每25位歌手推送一次
        
        # 初始化
        self.processed_singers_set = set()
        self.singers_to_process = []
        self.total_new_songs = 0
        self.total_updated_songs = 0
        self.session_start_time = datetime.now()
        
        # 統計資料
        self.stats = {
            'start_time': self.session_start_time,
            'processed_singers': 0,
            'successful_singers': 0,
            'skipped_singers': 0,
            'failed_singers': 0,
            'new_songs_added': 0,
            'git_pushes': 0,
            'website_queries': 0,
            'threshold_checks': 0
        }
        
        # 載入檢查點和歌手列表
        self.load_checkpoint()
        self.load_singers_list()
        
        # 設置信號處理
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        self.logger.info(f"🎯 正確基準爬蟲初始化完成")
        self.logger.info(f"基準設定: 5%差異閾值比較台灣點歌網")
        self.logger.info(f"待處理歌手: {len(self.singers_to_process)} 位")
        self.logger.info(f"並行線程: {self.parallel_threads}")
        self.logger.info(f"查詢延遲: {self.delay_range}")
        self.logger.info(f"自動Git推送: {'啟用' if self.auto_git_push else '停用'}")
    
    def setup_logging(self):
        """設置日誌系統"""
        log_dir = "correct_logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_filename = f"{log_dir}/correct_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def load_checkpoint(self):
        """載入檢查點"""
        if self.resume_from_checkpoint and os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                
                self.processed_singers_set = set(checkpoint.get('processed_singers', []))
                
                # 恢復統計資料
                saved_stats = checkpoint.get('session_stats', {})
                for key, value in saved_stats.items():
                    if key in self.stats:
                        if key == 'start_time':
                            try:
                                self.stats[key] = datetime.fromisoformat(value)
                            except:
                                self.stats[key] = self.session_start_time
                        else:
                            self.stats[key] = value
                
                self.logger.info(f"✅ 檢查點載入: {len(self.processed_singers_set)} 位歌手已處理")
                
            except Exception as e:
                self.logger.error(f"載入檢查點失敗: {e}")
                self.processed_singers_set = set()
    
    def save_checkpoint(self):
        """保存檢查點"""
        try:
            # 處理datetime序列化
            serializable_stats = {}
            for key, value in self.stats.items():
                if isinstance(value, datetime):
                    serializable_stats[key] = value.isoformat()
                else:
                    serializable_stats[key] = value
            
            checkpoint_data = {
                'last_updated': datetime.now().isoformat(),
                'processed_singers': list(self.processed_singers_set),
                'total_processed': len(self.processed_singers_set),
                'session_stats': serializable_stats,
                'threshold_percentage': self.threshold_percentage,
                'scraper_config': {
                    'parallel_threads': self.parallel_threads,
                    'delay_range': self.delay_range,
                    'batch_size': self.batch_size,
                    'git_push_interval': self.git_push_interval,
                    'threshold_percentage': self.threshold_percentage
                }
            }
            
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"檢查點已保存: {len(self.processed_singers_set)} 位歌手已處理")
            
        except Exception as e:
            self.logger.error(f"保存檢查點失敗: {e}")
    
    def load_singers_list(self):
        """載入歌手列表並過濾已處理的"""
        try:
            with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                singers_data = json.load(f)
            
            singers_list = list(singers_data.keys())
            
            # 移除已處理的歌手
            self.singers_to_process = [
                singer for singer in singers_list 
                if singer not in self.processed_singers_set
            ]
            
            self.logger.info(f"歌手列表載入完成: {len(singers_list)} 總數, {len(self.singers_to_process)} 待處理")
            
        except Exception as e:
            self.logger.error(f"載入歌手列表失敗: {e}")
            self.singers_to_process = []
    
    def signal_handler(self, signum, frame):
        """處理終止信號"""
        self.logger.info(f"收到終止信號 {signum}, 正在安全退出...")
        self.save_checkpoint()
        sys.exit(0)
    
    def check_singer_needs_processing(self, singer_name):
        """使用正確的台灣點歌網比較檢查歌手是否需要處理"""
        try:
            self.stats['threshold_checks'] += 1
            
            # 使用比較器檢查
            result = self.comparator.check_needs_scraping(singer_name, self.threshold_percentage)
            
            self.stats['website_queries'] += 1
            
            return {
                'needs_processing': result['needs_scraping'],
                'reason': result['reason'],
                'website_count': result.get('website_count', 0),
                'our_count': result.get('our_count', 0),
                'coverage_ratio': result.get('coverage_ratio', 0),
                'comparison_successful': True
            }
            
        except Exception as e:
            self.logger.error(f"檢查{singer_name}是否需要處理失敗: {e}")
            return {
                'needs_processing': False,
                'reason': 'check_failed',
                'comparison_successful': False,
                'error': str(e)
            }
    
    def search_singer_with_deduplication(self, singer_name):
        """搜索歌手並進行重複檢查"""
        try:
            self.logger.info(f"🔍 搜索歌手: {singer_name}")
            
            # 獲取台灣點歌網的完整資料
            website_data = self.comparator.get_singer_ktv_count_from_website(singer_name)
            
            if not website_data['search_successful']:
                return []
            
            # 找出我們資料庫中缺少的KTV編號
            missing_entries = self.comparator.find_missing_ktv_entries(singer_name)
            
            # 轉換為我們的格式
            new_songs = []
            songs_by_name = defaultdict(lambda: {'編號資訊': [], '語言': '', '歌手': singer_name})
            
            for entry in missing_entries:
                song_name = entry['song_name']
                company = entry['company']
                number = entry['number']
                
                # 推測語言（簡單規則）
                language = "國"  # 預設國語
                if any(char in song_name for char in "台語閩南語"):
                    language = "台"
                elif any(char in song_name for char in "英文English"):
                    language = "英"
                
                songs_by_name[song_name]['編號資訊'].append({
                    '公司': company,
                    '編號': number
                })
                songs_by_name[song_name]['語言'] = language
                songs_by_name[song_name]['歌名'] = song_name
            
            # 轉換為清單格式
            for song_name, song_info in songs_by_name.items():
                new_songs.append(song_info)
            
            self.logger.info(f"🎵 {singer_name}: 找到 {len(new_songs)} 首新歌曲")
            
            return new_songs
            
        except Exception as e:
            self.logger.error(f"搜索 {singer_name} 失敗: {e}")
            return []
    
    def integrate_singer_data(self, singer_name, new_songs):
        """整合歌手資料（避免重複）"""
        try:
            with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                singers_data = json.load(f)
            
            if singer_name not in singers_data:
                singers_data[singer_name] = {
                    '歌手名稱': singer_name,
                    '歌曲清單': []
                }
            
            existing_songs = singers_data[singer_name].get('歌曲清單', [])
            
            # 建立現有歌曲的KTV編號索引
            existing_entries = set()
            for song in existing_songs:
                for entry in song.get('編號資訊', []):
                    company = entry.get('公司', '')
                    number = entry.get('編號', '')
                    if company and number:
                        existing_entries.add(f"{company}:{number}")
            
            new_count = 0
            updated_count = 0
            
            for new_song in new_songs:
                song_name = new_song['歌名']
                
                # 檢查是否已存在同名歌曲
                existing_song = None
                for song in existing_songs:
                    if song.get('歌名') == song_name:
                        existing_song = song
                        break
                
                if existing_song:
                    # 更新現有歌曲的KTV編號
                    for new_entry in new_song['編號資訊']:
                        company = new_entry.get('公司', '')
                        number = new_entry.get('編號', '')
                        entry_key = f"{company}:{number}"
                        
                        if entry_key not in existing_entries:
                            existing_song['編號資訊'].append(new_entry)
                            existing_entries.add(entry_key)
                            updated_count += 1
                else:
                    # 新增歌曲
                    # 再次檢查KTV編號重複
                    unique_entries = []
                    for entry in new_song['編號資訊']:
                        company = entry.get('公司', '')
                        number = entry.get('編號', '')
                        entry_key = f"{company}:{number}"
                        
                        if entry_key not in existing_entries:
                            unique_entries.append(entry)
                            existing_entries.add(entry_key)
                    
                    if unique_entries:
                        new_song['編號資訊'] = unique_entries
                        existing_songs.append(new_song)
                        new_count += 1
            
            # 保存更新後的資料
            with open('public/singers_data.json', 'w', encoding='utf-8') as f:
                json.dump(singers_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ {singer_name}: 新增 {new_count} 首歌, 更新 {updated_count} 個編號")
            
            return new_count, updated_count
            
        except Exception as e:
            self.logger.error(f"整合 {singer_name} 資料失敗: {e}")
            return 0, 0
    
    def auto_git_push_update(self, singer_name, force=False):
        """自動Git推送更新"""
        if not self.auto_git_push:
            return
        
        try:
            processed_count = len(self.processed_singers_set)
            
            if force or processed_count % self.git_push_interval == 0:
                commit_message = f"🎯 正確基準爬蟲更新: 處理{processed_count}位歌手，基於5%差異閾值"
                
                subprocess.run(['git', 'add', 'public/singers_data.json'], check=True)
                subprocess.run(['git', 'commit', '-m', commit_message], check=True)
                subprocess.run(['git', 'push'], check=True)
                
                self.stats['git_pushes'] += 1
                self.logger.info(f"📤 Git推送完成: {commit_message}")
                
        except Exception as e:
            self.logger.error(f"Git推送失敗: {e}")
    
    def process_singer(self, singer_name):
        """處理單個歌手"""
        try:
            self.logger.info(f"🎤 處理歌手: {singer_name}")
            
            # 檢查是否需要處理
            check_result = self.check_singer_needs_processing(singer_name)
            
            if not check_result['needs_processing']:
                reason = check_result['reason']
                self.logger.info(f"⏭️ {singer_name}: 跳過處理 - {reason}")
                
                return {
                    'singer': singer_name,
                    'status': 'skipped',
                    'reason': reason,
                    'website_count': check_result.get('website_count', 0),
                    'our_count': check_result.get('our_count', 0)
                }
            
            # 需要處理 - 搜索並更新資料
            self.logger.info(f"✅ {singer_name}: 需要處理 - 我們{check_result.get('our_count', 0)} vs 網站{check_result.get('website_count', 0)}")
            
            # 延遲避免請求過於頻繁
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
            
            # 搜索新資料
            new_songs = self.search_singer_with_deduplication(singer_name)
            
            if new_songs:
                # 整合資料
                new_count, updated_count = self.integrate_singer_data(singer_name, new_songs)
                
                result = {
                    'singer': singer_name,
                    'status': 'processed',
                    'new_songs': new_count,
                    'updated_entries': updated_count,
                    'total_new_songs': len(new_songs),
                    'website_count': check_result.get('website_count', 0),
                    'our_count_before': check_result.get('our_count', 0)
                }
                
                self.stats['new_songs_added'] += new_count
                self.logger.info(f"🎉 {singer_name}: 成功處理 - 新增{new_count}首歌，更新{updated_count}個編號")
                
                return result
            else:
                return {
                    'singer': singer_name,
                    'status': 'no_new_data',
                    'website_count': check_result.get('website_count', 0),
                    'our_count': check_result.get('our_count', 0)
                }
                
        except Exception as e:
            self.logger.error(f"處理 {singer_name} 失敗: {e}")
            return {
                'singer': singer_name,
                'status': 'failed',
                'error': str(e)
            }
    
    def run_correct_scraping(self):
        """執行正確的基準爬取"""
        self.logger.info("=" * 60)
        self.logger.info("🎯 正確基準爬蟲開始執行")
        self.logger.info(f"基準設定: 與台灣點歌網比較，5%差異閾值")
        self.logger.info(f"重複檢查: 逐筆比對避免重複KTV編號")
        self.logger.info("=" * 60)
        
        if not self.singers_to_process:
            self.logger.info("✅ 所有歌手都已使用正確基準檢查完成！")
            return
        
        total_singers = len(self.singers_to_process)
        self.logger.info(f"開始處理 {total_singers} 位歌手...")
        
        # 分批處理
        batches = [self.singers_to_process[i:i + self.batch_size] 
                  for i in range(0, len(self.singers_to_process), self.batch_size)]
        
        for batch_num, batch_singers in enumerate(batches, 1):
            self.logger.info(f"\n--- 批次 {batch_num}/{len(batches)} (並行處理) ---")
            
            processed_in_batch = []
            
            # 使用線程池並行處理批次內的歌手
            with ThreadPoolExecutor(max_workers=self.parallel_threads) as executor:
                future_to_singer = {
                    executor.submit(self.process_singer, singer): singer 
                    for singer in batch_singers
                }
                
                for future in as_completed(future_to_singer):
                    singer = future_to_singer[future]
                    
                    try:
                        result = future.result(timeout=300)  # 5分鐘超時
                        processed_in_batch.append(result)
                        
                        # 更新統計
                        self.processed_singers_set.add(singer)
                        self.stats['processed_singers'] += 1
                        
                        if result['status'] == 'processed':
                            self.stats['successful_singers'] += 1
                        elif result['status'] == 'skipped':
                            self.stats['skipped_singers'] += 1
                        elif result['status'] == 'failed':
                            self.stats['failed_singers'] += 1
                        
                        self.logger.info(f"[{len(processed_in_batch)}/{len(batch_singers)}] 完成: {singer}")
                        
                    except Exception as e:
                        self.logger.error(f"處理 {singer} 時發生錯誤: {e}")
                        self.processed_singers_set.add(singer)
                        self.stats['processed_singers'] += 1
                        self.stats['failed_singers'] += 1
            
            # 保存檢查點
            self.save_checkpoint()
            
            # Git推送檢查
            if processed_in_batch:
                last_singer = processed_in_batch[-1]['singer']
                self.auto_git_push_update(last_singer)
            
            # 批次間休息
            if batch_num < len(batches):
                rest_time = 30
                self.logger.info(f"批次間休息{rest_time}秒...")
                time.sleep(rest_time)
        
        # 最終統計
        elapsed_time = datetime.now() - self.session_start_time
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("🎉 正確基準爬蟲執行完成！")
        self.logger.info("=" * 60)
        self.logger.info(f"📊 執行統計:")
        self.logger.info(f"   總處理時間: {elapsed_time}")
        self.logger.info(f"   處理歌手: {self.stats['processed_singers']} 位")
        self.logger.info(f"   成功處理: {self.stats['successful_singers']} 位")
        self.logger.info(f"   跳過歌手: {self.stats['skipped_singers']} 位")
        self.logger.info(f"   失敗歌手: {self.stats['failed_singers']} 位")
        self.logger.info(f"   新增歌曲: {self.stats['new_songs_added']} 首")
        self.logger.info(f"   網站查詢: {self.stats['website_queries']} 次")
        self.logger.info(f"   閾值檢查: {self.stats['threshold_checks']} 次")
        self.logger.info(f"   Git推送: {self.stats['git_pushes']} 次")
        
        # 最終Git推送
        if self.stats['successful_singers'] > 0:
            self.auto_git_push_update("final", force=True)
        
        # 保存最終檢查點
        self.save_checkpoint()

def main():
    """主程序"""
    try:
        # 保存PID
        with open('correct_scraper.pid', 'w') as f:
            f.write(str(os.getpid()))
        
        scraper = CorrectBenchmarkScraper()
        scraper.run_correct_scraping()
        
    except KeyboardInterrupt:
        print("\n用戶中斷執行")
    except Exception as e:
        logging.error(f"爬蟲執行失敗: {e}")
    finally:
        # 清理PID文件
        if os.path.exists('correct_scraper.pid'):
            os.remove('correct_scraper.pid')

if __name__ == "__main__":
    main()