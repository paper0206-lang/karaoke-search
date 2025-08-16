#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌手驅動智能爬蟲系統
基於現有歌手資料庫，智能檢測缺口並進行增量更新
避免重複下載，確保數據品質和完整性
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

class SingerDrivenScraper:
    def __init__(self):
        self.base_url = "https://song.corp.com.tw"
        self.threads = 5  # 減少線程數避免過載
        self.delay_range = (2.0, 4.0)  # 增加延遲確保穩定性
        
        # 設置信號處理
        signal.signal(signal.SIGINT, self._signal_handler)
        self.shutdown_requested = False
        
        # 載入現有資料庫
        self.existing_singers = self._load_existing_data()
        self.companies_to_check = [
            "音圓", "錢櫃", "好樂迪", "銀櫃", "金嗓", "弘音", 
            "點將家", "星據點", "享溫馨", "大唐", "瑞影", "MV",
            "金影", "音影", "嘉揚", "音遊", "美華"
        ]
        
        # 創建輸出目錄
        os.makedirs("singer_driven_results", exist_ok=True)
        
        # 統計
        self.stats = {
            'processed_singers': 0,
            'new_songs_found': 0,
            'updated_singers': 0,
            'total_requests': 0,
            'failed_requests': 0,
            'start_time': datetime.now()
        }
        self.stats_lock = threading.Lock()
        
        print("🎤 歌手驅動智能爬蟲系統")
        print(f"📊 已載入歌手資料庫: {len(self.existing_singers):,} 位歌手")
        print(f"🎯 目標KTV公司: {len(self.companies_to_check)} 家")
        print("=" * 60)
        
    def _signal_handler(self, signum, frame):
        print(f"\n⚠️ 接收到中斷信號 ({signum})，正在安全關閉...")
        self.shutdown_requested = True
    
    def _load_existing_data(self):
        """載入現有歌手資料庫"""
        try:
            with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ 載入歌手資料庫成功: {len(data)} 位歌手")
            return data
        except Exception as e:
            print(f"❌ 載入歌手資料庫失敗: {e}")
            return {}
    
    def categorize_singers(self):
        """將歌手按規模分類，制定不同策略"""
        categories = {
            'major': [],      # >50首 - 高價值目標
            'medium': [],     # 10-50首 - 穩定收益
            'minor': [],      # 5-9首 - 補全目標
            'micro': []       # 1-4首 - 批次處理
        }
        
        for singer, info in self.existing_singers.items():
            song_count = len(info.get('歌曲清單', []))
            
            if song_count > 50:
                categories['major'].append((singer, song_count))
            elif song_count >= 10:
                categories['medium'].append((singer, song_count))
            elif song_count >= 5:
                categories['minor'].append((singer, song_count))
            else:
                categories['micro'].append((singer, song_count))
        
        # 按歌曲數量排序
        for category in categories.values():
            category.sort(key=lambda x: x[1], reverse=True)
        
        return categories
    
    def check_singer_completeness(self, singer_name):
        """檢查歌手數據完整性，識別需要更新的項目"""
        if singer_name not in self.existing_singers:
            return {
                'exists': False,
                'needs_update': True,
                'missing_companies': self.companies_to_check,
                'current_songs': 0,
                'completeness_score': 0.0
            }
        
        singer_info = self.existing_singers[singer_name]
        songs = singer_info.get('歌曲清單', [])
        
        # 分析公司覆蓋度
        covered_companies = set()
        for song in songs:
            for code_info in song.get('編號資訊', []):
                company = code_info.get('公司', '')
                if company:
                    covered_companies.add(company)
        
        missing_companies = set(self.companies_to_check) - covered_companies
        completeness_score = len(covered_companies) / len(self.companies_to_check)
        
        # 檢查語言標記完整性
        missing_language = sum(1 for song in songs if not song.get('語言'))
        language_completeness = 1.0 - (missing_language / len(songs)) if songs else 0.0
        
        overall_score = (completeness_score + language_completeness) / 2
        
        return {
            'exists': True,
            'needs_update': overall_score < 0.8 or len(missing_companies) > 5,
            'missing_companies': list(missing_companies),
            'current_songs': len(songs),
            'completeness_score': overall_score,
            'covered_companies': list(covered_companies),
            'missing_language_count': missing_language
        }
    
    def search_singer_songs(self, singer_name, session=None):
        """搜索指定歌手的所有歌曲"""
        if session is None:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
        
        all_songs = []
        companies_found = set()
        
        print(f"🔍 搜索歌手: {singer_name}")
        
        for company in self.companies_to_check:
            if self.shutdown_requested:
                break
                
            try:
                # 智能延遲
                delay = random.uniform(*self.delay_range)
                time.sleep(delay)
                
                # 構建搜索URL
                search_url = f"{self.base_url}/songs.aspx?company={quote(company)}&singer={quote(singer_name)}"
                
                with self.stats_lock:
                    self.stats['total_requests'] += 1
                
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
                                link_text = link.get_text().strip()
                                parts = link_text.split()
                                
                                if len(parts) >= 4:
                                    song_data = {
                                        '歌名': parts[1],
                                        '歌手': singer_name,
                                        '語言': self._detect_language(parts[1]),  # 智能語言檢測
                                        '編號資訊': [{
                                            '公司': company,
                                            '編號': parts[0]
                                        }],
                                        'scraped_at': datetime.now().isoformat(),
                                        'source_company': company
                                    }
                                    company_songs.append(song_data)
                                    
                            except Exception as e:
                                continue
                        
                        all_songs.extend(company_songs)
                        print(f"   ✅ {company:10s}: {len(company_songs):3d} 首歌")
                    else:
                        print(f"   ❌ {company:10s}: 無數據")
                else:
                    print(f"   ❌ {company:10s}: HTTP {response.status_code}")
                    with self.stats_lock:
                        self.stats['failed_requests'] += 1
                        
            except Exception as e:
                print(f"   ❌ {company:10s}: 錯誤 - {str(e)[:30]}")
                with self.stats_lock:
                    self.stats['failed_requests'] += 1
                time.sleep(2)  # 錯誤後額外等待
        
        # 整合相同歌曲的不同公司編號
        integrated_songs = self._integrate_song_codes(all_songs)
        
        print(f"   📊 整合結果: {len(integrated_songs)} 首獨特歌曲，涵蓋 {len(companies_found)} 家KTV")
        
        return integrated_songs, companies_found
    
    def _detect_language(self, song_title):
        """智能語言檢測"""
        # 簡單的語言檢測邏輯
        chinese_chars = sum(1 for char in song_title if '\u4e00' <= char <= '\u9fff')
        english_chars = sum(1 for char in song_title if char.isalpha() and ord(char) < 128)
        
        if chinese_chars > english_chars:
            return '國'  # 預設為國語，可以後續優化
        elif english_chars > 0:
            return '英'
        else:
            return ''
    
    def _integrate_song_codes(self, songs):
        """整合相同歌曲的不同KTV公司編號"""
        songs_dict = {}
        
        for song in songs:
            key = f"{song.get('歌名', '')}_{song.get('歌手', '')}"
            
            if key not in songs_dict:
                songs_dict[key] = {
                    '歌名': song.get('歌名', ''),
                    '歌手': song.get('歌手', ''),
                    '語言': song.get('語言', ''),
                    '編號資訊': []
                }
            
            # 合併編號資訊
            for code_info in song.get('編號資訊', []):
                # 避免重複
                exists = any(
                    existing['公司'] == code_info['公司'] and existing['編號'] == code_info['編號']
                    for existing in songs_dict[key]['編號資訊']
                )
                
                if not exists:
                    songs_dict[key]['編號資訊'].append(code_info)
        
        return list(songs_dict.values())
    
    def update_singer_data(self, singer_name, new_songs, completeness_info):
        """更新歌手數據，智能合併新舊數據"""
        if singer_name not in self.existing_singers:
            # 新歌手
            self.existing_singers[singer_name] = {
                '歌手名稱': singer_name,
                '歌曲清單': new_songs
            }
            return len(new_songs), 0  # 新增歌曲數, 更新歌曲數
        
        # 現有歌手更新
        existing_songs = self.existing_singers[singer_name].get('歌曲清單', [])
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
                
                # 檢查是否有新的KTV編號
                merged_codes = existing_codes.copy()
                codes_added = False
                
                for new_code in new_codes:
                    exists = any(
                        existing['公司'] == new_code['公司'] and existing['編號'] == new_code['編號']
                        for existing in merged_codes
                    )
                    if not exists:
                        merged_codes.append(new_code)
                        codes_added = True
                
                if codes_added:
                    existing_dict[key]['編號資訊'] = merged_codes
                    updated_count += 1
                
                # 更新語言資訊（如果現有資訊不完整）
                if not existing_dict[key].get('語言') and new_song.get('語言'):
                    existing_dict[key]['語言'] = new_song.get('語言')
                    
            else:
                # 全新歌曲
                existing_dict[key] = new_song
                new_count += 1
        
        # 更新歌曲清單
        self.existing_singers[singer_name]['歌曲清單'] = list(existing_dict.values())
        
        return new_count, updated_count
    
    def process_singer(self, singer_name, priority='normal'):
        """處理單一歌手的數據更新"""
        try:
            # 檢查完整性
            completeness = self.check_singer_completeness(singer_name)
            
            if not completeness['needs_update']:
                print(f"⏭️  {singer_name}: 數據已完整 ({completeness['completeness_score']:.1%})")
                return None
            
            print(f"\n🎯 處理歌手: {singer_name}")
            print(f"   當前歌曲: {completeness['current_songs']} 首")
            print(f"   完整度: {completeness['completeness_score']:.1%}")
            print(f"   缺少公司: {len(completeness.get('missing_companies', []))} 家")
            
            # 創建會話
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            # 搜索歌手歌曲
            new_songs, companies_found = self.search_singer_songs(singer_name, session)
            
            if new_songs:
                # 更新數據
                new_count, updated_count = self.update_singer_data(singer_name, new_songs, completeness)
                
                # 保存單個歌手的結果
                self._save_singer_result(singer_name, new_songs, companies_found)
                
                # 更新統計
                with self.stats_lock:
                    self.stats['processed_singers'] += 1
                    self.stats['new_songs_found'] += new_count
                    if new_count > 0 or updated_count > 0:
                        self.stats['updated_singers'] += 1
                
                result = {
                    'singer': singer_name,
                    'new_songs': new_count,
                    'updated_songs': updated_count,
                    'total_songs': len(new_songs),
                    'companies_found': len(companies_found),
                    'completeness_before': completeness['completeness_score'],
                    'completeness_after': len(companies_found) / len(self.companies_to_check)
                }
                
                print(f"   ✅ 完成: 新增{new_count}首, 更新{updated_count}首, 涵蓋{len(companies_found)}家KTV")
                return result
            else:
                print(f"   ❌ 無新數據")
                return None
                
        except Exception as e:
            print(f"   ❌ 處理失敗: {str(e)[:50]}")
            return None
    
    def _save_singer_result(self, singer_name, songs, companies):
        """保存單個歌手的爬取結果"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"singer_driven_results/{singer_name}_{timestamp}.json"
            
            result_data = {
                'singer_name': singer_name,
                'scraped_at': datetime.now().isoformat(),
                'songs_count': len(songs),
                'companies_found': list(companies),
                'songs': songs
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"   ⚠️ 保存失敗: {e}")
    
    def run_smart_update(self, strategy='priority'):
        """執行智能更新策略"""
        categories = self.categorize_singers()
        
        print(f"\n🚀 開始智能更新 (策略: {strategy})")
        print(f"📊 歌手分類:")
        print(f"   大型歌手: {len(categories['major'])} 位")
        print(f"   中型歌手: {len(categories['medium'])} 位")
        print(f"   小型歌手: {len(categories['minor'])} 位")
        print(f"   微型歌手: {len(categories['micro'])} 位")
        print("=" * 60)
        
        results = []
        
        if strategy == 'priority':
            # 優先處理大型歌手
            print("🎯 階段1: 處理大型歌手 (>50首)")
            for singer_name, song_count in categories['major']:
                if self.shutdown_requested:
                    break
                result = self.process_singer(singer_name, 'high')
                if result:
                    results.append(result)
            
            # 處理中型歌手
            print("\n🎯 階段2: 處理中型歌手 (10-50首)")
            for singer_name, song_count in categories['medium'][:20]:  # 限制數量
                if self.shutdown_requested:
                    break
                result = self.process_singer(singer_name, 'normal')
                if result:
                    results.append(result)
        
        elif strategy == 'gap_fill':
            # 專注填補缺口
            all_singers = (categories['major'] + categories['medium'] + 
                          categories['minor'][:50])  # 限制小型歌手數量
            
            for singer_name, song_count in all_singers:
                if self.shutdown_requested:
                    break
                    
                completeness = self.check_singer_completeness(singer_name)
                if completeness['completeness_score'] < 0.7:  # 只處理完整度<70%的
                    result = self.process_singer(singer_name, 'gap_fill')
                    if result:
                        results.append(result)
        
        # 保存更新後的完整資料庫
        self._save_updated_database()
        
        # 生成報告
        self._generate_update_report(results)
        
        return results
    
    def _save_updated_database(self):
        """保存更新後的完整歌手資料庫"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 備份原始文件
            backup_file = f"singers_data_backup_{timestamp}.json"
            if os.path.exists('public/singers_data.json'):
                import shutil
                shutil.copy2('public/singers_data.json', backup_file)
                print(f"📁 原始資料備份: {backup_file}")
            
            # 保存更新後的資料
            with open('public/singers_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.existing_singers, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 歌手資料庫已更新: public/singers_data.json")
            
        except Exception as e:
            print(f"❌ 保存資料庫失敗: {e}")
    
    def _generate_update_report(self, results):
        """生成更新報告"""
        elapsed = datetime.now() - self.stats['start_time']
        
        print(f"\n" + "="*80)
        print("📊 歌手驅動更新完成報告")
        print("="*80)
        
        # 基本統計
        total_new_songs = sum(r['new_songs'] for r in results)
        total_updated_songs = sum(r['updated_songs'] for r in results)
        
        print(f"⏱️ 執行時間: {elapsed}")
        print(f"🎤 處理歌手: {len(results)} 位")
        print(f"🎵 新增歌曲: {total_new_songs} 首")
        print(f"🔄 更新歌曲: {total_updated_songs} 首")
        print(f"📡 總請求數: {self.stats['total_requests']}")
        print(f"❌ 失敗請求: {self.stats['failed_requests']}")
        print(f"✅ 成功率: {((self.stats['total_requests'] - self.stats['failed_requests']) / self.stats['total_requests'] * 100):.1f}%")
        
        # 詳細結果
        if results:
            print(f"\n🏆 更新最多的歌手:")
            sorted_results = sorted(results, key=lambda x: x['new_songs'], reverse=True)
            for i, result in enumerate(sorted_results[:10], 1):
                print(f"   {i:2d}. {result['singer']:15s}: +{result['new_songs']:3d}首 (更新{result['updated_songs']}首)")
        
        # 保存報告
        report_data = {
            'execution_time': str(elapsed),
            'stats': self.stats,
            'results': results,
            'generated_at': datetime.now().isoformat()
        }
        
        report_file = f"singer_driven_results/update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細報告: {report_file}")

def main():
    """主程序"""
    print("🎵 歌手驅動智能爬蟲系統")
    print("=" * 50)
    
    scraper = SingerDrivenScraper()
    
    try:
        # 選擇策略
        strategy = 'priority'  # 可選: 'priority', 'gap_fill'
        
        print(f"🎯 執行策略: {strategy}")
        print("💡 說明: 基於現有歌手資料庫，智能檢測並補全缺失數據")
        print("⚠️ 避免重複下載，確保數據品質")
        
        # 執行更新
        results = scraper.run_smart_update(strategy)
        
        if results:
            print(f"\n🎉 更新完成！成功處理 {len(results)} 位歌手")
        else:
            print(f"\n⚠️ 沒有需要更新的歌手")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ 用戶中斷，正在保存已完成的數據...")
        scraper._save_updated_database()
        
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()