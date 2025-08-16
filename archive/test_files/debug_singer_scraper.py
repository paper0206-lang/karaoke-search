#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌手關鍵字爬蟲 - 調試版本
保存HTML回應內容以分析網頁結構
"""

import requests
import json
import time
import random
import os
import re
from datetime import datetime
import logging

class DebugSingerScraper:
    def __init__(self):
        self.base_url = "https://song.corp.com.tw"
        self.search_url = f"{self.base_url}/index.aspx"
        
        # 只測試一位歌手
        self.test_singer = "周杰倫"
        
        # User-Agent
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        
        # 設置日誌
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
    
    def save_html_response(self, content, filename):
        """保存HTML回應內容"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"💾 HTML內容已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存HTML失敗: {e}")
    
    def debug_search(self):
        """調試搜尋流程"""
        print("🔍 開始調試歌手搜尋流程")
        print("=" * 40)
        
        session = self.create_session()
        
        try:
            # 1. 獲取首頁
            print("📄 步驟1: 獲取首頁...")
            initial_response = session.get(self.search_url, timeout=30)
            initial_response.raise_for_status()
            
            self.save_html_response(initial_response.text, "debug_01_initial_page.html")
            print(f"✅ 首頁狀態碼: {initial_response.status_code}")
            
            # 2. 分析表單結構
            print("\n🔍 步驟2: 分析表單結構...")
            
            # 查找ViewState
            viewstate_match = re.search(r'name="__VIEWSTATE".*?value="([^"]*)"', initial_response.text)
            eventvalidation_match = re.search(r'name="__EVENTVALIDATION".*?value="([^"]*)"', initial_response.text)
            
            print(f"ViewState 找到: {'是' if viewstate_match else '否'}")
            print(f"EventValidation 找到: {'是' if eventvalidation_match else '否'}")
            
            if viewstate_match:
                print(f"ViewState (前50字符): {viewstate_match.group(1)[:50]}...")
            
            # 查找搜尋相關的表單元素
            search_elements = []
            
            # 查找按歌手搜尋的選項
            singer_search_patterns = [
                r'name="[^"]*search[^"]*type[^"]*".*?value="[^"]*singer[^"]*"',
                r'value="singer".*?name="[^"]*search[^"]*type[^"]*"',
                r'singer.*?radio',
                r'歌手.*?radio'
            ]
            
            for pattern in singer_search_patterns:
                matches = re.findall(pattern, initial_response.text, re.IGNORECASE)
                if matches:
                    search_elements.extend(matches)
                    
            print(f"找到搜尋相關元素: {len(search_elements)} 個")
            
            # 查找關鍵字輸入框
            keyword_patterns = [
                r'name="[^"]*keyword[^"]*"',
                r'name="[^"]*txt[^"]*"',
                r'placeholder=".*?關鍵字.*?"'
            ]
            
            keyword_elements = []
            for pattern in keyword_patterns:
                matches = re.findall(pattern, initial_response.text, re.IGNORECASE)
                keyword_elements.extend(matches)
                
            print(f"找到關鍵字輸入框: {len(keyword_elements)} 個")
            for elem in keyword_elements[:3]:
                print(f"  • {elem}")
            
            # 查找搜尋按鈕
            button_patterns = [
                r'name="[^"]*but[^"]*sel[^"]*"',
                r'value="查詢"',
                r'value="搜尋"',
                r'type="submit"'
            ]
            
            button_elements = []
            for pattern in button_patterns:
                matches = re.findall(pattern, initial_response.text, re.IGNORECASE)
                button_elements.extend(matches)
                
            print(f"找到搜尋按鈕: {len(button_elements)} 個")
            
            if not viewstate_match:
                print("❌ 無法找到ViewState，可能需要調整搜尋策略")
                return
                
            # 3. 執行搜尋
            print(f"\n🎵 步驟3: 搜尋歌手 '{self.test_singer}'...")
            
            search_params = {
                '__VIEWSTATE': viewstate_match.group(1),
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                'ctl00$ContentPlaceHolder1$sel_company': '',
                'ctl00$ContentPlaceHolder1$txt_keyword': self.test_singer,
                'ctl00$ContentPlaceHolder1$sel_search_type': 'singer',
                'ctl00$ContentPlaceHolder1$but_sel': '查詢'
            }
            
            if eventvalidation_match:
                search_params['__EVENTVALIDATION'] = eventvalidation_match.group(1)
            
            print("📝 搜尋參數:")
            for key, value in search_params.items():
                if key not in ['__VIEWSTATE', '__EVENTVALIDATION']:
                    print(f"  • {key}: {value}")
                else:
                    print(f"  • {key}: {value[:30]}...")
            
            search_response = session.post(self.search_url, data=search_params, timeout=30)
            search_response.raise_for_status()
            
            self.save_html_response(search_response.text, f"debug_02_search_result_{self.test_singer}.html")
            print(f"✅ 搜尋回應狀態碼: {search_response.status_code}")
            
            # 4. 分析搜尋結果
            print("\n📊 步驟4: 分析搜尋結果...")
            
            # 檢查是否有"查無資料"等訊息
            no_data_patterns = [
                "查無資料",
                "沒有找到",
                "無符合條件",
                "找不到",
                "no data",
                "not found"
            ]
            
            found_no_data = False
            for pattern in no_data_patterns:
                if pattern in search_response.text:
                    print(f"⚠️ 發現無資料訊息: '{pattern}'")
                    found_no_data = True
            
            if not found_no_data:
                print("✅ 未發現明顯的無資料訊息")
            
            # 查找可能的表格結構
            table_patterns = [
                r'<table[^>]*>(.*?)</table>',
                r'<tbody[^>]*>(.*?)</tbody>',
                r'<tr[^>]*>(.*?)</tr>'
            ]
            
            for i, pattern in enumerate(table_patterns, 1):
                matches = re.findall(pattern, search_response.text, re.DOTALL | re.IGNORECASE)
                print(f"表格模式 {i}: 找到 {len(matches)} 個匹配")
                
                if matches and i == 3:  # tr 模式
                    print("前3個 <tr> 內容樣本:")
                    for j, match in enumerate(matches[:3], 1):
                        # 清理內容用於顯示
                        clean_content = re.sub(r'\s+', ' ', match[:200])
                        print(f"  TR{j}: {clean_content}...")
            
            # 查找GridView或其他控制項
            gridview_pattern = r'GridView\d*'
            gridview_matches = re.findall(gridview_pattern, search_response.text, re.IGNORECASE)
            if gridview_matches:
                print(f"找到GridView控制項: {set(gridview_matches)}")
            
            # 檢查是否有分頁相關元素
            pagination_patterns = [
                "下一頁",
                "上一頁", 
                "Page\\$Next",
                "Page\\$Prev",
                "__doPostBack"
            ]
            
            pagination_found = []
            for pattern in pagination_patterns:
                if re.search(pattern, search_response.text, re.IGNORECASE):
                    pagination_found.append(pattern)
                    
            if pagination_found:
                print(f"找到分頁元素: {pagination_found}")
            else:
                print("未找到明顯的分頁元素")
                
            # 5. 嘗試提取實際內容
            print("\n🔍 步驟5: 嘗試提取歌曲資訊...")
            
            # 查找包含中文的內容（可能是歌曲名稱）
            chinese_content = re.findall(r'[\u4e00-\u9fa5]+', search_response.text)
            chinese_words = [word for word in chinese_content if len(word) >= 2]
            
            print(f"找到中文內容: {len(chinese_words)} 個詞語")
            
            # 顯示一些可能是歌曲名稱的內容
            possible_songs = [word for word in chinese_words if 3 <= len(word) <= 20]
            if possible_songs:
                print("可能的歌曲名稱樣本:")
                for song in possible_songs[:10]:
                    if song not in ["查無資料", "沒有找到", "歌手", "歌名", "公司"]:
                        print(f"  • {song}")
            
            print(f"\n🎯 調試完成！請檢查保存的HTML檔案：")
            print(f"  • debug_01_initial_page.html - 首頁內容")
            print(f"  • debug_02_search_result_{self.test_singer}.html - 搜尋結果")
            
        except Exception as e:
            print(f"❌ 調試過程中發生錯誤: {e}")
            import traceback
            traceback.print_exc()

def main():
    debugger = DebugSingerScraper()
    debugger.debug_search()

if __name__ == "__main__":
    main()