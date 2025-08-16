#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精選策略爬蟲
針對代表性KTV公司進行小範圍高效數據收集
避免重複數據，專注於獲取有價值的內容
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

class SelectiveScraper:
    def __init__(self):
        # 精選代表性公司（基於數據品質分析）
        self.companies = {
            "弘音": {"max_pages": 2000, "priority": 1, "description": "老牌音響公司"},
            "金嗓": {"max_pages": 2000, "priority": 2, "description": "知名KTV設備商"},
            "瑞影": {"max_pages": 1500, "priority": 3, "description": "中型KTV業者"},
            "點將家": {"max_pages": 1000, "priority": 4, "description": "地方KTV連鎖"}
        }
        
        # 建立輸出目錄
        os.makedirs("selective_results", exist_ok=True)
        
        # 統計數據
        self.stats = {
            'companies_completed': 0,
            'total_songs': 0,
            'unique_songs': set(),
            'start_time': datetime.now()
        }
        self.stats_lock = threading.Lock()
        
        print("🎯 精選策略KTV爬蟲")
        print(f"📋 目標公司: {len(self.companies)} 家")
        print("🎪 策略: 小範圍高品質數據收集")
        print("=" * 50)
        
        for company, info in self.companies.items():
            print(f"   {company}: {info['max_pages']:,} 頁 ({info['description']})")
    
    def detect_actual_page_limit(self, company):
        """檢測公司的實際有效頁數"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        print(f"\n🔍 檢測 {company} 的實際頁面範圍...")
        
        # 檢查關鍵頁面以確定實際範圍
        test_pages = [1, 100, 500, 1000, 2000, 3000, 5000]
        valid_pages = []
        songs_per_page = []
        
        for page in test_pages:
            try:
                url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
                response = session.get(url, timeout=10)
                response.encoding = "utf-8"
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    song_links = soup.select('a[href^="mv.aspx?id="]')
                    
                    if song_links:
                        valid_pages.append(page)
                        songs_per_page.append(len(song_links))
                        print(f"   第{page}頁: ✅ {len(song_links)}首")
                        
                        # 檢查是否有重複內容（比較前3首歌）
                        if len(valid_pages) > 1:
                            current_songs = [link.get_text().strip()[:20] for link in song_links[:3]]
                            # 如果當前頁面歌曲與第1頁相同，可能遇到循環
                            if page > 100 and self.check_content_similarity(company, 1, page, session):
                                print(f"   ⚠️ 第{page}頁與前面頁面內容重複，可能到達循環點")
                                break
                    else:
                        print(f"   第{page}頁: ❌ 無數據")
                        break
                else:
                    print(f"   第{page}頁: ❌ HTTP {response.status_code}")
                    
                time.sleep(random.uniform(0.5, 1.0))
                
            except Exception as e:
                print(f"   第{page}頁: ❌ 錯誤: {str(e)[:30]}")
                break
        
        session.close()
        
        if valid_pages:
            actual_limit = max(valid_pages)
            avg_songs = sum(songs_per_page) / len(songs_per_page) if songs_per_page else 50
            estimated_total = actual_limit * avg_songs
            
            print(f"   ✅ {company} 實際範圍: 1-{actual_limit}頁 (預估{estimated_total:,.0f}首)")
            return actual_limit
        else:
            print(f"   ❌ {company} 無有效數據")
            return 0
    
    def check_content_similarity(self, company, page1, page2, session):
        """檢查兩個頁面的內容相似性"""
        try:
            urls = [
                f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page1}",
                f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page2}"
            ]
            
            contents = []
            for url in urls:
                response = session.get(url, timeout=10)
                response.encoding = "utf-8"
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    song_links = soup.select('a[href^="mv.aspx?id="]')
                    song_texts = [link.get_text().strip()[:30] for link in song_links[:5]]
                    contents.append(song_texts)
                else:
                    return False
                    
                time.sleep(0.5)
            
            # 檢查相似性
            if len(contents) == 2:
                intersection = set(contents[0]).intersection(set(contents[1]))
                similarity = len(intersection) / max(len(contents[0]), len(contents[1])) if contents[0] or contents[1] else 0
                return similarity > 0.8  # 80%以上相似認為重複
                
        except:
            pass
        
        return False
    
    def scrape_company(self, company, max_pages):
        """爬取單一公司數據"""
        print(f"\n🚀 開始爬取 {company} (上限 {max_pages} 頁)...")
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        all_songs = []
        unique_songs = set()
        pages_scraped = 0
        consecutive_empty = 0
        
        for page in range(1, max_pages + 1):
            try:
                # 智能延遲
                delay = random.uniform(1.5, 3.0)
                time.sleep(delay)
                
                url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
                response = session.get(url, timeout=10)
                response.encoding = "utf-8"
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    song_links = soup.select('a[href^="mv.aspx?id="]')
                    
                    if song_links:
                        consecutive_empty = 0
                        page_songs = []
                        new_songs = 0
                        
                        for link in song_links:
                            try:
                                link_text = link.get_text().strip()
                                parts = link_text.split()
                                
                                if len(parts) >= 4:
                                    song_key = f"{parts[1]}_{' '.join(parts[3:])}"
                                    
                                    song_data = {
                                        'company': company,
                                        'code': parts[0],
                                        'title': parts[1],
                                        'period': parts[2],
                                        'singer': ' '.join(parts[3:]),
                                        'page': page,
                                        'scraped_at': datetime.now().isoformat()
                                    }
                                    
                                    page_songs.append(song_data)
                                    
                                    # 檢查是否為新歌曲
                                    if song_key not in unique_songs:
                                        unique_songs.add(song_key)
                                        new_songs += 1
                                        
                            except:
                                continue
                        
                        all_songs.extend(page_songs)
                        pages_scraped += 1
                        
                        if page % 10 == 0 or new_songs == 0:
                            print(f"   第{page:4d}頁: {len(page_songs):2d}首歌 ({new_songs:2d}首新歌)")
                        
                        # 如果連續多頁沒有新歌，可能遇到重複循環
                        if new_songs == 0:
                            consecutive_empty += 1
                            if consecutive_empty >= 5:
                                print(f"   ⚠️ 連續{consecutive_empty}頁無新歌，停止爬取")
                                break
                        
                    else:
                        consecutive_empty += 1
                        print(f"   第{page}頁: 無數據 (連續{consecutive_empty}次)")
                        
                        if consecutive_empty >= 3:
                            print(f"   ✅ 到達數據終點，停止爬取")
                            break
                            
                else:
                    print(f"   第{page}頁: HTTP錯誤 {response.status_code}")
                    consecutive_empty += 1
                    
                    if consecutive_empty >= 3:
                        break
                    
            except Exception as e:
                print(f"   第{page}頁: 錯誤 - {str(e)[:50]}")
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    break
                time.sleep(2)
        
        session.close()
        
        # 保存公司數據
        company_file = f"selective_results/{company}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(company_file, 'w', encoding='utf-8') as f:
                json.dump(all_songs, f, ensure_ascii=False, indent=2)
            
            print(f"✅ {company} 完成:")
            print(f"   爬取頁面: {pages_scraped} 頁")
            print(f"   收集歌曲: {len(all_songs)} 首")
            print(f"   獨特歌曲: {len(unique_songs)} 首")
            print(f"   保存文件: {company_file}")
            
            # 更新統計
            with self.stats_lock:
                self.stats['companies_completed'] += 1
                self.stats['total_songs'] += len(all_songs)
                self.stats['unique_songs'].update(unique_songs)
            
            return {
                'company': company,
                'pages_scraped': pages_scraped,
                'total_songs': len(all_songs),
                'unique_songs': len(unique_songs),
                'file_path': company_file
            }
            
        except Exception as e:
            print(f"❌ {company} 保存失敗: {e}")
            return None
    
    def run_selective_scraping(self):
        """執行精選爬取"""
        print(f"\n🚀 開始精選爬取...")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = []
        
        # 按優先級順序執行
        sorted_companies = sorted(self.companies.items(), key=lambda x: x[1]['priority'])
        
        for company, info in sorted_companies:
            print(f"\n{'='*60}")
            print(f"🎯 處理 {company} (優先級 {info['priority']})")
            
            # 檢測實際範圍
            actual_limit = self.detect_actual_page_limit(company)
            
            if actual_limit > 0:
                # 使用較小的數值避免浪費時間
                scrape_limit = min(info['max_pages'], actual_limit, 1000)  # 最多1000頁
                
                result = self.scrape_company(company, scrape_limit)
                if result:
                    results.append(result)
            else:
                print(f"❌ {company} 跳過（無有效數據）")
        
        # 生成總結報告
        self.generate_final_report(results)
        
        return results
    
    def generate_final_report(self, results):
        """生成最終報告"""
        elapsed = datetime.now() - self.stats['start_time']
        
        print(f"\n" + "="*70)
        print("🎊 精選爬取完成報告")
        print("="*70)
        
        total_songs = 0
        total_pages = 0
        all_unique_songs = set()
        
        print(f"{'公司':<10} {'頁數':<8} {'總歌曲':<10} {'獨特歌曲':<10} {'效率':<8}")
        print("-" * 60)
        
        for result in results:
            company = result['company']
            pages = result['pages_scraped']
            songs = result['total_songs']
            unique = result['unique_songs']
            efficiency = f"{unique/pages:.1f}" if pages > 0 else "0"
            
            print(f"{company:<10} {pages:<8} {songs:<10} {unique:<10} {efficiency}首/頁")
            
            total_songs += songs
            total_pages += pages
            all_unique_songs.add(unique)  # 這裡簡化處理，實際應該合併去重
        
        print("-" * 60)
        print(f"{'總計':<10} {total_pages:<8} {total_songs:<10} {len(self.stats['unique_songs']):<10}")
        
        print(f"\n⏰ 執行統計:")
        print(f"   完成公司: {len(results)}/{len(self.companies)} 家")
        print(f"   總耗時: {elapsed}")
        print(f"   平均速度: {total_songs/(elapsed.total_seconds()/3600):.0f} 首歌/小時")
        
        # 與音圓對比
        yinyuan_songs = 44100
        print(f"\n📊 與音圓對比:")
        print(f"   音圓: {yinyuan_songs:,} 首")
        print(f"   精選收集: {total_songs:,} 首")
        print(f"   比例: {(total_songs/yinyuan_songs)*100:.1f}%")
        
        # 合併建議
        print(f"\n💡 建議:")
        if total_songs > 20000:
            print("   ✅ 收集到足夠數據量，品質良好")
            print("   📋 可以考慮整合到主資料庫")
        elif total_songs > 5000:
            print("   ⚠️ 數據量適中，可補充特定公司")
        else:
            print("   🔍 數據量較少，可能需要調整策略")

def main():
    scraper = SelectiveScraper()
    
    try:
        print("🎯 執行精選策略爬取...")
        print("💡 重點：小範圍、高品質、去重複")
        
        results = scraper.run_selective_scraping()
        
        if results:
            print(f"\n🎉 精選爬取成功完成！")
            print(f"📁 結果文件保存在 selective_results/ 目錄")
            print(f"🔄 可以進一步整合和分析數據")
        else:
            print(f"\n⚠️ 未獲得預期結果，可能需要調整策略")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ 用戶中斷")
        print(f"💾 已保存數據在 selective_results/ 目錄")
        
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()