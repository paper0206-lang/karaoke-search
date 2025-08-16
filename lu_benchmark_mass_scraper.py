#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基於盧廣仲基準的大規模歌手爬取系統
使用Taiwan Song King成功策略，按批次處理3,478位歌手
確保每位歌手達到盧廣仲的檢測對象標準
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
from collections import defaultdict

class LuBenchmarkMassScraper:
    def __init__(self):
        self.base_url = "https://song.corp.com.tw"
        
        # 基於盧廣仲成功經驗的配置
        self.companies_to_check = [
            "音圓", "錢櫃", "好樂迪", "銀櫃", "金嗓", "弘音", 
            "點將家", "星據點", "享溫馨", "大唐", "瑞影", "MV",
            "金影", "音影", "嘉揚", "音遊", "美華"
        ]
        
        # 盧廣仲基準標準
        self.lu_benchmark = {
            'total_songs': 12,
            'unique_songs': 12,
            'ktv_entries': 72,
            'companies_covered': 16,
            'languages': ['國', '台'],
            'taiwan_songs': 5,
            'mandarin_songs': 7
        }
        
        # 線程配置（基於Taiwan Song King成功經驗）
        self.max_workers = 3  # 減少併發避免被封
        self.delay_range = (3.0, 5.0)  # 增加延遲確保穩定
        
        # 載入歌手清單
        self.singers_to_process = self._load_singers_list()
        self.processed_singers = set()
        
        # 批次配置
        self.batch_size = 20  # 每批處理20位歌手
        self.current_batch = 0
        self.total_batches = (len(self.singers_to_process) + self.batch_size - 1) // self.batch_size
        
        # 統計
        self.stats = {
            'total_singers': len(self.singers_to_process),
            'processed_singers': 0,
            'successful_singers': 0,
            'new_songs_added': 0,
            'updated_singers': 0,
            'failed_singers': 0,
            'start_time': datetime.now(),
            'current_batch': 0
        }
        self.stats_lock = threading.Lock()
        
        # 設置信號處理
        signal.signal(signal.SIGINT, self._signal_handler)
        self.shutdown_requested = False
        
        # 創建輸出目錄
        os.makedirs("mass_scraping_results", exist_ok=True)
        
        print("🎤 基於盧廣仲基準的大規模歌手爬取系統")
        print(f"📊 目標歌手: {len(self.singers_to_process):,} 位")
        print(f"🎯 基準標準: {self.lu_benchmark['total_songs']}首歌，{self.lu_benchmark['companies_covered']}家KTV")
        print(f"📦 批次配置: {self.batch_size}位歌手/批，共{self.total_batches}批")
        print(f"🕐 預估時間: {self.total_batches * 30:.0f}分鐘")
        print("=" * 70)
    
    def _signal_handler(self, signum, frame):
        print(f"\n⚠️ 接收到中斷信號，正在安全關閉...")
        self.shutdown_requested = True
    
    def _load_singers_list(self):
        """載入歌手清單"""
        try:
            with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                singers_data = json.load(f)
            
            singers_list = list(singers_data.keys())
            
            # 移除盧廣仲（已作為基準完成）
            if "盧廣仲" in singers_list:
                singers_list.remove("盧廣仲")
            
            # 按歌曲數量排序（優先處理有更多歌曲的歌手）
            def get_song_count(singer):
                return len(singers_data.get(singer, {}).get('歌曲清單', []))
            
            singers_list.sort(key=get_song_count, reverse=True)
            
            print(f"✅ 載入歌手清單: {len(singers_list)} 位（已排除盧廣仲基準）")
            return singers_list
            
        except Exception as e:
            print(f"❌ 載入歌手清單失敗: {e}")
            return []
    
    def check_singer_against_benchmark(self, singer_name):
        """檢查歌手是否達到盧廣仲基準標準"""
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
                # 語言統計
                language = song.get('語言', '')
                if language == '台':
                    taiwan_songs += 1
                elif language == '國':
                    mandarin_songs += 1
                
                # 公司覆蓋度
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
            
            # 識別缺口
            gaps = []
            if total_songs < self.lu_benchmark['total_songs']:
                gaps.append(f'songs_insufficient_{total_songs}')
            if len(companies_covered) < 10:  # 最少10家KTV覆蓋
                gaps.append(f'company_coverage_low_{len(companies_covered)}')
            if taiwan_songs == 0 and mandarin_songs > 0:
                gaps.append('missing_taiwanese_songs')
            
            return {
                'meets_benchmark': overall_score >= 0.95,  # 95%才算達標
                'needs_processing': overall_score < 0.95,  # 95%以下需要處理
                'current_songs': total_songs,
                'companies_covered': len(companies_covered),
                'benchmark_score': overall_score,
                'gaps': gaps,
                'taiwan_songs': taiwan_songs,
                'mandarin_songs': mandarin_songs
            }
            
        except Exception as e:
            print(f"❌ 檢查{singer_name}基準失敗: {e}")
            return {
                'meets_benchmark': False,
                'needs_processing': True,
                'benchmark_score': 0.0,
                'gaps': ['check_failed']
            }
    
    def search_taiwan_songking_data(self, singer_name, session=None):
        """使用盧廣仲成功模式搜索Taiwan Song King資料"""
        if session is None:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
        
        all_songs = []
        companies_found = set()
        
        print(f"🔍 Taiwan Song King搜索: {singer_name}")
        
        for company in self.companies_to_check:
            if self.shutdown_requested:
                break
                
            try:
                # 使用盧廣仲成功的延遲策略
                delay = random.uniform(*self.delay_range)
                time.sleep(delay)
                
                # 構建搜索URL（Taiwan Song King模式）
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
                                    
                                    # 語言檢測（基於盧廣仲模式）
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
                            print(f"   ✅ {company:10s}: {len(company_songs):3d} 首歌")
                    else:
                        print(f"   ❌ {company:10s}: 無數據")
                else:
                    print(f"   ❌ {company:10s}: HTTP {response.status_code}")
                        
            except Exception as e:
                print(f"   ❌ {company:10s}: {str(e)[:30]}")
                time.sleep(2)
        
        # 轉換為我們的資料庫格式
        converted_songs = self._convert_to_database_format(singer_name, all_songs)
        
        print(f"   📊 {singer_name}: {len(converted_songs)}首獨特歌曲，{len(companies_found)}家KTV")
        
        return converted_songs, companies_found, all_songs
    
    def _detect_language_from_singer_info(self, singer_info):
        """從歌手資訊檢測語言（基於盧廣仲成功模式）"""
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
            # 基於歌名的簡單檢測
            return '國'  # 預設為國語
    
    def _convert_to_database_format(self, singer_name, raw_songs):
        """轉換Taiwan Song King資料為我們的資料庫格式"""
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
            
            # 添加KTV編號資訊
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
        """整合新歌曲到歌手資料庫"""
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
            print(f"❌ 整合{singer_name}資料失敗: {e}")
            return 0, 0
    
    def process_singer(self, singer_name):
        """處理單一歌手（基於盧廣仲模式）"""
        try:
            # 檢查基準
            benchmark_check = self.check_singer_against_benchmark(singer_name)
            
            if benchmark_check['meets_benchmark']:
                print(f"⏭️  {singer_name}: 已達基準標準 ({benchmark_check['benchmark_score']:.1%})")
                return {
                    'singer': singer_name,
                    'status': 'already_complete',
                    'benchmark_score': benchmark_check['benchmark_score']
                }
            
            print(f"\n🎯 處理歌手: {singer_name}")
            print(f"   當前歌曲: {benchmark_check['current_songs']} 首")
            print(f"   基準得分: {benchmark_check['benchmark_score']:.1%}")
            print(f"   需要改進: {', '.join(benchmark_check.get('gaps', []))}")
            
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
                
                # 保存個別結果
                self._save_singer_result(singer_name, new_songs, companies_found, raw_data)
                
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
                
                print(f"   ✅ 完成: +{new_count}首新歌，更新{updated_count}首，涵蓋{len(companies_found)}家KTV")
                print(f"   📊 基準提升: {benchmark_check['benchmark_score']:.1%} → {updated_benchmark['benchmark_score']:.1%}")
                
                return result
            else:
                print(f"   ❌ 無新資料")
                return {
                    'singer': singer_name,
                    'status': 'no_data',
                    'benchmark_score': benchmark_check['benchmark_score']
                }
                
        except Exception as e:
            print(f"   ❌ 處理失敗: {str(e)[:50]}")
            return {
                'singer': singer_name,
                'status': 'failed',
                'error': str(e)
            }
    
    def _save_singer_result(self, singer_name, songs, companies, raw_data):
        """保存個別歌手的結果"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mass_scraping_results/{singer_name}_{timestamp}.json"
            
            result_data = {
                'singer_name': singer_name,
                'scraped_at': datetime.now().isoformat(),
                'converted_songs': songs,
                'companies_found': list(companies),
                'raw_taiwan_data': raw_data,
                'benchmark_applied': 'lu_guangzhong_standard'
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"   ⚠️ 保存{singer_name}結果失敗: {e}")
    
    def process_batch(self, batch_singers):
        """處理一批歌手"""
        batch_results = []
        
        print(f"\n🚀 處理第{self.current_batch + 1}/{self.total_batches}批歌手")
        print(f"📋 本批歌手: {len(batch_singers)}位")
        print("-" * 50)
        
        for i, singer in enumerate(batch_singers, 1):
            if self.shutdown_requested:
                break
            
            print(f"[{i:2d}/{len(batch_singers)}] ", end="")
            result = self.process_singer(singer)
            batch_results.append(result)
            
            # 更新統計
            with self.stats_lock:
                self.stats['processed_singers'] += 1
                if result['status'] == 'processed':
                    self.stats['successful_singers'] += 1
                    self.stats['new_songs_added'] += result.get('new_songs', 0)
                    self.stats['updated_singers'] += 1
                elif result['status'] == 'failed':
                    self.stats['failed_singers'] += 1
        
        return batch_results
    
    def run_mass_scraping(self):
        """執行大規模爬取"""
        print(f"\n🚀 開始大規模歌手爬取")
        print(f"⏰ 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_results = []
        
        # 分批處理
        for batch_start in range(0, len(self.singers_to_process), self.batch_size):
            if self.shutdown_requested:
                break
                
            batch_end = min(batch_start + self.batch_size, len(self.singers_to_process))
            batch_singers = self.singers_to_process[batch_start:batch_end]
            
            self.current_batch = batch_start // self.batch_size
            
            batch_results = self.process_batch(batch_singers)
            all_results.extend(batch_results)
            
            # 保存批次進度
            self._save_batch_progress(self.current_batch, batch_results)
            
            # 批次間休息
            if not self.shutdown_requested and self.current_batch < self.total_batches - 1:
                print(f"\n⏸️  批次間休息30秒...")
                time.sleep(30)
        
        # 生成最終報告
        self._generate_final_report(all_results)
        
        return all_results
    
    def _save_batch_progress(self, batch_num, batch_results):
        """保存批次進度"""
        try:
            progress_file = f"mass_scraping_results/batch_{batch_num:03d}_progress.json"
            
            # 準備可序列化的統計資料
            serializable_stats = self.stats.copy()
            serializable_stats['start_time'] = self.stats['start_time'].isoformat()
            
            progress_data = {
                'batch_number': batch_num,
                'completed_at': datetime.now().isoformat(),
                'batch_results': batch_results,
                'overall_stats': serializable_stats
            }
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"⚠️ 保存批次進度失敗: {e}")
    
    def _generate_final_report(self, results):
        """生成最終報告"""
        elapsed = datetime.now() - self.stats['start_time']
        
        print(f"\n" + "="*80)
        print("🎊 大規模歌手爬取完成報告")
        print("="*80)
        
        # 統計分析
        successful_results = [r for r in results if r['status'] == 'processed']
        already_complete = [r for r in results if r['status'] == 'already_complete']
        failed_results = [r for r in results if r['status'] == 'failed']
        
        total_new_songs = sum(r.get('new_songs', 0) for r in successful_results)
        total_updated_songs = sum(r.get('updated_songs', 0) for r in successful_results)
        
        print(f"⏱️ 執行時間: {elapsed}")
        print(f"🎤 處理歌手: {len(results)}/{len(self.singers_to_process)} 位")
        print(f"✅ 成功處理: {len(successful_results)} 位")
        print(f"📋 已達標準: {len(already_complete)} 位")
        print(f"❌ 處理失敗: {len(failed_results)} 位")
        print(f"🎵 新增歌曲: {total_new_songs} 首")
        print(f"🔄 更新歌曲: {total_updated_songs} 首")
        
        if successful_results:
            # 基準達成分析
            meets_benchmark = sum(1 for r in successful_results if r.get('meets_benchmark_now', False))
            print(f"🎯 達成盧廣仲基準: {meets_benchmark}/{len(successful_results)} 位")
            
            # 最佳表現
            print(f"\n🏆 最佳表現歌手:")
            top_performers = sorted(successful_results, key=lambda x: x.get('new_songs', 0), reverse=True)
            for i, result in enumerate(top_performers[:10], 1):
                benchmark_improvement = result.get('benchmark_after', 0) - result.get('benchmark_before', 0)
                print(f"   {i:2d}. {result['singer']:15s}: +{result.get('new_songs', 0):3d}首 "
                      f"(基準提升 {benchmark_improvement:+.1%})")
        
        # 保存詳細報告
        report_file = f"mass_scraping_results/final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 準備可序列化的統計資料
        serializable_stats = self.stats.copy()
        serializable_stats['start_time'] = self.stats['start_time'].isoformat()
        
        report_data = {
            'execution_summary': {
                'start_time': self.stats['start_time'].isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration': str(elapsed),
                'benchmark_standard': self.lu_benchmark
            },
            'statistics': serializable_stats,
            'detailed_results': results,
            'lu_benchmark_compliance': {
                'singers_meeting_benchmark': meets_benchmark if successful_results else 0,
                'benchmark_achievement_rate': meets_benchmark / len(successful_results) if successful_results else 0
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細報告: {report_file}")
        print(f"📁 個別結果: mass_scraping_results/ 目錄")

def main():
    print("🎵 基於盧廣仲基準的大規模歌手爬取系統")
    print("=" * 60)
    
    scraper = LuBenchmarkMassScraper()
    
    try:
        print("🎯 執行策略: 基於Taiwan Song King成功模式")
        print("📏 品質標準: 盧廣仲檢測對象基準")
        print("⚠️ 確保每位歌手達到一致的品質標準")
        
        results = scraper.run_mass_scraping()
        
        if results:
            successful_count = sum(1 for r in results if r['status'] == 'processed')
            print(f"\n🎉 大規模爬取完成！成功處理 {successful_count}/{len(results)} 位歌手")
            print(f"📊 建議查看detailed_report了解完整結果")
        else:
            print(f"\n⚠️ 未能完成預期的爬取任務")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ 用戶中斷，已保存完成的數據")
        
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()