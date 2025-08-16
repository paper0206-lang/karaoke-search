#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
數據品質檢查器
檢查不同KTV公司間的數據重複情況和品質
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
from urllib.parse import quote

class DataQualityChecker:
    def __init__(self):
        # 選擇幾家代表性公司進行深入分析
        self.test_companies = ["音圓", "弘音", "金嗓", "瑞影"]
        
        print("🔍 KTV公司數據品質檢查器")
        print("🎯 檢查數據重複情況和真實性")
        print(f"📋 測試公司: {', '.join(self.test_companies)}")
        print("=" * 50)
    
    def sample_company_data(self, company, pages_to_check=None):
        """採樣單一公司的數據"""
        if pages_to_check is None:
            pages_to_check = [1, 10, 100, 1000, 5000, 10000]
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        print(f"\n🔍 採樣 {company} 數據...")
        
        company_data = {
            'company': company,
            'pages_checked': [],
            'songs': [],
            'unique_songs': set(),
            'unique_singers': set(),
            'song_codes': set(),
        }
        
        for page in pages_to_check:
            try:
                url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
                print(f"   第{page}頁...", end="", flush=True)
                
                response = session.get(url, timeout=10)
                response.encoding = "utf-8"
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    song_links = soup.select('a[href^="mv.aspx?id="]')
                    
                    if song_links:
                        page_songs = []
                        for link in song_links:
                            try:
                                link_text = link.get_text().strip()
                                parts = link_text.split()
                                
                                if len(parts) >= 4:
                                    song_info = {
                                        'code': parts[0],
                                        'title': parts[1],
                                        'period': parts[2],
                                        'singer': ' '.join(parts[3:]),
                                        'page': page
                                    }
                                    page_songs.append(song_info)
                                    
                                    # 收集統計信息
                                    company_data['unique_songs'].add(f"{parts[1]}_{' '.join(parts[3:])}")
                                    company_data['unique_singers'].add(' '.join(parts[3:]))
                                    company_data['song_codes'].add(parts[0])
                                    
                            except Exception as e:
                                continue
                        
                        company_data['pages_checked'].append(page)
                        company_data['songs'].extend(page_songs)
                        print(f" ✅ ({len(page_songs)}首)")
                        
                    else:
                        print(f" ❌ (無數據)")
                        break
                else:
                    print(f" ❌ (HTTP {response.status_code})")
                    
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f" ❌ (錯誤: {str(e)[:30]})")
        
        session.close()
        
        print(f"   ✅ {company} 採樣完成:")
        print(f"      檢查頁面: {len(company_data['pages_checked'])} 頁")
        print(f"      收集歌曲: {len(company_data['songs'])} 首")
        print(f"      獨特歌曲: {len(company_data['unique_songs'])} 首")
        print(f"      獨特歌手: {len(company_data['unique_singers'])} 位")
        print(f"      歌曲編號: {len(company_data['song_codes'])} 個")
        
        return company_data
    
    def analyze_data_overlap(self, companies_data):
        """分析公司間數據重疊情況"""
        print(f"\n📊 數據重疊分析:")
        print("=" * 60)
        
        # 收集所有數據
        all_songs = set()
        all_singers = set()
        all_codes = set()
        
        for data in companies_data:
            all_songs.update(data['unique_songs'])
            all_singers.update(data['unique_singers'])
            all_codes.update(data['song_codes'])
        
        print(f"所有公司合計:")
        print(f"   總獨特歌曲: {len(all_songs)} 首")
        print(f"   總獨特歌手: {len(all_singers)} 位")
        print(f"   總歌曲編號: {len(all_codes)} 個")
        
        # 分析重疊
        print(f"\n🔄 公司間重疊分析:")
        
        for i, data1 in enumerate(companies_data):
            for j, data2 in enumerate(companies_data):
                if i < j:
                    company1 = data1['company']
                    company2 = data2['company']
                    
                    songs1 = data1['unique_songs']
                    songs2 = data2['unique_songs']
                    
                    overlap = songs1.intersection(songs2)
                    overlap_rate = len(overlap) / max(len(songs1), len(songs2)) * 100
                    
                    print(f"   {company1} vs {company2}: {len(overlap)} 首重疊 ({overlap_rate:.1f}%)")
        
        # 分析編號格式
        print(f"\n🏷️ 歌曲編號格式分析:")
        code_patterns = {}
        
        for data in companies_data:
            company = data['company']
            codes = list(data['song_codes'])[:10]  # 取前10個編號分析
            
            patterns = []
            for code in codes:
                if code.isdigit():
                    patterns.append("純數字")
                elif any(c.isalpha() for c in code) and any(c.isdigit() for c in code):
                    patterns.append("字母數字混合")
                else:
                    patterns.append("其他格式")
            
            most_common = max(set(patterns), key=patterns.count) if patterns else "無"
            code_patterns[company] = most_common
            
            print(f"   {company}: {most_common} (樣本: {', '.join(codes[:3])})")
    
    def check_data_authenticity(self, companies_data):
        """檢查數據真實性"""
        print(f"\n🔍 數據真實性檢查:")
        print("=" * 60)
        
        for data in companies_data:
            company = data['company']
            songs = data['songs']
            
            if not songs:
                print(f"{company}: 無數據")
                continue
            
            # 分析歌曲時期分布
            periods = [song['period'] for song in songs if song['period']]
            period_counts = {}
            
            for period in periods:
                period_counts[period] = period_counts.get(period, 0) + 1
            
            # 分析重複歌曲
            song_titles = [song['title'] for song in songs]
            duplicate_titles = {}
            
            for title in song_titles:
                duplicate_titles[title] = duplicate_titles.get(title, 0) + 1
            
            duplicates = {k: v for k, v in duplicate_titles.items() if v > 1}
            
            print(f"{company}:")
            print(f"   時期分布: {len(period_counts)} 個不同期別")
            if period_counts:
                top_periods = sorted(period_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"   主要期別: {', '.join([f'{p}({c}首)' for p, c in top_periods])}")
            
            print(f"   重複歌名: {len(duplicates)} 個 ({len(duplicates)/len(song_titles)*100:.1f}%)")
            
            if duplicates:
                top_duplicates = sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"   重複最多: {', '.join([f'{t}({c}次)' for t, c in top_duplicates])}")
    
    def run_quality_check(self):
        """執行完整品質檢查"""
        print("🚀 開始數據品質檢查...")
        
        companies_data = []
        
        # 採樣各公司數據
        for company in self.test_companies:
            data = self.sample_company_data(company)
            companies_data.append(data)
        
        # 執行各項分析
        self.analyze_data_overlap(companies_data)
        self.check_data_authenticity(companies_data)
        
        # 生成結論和建議
        self.generate_recommendations(companies_data)
        
        return companies_data
    
    def generate_recommendations(self, companies_data):
        """生成建議"""
        print(f"\n💡 結論和建議:")
        print("=" * 60)
        
        # 計算平均重疊率
        total_songs = sum(len(data['unique_songs']) for data in companies_data)
        total_unique = len(set().union(*[data['unique_songs'] for data in companies_data]))
        
        if total_songs > 0:
            duplicate_rate = (total_songs - total_unique) / total_songs * 100
            print(f"📈 總體重複率: {duplicate_rate:.1f}%")
            
            if duplicate_rate > 80:
                print("🚨 發現極高重複率！")
                print("   建議: 只爬取1-2家代表性公司")
                print("   原因: 公司間數據高度重複，完整爬取意義不大")
                
            elif duplicate_rate > 50:
                print("⚠️ 發現較高重複率")
                print("   建議: 選擇3-4家公司，避免重複爬取")
                print("   策略: 先爬取數據品質最好的公司")
                
            elif duplicate_rate > 20:
                print("✅ 重複率在合理範圍內")
                print("   建議: 可以爬取多家公司")
                print("   策略: 實施去重處理")
                
            else:
                print("🎯 各公司數據相對獨立")
                print("   建議: 爬取所有公司以獲得最完整數據")
        
        # 推薦爬取順序
        if companies_data:
            print(f"\n📋 推薦爬取順序:")
            # 按獨特歌曲數排序
            sorted_companies = sorted(companies_data, key=lambda x: len(x['unique_songs']), reverse=True)
            
            for i, data in enumerate(sorted_companies, 1):
                company = data['company']
                unique_count = len(data['unique_songs'])
                print(f"   {i}. {company} ({unique_count} 首獨特歌曲)")

def main():
    checker = DataQualityChecker()
    
    try:
        results = checker.run_quality_check()
        
        print(f"\n🎯 接下來:")
        print(f"   1. 根據分析結果調整爬取策略")
        print(f"   2. 優先爬取數據品質最好的公司")
        print(f"   3. 考慮實施去重機制")
        
    except Exception as e:
        print(f"❌ 檢查過程出錯: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()