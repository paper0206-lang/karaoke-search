#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌手關鍵字爬蟲 - 小規模測試版本
測試幾位知名歌手，驗證爬蟲功能和數據格式
"""

import requests
import json
import time
import random
import os
import re
from datetime import datetime
import logging

class TestSingerScraper:
    def __init__(self):
        self.base_url = "https://song.corp.com.tw"
        self.search_url = f"{self.base_url}/index.aspx"
        
        # 測試用歌手清單 - 選擇知名度高的歌手
        self.test_singers = [
            "周杰倫",
            "蔡依林", 
            "林俊傑",
            "鄧紫棋",
            "五月天"
        ]
        
        # 測試結果
        self.test_results = {
            "test_info": {
                "test_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "test_singers": self.test_singers,
                "total_test_singers": len(self.test_singers)
            },
            "results": {},
            "summary": {
                "successful_singers": [],
                "failed_singers": [],
                "singers_with_songs": [],
                "singers_without_songs": [],
                "total_songs_found": 0
            }
        }
        
        # User-Agent
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        
        # 設置簡單日誌
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
    def create_session(self):
        """創建會話"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        return session
    
    def process_song_title(self, title):
        """處理歌曲標題 - 將(lv)轉換為(Live版)"""
        if not title:
            return title
            
        # 處理Live版本標記
        title = re.sub(r'\(lv\)', '(Live版)', title, flags=re.IGNORECASE)
        title = re.sub(r'\(LV\)', '(Live版)', title)
        
        # 清理多餘空格
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title
    
    def search_singer_songs(self, singer_name, session, max_pages=3):
        """搜尋單一歌手的歌曲 - 限制頁數用於測試"""
        try:
            self.logger.info(f"🔍 測試搜尋歌手: {singer_name}")
            
            # 首先獲取首頁以取得必要的表單數據
            initial_response = session.get(self.search_url, timeout=30)
            initial_response.raise_for_status()
            
            # 提取ViewState等表單數據
            viewstate_match = re.search(r'name="__VIEWSTATE".*?value="([^"]*)"', initial_response.text)
            eventvalidation_match = re.search(r'name="__EVENTVALIDATION".*?value="([^"]*)"', initial_response.text)
            
            if not viewstate_match:
                self.logger.error("無法找到ViewState")
                return None
            
            # 構建搜尋參數
            search_params = {
                '__VIEWSTATE': viewstate_match.group(1),
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                'ctl00$ContentPlaceHolder1$sel_company': '',  # 全部公司
                'ctl00$ContentPlaceHolder1$txt_keyword': singer_name,
                'ctl00$ContentPlaceHolder1$sel_search_type': 'singer',
                'ctl00$ContentPlaceHolder1$but_sel': '查詢'
            }
            
            if eventvalidation_match:
                search_params['__EVENTVALIDATION'] = eventvalidation_match.group(1)
            
            # 執行搜尋
            response = session.post(self.search_url, data=search_params, timeout=30)
            response.raise_for_status()
            
            # 檢查是否有結果
            if "查無資料" in response.text or "沒有找到" in response.text or "無符合條件" in response.text:
                self.logger.info(f"⚪ {singer_name}: 無搜尋結果")
                return []
            
            songs = []
            page_num = 1
            
            # 處理搜尋結果頁面
            while page_num <= max_pages:
                self.logger.info(f"   📄 處理第 {page_num} 頁...")
                
                # 解析當前頁面的歌曲
                page_songs = self.parse_songs_from_page(response.text, singer_name)
                
                if not page_songs:
                    self.logger.info(f"   🏁 第 {page_num} 頁無歌曲，搜尋完成")
                    break
                    
                songs.extend(page_songs)
                self.logger.info(f"   ✅ 第 {page_num} 頁找到 {len(page_songs)} 首歌曲")
                
                # 檢查是否有下一頁且未達最大頁數
                if page_num >= max_pages or not self.has_next_page(response.text):
                    self.logger.info(f"   🏁 達到測試頁數限制或無下一頁")
                    break
                
                # 翻到下一頁
                time.sleep(random.uniform(1, 2))  # 測試用較短延遲
                next_page_response = self.goto_next_page(session, response.text)
                
                if not next_page_response:
                    self.logger.warning(f"   ⚠️ 無法翻到下一頁，結束搜尋")
                    break
                    
                response = next_page_response
                page_num += 1
            
            self.logger.info(f"✅ {singer_name}: 測試完成，找到 {len(songs)} 首歌曲")
            return songs
            
        except Exception as e:
            self.logger.error(f"❌ 搜尋 {singer_name} 失敗: {e}")
            return None
    
    def parse_songs_from_page(self, html_content, singer_name):
        """從頁面解析歌曲資訊"""
        songs = []
        
        try:
            # 尋找歌曲表格 - 根據實際網站結構調整
            # 嘗試多種可能的表格結構
            
            # 方法1: 尋找包含歌曲資訊的表格行
            song_patterns = [
                r'<tr[^>]*>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?</tr>',
                r'<tr[^>]*class="[^"]*"[^>]*>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?</tr>'
            ]
            
            for pattern in song_patterns:
                matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
                
                if matches:
                    for match in matches:
                        if len(match) >= 3:
                            # 清理HTML標籤和空白
                            col1 = re.sub(r'<[^>]+>', '', match[0]).strip()
                            col2 = re.sub(r'<[^>]+>', '', match[1]).strip()
                            col3 = re.sub(r'<[^>]+>', '', match[2]).strip()
                            
                            # 判斷哪一欄是什麼資料 (需要根據實際網站調整)
                            # 假設：編號、歌名、歌手 或 歌名、歌手、編號
                            song_id = ""
                            song_name = ""
                            artist_name = ""
                            
                            # 嘗試識別編號格式 (通常是數字)
                            if re.match(r'^\d+$', col1.replace('-', '').replace('_', '')):
                                song_id = col1
                                song_name = col2
                                artist_name = col3
                            elif re.match(r'^\d+$', col3.replace('-', '').replace('_', '')):
                                song_name = col1
                                artist_name = col2
                                song_id = col3
                            else:
                                # 如果沒有明顯的編號格式，假設前兩個是歌名和歌手
                                song_name = col1
                                artist_name = col2
                                song_id = col3
                            
                            # 過濾有效的歌曲資料
                            if song_name and len(song_name.strip()) > 0 and song_name != "歌名" and song_name != "歌曲名稱":
                                # 處理Live版本
                                processed_title = self.process_song_title(song_name)
                                is_live = "(Live版)" in processed_title
                                
                                song_info = {
                                    "song_id": song_id,
                                    "song_name": processed_title,
                                    "singer": artist_name,
                                    "search_keyword": singer_name,
                                    "is_live": is_live,
                                    "found_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    "raw_data": {
                                        "col1": col1,
                                        "col2": col2, 
                                        "col3": col3
                                    }
                                }
                                
                                songs.append(song_info)
                    break  # 如果找到資料就不用嘗試其他模式
            
            # 如果上述方法都沒找到，嘗試更寬泛的搜尋
            if not songs:
                # 尋找可能包含歌曲名稱的文字
                song_titles = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9\s\(\)]+', html_content)
                # 這部分需要更精確的邏輯來識別真正的歌曲名稱
                
        except Exception as e:
            self.logger.error(f"解析頁面失敗: {e}")
            
        return songs
    
    def has_next_page(self, html_content):
        """檢查是否有下一頁"""
        next_patterns = [
            r'下一頁',
            r'next',
            r'&gt;',
            r'Page\$Next',
            r'__doPostBack.*?Next'
        ]
        
        for pattern in next_patterns:
            if re.search(pattern, html_content, re.IGNORECASE):
                return True
                
        return False
    
    def goto_next_page(self, session, html_content):
        """跳轉到下一頁"""
        try:
            # 提取ViewState等必要參數
            viewstate_match = re.search(r'name="__VIEWSTATE".*?value="([^"]*)"', html_content)
            eventvalidation_match = re.search(r'name="__EVENTVALIDATION".*?value="([^"]*)"', html_content)
            
            if not viewstate_match:
                return None
                
            # 構建下一頁請求
            next_page_data = {
                '__VIEWSTATE': viewstate_match.group(1),
                '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$GridView1',
                '__EVENTARGUMENT': 'Page$Next'
            }
            
            if eventvalidation_match:
                next_page_data['__EVENTVALIDATION'] = eventvalidation_match.group(1)
            
            response = session.post(self.search_url, data=next_page_data, timeout=30)
            response.raise_for_status()
            
            return response
            
        except Exception as e:
            self.logger.error(f"翻頁失敗: {e}")
            return None
    
    def run_test(self):
        """執行測試"""
        print("🧪 開始歌手關鍵字爬蟲小規模測試")
        print("=" * 50)
        print(f"📋 測試歌手: {', '.join(self.test_singers)}")
        print(f"🎯 每位歌手最多測試 3 頁")
        print()
        
        session = self.create_session()
        
        for singer in self.test_singers:
            try:
                print(f"🔍 測試歌手: {singer}")
                
                # 搜尋歌手歌曲
                songs = self.search_singer_songs(singer, session, max_pages=3)
                
                if songs is None:
                    # 搜尋失敗
                    self.test_results["results"][singer] = {
                        "status": "failed",
                        "error": "搜尋過程發生錯誤",
                        "songs": []
                    }
                    self.test_results["summary"]["failed_singers"].append(singer)
                    print(f"❌ {singer}: 搜尋失敗")
                    
                elif len(songs) == 0:
                    # 沒有找到歌曲
                    self.test_results["results"][singer] = {
                        "status": "no_songs",
                        "songs_count": 0,
                        "songs": []
                    }
                    self.test_results["summary"]["singers_without_songs"].append(singer)
                    self.test_results["summary"]["successful_singers"].append(singer)
                    print(f"⚪ {singer}: 搜尋成功但無歌曲")
                    
                else:
                    # 找到歌曲
                    self.test_results["results"][singer] = {
                        "status": "success",
                        "songs_count": len(songs),
                        "songs": songs[:10]  # 最多顯示前10首作為樣本
                    }
                    self.test_results["summary"]["singers_with_songs"].append(singer)
                    self.test_results["summary"]["successful_singers"].append(singer)
                    self.test_results["summary"]["total_songs_found"] += len(songs)
                    print(f"✅ {singer}: 找到 {len(songs)} 首歌曲")
                    
                    # 顯示前3首歌曲作為樣本
                    for i, song in enumerate(songs[:3], 1):
                        live_mark = " 🎤" if song["is_live"] else ""
                        print(f"   {i}. {song['song_name']}{live_mark}")
                
                # 測試間隔
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                self.logger.error(f"測試 {singer} 時發生異常: {e}")
                self.test_results["results"][singer] = {
                    "status": "error",
                    "error": str(e),
                    "songs": []
                }
                self.test_results["summary"]["failed_singers"].append(singer)
        
        # 保存測試結果
        self.save_test_results()
        self.print_test_summary()
    
    def save_test_results(self):
        """保存測試結果"""
        filename = f"test_singer_scraper_results_{time.strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 測試結果已保存到: {filename}")
            self.results_file = filename
        except Exception as e:
            print(f"❌ 保存測試結果失敗: {e}")
    
    def print_test_summary(self):
        """打印測試摘要"""
        print("\n" + "=" * 50)
        print("📊 測試結果摘要")
        print("=" * 50)
        
        summary = self.test_results["summary"]
        
        print(f"🎵 測試歌手總數: {self.test_results['test_info']['total_test_singers']}")
        print(f"✅ 搜尋成功: {len(summary['successful_singers'])}")
        print(f"❌ 搜尋失敗: {len(summary['failed_singers'])}")
        print(f"🎶 有歌曲歌手: {len(summary['singers_with_songs'])}")
        print(f"⚪ 無歌曲歌手: {len(summary['singers_without_songs'])}")
        print(f"🎵 總歌曲數: {summary['total_songs_found']}")
        
        # 詳細結果
        print(f"\n📋 詳細結果:")
        for singer, result in self.test_results["results"].items():
            status = result["status"]
            if status == "success":
                songs_count = result["songs_count"]
                print(f"   ✅ {singer}: {songs_count} 首歌曲")
                
                # 顯示歌曲樣本
                if result["songs"]:
                    print(f"      🎵 歌曲樣本:")
                    for song in result["songs"][:5]:
                        live_mark = " (Live版)" if song["is_live"] else ""
                        print(f"         • {song['song_name']}{live_mark}")
                    
                    if result["songs_count"] > 5:
                        print(f"         ... 還有 {result['songs_count'] - 5} 首")
                        
            elif status == "no_songs":
                print(f"   ⚪ {singer}: 搜尋成功但無歌曲")
            elif status == "failed" or status == "error":
                error_msg = result.get("error", "未知錯誤")
                print(f"   ❌ {singer}: 失敗 ({error_msg})")
        
        if hasattr(self, 'results_file'):
            print(f"\n📄 完整結果請查看: {self.results_file}")

def main():
    tester = TestSingerScraper()
    tester.run_test()

if __name__ == "__main__":
    main()