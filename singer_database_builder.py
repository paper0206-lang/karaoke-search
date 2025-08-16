#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌手資料庫建構器
收集華語流行、台語、樂團組合的完整歌手名單
用於KTV歌曲搜尋的關鍵字資料庫
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import quote, unquote
import random

class SingerDatabaseBuilder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        })
        
        # 基礎歌手資料庫
        self.singers_database = {
            'mandarin_singers': set(),  # 華語歌手
            'taiwanese_singers': set(), # 台語歌手  
            'bands_groups': set(),      # 樂團組合
            'hong_kong_singers': set(), # 香港歌手
            'mainland_singers': set(),  # 大陸歌手
            'classic_singers': set()    # 經典老歌手
        }
    
    def add_manual_famous_singers(self):
        """手動添加知名歌手（確保不遺漏重要歌手）"""
        print("📝 添加手動收集的知名歌手...")
        
        # 華語流行天王天后
        mandarin_superstars = [
            "周杰倫", "蔡依林", "林俊傑", "張惠妹", "王力宏", "陶喆", "林宥嘉",
            "蕭敬騰", "田馥甄", "楊丞琳", "羅志祥", "潘瑋柏", "周興哲", "高爾宣",
            "A-Lin", "鄧紫棋", "陳綺貞", "張韶涵", "梁靜茹", "孫燕姿",
            "李玖哲", "品冠", "光良", "動力火車", "信", "伍佰", "庾澄慶",
            "張信哲", "劉德華", "張學友", "郭富城", "黎明", "陳奕迅", "容祖兒",
            "楊千嬅", "謝霆鋒", "古巨基", "陳慧琳", "鄭秀文", "關淑怡", "彭佳慧"
        ]
        
        # 台語歌手
        taiwanese_singers = [
            "江蕙", "張秀卿", "陳雷", "黃乙玲", "龍千玉", "蔡秋鳳", "蔡小虎",
            "洪榮宏", "葉啟田", "文夏", "鳳飛飛", "蔡琴", "蘇芮", "黃妃",
            "謝金燕", "羅時豐", "翁立友", "許富凱", "蕭煌奇", "茄子蛋", "滅火器",
            "陳昇", "伍佰", "豬頭皮", "黃連煜", "朱海君", "施文彬", "方瑞娥",
            "袁小迪", "秀蘭瑪雅", "孫協志", "王中平", "唐飛", "詹雅雯"
        ]
        
        # 樂團組合
        bands_groups = [
            "五月天", "蘇打綠", "F.I.R.", "S.H.E", "飛兒樂團", "信樂團", "脫拉庫",
            "董事長樂團", "滅火器", "茄子蛋", "草東沒有派對", "老王樂隊", "宇宙人",
            "八十八顆芭樂籽", "閃靈", "Chthonic", "麋先生", "告五人", "持修",
            "動力火車", "優客李林", "小虎隊", "四分衛", "1976", "濁水溪公社",
            "血肉果汁機", "大支", "拍謝少年", "雞蛋蒸肉餅", "透明雜誌", "椅子樂團"
        ]
        
        # 大陸歌手
        mainland_singers = [
            "周深", "毛不易", "李健", "陳奕迅", "薛之謙", "汪蘇瀧", "胡彥斌",
            "林志炫", "韓紅", "那英", "王菲", "孫楠", "譚維維", "張靚穎",
            "華晨宇", "鄧紫棋", "G.E.M.", "李榮浩", "陳粒", "房東的貓"
        ]
        
        # 經典老歌手
        classic_singers = [
            "鄧麗君", "張雨生", "黃家駒", "Leslie", "張國榮", "譚詠麟", "梅艷芳",
            "徐小鳳", "林子祥", "溫拿", "Beyond", "達明一派", "太極樂隊",
            "羅大佑", "李宗盛", "齊秦", "趙傳", "張宇", "辛曉琪", "潘越雲",
            "蔡幸娟", "高勝美", "林慧萍", "金智娟", "王傑", "巫啟賢", "童安格"
        ]
        
        # 添加到對應分類
        self.singers_database['mandarin_singers'].update(mandarin_superstars)
        self.singers_database['taiwanese_singers'].update(taiwanese_singers)
        self.singers_database['bands_groups'].update(bands_groups)
        self.singers_database['mainland_singers'].update(mainland_singers)
        self.singers_database['classic_singers'].update(classic_singers)
        
        total_manual = sum(len(singers) for singers in self.singers_database.values())
        print(f"✅ 手動添加完成，共 {total_manual} 位歌手")
    
    def fetch_wikipedia_singers(self, category_urls):
        """從維基百科分類頁面抓取歌手名單"""
        print("\n🌐 從維基百科抓取歌手資料...")
        
        wikipedia_singers = set()
        
        for category_name, url in category_urls.items():
            print(f"📖 抓取 {category_name}...")
            
            try:
                response = self.session.get(url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 查找分類頁面中的歌手連結
                    category_content = soup.find('div', {'class': 'mw-category'})
                    if category_content:
                        links = category_content.find_all('a')
                        
                        for link in links:
                            singer_name = link.get_text().strip()
                            # 過濾掉分類連結等非歌手名稱
                            if (not singer_name.startswith('分類:') and 
                                not singer_name.startswith('Category:') and
                                len(singer_name) > 1 and len(singer_name) < 15):
                                wikipedia_singers.add(singer_name)
                                
                        print(f"   ✅ 從 {category_name} 找到 {len([l for l in links if not l.get_text().startswith('分類')])} 位歌手")
                    else:
                        print(f"   ❌ 無法解析 {category_name} 內容")
                else:
                    print(f"   ❌ 無法訪問 {category_name}: HTTP {response.status_code}")
                    
                time.sleep(2)  # 避免過於頻繁請求
                
            except Exception as e:
                print(f"   ❌ 抓取 {category_name} 失敗: {e}")
        
        # 將維基百科歌手添加到華語歌手分類
        self.singers_database['mandarin_singers'].update(wikipedia_singers)
        print(f"✅ 維基百科抓取完成，共找到 {len(wikipedia_singers)} 位額外歌手")
        
        return wikipedia_singers
    
    def fetch_music_platform_data(self):
        """從音樂平台抓取熱門歌手（如果可能）"""
        print("\n🎵 嘗試從音樂平台獲取熱門歌手...")
        
        platform_singers = set()
        
        # 這裡可以添加對各音樂平台的抓取邏輯
        # 由於版權和反爬限制，先跳過實際實現
        print("⚠️ 音樂平台抓取暫時跳過（需要處理反爬和API限制）")
        
        return platform_singers
    
    def clean_and_deduplicate(self):
        """清理和去重歌手名單"""
        print("\n🧹 清理和去重歌手資料...")
        
        all_singers_before = sum(len(singers) for singers in self.singers_database.values())
        
        for category, singers in self.singers_database.items():
            # 轉換為列表進行處理
            singers_list = list(singers)
            cleaned_singers = set()
            
            for singer in singers_list:
                # 基本清理
                cleaned_name = singer.strip()
                
                # 移除特殊字符但保留中文、英文、數字
                cleaned_name = re.sub(r'[^\w\s\u4e00-\u9fff.-]', '', cleaned_name)
                
                # 跳過過短或過長的名稱
                if 1 <= len(cleaned_name) <= 20:
                    cleaned_singers.add(cleaned_name)
            
            # 更新清理後的資料
            self.singers_database[category] = cleaned_singers
            
        all_singers_after = sum(len(singers) for singers in self.singers_database.values())
        print(f"✅ 清理完成：{all_singers_before} → {all_singers_after} 位歌手")
    
    def create_search_keywords(self):
        """創建搜尋關鍵字資料庫"""
        print("\n🔍 創建搜尋關鍵字資料庫...")
        
        # 合併所有歌手
        all_singers = set()
        for singers in self.singers_database.values():
            all_singers.update(singers)
        
        # 創建關鍵字變體（處理常見的名字變化）
        search_keywords = set(all_singers)
        
        # 添加常見變體
        for singer in list(all_singers):
            # 去除空格的版本
            no_space = singer.replace(' ', '')
            if no_space != singer:
                search_keywords.add(no_space)
            
            # 處理英文名的點號變體
            if '.' in singer:
                no_dot = singer.replace('.', '')
                search_keywords.add(no_dot)
        
        keyword_database = {
            'singers_by_category': {k: list(v) for k, v in self.singers_database.items()},
            'all_singers': sorted(list(all_singers)),
            'search_keywords': sorted(list(search_keywords)),
            'statistics': {
                'total_singers': len(all_singers),
                'total_keywords': len(search_keywords),
                'mandarin_singers': len(self.singers_database['mandarin_singers']),
                'taiwanese_singers': len(self.singers_database['taiwanese_singers']),
                'bands_groups': len(self.singers_database['bands_groups']),
                'hong_kong_singers': len(self.singers_database['hong_kong_singers']),
                'mainland_singers': len(self.singers_database['mainland_singers']),
                'classic_singers': len(self.singers_database['classic_singers'])
            }
        }
        
        print(f"✅ 關鍵字資料庫創建完成：{len(search_keywords)} 個搜尋關鍵字")
        
        return keyword_database
    
    def save_database(self, database, filename):
        """儲存歌手資料庫"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(database, f, ensure_ascii=False, indent=2)
            print(f"💾 歌手資料庫已保存到: {filename}")
        except Exception as e:
            print(f"❌ 儲存失敗: {e}")
    
    def print_statistics(self, database):
        """顯示統計資訊"""
        print("\n📊 歌手資料庫統計:")
        print("=" * 40)
        
        stats = database['statistics']
        
        print(f"🎤 華語歌手: {stats['mandarin_singers']} 位")
        print(f"🎭 台語歌手: {stats['taiwanese_singers']} 位") 
        print(f"🎸 樂團組合: {stats['bands_groups']} 個")
        print(f"🏢 香港歌手: {stats['hong_kong_singers']} 位")
        print(f"🌏 大陸歌手: {stats['mainland_singers']} 位")
        print(f"⭐ 經典歌手: {stats['classic_singers']} 位")
        print(f"📝 搜尋關鍵字總數: {stats['total_keywords']} 個")
        print(f"🎵 歌手總數: {stats['total_singers']} 位")
        
        # 顯示部分歌手樣本
        print(f"\n🌟 部分知名歌手樣本:")
        sample_singers = database['all_singers'][:20]
        for i, singer in enumerate(sample_singers, 1):
            print(f"   {i:2d}. {singer}")
        
        if len(database['all_singers']) > 20:
            print(f"   ... 還有 {len(database['all_singers']) - 20} 位歌手")

def main():
    builder = SingerDatabaseBuilder()
    
    print("🎵 開始建構華語歌手搜尋關鍵字資料庫")
    print("=" * 60)
    
    # 1. 添加手動收集的知名歌手
    builder.add_manual_famous_singers()
    
    # 2. 從維基百科抓取歌手資料
    wikipedia_urls = {
        '台灣華語流行歌手': 'https://zh.wikipedia.org/zh-tw/Category:台灣華語流行音樂歌手',
        '香港歌手': 'https://zh.wikipedia.org/zh-tw/Category:香港歌手',
        '台語歌手': 'https://zh.wikipedia.org/zh-tw/Category:閩南語歌手',
        '華語樂團': 'https://zh.wikipedia.org/zh-tw/Category:華語流行音樂團體'
    }
    
    wikipedia_singers = builder.fetch_wikipedia_singers(wikipedia_urls)
    
    # 3. 從音樂平台獲取資料（暫時跳過）
    builder.fetch_music_platform_data()
    
    # 4. 清理和去重
    builder.clean_and_deduplicate()
    
    # 5. 創建關鍵字資料庫
    keyword_database = builder.create_search_keywords()
    
    # 6. 儲存資料庫
    filename = f"singer_keywords_database_{time.strftime('%Y%m%d_%H%M%S')}.json"
    builder.save_database(keyword_database, filename)
    
    # 7. 顯示統計
    builder.print_statistics(keyword_database)
    
    print(f"\n🎯 總結:")
    print(f"   📦 已建立包含 {keyword_database['statistics']['total_singers']} 位歌手的搜尋資料庫")
    print(f"   🔍 共產生 {keyword_database['statistics']['total_keywords']} 個搜尋關鍵字")
    print(f"   💾 資料已儲存至 {filename}")
    print(f"\n🚀 接下來可以用這些歌手名稱測試 song.corp.com.tw 的搜尋功能！")

if __name__ == "__main__":
    main()