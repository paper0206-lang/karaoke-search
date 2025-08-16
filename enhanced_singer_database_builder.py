#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版歌手資料庫建構器
大幅擴充華語、台語、各年代、各地區歌手資料庫
目標：建立最完整的KTV歌手搜尋關鍵字資料庫
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import quote, unquote
import random

class EnhancedSingerDatabaseBuilder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        })
        
        # 增強版歌手資料庫分類
        self.singers_database = {
            'taiwan_mandarin': set(),    # 台灣華語歌手
            'taiwan_hokkien': set(),     # 台語歌手
            'hong_kong': set(),          # 香港歌手
            'mainland_china': set(),     # 大陸歌手
            'singapore_malaysia': set(), # 星馬歌手
            'bands_groups': set(),       # 樂團組合
            'classic_60s_70s': set(),    # 60-70年代經典
            'golden_80s_90s': set(),     # 80-90年代黃金期
            'new_millennium': set(),     # 2000年代
            'current_popular': set(),    # 當代流行
            'indie_alternative': set(),  # 獨立音樂
            'folk_acoustic': set(),      # 民謠創作
            'rock_metal': set(),         # 搖滾重金屬
            'electronic_pop': set(),     # 電子流行
            'rap_hiphop': set()          # 饒舌嘻哈
        }
    
    def add_comprehensive_singers(self):
        """添加全面的歌手資料"""
        print("📝 添加全面歌手資料庫...")
        
        # 台灣華語流行天王天后
        taiwan_mandarin = [
            # 超級天王天后
            "周杰倫", "蔡依林", "張惠妹", "王力宏", "陶喆", "林俊傑", "蕭敬騰",
            "田馥甄", "楊丞琳", "羅志祥", "潘瑋柏", "周興哲", "高爾宣", "A-Lin",
            "陳綺貞", "張韶涵", "梁靜茹", "孫燕姿", "李玖哲", "品冠", "光良",
            "信", "伍佰", "庾澄慶", "張信哲", "彭佳慧", "林宥嘉", "蘇打綠",
            
            # 新生代
            "告五人", "持修", "頑童MJ116", "韋禮安", "林哲熹", "魏嘉瑩",
            "9m88", "Julia Wu", "婁峻碩", "ØZI", "BCW", "Leo王",
            "家家", "徐佳瑩", "戴愛玲", "艾怡良", "郁可唯", "楊乃文",
            
            # 創作歌手
            "盧廣仲", "陳奕迅", "方大同", "李榮浩", "薛之謙", "毛不易",
            "周深", "華晨宇", "胡彥斌", "林志炫", "黃小琥", "萬芳",
            "陳昇", "伍思凱", "李宗盛", "羅大佑", "齊秦", "趙傳",
            
            # 樂壇前輩
            "張宇", "辛曉琪", "潘越雲", "蔡幸娟", "高勝美", "林慧萍",
            "金智娟", "王傑", "巫啟賢", "童安格", "姜育恆", "周華健"
        ]
        
        # 台語歌手大全
        taiwan_hokkien = [
            # 台語天王天后
            "江蕙", "張秀卿", "陳雷", "黃乙玲", "龍千玉", "蔡秋鳳", "蔡小虎",
            "洪榮宏", "葉啟田", "文夏", "鳳飛飛", "蔡琴", "蘇芮", "黃妃",
            "謝金燕", "羅時豐", "翁立友", "許富凱", "蕭煌奇", "朱海君",
            
            # 經典台語歌手
            "施文彬", "方瑞娥", "袁小迪", "秀蘭瑪雅", "孫協志", "王中平",
            "唐飛", "詹雅雯", "陳盈潔", "林淑蓉", "曾心梅", "陳一郎",
            "王瑞霞", "林良歡", "吳俊宏", "黃西田", "陳隨意", "康康",
            
            # 新台語
            "茄子蛋", "滅火器", "拍謝少年", "董事長樂團", "豬頭皮", "黃連煜",
            "林強", "伍佰", "陳明章", "黃妃", "謝宇威", "蕭賀碩",
            
            # 台語創作
            "陳建年", "胡德夫", "紀曉君", "張震嶽", "陳綺貞", "盧廣仲",
            "李英宏", "9m88", "魏如萱", "徐佳瑩", "艾怡良", "萬芳"
        ]
        
        # 香港歌手
        hong_kong = [
            # 四大天王及天后
            "劉德華", "張學友", "郭富城", "黎明", "陳奕迅", "容祖兒",
            "楊千嬅", "謝霆鋒", "古巨基", "陳慧琳", "鄭秀文", "關淑怡",
            "梅艷芳", "張國榮", "譚詠麟", "徐小鳳", "林子祥", "羅文",
            
            # 經典香港歌手
            "Beyond", "黃家駒", "黃家強", "黃貫中", "葉世榮", "達明一派",
            "太極樂隊", "溫拿", "草蜢", "許志安", "劉德華", "鄭伊健",
            "陳小春", "吳奇隆", "蘇永康", "李克勤", "張衛健", "鄭中基",
            
            # 新一代
            "陳柏宇", "方皓玟", "謝安琪", "何韻詩", "衛蘭", "鄧紫棋",
            "吳雨霏", "李幸倪", "馮允謙", "岑寧兒", "周柏豪", "張敬軒"
        ]
        
        # 大陸歌手
        mainland_china = [
            # 當紅歌手
            "周深", "毛不易", "李健", "薛之謙", "汪蘇瀧", "胡彥斌",
            "林志炫", "韓紅", "那英", "王菲", "孫楠", "譚維維",
            "張靚穎", "華晨宇", "鄧紫棋", "李榮浩", "陳粒", "房東的貓",
            
            # 經典歌手
            "刀郎", "鳳凰傳奇", "玖月奇蹟", "筷子兄弟", "羽泉", "水木年華",
            "縱貫線", "動力火車", "蘇打綠", "信樂團", "飛兒樂團",
            
            # 新生代
            "周筆暢", "李宇春", "張藝興", "易烊千璽", "王一博", "肖戰",
            "蔡徐坤", "范丞丞", "朱一龍", "王俊凱", "王源", "易烊千璽"
        ]
        
        # 樂團組合大全
        bands_groups = [
            # 台灣樂團
            "五月天", "蘇打綠", "F.I.R.", "S.H.E", "飛兒樂團", "信樂團",
            "脫拉庫", "董事長樂團", "滅火器", "茄子蛋", "草東沒有派對",
            "老王樂隊", "宇宙人", "八十八顆芭樂籽", "閃靈", "麋先生",
            "四分衛", "1976", "濁水溪公社", "血肉果汁機", "大支",
            "透明雜誌", "椅子樂團", "告五人", "持修", "9m88",
            
            # 香港樂團
            "Beyond", "達明一派", "太極樂隊", "溫拿", "草蜢", "軟硬天師",
            "at17", "my little airport", "RubberBand", "Dear Jane",
            
            # 大陸樂團
            "零點樂隊", "黑豹樂隊", "唐朝樂隊", "崔健", "竇唯", "何勇",
            "張楚", "新褲子樂隊", "萬能青年旅店", "刺猬樂隊", "重塑雕像的權利",
            "痛仰樂隊", "謝天笑", "左小祖咒", "李志", "宋冬野"
        ]
        
        # 60-70年代經典
        classic_60s_70s = [
            "鄧麗君", "白光", "姚蘇蓉", "崔苔青", "甄妮", "徐小鳳",
            "沈雁", "黃鶯鶯", "蔡琴", "蘇芮", "潘越雲", "蔡幸娟",
            "鳳飛飛", "高勝美", "林慧萍", "金智娟", "包娜娜", "林竹君"
        ]
        
        # 80-90年代黃金期
        golden_80s_90s = [
            "費玉清", "張雨生", "童安格", "姜育恆", "周華健", "王傑",
            "巫啟賢", "辛曉琪", "千百惠", "孟庭葦", "陳淑樺", "林憶蓮",
            "齊秦", "趙傳", "張宇", "伍思凱", "李宗盛", "羅大佑",
            "蔡琴", "蘇芮", "潘越雲", "萬芳", "黃小琥", "楊林"
        ]
        
        # 獨立音樂
        indie_alternative = [
            "拍謝少年", "老王樂隊", "草東沒有派對", "透明雜誌", "椅子樂團",
            "理想混蛋", "夕陽紅樂隊", "告五人", "持修", "雞蛋蒸肉餅",
            "美秀集團", "珂拉琪", "淺堤", "縱貫線", "逆流而上",
            "血肉果汁機", "濁水溪公社", "閃靈", "Chthonic"
        ]
        
        # 添加到對應分類
        self.singers_database['taiwan_mandarin'].update(taiwan_mandarin)
        self.singers_database['taiwan_hokkien'].update(taiwan_hokkien)
        self.singers_database['hong_kong'].update(hong_kong)
        self.singers_database['mainland_china'].update(mainland_china)
        self.singers_database['bands_groups'].update(bands_groups)
        self.singers_database['classic_60s_70s'].update(classic_60s_70s)
        self.singers_database['golden_80s_90s'].update(golden_80s_90s)
        self.singers_database['indie_alternative'].update(indie_alternative)
        
        # 添加星馬歌手
        singapore_malaysia = [
            "林俊傑", "孫燕姿", "蔡健雅", "陳潔儀", "Tanya蔡健雅", "阿杜",
            "林宇中", "By2", "謝和弦", "梁靜茹", "戴佩妮", "光良",
            "品冠", "巫啟賢", "王力宏", "陶喆", "張棟樑", "溫力銘"
        ]
        self.singers_database['singapore_malaysia'].update(singapore_malaysia)
        
        # 當代流行
        current_popular = [
            "告五人", "持修", "頑童MJ116", "韋禮安", "婁峻碩", "ØZI",
            "BCW", "Leo王", "Julia Wu", "魏嘉瑩", "9m88", "家家",
            "徐佳瑩", "戴愛玲", "艾怡良", "郁可唯", "楊乃文", "魏如萱",
            "周興哲", "高爾宣", "林哲熹", "鄧紫棋", "G.E.M."
        ]
        self.singers_database['current_popular'].update(current_popular)
        
        # 饒舌嘻哈
        rap_hiphop = [
            "頑童MJ116", "Leo王", "ØZI", "BCW", "大支", "熊仔",
            "國蛋", "蛋堡", "婁峻碩", "高爾宣", "OSHEN", "J.Sheon",
            "血肉果汁機", "陳珊妮", "春艷", "Barry Chen", "呂士軒"
        ]
        self.singers_database['rap_hiphop'].update(rap_hiphop)
        
        total_manual = sum(len(singers) for singers in self.singers_database.values())
        print(f"✅ 全面歌手資料添加完成，共 {total_manual} 位歌手")
    
    def add_ktv_popular_singers(self):
        """添加KTV熱門歌手"""
        print("🎤 添加KTV熱門歌手...")
        
        ktv_favorites = [
            # KTV必點天王天后
            "周杰倫", "林俊傑", "蔡依林", "張惠妹", "王力宏", "陶喆",
            "五月天", "蘇打綠", "S.H.E", "飛兒樂團", "羅志祥", "蕭敬騰",
            "田馥甄", "楊丞琳", "梁靜茹", "孫燕姿", "張韶涵", "陳綺貞",
            
            # KTV經典歌手
            "張學友", "劉德華", "陳奕迅", "Beyond", "黃家駒", "譚詠麟",
            "張國榮", "梅艷芳", "容祖兒", "楊千嬅", "鄧麗君", "費玉清",
            "童安格", "姜育恆", "周華健", "齊秦", "張雨生", "王傑",
            
            # 台語KTV經典
            "江蕙", "陳雷", "龍千玉", "黃乙玲", "張秀卿", "洪榮宏",
            "羅時豐", "葉啟田", "蔡小虎", "蔡秋鳳", "翁立友", "許富凱",
            
            # 新世代KTV寵兒  
            "告五人", "持修", "周興哲", "高爾宣", "韋禮安", "徐佳瑩",
            "家家", "戴愛玲", "艾怡良", "魏如萱", "9m88", "Julia Wu"
        ]
        
        # 分散到各個類別
        for singer in ktv_favorites:
            # 添加到最適合的類別
            if singer in ["江蕙", "陳雷", "龍千玉", "黃乙玲", "張秀卿"]:
                self.singers_database['taiwan_hokkien'].add(singer)
            elif singer in ["張學友", "劉德華", "陳奕迅", "Beyond"]:
                self.singers_database['hong_kong'].add(singer)
            elif singer in ["告五人", "持修", "周興哲", "高爾宣"]:
                self.singers_database['current_popular'].add(singer)
            else:
                self.singers_database['taiwan_mandarin'].add(singer)
    
    def fetch_more_wikipedia_data(self):
        """從更多維基百科分類獲取歌手"""
        print("\n🌐 從維基百科獲取更多歌手資料...")
        
        wikipedia_urls = {
            '華語流行音樂歌手': 'https://zh.wikipedia.org/zh-tw/Category:華語流行音樂歌手',
            '台灣華語流行歌手': 'https://zh.wikipedia.org/zh-tw/Category:台灣華語流行音樂歌手',
            '香港歌手': 'https://zh.wikipedia.org/zh-tw/Category:香港歌手',
            '台語歌手': 'https://zh.wikipedia.org/zh-tw/Category:閩南語歌手',
            '華語樂團': 'https://zh.wikipedia.org/zh-tw/Category:華語流行音樂團體',
            '台灣男歌手': 'https://zh.wikipedia.org/zh-tw/Category:台灣男歌手',
            '台灣女歌手': 'https://zh.wikipedia.org/zh-tw/Category:台灣女歌手',
            '中國大陸歌手': 'https://zh.wikipedia.org/zh-tw/Category:中华人民共和国歌手'
        }
        
        all_wikipedia_singers = set()
        
        for category_name, url in wikipedia_urls.items():
            print(f"📖 抓取 {category_name}...")
            
            try:
                response = self.session.get(url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 查找所有連結
                    links = soup.find_all('a')
                    category_singers = 0
                    
                    for link in links:
                        href = link.get('href', '')
                        if '/wiki/' in href and ':' not in href:
                            singer_name = link.get_text().strip()
                            
                            # 過濾條件更嚴格
                            if (len(singer_name) >= 2 and len(singer_name) <= 20 and
                                not singer_name.startswith(('分類', 'Category', '維基', 'Wiki')) and
                                not any(char in singer_name for char in ['/', '(', ')', '[', ']', ':', '?', '!']) and
                                not singer_name.isdigit()):
                                
                                all_wikipedia_singers.add(singer_name)
                                category_singers += 1
                    
                    print(f"   ✅ 從 {category_name} 找到 {category_singers} 位歌手")
                else:
                    print(f"   ❌ 無法訪問 {category_name}")
                    
                time.sleep(2)  # 避免請求過頻
                
            except Exception as e:
                print(f"   ❌ 抓取 {category_name} 失敗: {e}")
        
        # 將維基百科歌手分散添加到各類別
        for singer in all_wikipedia_singers:
            self.singers_database['taiwan_mandarin'].add(singer)
        
        print(f"✅ 維基百科抓取完成，共找到 {len(all_wikipedia_singers)} 位額外歌手")
        
        return all_wikipedia_singers
    
    def clean_and_deduplicate_enhanced(self):
        """增強版清理和去重"""
        print("\n🧹 增強版清理和去重...")
        
        all_singers_before = sum(len(singers) for singers in self.singers_database.values())
        
        # 先合併所有歌手找重複
        all_unique_singers = set()
        for category, singers in self.singers_database.items():
            all_unique_singers.update(singers)
        
        # 清理每個類別
        for category, singers in self.singers_database.items():
            cleaned_singers = set()
            
            for singer in singers:
                # 更嚴格的清理
                cleaned_name = singer.strip()
                cleaned_name = re.sub(r'[^\w\s\u4e00-\u9fff.&-]', '', cleaned_name)
                
                # 長度和內容檢查
                if (2 <= len(cleaned_name) <= 25 and
                    not cleaned_name.isdigit() and
                    not cleaned_name.startswith('Category') and
                    cleaned_name not in ['', ' ', '　']):
                    cleaned_singers.add(cleaned_name)
            
            self.singers_database[category] = cleaned_singers
        
        all_singers_after = sum(len(singers) for singers in self.singers_database.values())
        unique_singers = len(all_unique_singers)
        
        print(f"✅ 清理完成：{all_singers_before} → {all_singers_after} 位歌手")
        print(f"🎵 去重後實際歌手數：{unique_singers} 位")
    
    def create_enhanced_search_keywords(self):
        """創建增強版搜尋關鍵字"""
        print("\n🔍 創建增強版搜尋關鍵字資料庫...")
        
        # 合併所有歌手
        all_singers = set()
        for singers in self.singers_database.values():
            all_singers.update(singers)
        
        # 創建搜尋關鍵字變體
        search_keywords = set(all_singers)
        
        # 添加更多變體
        for singer in list(all_singers):
            # 英文名處理
            if '.' in singer:
                search_keywords.add(singer.replace('.', ''))
                search_keywords.add(singer.replace('.', ' '))
            
            # 空格處理
            if ' ' in singer:
                search_keywords.add(singer.replace(' ', ''))
            
            # 特殊符號處理
            if '&' in singer:
                search_keywords.add(singer.replace('&', ''))
                search_keywords.add(singer.replace('&', 'and'))
            
            # 樂團/組合變體
            if singer.endswith('樂團'):
                search_keywords.add(singer.replace('樂團', ''))
            if singer.endswith('樂隊'):
                search_keywords.add(singer.replace('樂隊', ''))
        
        # 創建完整資料庫
        enhanced_database = {
            'singers_by_category': {k: sorted(list(v)) for k, v in self.singers_database.items()},
            'all_singers': sorted(list(all_singers)),
            'search_keywords': sorted(list(search_keywords)),
            'statistics': {
                'total_singers': len(all_singers),
                'total_keywords': len(search_keywords),
                'taiwan_mandarin': len(self.singers_database['taiwan_mandarin']),
                'taiwan_hokkien': len(self.singers_database['taiwan_hokkien']),
                'hong_kong': len(self.singers_database['hong_kong']),
                'mainland_china': len(self.singers_database['mainland_china']),
                'singapore_malaysia': len(self.singers_database['singapore_malaysia']),
                'bands_groups': len(self.singers_database['bands_groups']),
                'classic_60s_70s': len(self.singers_database['classic_60s_70s']),
                'golden_80s_90s': len(self.singers_database['golden_80s_90s']),
                'new_millennium': len(self.singers_database['new_millennium']),
                'current_popular': len(self.singers_database['current_popular']),
                'indie_alternative': len(self.singers_database['indie_alternative']),
                'folk_acoustic': len(self.singers_database['folk_acoustic']),
                'rock_metal': len(self.singers_database['rock_metal']),
                'electronic_pop': len(self.singers_database['electronic_pop']),
                'rap_hiphop': len(self.singers_database['rap_hiphop'])
            },
            'category_descriptions': {
                'taiwan_mandarin': '台灣華語流行歌手',
                'taiwan_hokkien': '台語/閩南語歌手',
                'hong_kong': '香港歌手',
                'mainland_china': '中國大陸歌手',
                'singapore_malaysia': '新加坡馬來西亞歌手',
                'bands_groups': '樂團組合',
                'classic_60s_70s': '60-70年代經典歌手',
                'golden_80s_90s': '80-90年代黃金期歌手',
                'new_millennium': '2000年代歌手',
                'current_popular': '當代流行歌手',
                'indie_alternative': '獨立另類音樂',
                'folk_acoustic': '民謠創作歌手',
                'rock_metal': '搖滾重金屬',
                'electronic_pop': '電子流行音樂',
                'rap_hiphop': '饒舌嘻哈'
            }
        }
        
        print(f"✅ 增強版關鍵字資料庫創建完成：{len(search_keywords)} 個搜尋關鍵字")
        
        return enhanced_database
    
    def save_enhanced_database(self, database, filename):
        """儲存增強版資料庫"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(database, f, ensure_ascii=False, indent=2)
            print(f"💾 增強版歌手資料庫已保存到: {filename}")
        except Exception as e:
            print(f"❌ 儲存失敗: {e}")
    
    def print_enhanced_statistics(self, database):
        """顯示增強版統計資訊"""
        print("\n📊 增強版歌手資料庫統計:")
        print("=" * 50)
        
        stats = database['statistics']
        descriptions = database['category_descriptions']
        
        print("🌏 地區分布:")
        print(f"   🇹🇼 台灣華語: {stats['taiwan_mandarin']} 位")
        print(f"   🎭 台語歌手: {stats['taiwan_hokkien']} 位")
        print(f"   🇭🇰 香港歌手: {stats['hong_kong']} 位")
        print(f"   🇨🇳 大陸歌手: {stats['mainland_china']} 位")
        print(f"   🇸🇬 星馬歌手: {stats['singapore_malaysia']} 位")
        
        print("\n📅 年代分布:")
        print(f"   📻 60-70年代: {stats['classic_60s_70s']} 位")
        print(f"   💽 80-90年代: {stats['golden_80s_90s']} 位")
        print(f"   💿 2000年代: {stats['new_millennium']} 位")
        print(f"   🎵 當代流行: {stats['current_popular']} 位")
        
        print("\n🎸 音樂類型:")
        print(f"   🎸 樂團組合: {stats['bands_groups']} 個")
        print(f"   🎨 獨立音樂: {stats['indie_alternative']} 位")
        print(f"   🎤 饒舌嘻哈: {stats['rap_hiphop']} 位")
        
        print(f"\n📝 總計:")
        print(f"   🎵 歌手總數: {stats['total_singers']} 位")
        print(f"   🔍 搜尋關鍵字: {stats['total_keywords']} 個")
        
        # 顯示各類別樣本
        print(f"\n🌟 各類別代表歌手:")
        
        sample_categories = ['taiwan_mandarin', 'taiwan_hokkien', 'hong_kong', 'mainland_china', 'bands_groups']
        
        for category in sample_categories:
            if category in database['singers_by_category']:
                singers = database['singers_by_category'][category]
                description = descriptions.get(category, category)
                print(f"\n   📂 {description} (共{len(singers)}位):")
                
                # 顯示前10位作為樣本
                for i, singer in enumerate(singers[:10], 1):
                    print(f"      {i:2d}. {singer}")
                
                if len(singers) > 10:
                    print(f"      ... 還有 {len(singers) - 10} 位")

def main():
    builder = EnhancedSingerDatabaseBuilder()
    
    print("🎵 開始建構增強版華語歌手搜尋關鍵字資料庫")
    print("=" * 70)
    
    # 1. 添加全面歌手資料
    builder.add_comprehensive_singers()
    
    # 2. 添加KTV熱門歌手
    builder.add_ktv_popular_singers()
    
    # 3. 從維基百科獲取更多資料
    builder.fetch_more_wikipedia_data()
    
    # 4. 增強版清理和去重
    builder.clean_and_deduplicate_enhanced()
    
    # 5. 創建增強版關鍵字資料庫
    enhanced_database = builder.create_enhanced_search_keywords()
    
    # 6. 儲存資料庫
    filename = f"enhanced_singer_keywords_database_{time.strftime('%Y%m%d_%H%M%S')}.json"
    builder.save_enhanced_database(enhanced_database, filename)
    
    # 7. 顯示統計
    builder.print_enhanced_statistics(enhanced_database)
    
    print(f"\n🎯 增強版資料庫總結:")
    print(f"   📦 已建立包含 {enhanced_database['statistics']['total_singers']} 位歌手的完整資料庫")
    print(f"   🔍 共產生 {enhanced_database['statistics']['total_keywords']} 個搜尋關鍵字")
    print(f"   🏷️ 涵蓋 {len([k for k,v in enhanced_database['statistics'].items() if isinstance(v, int) and v > 0])} 個分類")
    print(f"   💾 資料已儲存至 {filename}")
    print(f"\n🚀 現在可以用這個大幅增強的資料庫測試 KTV 網站搜尋功能！")

if __name__ == "__main__":
    main()