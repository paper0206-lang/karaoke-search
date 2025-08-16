#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正版背景大規模爬蟲系統
修正問題：
1. 檢查點JSON序列化錯誤
2. 基準設定調整到95%
3. 增加自動Git推送功能
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

class FixedBackgroundScraper:
    def __init__(self, resume_from_checkpoint=True):
        # 設置日誌
        self.setup_logging()
        self.logger = logging.getLogger('FixedBackgroundScraper')
        
        self.base_url = "https://song.corp.com.tw"
        
        # 修正後的基準配置 - 95%
        self.lu_benchmark = {
            'total_songs': 12,
            'companies_covered': 16,
            'benchmark_threshold': 0.95  # 95%才算達標
        }
        
        # KTV公司清單
        self.companies_to_check = [
            "音圓", "錢櫃", "好樂迪", "銀櫃", "金嗓", "弘音", 
            "點將家", "星據點", "享溫馨", "大唐", "瑞影", "MV",
            "金影", "音影", "嘉揚", "音遊", "美華"
        ]
        
        # 背景執行配置
        self.resume_from_checkpoint = resume_from_checkpoint
        self.checkpoint_file = "fixed_background_checkpoint.json"
        self.max_singers_per_session = 200
        self.batch_size = 5
        self.delay_range = (4.0, 7.0)
        
        # Git自動推送配置
        self.auto_git_push = True
        self.git_push_interval = 10  # 每10位歌手推送一次
        
        # 設置信號處理
        signal.signal(signal.SIGINT, self._signal_handler)
        self.shutdown_requested = False
        
        # 載入歌手清單
        self.singers_to_process = self._load_singers_list()
        self.processed_singers_set = self.load_checkpoint()
        
        # 過濾已處理的歌手
        self.filter_unprocessed_singers()
        
        # 統計
        self.stats = {
            'total_singers': len(self.singers_to_process),
            'processed_singers': 0,
            'successful_singers': 0,
            'new_songs_added': 0,
            'updated_singers': 0,
            'failed_singers': 0,
            'git_pushes': 0,
            'start_time': datetime.now()
        }
        self.stats_lock = threading.Lock()
        
        # 創建輸出目錄
        os.makedirs("fixed_scraping_results", exist_ok=True)
        
        self.logger.info(f"修正版背景爬蟲初始化完成")
        self.logger.info(f"基準設定: 95%才算達標")
        self.logger.info(f"待處理歌手: {len(self.singers_to_process)} 位")
        self.logger.info(f"自動Git推送: {'啟用' if self.auto_git_push else '停用'}")
        
    def setup_logging(self):
        """設置日誌系統"""
        log_dir = "fixed_logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = f"{log_dir}/fixed_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def _signal_handler(self, signum, frame):
        self.logger.info(f"接收到中斷信號 ({signum})，正在安全關閉...")
        self.shutdown_requested = True
    
    def _load_singers_list(self):
        """載入歌手清單"""
        try:
            with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                singers_data = json.load(f)
            
            singers_list = list(singers_data.keys())
            
            # 移除盧廣仲（已作為基準）
            if "盧廣仲" in singers_list:
                singers_list.remove("盧廣仲")
            
            # 按歌曲數量排序
            def get_song_count(singer):
                return len(singers_data.get(singer, {}).get('歌曲清單', []))
            
            singers_list.sort(key=get_song_count, reverse=True)
            
            self.logger.info(f"載入歌手清單: {len(singers_list)} 位")
            return singers_list
            
        except Exception as e:
            self.logger.error(f"載入歌手清單失敗: {e}")
            return []
    
    def load_checkpoint(self):
        """載入檢查點 - 修正JSON序列化問題"""
        if not self.resume_from_checkpoint or not os.path.exists(self.checkpoint_file):
            self.logger.info("沒有檢查點文件，從頭開始")
            return set()
        
        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            processed_set = set(checkpoint_data.get('processed_singers', []))
            self.logger.info(f"載入檢查點: 已處理 {len(processed_set)} 位歌手")
            
            return processed_set
            
        except Exception as e:
            self.logger.error(f"載入檢查點失敗: {e}")
            return set()
    
    def save_checkpoint(self, additional_processed=None):
        """保存檢查點 - 修正JSON序列化問題"""
        if additional_processed:
            self.processed_singers_set.update(additional_processed)
        
        # 確保所有datetime對象都轉換為字符串
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
            'benchmark_threshold': self.lu_benchmark['benchmark_threshold']
        }
        
        try:
            # 原子性寫入
            temp_file = self.checkpoint_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
            
            os.rename(temp_file, self.checkpoint_file)
            self.logger.info(f"檢查點已保存: {len(self.processed_singers_set)} 位歌手已處理")
            
        except Exception as e:
            self.logger.error(f"保存檢查點失敗: {e}")
    
    def filter_unprocessed_singers(self):
        """過濾未處理的歌手"""
        original_count = len(self.singers_to_process)
        
        # 移除已處理的歌手
        self.singers_to_process = [
            singer for singer in self.singers_to_process 
            if singer not in self.processed_singers_set
        ]
        
        # 限制本次會話的處理數量
        if len(self.singers_to_process) > self.max_singers_per_session:
            self.logger.info(f"限制本次會話處理數量: {self.max_singers_per_session}")
            self.singers_to_process = self.singers_to_process[:self.max_singers_per_session]
        
        self.logger.info(f"歌手過濾完成: {original_count} → {len(self.singers_to_process)} 位")
    
    def check_singer_against_benchmark(self, singer_name):
        """檢查歌手是否達到95%基準標準"""
        try:
            with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                singers_data = json.load(f)
            
            if singer_name not in singers_data:
                return {
                    'meets_benchmark': False,
                    'needs_processing': True,
                    'current_songs': 0,
                    'benchmark_score': 0.0,
                    'gaps': ['complete_absence']
                }
            
            singer_info = singers_data[singer_name]
            songs = singer_info.get('歌曲清單', [])
            
            # 計算各項指標
            total_songs = len(songs)
            companies_covered = set()
            taiwan_songs = 0
            mandarin_songs = 0
            
            for song in songs:
                language = song.get('語言', '')
                if language == '台':
                    taiwan_songs += 1
                elif language == '國':
                    mandarin_songs += 1
                
                for code_info in song.get('編號資訊', []):
                    company = code_info.get('公司', '')
                    if company:
                        companies_covered.add(company)
            
            # 計算基準得分
            scores = {
                'song_count': min(total_songs / self.lu_benchmark['total_songs'], 1.0),
                'company_coverage': len(companies_covered) / self.lu_benchmark['companies_covered'],
                'language_diversity': 1.0 if (taiwan_songs > 0 and mandarin_songs > 0) else 0.5
            }
            
            overall_score = sum(scores.values()) / len(scores)
            
            # 95%基準檢查
            meets_benchmark = overall_score >= self.lu_benchmark['benchmark_threshold']
            needs_processing = overall_score < self.lu_benchmark['benchmark_threshold']
            
            # 識別缺口
            gaps = []
            if total_songs < self.lu_benchmark['total_songs']:
                gaps.append(f'songs_insufficient_{total_songs}')
            if len(companies_covered) < 12:  # 至少12家KTV覆蓋
                gaps.append(f'company_coverage_low_{len(companies_covered)}')
            if taiwan_songs == 0 and mandarin_songs > 0:
                gaps.append('missing_taiwanese_songs')
            
            return {
                'meets_benchmark': meets_benchmark,
                'needs_processing': needs_processing,
                'current_songs': total_songs,
                'companies_covered': len(companies_covered),
                'benchmark_score': overall_score,
                'gaps': gaps,
                'taiwan_songs': taiwan_songs,
                'mandarin_songs': mandarin_songs
            }
            
        except Exception as e:
            self.logger.error(f"檢查{singer_name}基準失敗: {e}")
            return {
                'meets_benchmark': False,
                'needs_processing': True,
                'benchmark_score': 0.0,
                'gaps': ['check_failed']
            }
    
    def search_taiwan_songking_data(self, singer_name, session=None):
        """搜索Taiwan Song King資料"""
        if session is None:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
        
        all_songs = []
        companies_found = set()
        
        self.logger.info(f"搜索: {singer_name}")
        
        for company in self.companies_to_check:
            if self.shutdown_requested:
                break
                
            try:
                delay = random.uniform(*self.delay_range)
                time.sleep(delay)
                
                search_url = f"{self.base_url}/songs.aspx?company={quote(company)}&singer={quote(singer_name)}"
                
                response = session.get(search_url, timeout=15)
                response.encoding = "utf-8"
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    song_links = soup.select('a[href^="mv.aspx?id="]')
                    
                    if song_links:
                        companies_found.add(company)
                        company_songs = []
                        
                        for link in song_links:
                            try:
                                raw_text = link.get_text().strip()
                                parts = raw_text.split('\n')
                                
                                if len(parts) >= 3:
                                    number = parts[0].strip()
                                    song_title = parts[1].strip()
                                    singer_info = parts[2].strip()
                                    
                                    language = self._detect_language_from_singer_info(singer_info)
                                    
                                    song_data = {
                                        "company": company,
                                        "raw_text": raw_text,
                                        "number": number,
                                        "song_title": song_title,
                                        "singer_info": singer_info,
                                        "language": language,
                                        "url": link.get('href', ''),
                                        "scraped_at": datetime.now().isoformat()
                                    }
                                    
                                    company_songs.append(song_data)
                                    
                            except Exception:
                                continue
                        
                        all_songs.extend(company_songs)
                        if company_songs:
                            self.logger.info(f"   ✅ {company:10s}: {len(company_songs):3d} 首歌")
                    else:
                        self.logger.info(f"   ❌ {company:10s}: 無數據")
                else:
                    self.logger.info(f"   ❌ {company:10s}: HTTP {response.status_code}")
                        
            except Exception as e:
                self.logger.error(f"   ❌ {company:10s}: {str(e)[:30]}")
                time.sleep(2)
        
        # 轉換為資料庫格式
        converted_songs = self._convert_to_database_format(singer_name, all_songs)
        
        self.logger.info(f"   📊 {singer_name}: {len(converted_songs)}首獨特歌曲，{len(companies_found)}家KTV")
        
        return converted_songs, companies_found, all_songs
    
    def _detect_language_from_singer_info(self, singer_info):
        """語言檢測"""
        if '台' in singer_info:
            return '台'
        elif '國' in singer_info:
            return '國'
        elif '英' in singer_info or 'English' in singer_info:
            return '英'
        elif '粵' in singer_info or '港' in singer_info:
            return '粵'
        elif '日' in singer_info:
            return '日'
        else:
            return '國'  # 預設為國語
    
    def _convert_to_database_format(self, singer_name, raw_songs):
        """轉換Taiwan Song King資料為資料庫格式"""
        songs_dict = {}
        
        for song in raw_songs:
            song_title = song.get('song_title', '')
            key = f"{song_title}_{singer_name}"
            
            if key not in songs_dict:
                songs_dict[key] = {
                    "歌名": song_title,
                    "歌手": singer_name,
                    "語言": song.get('language', ''),
                    "編號資訊": []
                }
            
            code_info = {
                "公司": song.get('company', ''),
                "編號": song.get('number', '')
            }
            
            # 避免重複
            existing_codes = songs_dict[key]['編號資訊']
            if not any(
                existing['公司'] == code_info['公司'] and existing['編號'] == code_info['編號']
                for existing in existing_codes
            ):
                songs_dict[key]['編號資訊'].append(code_info)
        
        return list(songs_dict.values())
    
    def integrate_singer_data(self, singer_name, new_songs):
        """整合歌手資料到資料庫"""
        try:
            with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                singers_data = json.load(f)
            
            if singer_name not in singers_data:
                singers_data[singer_name] = {
                    '歌手名稱': singer_name,
                    '歌曲清單': []
                }
            
            existing_songs = singers_data[singer_name].get('歌曲清單', [])
            existing_dict = {}
            
            # 建立現有歌曲索引
            for song in existing_songs:
                key = f"{song.get('歌名', '')}_{song.get('歌手', '')}"
                existing_dict[key] = song
            
            new_count = 0
            updated_count = 0
            
            for new_song in new_songs:
                key = f"{new_song.get('歌名', '')}_{new_song.get('歌手', '')}"
                
                if key in existing_dict:
                    # 合併編號資訊
                    existing_codes = existing_dict[key].get('編號資訊', [])
                    new_codes = new_song.get('編號資訊', [])
                    
                    merged_codes = existing_codes.copy()
                    codes_added = False
                    
                    for new_code in new_codes:
                        if not any(
                            existing['公司'] == new_code['公司'] and existing['編號'] == new_code['編號']
                            for existing in merged_codes
                        ):
                            merged_codes.append(new_code)
                            codes_added = True
                    
                    if codes_added:
                        existing_dict[key]['編號資訊'] = merged_codes
                        updated_count += 1
                    
                    # 更新語言資訊
                    if not existing_dict[key].get('語言') and new_song.get('語言'):
                        existing_dict[key]['語言'] = new_song.get('語言')
                else:
                    # 全新歌曲
                    existing_dict[key] = new_song
                    new_count += 1
            
            # 更新歌曲清單
            singers_data[singer_name]['歌曲清單'] = list(existing_dict.values())
            
            # 保存更新
            with open('public/singers_data.json', 'w', encoding='utf-8') as f:
                json.dump(singers_data, f, ensure_ascii=False, indent=2)
            
            return new_count, updated_count
            
        except Exception as e:
            self.logger.error(f"整合{singer_name}資料失敗: {e}")
            return 0, 0
    
    def auto_git_push_update(self, singer_name, force=False):
        """自動Git推送更新"""
        if not self.auto_git_push:
            return
        
        try:
            # 檢查是否需要推送
            if not force and self.stats['processed_singers'] % self.git_push_interval != 0:
                return
            
            self.logger.info(f"開始Git推送...")
            
            # Git add
            subprocess.run(['git', 'add', 'public/singers_data.json'], 
                         check=True, capture_output=True, text=True)
            
            # Git commit
            commit_message = f"🎵 背景爬蟲更新: 處理{self.stats['processed_singers']}位歌手，新增{self.stats['new_songs_added']}首歌"
            
            subprocess.run(['git', 'commit', '-m', commit_message], 
                         check=True, capture_output=True, text=True)
            
            # Git push
            result = subprocess.run(['git', 'push'], 
                                  check=True, capture_output=True, text=True)
            
            with self.stats_lock:
                self.stats['git_pushes'] += 1
            
            self.logger.info(f"✅ Git推送成功 (第{self.stats['git_pushes']}次)")
            
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Git推送失敗: {e.stderr}")
        except Exception as e:
            self.logger.error(f"Git推送異常: {e}")
    
    def process_singer(self, singer_name):
        """處理單一歌手"""
        try:
            self.logger.info(f"開始處理: {singer_name}")
            
            # 檢查95%基準
            benchmark_check = self.check_singer_against_benchmark(singer_name)
            
            if benchmark_check['meets_benchmark']:
                self.logger.info(f"{singer_name}: 已達95%基準標準 ({benchmark_check['benchmark_score']:.1%})")
                return {
                    'singer': singer_name,
                    'status': 'already_complete',
                    'benchmark_score': benchmark_check['benchmark_score']
                }
            
            self.logger.info(f"{singer_name}: 當前基準 {benchmark_check['benchmark_score']:.1%}, 開始搜尋...")
            
            # 搜索Taiwan Song King資料
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            new_songs, companies_found, raw_data = self.search_taiwan_songking_data(singer_name, session)
            session.close()
            
            if new_songs:
                # 整合資料
                new_count, updated_count = self.integrate_singer_data(singer_name, new_songs)
                
                # 重新檢查基準
                updated_benchmark = self.check_singer_against_benchmark(singer_name)
                
                result = {
                    'singer': singer_name,
                    'status': 'processed',
                    'new_songs': new_count,
                    'updated_songs': updated_count,
                    'total_new_songs': len(new_songs),
                    'companies_found': len(companies_found),
                    'benchmark_before': benchmark_check['benchmark_score'],
                    'benchmark_after': updated_benchmark['benchmark_score'],
                    'meets_benchmark_now': updated_benchmark['meets_benchmark']
                }
                
                self.logger.info(f"{singer_name}: 完成 +{new_count}首新歌, 基準 {benchmark_check['benchmark_score']:.1%} → {updated_benchmark['benchmark_score']:.1%}")
                
                # 嘗試Git推送
                self.auto_git_push_update(singer_name)
                
                return result
            else:
                self.logger.warning(f"{singer_name}: 無新資料")
                return {
                    'singer': singer_name,
                    'status': 'no_data',
                    'benchmark_score': benchmark_check['benchmark_score']
                }
                
        except Exception as e:
            self.logger.error(f"{singer_name}: 處理失敗 - {str(e)}")
            return {
                'singer': singer_name,
                'status': 'failed',
                'error': str(e)
            }
    
    def run_fixed_scraping(self):
        """執行修正版爬取"""
        self.logger.info("=" * 60)
        self.logger.info("修正版背景大規模爬蟲開始執行")
        self.logger.info(f"基準設定: {self.lu_benchmark['benchmark_threshold']*100:.0f}%才算達標")
        self.logger.info("=" * 60)
        
        if not self.singers_to_process:
            self.logger.info("沒有歌手需要處理")
            return []
        
        # 快速篩選需要改進的歌手
        self.logger.info("快速篩選需要改進的歌手...")
        needs_improvement = []
        
        for i, singer in enumerate(self.singers_to_process, 1):
            if self.shutdown_requested:
                break
                
            if i % 50 == 0:
                self.logger.info(f"篩選進度: {i}/{len(self.singers_to_process)}")
            
            benchmark_check = self.check_singer_against_benchmark(singer)
            
            if benchmark_check['needs_processing']:
                needs_improvement.append(singer)
        
        self.singers_to_process = needs_improvement
        self.logger.info(f"篩選完成: {len(needs_improvement)} 位歌手需要改進")
        
        if not self.singers_to_process:
            self.logger.info("所有歌手都已達到95%基準標準！")
            return []
        
        all_results = []
        
        # 分批處理
        for batch_start in range(0, len(self.singers_to_process), self.batch_size):
            if self.shutdown_requested:
                break
                
            batch_end = min(batch_start + self.batch_size, len(self.singers_to_process))
            batch_singers = self.singers_to_process[batch_start:batch_end]
            
            batch_num = batch_start // self.batch_size
            total_batches = (len(self.singers_to_process) + self.batch_size - 1) // self.batch_size
            
            self.logger.info(f"\n--- 批次 {batch_num + 1}/{total_batches} ---")
            
            batch_results = []
            processed_in_batch = []
            
            for i, singer in enumerate(batch_singers, 1):
                if self.shutdown_requested:
                    break
                
                self.logger.info(f"[{i:2d}/{len(batch_singers)}] 處理中: {singer}")
                
                result = self.process_singer(singer)
                batch_results.append(result)
                processed_in_batch.append(singer)
                
                # 更新統計
                with self.stats_lock:
                    self.stats['processed_singers'] += 1
                    if result['status'] == 'processed':
                        self.stats['successful_singers'] += 1
                        self.stats['new_songs_added'] += result.get('new_songs', 0)
                        self.stats['updated_singers'] += 1
                    elif result['status'] == 'failed':
                        self.stats['failed_singers'] += 1
                
                # 每處理5個歌手保存檢查點
                if i % 5 == 0:
                    self.save_checkpoint(processed_in_batch[-5:])
            
            all_results.extend(batch_results)
            
            # 批次完成保存檢查點
            self.save_checkpoint(processed_in_batch)
            
            # 批次間休息
            if not self.shutdown_requested and batch_num < total_batches - 1:
                self.logger.info("批次間休息45秒...")
                time.sleep(45)
        
        # 最終Git推送
        if self.auto_git_push and all_results:
            self.auto_git_push_update("final", force=True)
        
        self.logger.info("修正版背景爬蟲執行完成")
        return all_results

def main():
    """主程序"""
    print("🔧 修正版背景大規模爬蟲系統")
    print("=" * 50)
    
    # 檢查是否要恢復
    resume = True
    if len(sys.argv) > 1 and sys.argv[1] == '--fresh':
        resume = False
        print("🆕 重新開始（忽略檢查點）")
    
    scraper = FixedBackgroundScraper(resume_from_checkpoint=resume)
    
    try:
        results = scraper.run_fixed_scraping()
        
        if results:
            successful_count = sum(1 for r in results if r['status'] == 'processed')
            improved_count = sum(1 for r in results 
                               if r['status'] == 'processed' and r.get('meets_benchmark_now', False))
            total_new_songs = sum(r.get('new_songs', 0) for r in results if r['status'] == 'processed')
            
            print(f"\n🎉 修正版執行完成！")
            print(f"✅ 成功處理: {successful_count}/{len(results)} 位歌手")
            print(f"🎯 達到95%基準: {improved_count} 位歌手")
            print(f"🎵 新增歌曲: {total_new_songs} 首")
            print(f"📤 Git推送: {scraper.stats['git_pushes']} 次")
            print(f"📊 詳細日誌: fixed_logs/ 目錄")
        else:
            print(f"\n✅ 所有歌手都已達到95%基準標準！")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ 用戶中斷，檢查點已保存")
        scraper.logger.info("用戶中斷，數據已保存")
        
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
        scraper.logger.error(f"執行錯誤: {e}", exc_info=True)

if __name__ == "__main__":
    main()