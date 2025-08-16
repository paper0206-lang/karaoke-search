#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改進的台灣點歌網比較器
基於HAR文件分析，使用正確的搜索方式
優先處理覆蓋率低的歌手
"""

import json
import requests
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import quote
import logging
from collections import defaultdict

class ImprovedTaiwanComparator:
    def __init__(self):
        self.base_url = "https://song.corp.com.tw"
        self.session = requests.Session()
        self.logger = logging.getLogger('ImprovedTaiwanComparator')
        
        # 設置用戶代理（基於HAR文件）
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'DNT': '1'
        })
    
    def get_singer_ktv_count_from_website_correct(self, singer_name, max_pages=None):
        """使用正確的搜索方式查詢台灣點歌網（基於HAR文件分析，支持分頁）"""
        try:
            if max_pages:
                self.logger.info(f"🔍 正確方式查詢台灣點歌網: {singer_name} (最多檢查{max_pages}頁)")
            else:
                self.logger.info(f"🔍 正確方式查詢台灣點歌網: {singer_name} (無上限檢查)")
            
            all_ktv_entries = []
            page = 1
            consecutive_empty_pages = 0
            max_empty_pages = 3  # 連續3頁無資料就停止
            
            while (max_pages is None or page <= max_pages) and consecutive_empty_pages < max_empty_pages:
                try:
                    # 使用HAR文件中發現的正確搜索方式 + 分頁
                    search_url = f"{self.base_url}/songs.aspx?company=全部&keyword={quote(singer_name)}&page={page}"
                    
                    self.logger.debug(f"📡 第{page}頁 URL: {search_url}")
                    
                    # 智能延遲避免過於頻繁
                    if page > 1:
                        time.sleep(random.uniform(1, 2))
                    
                    response = self.session.get(search_url, timeout=20)
                    response.encoding = "utf-8"
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        
                        # 尋找歌曲連結
                        song_links = soup.select('a[href^="mv.aspx?id="]')
                        
                        if song_links:
                            # 重置空頁計數器
                            consecutive_empty_pages = 0
                            page_entries = []
                            
                            for link in song_links:
                                try:
                                    raw_text = link.get_text().strip()
                                    href = link.get('href', '')
                                    
                                    # 解析歌曲ID
                                    song_id = None
                                    if 'id=' in href:
                                        song_id = href.split('id=')[1].split('&')[0]
                                    
                                    # 解析歌曲信息
                                    lines = raw_text.split('\n')
                                    if len(lines) >= 2:
                                        song_name = lines[0].strip()
                                        additional_info = lines[1].strip() if len(lines) > 1 else ""
                                        
                                        # 檢查是否真的包含歌手名稱（避免無關歌曲）
                                        if singer_name in raw_text or singer_name in additional_info:
                                            entry = {
                                                'song_name': song_name,
                                                'singer': singer_name,
                                                'song_id': song_id,
                                                'additional_info': additional_info,
                                                'raw_text': raw_text,
                                                'page': page
                                            }
                                            page_entries.append(entry)
                                            
                                except Exception as e:
                                    self.logger.debug(f"解析歌曲連結失敗: {e}")
                                    continue
                            
                            all_ktv_entries.extend(page_entries)
                            self.logger.info(f"   第{page}頁: {len(page_entries)} 首歌")
                            
                        else:
                            # 本頁無歌曲資料
                            consecutive_empty_pages += 1
                            self.logger.info(f"   第{page}頁: 無資料 ({consecutive_empty_pages}/{max_empty_pages})")
                    
                    else:
                        self.logger.warning(f"第{page}頁 HTTP錯誤: {response.status_code}")
                        consecutive_empty_pages += 1
                    
                    page += 1
                    
                except Exception as e:
                    self.logger.error(f"第{page}頁查詢失敗: {e}")
                    consecutive_empty_pages += 1
                    page += 1
                    continue
            
            # 統計總數
            total_ktv_entries = len(all_ktv_entries)
            unique_songs = len(set(entry['song_name'] for entry in all_ktv_entries if entry['song_name']))
            pages_checked = page - 1
            
            self.logger.info(f"🎵 {singer_name} 完整搜索結果:")
            self.logger.info(f"   檢查頁數: {pages_checked} 頁")
            self.logger.info(f"   KTV編號總數: {total_ktv_entries}")
            self.logger.info(f"   獨特歌曲數: {unique_songs}")
            
            # 如果結果仍然很少，可能需要檢查是否有其他問題
            if total_ktv_entries < 20 and pages_checked < 3:
                self.logger.warning(f"⚠️ {singer_name} 搜索結果較少，可能需要調整策略")
                
                # 保存第一頁內容以供調試
                debug_file = f"debug_paginated_search_{singer_name}_{int(time.time())}.html"
                try:
                    first_page_url = f"{self.base_url}/songs.aspx?company=全部&keyword={quote(singer_name)}&page=1"
                    debug_response = self.session.get(first_page_url, timeout=15)
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(debug_response.text)
                    self.logger.info(f"🔧 第一頁內容已保存至: {debug_file}")
                except:
                    pass
            
            return {
                'singer_name': singer_name,
                'total_ktv_entries': total_ktv_entries,
                'unique_songs': unique_songs,
                'ktv_entries': all_ktv_entries,
                'pages_checked': pages_checked,
                'search_successful': True,
                'method': 'correct_paginated_search'
            }
                
        except Exception as e:
            self.logger.error(f"查詢 {singer_name} 失敗: {e}")
            return {
                'singer_name': singer_name,
                'total_ktv_entries': 0,
                'unique_songs': 0,
                'ktv_entries': [],
                'pages_checked': 0,
                'search_successful': False,
                'error': str(e)
            }
    
    def get_our_database_ktv_count(self, singer_name):
        """獲取我們資料庫中歌手的KTV編號總數"""
        try:
            with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                singers_data = json.load(f)
            
            if singer_name not in singers_data:
                return {
                    'singer_name': singer_name,
                    'total_ktv_entries': 0,
                    'companies_count': 0,
                    'unique_songs': 0,
                    'exists': False
                }
            
            singer_info = singers_data[singer_name]
            songs = singer_info.get('歌曲清單', [])
            
            total_ktv_entries = 0
            companies = set()
            
            for song in songs:
                ktv_entries = song.get('編號資訊', [])
                total_ktv_entries += len(ktv_entries)
                
                for entry in ktv_entries:
                    company = entry.get('公司', '')
                    if company:
                        companies.add(company)
            
            return {
                'singer_name': singer_name,
                'total_ktv_entries': total_ktv_entries,
                'companies_count': len(companies),
                'unique_songs': len(songs),
                'exists': True
            }
            
        except Exception as e:
            self.logger.error(f"讀取資料庫失敗: {e}")
            return {
                'singer_name': singer_name,
                'total_ktv_entries': 0,
                'companies_count': 0,
                'unique_songs': 0,
                'exists': False,
                'error': str(e)
            }
    
    def check_needs_scraping_with_priority(self, singer_name, threshold_percentage=0.05):
        """檢查歌手是否需要爬取，並計算優先級分數"""
        try:
            self.logger.info(f"🎯 檢查 {singer_name} 需求和優先級...")
            
            # 獲取我們資料庫的數據
            our_data = self.get_our_database_ktv_count(singer_name)
            
            if not our_data['exists']:
                # 新歌手，最高優先級
                return {
                    'needs_scraping': True,
                    'priority_score': 100.0,
                    'reason': 'new_singer',
                    'our_count': 0,
                    'website_count': 'unknown',
                    'coverage_ratio': 0.0,
                    'priority_level': 'highest'
                }
            
            # 如果資料很少，優先處理
            our_count = our_data['total_ktv_entries']
            if our_count < 10:
                return {
                    'needs_scraping': True,
                    'priority_score': 90.0 - our_count,  # 資料越少優先級越高
                    'reason': 'insufficient_data',
                    'our_count': our_count,
                    'website_count': 'to_be_checked',
                    'coverage_ratio': 0.0,
                    'priority_level': 'very_high'
                }
            
            # 查詢台灣點歌網數據（使用正確方式）
            website_data = self.get_singer_ktv_count_from_website_correct(singer_name)
            
            if not website_data['search_successful']:
                # 如果網站查詢失敗，基於現有資料決定
                if our_count < 50:
                    return {
                        'needs_scraping': True,
                        'priority_score': 50.0,
                        'reason': 'website_check_failed_but_low_data',
                        'our_count': our_count,
                        'website_count': 'failed',
                        'coverage_ratio': 0.0,
                        'priority_level': 'medium'
                    }
                else:
                    return {
                        'needs_scraping': False,
                        'priority_score': 0.0,
                        'reason': 'website_check_failed_sufficient_data',
                        'our_count': our_count,
                        'website_count': 'failed',
                        'coverage_ratio': 1.0,
                        'priority_level': 'low'
                    }
            
            website_count = website_data['total_ktv_entries']
            
            # 如果台灣點歌網沒有資料，不需要爬取
            if website_count == 0:
                return {
                    'needs_scraping': False,
                    'priority_score': 0.0,
                    'reason': 'no_data_on_website',
                    'our_count': our_count,
                    'website_count': website_count,
                    'coverage_ratio': 1.0,
                    'priority_level': 'none'
                }
            
            # 計算覆蓋率和優先級
            coverage_ratio = our_count / website_count if website_count > 0 else 1.0
            difference_percentage = abs(1 - coverage_ratio)
            
            # 計算優先級分數（0-100）
            priority_score = 0.0
            priority_level = 'none'
            needs_scraping = False
            
            if coverage_ratio < 0.5:  # 覆蓋率 < 50%
                priority_score = 80.0 + (0.5 - coverage_ratio) * 40  # 80-100分
                priority_level = 'very_high'
                needs_scraping = True
                reason = 'very_low_coverage'
            elif coverage_ratio < 0.8:  # 覆蓋率 50-80%
                priority_score = 60.0 + (0.8 - coverage_ratio) * 66.7  # 60-80分
                priority_level = 'high'
                needs_scraping = True
                reason = 'low_coverage'
            elif coverage_ratio < 0.95:  # 覆蓋率 80-95%
                priority_score = 20.0 + (0.95 - coverage_ratio) * 266.7  # 20-60分
                priority_level = 'medium'
                needs_scraping = True
                reason = 'medium_coverage_gap'
            elif coverage_ratio < 1.05:  # 覆蓋率 95-105% (5%以內)
                priority_score = 5.0
                priority_level = 'low'
                needs_scraping = False  # 5%以內不需要爬取
                reason = 'within_5_percent_threshold'
            else:  # 覆蓋率 > 105%
                priority_score = 0.0
                priority_level = 'none'
                needs_scraping = False
                reason = 'our_data_more_complete'
            
            result = {
                'needs_scraping': needs_scraping,
                'priority_score': priority_score,
                'reason': reason,
                'our_count': our_count,
                'website_count': website_count,
                'coverage_ratio': coverage_ratio,
                'difference_percentage': difference_percentage,
                'priority_level': priority_level,
                'threshold_percentage': threshold_percentage
            }
            
            log_msg = f"{'✅ 需要' if needs_scraping else '⏭️ 跳過'} {singer_name}: "
            log_msg += f"我們{our_count} vs 網站{website_count} "
            log_msg += f"(覆蓋率{coverage_ratio:.1%}, 優先級{priority_score:.1f}分)"
            self.logger.info(log_msg)
            
            return result
            
        except Exception as e:
            self.logger.error(f"檢查 {singer_name} 失敗: {e}")
            return {
                'needs_scraping': False,
                'priority_score': 0.0,
                'reason': 'check_failed',
                'error': str(e),
                'priority_level': 'error'
            }
    
    def get_priority_sorted_singers(self, max_singers=None):
        """獲取按優先級排序的歌手列表"""
        try:
            with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                singers_data = json.load(f)
            
            singers_priority = []
            
            # 快速評估所有歌手的優先級（不查詢網站）
            for singer_name in singers_data.keys():
                singer_info = singers_data[singer_name]
                songs = singer_info.get('歌曲清單', [])
                
                total_ktv_entries = 0
                for song in songs:
                    total_ktv_entries += len(song.get('編號資訊', []))
                
                # 基於現有資料計算初步優先級
                if total_ktv_entries == 0:
                    priority_score = 100.0
                    priority_level = 'highest'
                elif total_ktv_entries < 5:
                    priority_score = 95.0 - total_ktv_entries
                    priority_level = 'very_high'
                elif total_ktv_entries < 20:
                    priority_score = 80.0 - total_ktv_entries
                    priority_level = 'high'
                elif total_ktv_entries < 50:
                    priority_score = 50.0 - (total_ktv_entries - 20)
                    priority_level = 'medium'
                else:
                    priority_score = 10.0 - min(total_ktv_entries - 50, 10)
                    priority_level = 'low'
                
                singers_priority.append({
                    'singer': singer_name,
                    'current_ktv_entries': total_ktv_entries,
                    'current_songs': len(songs),
                    'estimated_priority_score': priority_score,
                    'estimated_priority_level': priority_level
                })
            
            # 按優先級分數排序（高分優先）
            singers_priority.sort(key=lambda x: x['estimated_priority_score'], reverse=True)
            
            if max_singers:
                singers_priority = singers_priority[:max_singers]
            
            self.logger.info(f"📊 優先級排序完成: {len(singers_priority)} 位歌手")
            self.logger.info(f"   最高優先級: {singers_priority[0]['singer']} ({singers_priority[0]['estimated_priority_score']:.1f}分)")
            self.logger.info(f"   最低優先級: {singers_priority[-1]['singer']} ({singers_priority[-1]['estimated_priority_score']:.1f}分)")
            
            return singers_priority
            
        except Exception as e:
            self.logger.error(f"獲取優先級排序失敗: {e}")
            return []

def test_improved_comparator():
    """測試改進的比較器"""
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    comparator = ImprovedTaiwanComparator()
    
    # 測試正確的搜索方式
    test_singer = "盧廣仲"
    print(f"🧪 測試改進的搜索方式: {test_singer}")
    
    result = comparator.check_needs_scraping_with_priority(test_singer)
    
    print(f"\n結果:")
    print(f"   需要爬取: {'是' if result['needs_scraping'] else '否'}")
    print(f"   優先級分數: {result['priority_score']:.1f}")
    print(f"   優先級等級: {result['priority_level']}")
    print(f"   覆蓋率: {result.get('coverage_ratio', 0):.1%}")
    
    # 測試優先級排序
    print(f"\n🎯 測試優先級排序 (前10位):")
    priority_list = comparator.get_priority_sorted_singers(max_singers=10)
    
    for i, item in enumerate(priority_list, 1):
        print(f"   {i:2d}. {item['singer']:8} - {item['estimated_priority_score']:5.1f}分 "
              f"({item['current_ktv_entries']:3d}筆KTV, {item['current_songs']:2d}首歌)")

if __name__ == "__main__":
    test_improved_comparator()