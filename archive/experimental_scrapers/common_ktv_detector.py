#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
常用KTV公司檢測器
檢測適合一般消費者的中小型KTV公司數據規模
避開大型連鎖（錢櫃、好樂迪、銀櫃、星聚點）
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

class CommonKTVDetector:
    def __init__(self):
        # 常見的中小型KTV公司（避開大型連鎖）
        self.companies = [
            "弘音", "金嗓", "音圓原廠", "瑞影", 
            "點將家", "嘉揚", "音遊", "音影", 
            "美華", "金影", "金嗓/投幣", "一級棒",
            "享溫馨", "大唐", "MV", "金嗓/家庭"
        ]
        
        print("🎤 常用KTV公司數據規模檢測器")
        print("🎯 針對一般消費者常用的中小型KTV業者")
        print(f"📋 檢測公司: {', '.join(self.companies[:8])}...")
        if len(self.companies) > 8:
            print(f"           {', '.join(self.companies[8:])}")
        print("=" * 60)
    
    def quick_detect_company(self, company):
        """快速檢測單一公司的數據規模（使用採樣點檢測）"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        print(f"\n🔍 檢測 {company}...")
        
        # 使用採樣點快速檢測（減少請求次數）
        test_pages = [1, 50, 100, 500, 1000, 2000, 5000, 8000, 10000, 15000, 20000]
        last_valid = 0
        sample_songs = []
        
        for page in test_pages:
            try:
                url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
                print(f"   測試第{page}頁...", end="", flush=True)
                
                response = session.get(url, timeout=10)
                response.encoding = "utf-8"
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    song_links = soup.select('a[href^="mv.aspx?id="]')
                    
                    if len(song_links) > 0:
                        last_valid = page
                        print(f" ✅ ({len(song_links)}首)")
                        
                        # 收集樣本歌曲（前幾頁）
                        if page <= 100 and len(sample_songs) < 10:
                            for link in song_links[:3]:  # 每頁取3首作樣本
                                try:
                                    link_text = link.get_text().strip()
                                    parts = link_text.split()
                                    
                                    if len(parts) >= 4:
                                        song_info = {
                                            '編號': parts[0],
                                            '歌名': parts[1],
                                            '期別': parts[2],
                                            '歌手': ' '.join(parts[3:])
                                        }
                                        sample_songs.append(song_info)
                                except:
                                    continue
                    else:
                        print(f" ❌ (無數據)")
                        break
                else:
                    print(f" ❌ (HTTP {response.status_code})")
                    break
                
                time.sleep(random.uniform(0.5, 1.0))  # 較短延遲
                
            except Exception as e:
                print(f" ❌ (錯誤: {str(e)[:30]})")
                time.sleep(1)
                break
        
        # 如果找到有效頁面且較大，進行更精確搜尋
        if last_valid >= 10000:
            print(f"   {company} 數據量較大，進行精確搜尋...")
            # 簡單的二分搜尋
            low = last_valid
            high = min(last_valid * 2, 50000)
            
            for _ in range(5):  # 最多5次精確搜尋
                mid = (low + high) // 2
                try:
                    url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={mid}"
                    response = session.get(url, timeout=10)
                    response.encoding = "utf-8"
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        song_links = soup.select('a[href^="mv.aspx?id="]')
                        
                        if len(song_links) > 0:
                            last_valid = mid
                            low = mid + 1
                        else:
                            high = mid - 1
                    else:
                        high = mid - 1
                        
                    time.sleep(1)
                except:
                    break
        
        session.close()
        
        # 統計結果
        estimated_songs = last_valid * 50 if last_valid > 0 else 0
        
        result = {
            'company': company,
            'max_page': last_valid,
            'estimated_songs': estimated_songs,
            'sample_songs': sample_songs,
            'category': self.categorize_by_size(estimated_songs)
        }
        
        print(f"✅ {company} 完成:")
        print(f"   最大頁數: {last_valid:,} 頁")
        print(f"   預估歌曲: {estimated_songs:,} 首")
        print(f"   規模分類: {result['category']}")
        
        if sample_songs:
            print(f"   樣本歌曲: {sample_songs[0]['歌名']} - {sample_songs[0]['歌手']}")
        
        return result
    
    def categorize_by_size(self, songs):
        """根據歌曲數量分類"""
        if songs == 0:
            return "無數據"
        elif songs < 10000:
            return "小型(<1萬首)"
        elif songs < 50000:
            return "中小型(1-5萬首)"
        elif songs < 200000:
            return "中型(5-20萬首)"
        elif songs < 500000:
            return "大型(20-50萬首)"
        else:
            return "超大型(>50萬首)"
    
    def estimate_scraping_time(self, songs):
        """估算爬取時間（基於音圓實際表現）"""
        if songs == 0:
            return "0分鐘"
        
        songs_per_hour = 74413  # 基於音圓實際表現
        hours = songs / songs_per_hour
        
        if hours < 1:
            return f"{hours * 60:.0f}分鐘"
        elif hours < 24:
            return f"{hours:.1f}小時"
        else:
            days = hours / 24
            return f"{days:.1f}天"
    
    def detect_all_companies(self):
        """檢測所有公司"""
        start_time = datetime.now()
        results = []
        
        print("🚀 開始檢測常用KTV公司...")
        
        # 並行檢測（較少線程避免過載）
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_company = {
                executor.submit(self.quick_detect_company, company): company
                for company in self.companies
            }
            
            for future in as_completed(future_to_company):
                company = future_to_company[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"❌ {company} 檢測失敗: {e}")
                    results.append({
                        'company': company,
                        'max_page': 0,
                        'estimated_songs': 0,
                        'category': '檢測失敗',
                        'error': str(e)
                    })
        
        # 生成分析報告
        self.generate_analysis_report(results, start_time)
        
        return results
    
    def generate_analysis_report(self, results, start_time):
        """生成詳細分析報告"""
        elapsed = datetime.now() - start_time
        
        print(f"\n" + "=" * 70)
        print("📊 常用KTV公司數據分析報告")
        print("=" * 70)
        
        # 按規模分類
        categories = {}
        successful_results = [r for r in results if 'error' not in r and r['estimated_songs'] > 0]
        
        for result in successful_results:
            category = result['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # 按歌曲數量排序
        successful_results.sort(key=lambda x: x['estimated_songs'], reverse=True)
        
        print(f"{'公司':<12} {'頁數':<10} {'歌曲數':<12} {'規模':<15} {'預估時間':<10}")
        print("-" * 70)
        
        total_songs = 0
        suitable_companies = []  # 適合爬取的公司
        
        for result in successful_results:
            company = result['company']
            pages = result['max_page']
            songs = result['estimated_songs']
            category = result['category']
            time_est = self.estimate_scraping_time(songs)
            
            print(f"{company:<12} {pages:,}頁{'':<4} {songs:,}首{'':<6} {category:<15} {time_est}")
            
            total_songs += songs
            
            # 標記適合爬取的公司（中小型和中型）
            if 1000 <= songs <= 200000:  # 1000首到20萬首之間
                suitable_companies.append(result)
        
        # 失敗的公司
        failed_results = [r for r in results if 'error' in r or r['estimated_songs'] == 0]
        if failed_results:
            print(f"\n❌ 無數據或檢測失敗:")
            for result in failed_results:
                reason = result.get('error', '無數據')
                print(f"   {result['company']}: {reason[:50]}")
        
        print("-" * 70)
        print(f"檢測成功: {len(successful_results)}/{len(self.companies)} 家公司")
        print(f"總預估歌曲: {total_songs:,} 首")
        print(f"檢測耗時: {elapsed}")
        
        # 推薦爬取策略
        print(f"\n💡 推薦爬取策略:")
        
        if suitable_companies:
            suitable_companies.sort(key=lambda x: x['estimated_songs'])
            total_suitable = sum(r['estimated_songs'] for r in suitable_companies)
            total_time = self.estimate_scraping_time(total_suitable)
            
            print(f"📋 建議優先爬取 ({len(suitable_companies)} 家公司):")
            for result in suitable_companies:
                time_est = self.estimate_scraping_time(result['estimated_songs'])
                print(f"   {result['company']}: {result['estimated_songs']:,} 首 ({time_est})")
            
            print(f"\n⏰ 建議公司總計: {total_suitable:,} 首歌，預估 {total_time}")
            
            if total_suitable < 100000:  # 少於10萬首
                print("   ✅ 數據量適中，可以並行爬取")
            elif total_suitable < 300000:  # 10-30萬首
                print("   ⚠️ 數據量較大，建議分批執行")
            else:
                print("   🚨 數據量很大，強烈建議分階段執行")
        
        # 與音圓對比
        yinyuan_songs = 44100
        print(f"\n📈 與音圓 ({yinyuan_songs:,} 首) 對比:")
        for result in successful_results[:5]:  # 顯示前5大
            songs = result['estimated_songs']
            if songs > 0:
                ratio = (songs / yinyuan_songs) * 100
                print(f"   {result['company']}: {ratio:.0f}% ({songs:,} 首)")

def main():
    detector = CommonKTVDetector()
    
    try:
        results = detector.detect_all_companies()
        
        # 提取適合的公司
        suitable = [r for r in results if 1000 <= r.get('estimated_songs', 0) <= 200000]
        
        if suitable:
            print(f"\n🎯 接下來建議:")
            print(f"   1. 優先爬取適中規模的 {len(suitable)} 家公司")
            print(f"   2. 執行: python suitable_ktv_scraper.py")
            print(f"   3. 完成後再考慮是否處理大型公司")
        else:
            print(f"\n⚠️ 未找到合適規模的公司，可能需要調整策略")
        
    except Exception as e:
        print(f"❌ 檢測過程出錯: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()