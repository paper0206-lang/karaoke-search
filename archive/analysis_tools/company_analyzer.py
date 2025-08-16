#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣KTV公司數據量分析器
檢測每家公司的總頁數和預估時間
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime, timedelta
from urllib.parse import quote
import concurrent.futures
import threading

class CompanyAnalyzer:
    def __init__(self):
        self.companies = [
            "音圓", "弘音", "金嗓", "音圓原廠", "瑞影", "點將家", "嘉揚", "音遊",
            "音影", "美華", "金影", "金嗓/投幣", "一級棒", "錢櫃", "好樂迪", "星據點",
            "銀櫃", "享溫馨", "大唐", "MV", "金嗓/家庭"
        ]
        
        self.session_lock = threading.Lock()
        self.sessions = {}
        
        # 每家公司的分析結果
        self.company_stats = {}
        
    def _get_session(self, thread_id):
        """獲取線程專用session"""
        with self.session_lock:
            if thread_id not in self.sessions:
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
                })
                self.sessions[thread_id] = session
            return self.sessions[thread_id]
    
    def detect_company_total_pages(self, company):
        """檢測單一公司的總頁數"""
        thread_id = threading.get_ident()
        session = self._get_session(thread_id)
        
        print(f"🔍 檢測 {company} 的總頁數...")
        
        # 二分搜尋法找最後一頁
        low = 1
        high = 20000  # 設定一個合理的上限
        last_valid_page = 0
        
        while low <= high:
            mid = (low + high) // 2
            
            try:
                url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={mid}"
                response = session.get(url, timeout=10)
                response.encoding = "utf-8"
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    song_links = soup.select('a[href^="mv.aspx?id="]')
                    
                    if len(song_links) > 0:
                        last_valid_page = mid
                        low = mid + 1  # 繼續往上找
                        print(f"   第{mid}頁 ✅ 有{len(song_links)}首歌")
                    else:
                        high = mid - 1  # 往下找
                        print(f"   第{mid}頁 ❌ 無數據")
                else:
                    high = mid - 1
                    print(f"   第{mid}頁 ❌ HTTP {response.status_code}")
                
                # 禮貌延遲
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f"   第{mid}頁 ❌ 錯誤: {e}")
                high = mid - 1
                time.sleep(2)
        
        # 驗證最後一頁
        if last_valid_page > 0:
            try:
                # 檢查最後幾頁確保準確性
                for check_page in range(max(1, last_valid_page - 2), last_valid_page + 3):
                    url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={check_page}"
                    response = session.get(url, timeout=10)
                    response.encoding = "utf-8"
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        song_links = soup.select('a[href^="mv.aspx?id="]')
                        
                        if len(song_links) > 0:
                            last_valid_page = max(last_valid_page, check_page)
                        
                    time.sleep(1)
                    
            except Exception as e:
                print(f"   驗證失敗: {e}")
        
        return last_valid_page
    
    def analyze_all_companies(self):
        """分析所有公司"""
        print("🎯 開始分析所有公司的數據量")
        print("=" * 60)
        
        start_time = time.time()
        
        # 使用線程池並行檢測
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_company = {
                executor.submit(self.detect_company_total_pages, company): company
                for company in self.companies
            }
            
            for future in concurrent.futures.as_completed(future_to_company):
                company = future_to_company[future]
                try:
                    total_pages = future.result()
                    
                    # 計算統計數據
                    total_songs = total_pages * 50  # 每頁50首歌
                    
                    self.company_stats[company] = {
                        'total_pages': total_pages,
                        'total_songs': total_songs,
                        'status': 'success'
                    }
                    
                    print(f"✅ {company}: {total_pages:,} 頁 ({total_songs:,} 首歌)")
                    
                except Exception as e:
                    print(f"❌ {company}: 檢測失敗 - {e}")
                    self.company_stats[company] = {
                        'total_pages': 0,
                        'total_songs': 0,
                        'status': 'failed',
                        'error': str(e)
                    }
        
        analysis_time = time.time() - start_time
        
        # 生成報告
        self._generate_report(analysis_time)
        
        # 保存結果
        self._save_results()
    
    def _generate_report(self, analysis_time):
        """生成分析報告"""
        print("\n" + "=" * 60)
        print("📊 公司數據量分析報告")
        print("=" * 60)
        
        total_pages = 0
        total_songs = 0
        successful_companies = 0
        
        # 按頁數排序
        sorted_companies = sorted(
            [(company, stats) for company, stats in self.company_stats.items() if stats['status'] == 'success'],
            key=lambda x: x[1]['total_pages'],
            reverse=True
        )
        
        print(f"{'排名':<4} {'公司名稱':<12} {'總頁數':<10} {'歌曲數':<12} {'預估時間':<10}")
        print("-" * 60)
        
        for rank, (company, stats) in enumerate(sorted_companies, 1):
            pages = stats['total_pages']
            songs = stats['total_songs']
            
            # 估算單公司完成時間（基於5線程，119K首/小時）
            est_hours = songs / 119000 if songs > 0 else 0
            
            if est_hours < 1:
                time_str = f"{est_hours * 60:.0f}分鐘"
            else:
                time_str = f"{est_hours:.1f}小時"
            
            print(f"{rank:<4} {company:<12} {pages:,}頁{'':<4} {songs:,}首{'':<6} {time_str}")
            
            total_pages += pages
            total_songs += songs
            successful_companies += 1
        
        # 失敗的公司
        failed_companies = [company for company, stats in self.company_stats.items() if stats['status'] == 'failed']
        if failed_companies:
            print(f"\n❌ 檢測失敗的公司 ({len(failed_companies)}):")
            for company in failed_companies:
                error = self.company_stats[company].get('error', '未知錯誤')
                print(f"   {company}: {error}")
        
        print("\n" + "=" * 60)
        print("📈 總體統計")
        print("=" * 60)
        print(f"成功檢測公司: {successful_companies}/{len(self.companies)} 家")
        print(f"總頁數: {total_pages:,} 頁")
        print(f"總歌曲數: {total_songs:,} 首")
        print(f"檢測耗時: {analysis_time:.1f} 秒")
        
        # 完成時間估算
        if total_songs > 0:
            # 基於5線程，預估119K首/小時的速度
            total_hours = total_songs / 119000
            total_days = total_hours / 24
            
            completion_time = datetime.now() + timedelta(hours=total_hours)
            
            print(f"\n⏰ 完成時間估算 (5線程):")
            print(f"總耗時: {total_days:.1f} 天 ({total_hours:.1f} 小時)")
            print(f"預計完成: {completion_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 每日進度估算
            songs_per_day = 119000 * 24  # 每天能爬的歌曲數
            print(f"每日進度: {songs_per_day:,} 首歌")
        
        print("\n💡 建議:")
        if total_songs > 5000000:  # 超過500萬首
            print("   - 數據量極大，建議分階段執行")
            print("   - 考慮只爬取前10大公司")
            print("   - 準備足夠的存儲空間 (>5GB)")
        elif total_songs > 1000000:  # 超過100萬首
            print("   - 數據量較大，建議使用分批保存")
            print("   - 監控系統資源使用")
        else:
            print("   - 數據量適中，可以一次性完成")
    
    def _save_results(self):
        """保存分析結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"company_analysis_{timestamp}.json"
        
        analysis_data = {
            'timestamp': timestamp,
            'analysis_date': datetime.now().isoformat(),
            'companies': self.company_stats,
            'summary': {
                'total_companies': len(self.companies),
                'successful_detections': len([s for s in self.company_stats.values() if s['status'] == 'success']),
                'total_pages': sum(s['total_pages'] for s in self.company_stats.values() if s['status'] == 'success'),
                'total_songs': sum(s['total_songs'] for s in self.company_stats.values() if s['status'] == 'success')
            }
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 分析結果已保存: {filename}")
            
        except Exception as e:
            print(f"\n❌ 保存結果失敗: {e}")
    
    def cleanup(self):
        """清理資源"""
        for session in self.sessions.values():
            session.close()

def main():
    """主程序"""
    print("🎵 台灣KTV公司數據量分析器")
    print("🔍 檢測每家公司的總頁數和歌曲數量")
    print("=" * 60)
    
    analyzer = CompanyAnalyzer()
    
    try:
        analyzer.analyze_all_companies()
        
    except KeyboardInterrupt:
        print("\n⚠️ 用戶中斷分析")
    except Exception as e:
        print(f"\n❌ 分析過程發生錯誤: {e}")
    finally:
        analyzer.cleanup()

if __name__ == "__main__":
    main()