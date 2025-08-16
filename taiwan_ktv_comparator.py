#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣點歌網KTV編號比較器
實現正確的動態基準檢查機制
"""

import json
import requests
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import quote
import logging

class TaiwanKTVComparator:
    def __init__(self):
        self.base_url = "https://song.corp.com.tw"
        self.session = requests.Session()
        self.logger = logging.getLogger('TaiwanKTVComparator')
        
        # 設置用戶代理
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # KTV公司清單
        self.companies_to_check = [
            "音圓", "錢櫃", "好樂迪", "銀櫃", "金嗓", "弘音", 
            "點將家", "星據點", "享溫馨", "大唐", "瑞影", "MV",
            "金影", "音影", "嘉揚", "音遊", "美華"
        ]
    
    def get_singer_ktv_count_from_website(self, singer_name):
        """從台灣點歌網獲取歌手的KTV編號總數（使用正確的查詢方式）"""
        try:
            self.logger.info(f"🔍 查詢台灣點歌網: {singer_name}")
            
            all_ktv_entries = []
            companies_found = set()
            
            # 使用與原爬蟲相同的並行搜索方法
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            def search_company(company):
                """搜索單個KTV公司"""
                try:
                    # 延遲避免過於頻繁
                    time.sleep(random.uniform(1, 2))
                    
                    search_url = f"{self.base_url}/songs.aspx?company={quote(company)}&singer={quote(singer_name)}"
                    
                    response = self.session.get(search_url, timeout=15)
                    response.encoding = "utf-8"
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        song_links = soup.select('a[href^="mv.aspx?id="]')
                        
                        company_entries = []
                        
                        if song_links:
                            companies_found.add(company)
                            
                            for link in song_links:
                                try:
                                    raw_text = link.get_text().strip()
                                    parts = raw_text.split('\n')
                                    
                                    if len(parts) >= 3:
                                        number = parts[0].strip()
                                        song_name = parts[1].strip()
                                        
                                        # 推測語言
                                        language = "國"  # 預設
                                        if any(char in song_name for char in "台語閩南語"):
                                            language = "台"
                                        elif any(char in song_name for char in "英文English"):
                                            language = "英"
                                        
                                        company_entries.append({
                                            'song_name': song_name,
                                            'singer': singer_name,
                                            'company': company,
                                            'number': number,
                                            'language': language
                                        })
                                        
                                except Exception as e:
                                    self.logger.debug(f"解析歌曲連結失敗: {e}")
                                    continue
                        
                        return company_entries
                    else:
                        self.logger.debug(f"{company} 搜索失敗: {response.status_code}")
                        return []
                        
                except Exception as e:
                    self.logger.debug(f"搜索 {company} 失敗: {e}")
                    return []
            
            # 並行搜索所有KTV公司
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_company = {
                    executor.submit(search_company, company): company 
                    for company in self.companies_to_check
                }
                
                for future in as_completed(future_to_company):
                    company = future_to_company[future]
                    try:
                        company_entries = future.result(timeout=30)
                        all_ktv_entries.extend(company_entries)
                        
                        if company_entries:
                            self.logger.info(f"   {company}: {len(company_entries)} 首歌")
                        
                    except Exception as e:
                        self.logger.warning(f"處理 {company} 結果失敗: {e}")
            
            # 統計總數
            total_ktv_entries = len(all_ktv_entries)
            companies_count = len(companies_found)
            unique_songs = len(set(entry['song_name'] for entry in all_ktv_entries))
            
            self.logger.info(f"🎵 {singer_name} 台灣點歌網統計:")
            self.logger.info(f"   KTV編號總數: {total_ktv_entries}")
            self.logger.info(f"   涵蓋KTV公司: {companies_count}")
            self.logger.info(f"   獨特歌曲數: {unique_songs}")
            
            return {
                'singer_name': singer_name,
                'total_ktv_entries': total_ktv_entries,
                'companies_count': companies_count,
                'unique_songs': unique_songs,
                'ktv_entries': all_ktv_entries,
                'search_successful': True
            }
            
        except Exception as e:
            self.logger.error(f"查詢 {singer_name} 失敗: {e}")
            return {
                'singer_name': singer_name,
                'total_ktv_entries': 0,
                'companies_count': 0,
                'unique_songs': 0,
                'ktv_entries': [],
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
    
    def check_needs_scraping(self, singer_name, threshold_percentage=0.05):
        """檢查歌手是否需要爬取資料（基於5%差異閾值）"""
        try:
            self.logger.info(f"🎯 檢查 {singer_name} 是否需要爬取...")
            
            # 獲取台灣點歌網數據
            website_data = self.get_singer_ktv_count_from_website(singer_name)
            
            if not website_data['search_successful']:
                self.logger.warning(f"台灣點歌網查詢失敗，跳過 {singer_name}")
                return {
                    'needs_scraping': False,
                    'reason': 'website_query_failed',
                    'website_data': website_data,
                    'our_data': None
                }
            
            # 獲取我們資料庫的數據
            our_data = self.get_our_database_ktv_count(singer_name)
            
            website_count = website_data['total_ktv_entries']
            our_count = our_data['total_ktv_entries']
            
            # 如果台灣點歌網沒有資料，不需要爬取
            if website_count == 0:
                return {
                    'needs_scraping': False,
                    'reason': 'no_data_on_website',
                    'website_data': website_data,
                    'our_data': our_data
                }
            
            # 計算差異百分比
            if website_count > 0:
                coverage_ratio = our_count / website_count
                difference_percentage = abs(1 - coverage_ratio)
                
                # 如果我們的數量比台灣點歌網少超過5%，就需要爬取
                needs_scraping = coverage_ratio < (1 - threshold_percentage)
                
                result = {
                    'needs_scraping': needs_scraping,
                    'reason': 'difference_threshold_check',
                    'website_count': website_count,
                    'our_count': our_count,
                    'coverage_ratio': coverage_ratio,
                    'difference_percentage': difference_percentage,
                    'threshold': threshold_percentage,
                    'website_data': website_data,
                    'our_data': our_data
                }
                
                if needs_scraping:
                    self.logger.info(f"✅ {singer_name} 需要爬取: 我們{our_count} vs 網站{website_count} (覆蓋率{coverage_ratio:.1%})")
                else:
                    self.logger.info(f"⏭️ {singer_name} 無需爬取: 我們{our_count} vs 網站{website_count} (覆蓋率{coverage_ratio:.1%})")
                
                return result
            
        except Exception as e:
            self.logger.error(f"檢查 {singer_name} 失敗: {e}")
            return {
                'needs_scraping': False,
                'reason': 'check_failed',
                'error': str(e)
            }
    
    def find_missing_ktv_entries(self, singer_name):
        """找出我們資料庫中缺少的KTV編號"""
        try:
            # 獲取台灣點歌網的完整KTV編號清單
            website_data = self.get_singer_ktv_count_from_website(singer_name)
            
            if not website_data['search_successful']:
                return []
            
            # 獲取我們資料庫的KTV編號
            our_data = self.get_our_database_ktv_count(singer_name)
            
            # 建立我們資料庫中的編號集合
            our_entries = set()
            
            try:
                with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                    singers_data = json.load(f)
                
                if singer_name in singers_data:
                    songs = singers_data[singer_name].get('歌曲清單', [])
                    
                    for song in songs:
                        for entry in song.get('編號資訊', []):
                            company = entry.get('公司', '')
                            number = entry.get('編號', '')
                            if company and number:
                                our_entries.add(f"{company}:{number}")
            
            except Exception as e:
                self.logger.error(f"讀取資料庫失敗: {e}")
            
            # 找出缺少的編號
            missing_entries = []
            
            for entry in website_data['ktv_entries']:
                company = entry['company']
                number = entry['number']
                entry_key = f"{company}:{number}"
                
                if entry_key not in our_entries:
                    missing_entries.append(entry)
            
            self.logger.info(f"🔍 {singer_name} 缺少的KTV編號: {len(missing_entries)} 筆")
            
            return missing_entries
            
        except Exception as e:
            self.logger.error(f"查找缺少編號失敗: {e}")
            return []

def test_comparator():
    """測試比較器功能"""
    comparator = TaiwanKTVComparator()
    
    # 設置日誌
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 測試幾個歌手
    test_singers = ["周杰倫", "蔡依林", "盧廣仲"]
    
    for singer in test_singers:
        print(f"\n{'='*60}")
        print(f"測試歌手: {singer}")
        print(f"{'='*60}")
        
        result = comparator.check_needs_scraping(singer)
        
        print(f"結果: {'需要爬取' if result['needs_scraping'] else '無需爬取'}")
        print(f"原因: {result['reason']}")
        
        if 'website_count' in result:
            print(f"台灣點歌網: {result['website_count']} 筆")
            print(f"我們資料庫: {result['our_count']} 筆")
            print(f"覆蓋率: {result['coverage_ratio']:.1%}")
        
        # 短暫延遲避免請求過於頻繁
        time.sleep(random.uniform(2, 4))

if __name__ == "__main__":
    test_comparator()