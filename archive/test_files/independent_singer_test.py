#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
獨立歌手搜尋測試 - 基於原有技術實現方式
不依賴舊有資料，獨立驗證歌手搜尋的可行性
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
from datetime import datetime
from urllib.parse import quote

class IndependentSingerTest:
    def __init__(self):
        self.base_url = "https://song.corp.com.tw"
        
        # 測試歌手清單（包含不同類型）
        self.test_singers = [
            "周杰倫",    # 流行歌手
            "蔡依林",    # 流行歌手
            "詹雅雯",    # 台語歌手
            "龍千玉",    # 台語歌手
            "五月天"     # 樂團
        ]
        
        # 測試結果
        self.test_results = {
            "test_info": {
                "test_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "method": "independent_verification",
                "approach": ["company_browsing", "direct_search", "page_analysis"]
            },
            "company_browsing_test": {},
            "search_functionality_test": {},
            "singer_discovery": {},
            "summary": {}
        }
        
        # 會話設定
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        
    def process_song_title(self, title):
        """處理歌曲標題 - 將(lv)轉換為(Live版)"""
        if not title:
            return title, False
            
        is_live = False
        
        # 處理Live版本標記
        if re.search(r'\(lv\)', title, re.IGNORECASE):
            title = re.sub(r'\(lv\)', '(Live版)', title, flags=re.IGNORECASE)
            is_live = True
        elif '(LV)' in title:
            title = title.replace('(LV)', '(Live版)')
            is_live = True
            
        return title, is_live
    
    def test_company_browsing(self, company="音圓", max_pages=5):
        """測試公司分類瀏覽功能 - 基於原有技術"""
        print(f"🔍 測試公司分類瀏覽: {company}")
        
        found_singers = set()
        songs_by_singer = {}
        total_songs = 0
        
        try:
            for page_num in range(1, max_pages + 1):
                print(f"   📄 檢查第 {page_num} 頁...")
                
                # 使用原有的URL模式
                url = f"{self.base_url}/songs.aspx?company={quote(company)}&page={page_num}"
                
                response = self.session.get(url, timeout=15)
                response.encoding = "utf-8"
                
                if response.status_code != 200:
                    print(f"   ❌ 第{page_num}頁請求失敗: HTTP {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # 使用原有的選擇器
                song_links = soup.select('a[href^="mv.aspx?id="]')
                
                if not song_links:
                    print(f"   ⚪ 第{page_num}頁無歌曲連結")
                    continue
                
                page_songs = 0
                for link in song_links:
                    try:
                        link_text = link.get_text().strip()
                        parts = link_text.split()
                        
                        if len(parts) >= 4:
                            song_id = parts[0]
                            song_name = parts[1]
                            period = parts[2]
                            singer_name = ' '.join(parts[3:])
                            
                            # 處理Live版本
                            processed_title, is_live = self.process_song_title(song_name)
                            
                            # 記錄歌手
                            found_singers.add(singer_name)
                            
                            if singer_name not in songs_by_singer:
                                songs_by_singer[singer_name] = []
                                
                            song_info = {
                                "song_id": song_id,
                                "song_name": processed_title,
                                "original_song_name": song_name,
                                "period": period,
                                "singer": singer_name,
                                "is_live": is_live,
                                "page": page_num,
                                "found_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            songs_by_singer[singer_name].append(song_info)
                            page_songs += 1
                            total_songs += 1
                            
                    except Exception as e:
                        continue
                
                print(f"   ✅ 第{page_num}頁: {page_songs} 首歌曲，累計 {len(found_singers)} 位歌手")
                
                # 測試延遲
                time.sleep(random.uniform(1, 2))
        
        except Exception as e:
            print(f"   ❌ 公司瀏覽測試失敗: {e}")
        
        # 檢查我們的測試歌手
        test_singer_results = {}
        for test_singer in self.test_singers:
            if test_singer in found_singers:
                song_count = len(songs_by_singer[test_singer])
                test_singer_results[test_singer] = {
                    "found": True,
                    "song_count": song_count,
                    "songs": songs_by_singer[test_singer][:3]  # 前3首作為樣本
                }
                print(f"   ✅ 找到測試歌手: {test_singer} ({song_count} 首歌)")
            else:
                test_singer_results[test_singer] = {
                    "found": False,
                    "song_count": 0,
                    "songs": []
                }
                print(f"   ❌ 未找到測試歌手: {test_singer}")
        
        self.test_results["company_browsing_test"] = {
            "company": company,
            "pages_tested": max_pages,
            "total_songs_found": total_songs,
            "total_singers_found": len(found_singers),
            "test_singers_results": test_singer_results,
            "top_singers": dict(list({k: len(v) for k, v in songs_by_singer.items()}.items())[:10])
        }
        
        return found_singers, songs_by_singer
    
    def test_search_functionality(self):
        """測試搜尋功能"""
        print(f"\n🔍 測試網站搜尋功能...")
        
        search_results = {}
        
        try:
            # 1. 獲取首頁，查找搜尋表單
            print("   📄 分析首頁搜尋功能...")
            response = self.session.get(f"{self.base_url}/index.aspx", timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # 查找搜尋相關元素
                search_forms = soup.find_all('form')
                search_inputs = soup.find_all('input', {'type': ['text', 'search']})
                search_buttons = soup.find_all(['input', 'button'], string=re.compile(r'搜尋|查詢|search', re.I))
                
                print(f"   📝 找到 {len(search_forms)} 個表單")
                print(f"   📝 找到 {len(search_inputs)} 個輸入框") 
                print(f"   📝 找到 {len(search_buttons)} 個搜尋按鈕")
                
                # 嘗試搜尋測試
                for i, test_singer in enumerate(self.test_singers[:2]):  # 只測試前2位
                    print(f"   🎵 測試搜尋歌手: {test_singer}")
                    
                    try:
                        # 這裡需要根據實際的表單結構調整
                        # 先嘗試簡單的GET搜尋
                        search_url = f"{self.base_url}/index.aspx?keyword={quote(test_singer)}"
                        search_response = self.session.get(search_url, timeout=15)
                        
                        if search_response.status_code == 200:
                            # 簡單檢查是否有相關結果
                            content = search_response.text
                            has_results = (test_singer in content or 
                                         "歌曲" in content or 
                                         "mv.aspx" in content)
                            
                            search_results[test_singer] = {
                                "method": "GET_search",
                                "status_code": search_response.status_code,
                                "has_potential_results": has_results,
                                "content_length": len(content)
                            }
                            
                            print(f"      {'✅' if has_results else '❌'} GET搜尋結果: {'有潛在結果' if has_results else '無明顯結果'}")
                        
                    except Exception as e:
                        search_results[test_singer] = {
                            "method": "GET_search",
                            "error": str(e)
                        }
                        print(f"      ❌ 搜尋失敗: {e}")
                    
                    time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"   ❌ 搜尋功能測試失敗: {e}")
        
        self.test_results["search_functionality_test"] = {
            "search_available": len(search_results) > 0,
            "test_results": search_results
        }
    
    def run_independent_test(self):
        """執行完整的獨立測試"""
        print("🧪 開始獨立歌手搜尋驗證測試")
        print("=" * 60)
        print(f"📋 測試目標: {', '.join(self.test_singers)}")
        print(f"🎯 驗證方法: 公司瀏覽 + 搜尋功能 + 實際發現")
        print()
        
        # 1. 測試公司分類瀏覽
        found_singers, songs_by_singer = self.test_company_browsing(max_pages=10)
        
        # 2. 測試搜尋功能
        self.test_search_functionality()
        
        # 3. 分析發現的歌手
        print(f"\n🎵 歌手發現分析...")
        singer_analysis = {}
        
        # 分析歌手類型
        if songs_by_singer:
            for singer, songs in list(songs_by_singer.items())[:20]:  # 分析前20位歌手
                song_count = len(songs)
                live_count = sum(1 for song in songs if song.get("is_live", False))
                
                singer_analysis[singer] = {
                    "song_count": song_count,
                    "live_songs": live_count,
                    "regular_songs": song_count - live_count,
                    "sample_songs": [song["song_name"] for song in songs[:3]]
                }
        
        self.test_results["singer_discovery"] = {
            "total_discovered": len(found_singers),
            "analysis_sample": singer_analysis
        }
        
        # 4. 生成總結
        self.generate_test_summary()
        
        # 5. 保存結果
        self.save_test_results()
    
    def generate_test_summary(self):
        """生成測試總結"""
        company_test = self.test_results["company_browsing_test"]
        search_test = self.test_results["search_functionality_test"]
        discovery = self.test_results["singer_discovery"]
        
        # 統計測試歌手結果
        found_count = 0
        not_found_count = 0
        total_songs = 0
        
        for singer, result in company_test["test_singers_results"].items():
            if result["found"]:
                found_count += 1
                total_songs += result["song_count"]
            else:
                not_found_count += 1
        
        summary = {
            "test_success": company_test["total_songs_found"] > 0,
            "company_browsing_works": company_test["total_songs_found"] > 0,
            "search_functionality_available": search_test["search_available"],
            "test_singers_found": found_count,
            "test_singers_not_found": not_found_count,
            "total_test_songs": total_songs,
            "recommendation": self.get_recommendation(found_count, company_test["total_songs_found"])
        }
        
        self.test_results["summary"] = summary
    
    def get_recommendation(self, found_singers, total_songs):
        """基於測試結果提供建議"""
        if found_singers >= 3 and total_songs > 50:
            return "建議：可以使用公司分類瀏覽方式實現歌手歌曲收集"
        elif found_singers >= 1 and total_songs > 20:
            return "建議：公司瀏覽可行，但可能需要擴大搜尋範圍"
        elif total_songs > 0:
            return "建議：網站有數據，但測試歌手可能不在此資料庫中，需調整歌手清單"
        else:
            return "建議：需要重新評估技術方案或網站結構"
    
    def save_test_results(self):
        """保存測試結果"""
        filename = f"independent_singer_test_{time.strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            print(f"💾 測試結果已保存到: {filename}")
            self.results_file = filename
        except Exception as e:
            print(f"❌ 保存測試結果失敗: {e}")
    
    def print_detailed_results(self):
        """打印詳細測試結果"""
        print("\n" + "=" * 60)
        print("📊 獨立歌手搜尋驗證結果")
        print("=" * 60)
        
        summary = self.test_results["summary"]
        company_test = self.test_results["company_browsing_test"]
        
        print(f"🎯 測試狀態: {'成功' if summary['test_success'] else '失敗'}")
        print(f"🏢 公司瀏覽: {'可用' if summary['company_browsing_works'] else '不可用'}")
        print(f"🔍 搜尋功能: {'可用' if summary['search_functionality_available'] else '不確定'}")
        print(f"📈 發現歌手: {self.test_results['singer_discovery']['total_discovered']} 位")
        print(f"✅ 測試歌手找到: {summary['test_singers_found']} / {len(self.test_singers)}")
        print(f"🎵 測試歌曲總數: {summary['total_test_songs']}")
        
        print(f"\n📋 各測試歌手詳細結果:")
        for singer, result in company_test["test_singers_results"].items():
            if result["found"]:
                print(f"   ✅ {singer}: {result['song_count']} 首歌曲")
                if result["songs"]:
                    print(f"      🎵 樣本歌曲:")
                    for song in result["songs"]:
                        live_mark = " (Live版)" if song.get("is_live") else ""
                        print(f"         • {song['song_name']}{live_mark}")
            else:
                print(f"   ❌ {singer}: 未找到")
        
        print(f"\n💡 建議: {summary['recommendation']}")
        
        if hasattr(self, 'results_file'):
            print(f"\n📄 完整結果請查看: {self.results_file}")

def main():
    tester = IndependentSingerTest()
    
    try:
        tester.run_independent_test()
        tester.print_detailed_results()
    except KeyboardInterrupt:
        print("\n🛑 測試被用戶中斷")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    main()