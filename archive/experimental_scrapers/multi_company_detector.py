#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多公司數據規模檢測器
快速檢測錢櫃、好樂迪、銀櫃的數據規模
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

class MultiCompanyDetector:
    def __init__(self):
        # 目標公司
        self.companies = ["錢櫃", "好樂迪", "銀櫃"]
        
        print("🎤 多公司數據規模檢測器")
        print(f"🎯 目標公司: {', '.join(self.companies)}")
        print("=" * 50)
    
    def detect_company_scale(self, company):
        """檢測單一公司的數據規模"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        print(f"\n🔍 檢測 {company}...")
        
        # 使用二分搜索法快速找到最大頁數
        low = 1
        high = 50000  # 設置較高上限
        last_valid = 0
        max_checks = 15  # 限制檢查次數避免過久
        checks = 0
        
        while low <= high and checks < max_checks:
            mid = (low + high) // 2
            checks += 1
            
            try:
                url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={mid}"
                print(f"   檢測第{mid}頁...", end="", flush=True)
                
                response = session.get(url, timeout=10)
                response.encoding = "utf-8"
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    song_links = soup.select('a[href^="mv.aspx?id="]')
                    
                    if len(song_links) > 0:
                        last_valid = mid
                        low = mid + 1
                        print(f" ✅ ({len(song_links)}首)")
                    else:
                        high = mid - 1
                        print(f" ❌ (無數據)")
                else:
                    high = mid - 1
                    print(f" ❌ (HTTP {response.status_code})")
                
                time.sleep(random.uniform(0.8, 1.5))
                
            except Exception as e:
                print(f" ❌ (錯誤: {e})")
                high = mid - 1
                time.sleep(2)
        
        session.close()
        
        # 結果統計
        total_songs = last_valid * 50 if last_valid > 0 else 0
        
        result = {
            'company': company,
            'max_page': last_valid,
            'estimated_songs': total_songs,
            'checks_performed': checks
        }
        
        print(f"✅ {company} 檢測完成:")
        print(f"   最大頁數: {last_valid:,} 頁")
        print(f"   預估歌曲: {total_songs:,} 首")
        print(f"   檢查次數: {checks} 次")
        
        return result
    
    def estimate_scraping_time(self, songs_count):
        """估算爬取時間"""
        # 基於音圓的實際表現：74,413 首歌/小時
        songs_per_hour = 74413
        hours = songs_count / songs_per_hour
        
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
        
        print("🚀 開始並行檢測...")
        
        # 並行檢測以提高速度
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_company = {
                executor.submit(self.detect_company_scale, company): company
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
                        'error': str(e)
                    })
        
        # 生成總結報告
        self.generate_summary_report(results, start_time)
        
        return results
    
    def generate_summary_report(self, results, start_time):
        """生成總結報告"""
        elapsed = datetime.now() - start_time
        
        print(f"\n" + "=" * 60)
        print("📊 多公司數據規模檢測報告")
        print("=" * 60)
        
        # 排序結果（按歌曲數量）
        successful_results = [r for r in results if 'error' not in r and r['estimated_songs'] > 0]
        successful_results.sort(key=lambda x: x['estimated_songs'], reverse=True)
        
        print(f"{'公司':<10} {'最大頁數':<12} {'預估歌曲':<14} {'爬取時間':<12}")
        print("-" * 60)
        
        total_songs = 0
        total_pages = 0
        
        for result in successful_results:
            company = result['company']
            pages = result['max_page']
            songs = result['estimated_songs']
            time_est = self.estimate_scraping_time(songs)
            
            print(f"{company:<10} {pages:,}頁{'':<6} {songs:,}首{'':<8} {time_est}")
            
            total_songs += songs
            total_pages += pages
        
        # 失敗的公司
        failed_results = [r for r in results if 'error' in r or r['estimated_songs'] == 0]
        if failed_results:
            print(f"\n❌ 檢測失敗或無數據:")
            for result in failed_results:
                error = result.get('error', '無數據')
                print(f"   {result['company']}: {error}")
        
        print("-" * 60)
        print(f"{'總計':<10} {total_pages:,}頁{'':<6} {total_songs:,}首")
        
        if total_songs > 0:
            total_time_est = self.estimate_scraping_time(total_songs)
            print(f"\n⏰ 預估總爬取時間: {total_time_est}")
            print(f"🔍 檢測耗時: {elapsed}")
        
        # 推薦策略
        print(f"\n💡 推薦爬取策略:")
        if total_songs > 200000:  # 超過20萬首
            print("   - 數據量較大，建議分批執行")
            print("   - 優先爬取數據量適中的公司")
            print("   - 考慮使用更保守的延遲設置")
        elif total_songs > 50000:  # 5-20萬首
            print("   - 數據量適中，可並行爬取")
            print("   - 建議3-5公司並行處理")
        else:
            print("   - 數據量較小，可快速完成")
        
        # 與音圓比較
        yinyuan_songs = 44100
        print(f"\n📈 與音圓數據對比:")
        print(f"   音圓已完成: {yinyuan_songs:,} 首")
        for result in successful_results[:3]:  # 顯示前3大
            company = result['company']
            songs = result['estimated_songs']
            if songs > 0:
                ratio = (songs / yinyuan_songs) * 100
                print(f"   {company}: {songs:,} 首 (音圓的 {ratio:.0f}%)")

def main():
    detector = MultiCompanyDetector()
    
    try:
        results = detector.detect_all_companies()
        
        print(f"\n🚀 接下來可以:")
        print(f"   1. python multi_company_scraper.py  # 啟動多公司爬蟲")
        print(f"   2. 根據數據量調整爬取策略")
        
    except Exception as e:
        print(f"❌ 檢測過程出錯: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()