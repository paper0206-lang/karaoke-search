#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面平衡歌手資料庫建構器
大幅擴充各個分類，創建平衡的歌手資料庫
目標：讓每個分類都有豐富的歌手數量
"""

import json
import time
import re
from collections import defaultdict

class ComprehensiveSingerDatabaseBuilder:
    def __init__(self):
        # 平衡的歌手資料庫分類
        self.singers_database = {
            'taiwan_mandarin': set(),    # 台灣華語歌手 (目標：400-500位)
            'taiwan_hokkien': set(),     # 台語歌手 (目標：200-300位) 
            'hong_kong': set(),          # 香港歌手 (目標：200-300位)
            'mainland_china': set(),     # 大陸歌手 (目標：200-300位)
            'singapore_malaysia': set(), # 星馬歌手 (目標：50-100位)
            'bands_groups': set(),       # 樂團組合 (目標：100-150位)
            'classic_60s_70s': set(),    # 60-70年代經典 (目標：50-80位)
            'golden_80s_90s': set(),     # 80-90年代黃金期 (目標：80-120位)
            'current_popular': set(),    # 當代流行 (目標：100-150位)
            'indie_alternative': set(),  # 獨立音樂 (目標：80-100位)
            'rap_hiphop': set()          # 饒舌嘻哈 (目標：50-80位)
        }
    
    def add_massive_taiwan_hokkien_singers(self):
        """大幅擴充台語歌手"""
        print("🎭 大幅擴充台語歌手資料庫...")
        
        # 經典台語天王天后
        classic_hokkien = [
            "江蕙", "張秀卿", "陳雷", "黃乙玲", "龍千玉", "蔡秋鳳", "蔡小虎",
            "洪榮宏", "葉啟田", "文夏", "鳳飛飛", "蔡琴", "蘇芮", "黃妃",
            "謝金燕", "羅時豐", "翁立友", "許富凱", "蕭煌奇", "朱海君",
            "施文彬", "方瑞娥", "袁小迪", "秀蘭瑪雅", "孫協志", "王中平",
            "唐飛", "詹雅雯", "陳盈潔", "林淑蓉", "曾心梅", "陳一郎"
        ]
        
        # 台語老牌歌手
        veteran_hokkien = [
            "王瑞霞", "林良歡", "吳俊宏", "黃西田", "陳隨意", "康康",
            "黃乙玲", "蔡幸娟", "陳思安", "葉勝欽", "陳百潭", "陳芬蘭",
            "林淑容", "高向鵬", "黃思婷", "余天", "余苑綺", "白冰冰",
            "張玲", "張蓉蓉", "郭金發", "陳小雲", "陳美鳳", "沈文程",
            "江志豐", "向蕙玲", "陳淑萍", "李茂山", "李亞明", "金門王",
            "李炳輝", "黃克林", "陳昇", "伍佰", "豬頭皮", "黃連煜"
        ]
        
        # 新台語世代
        modern_hokkien = [
            "茄子蛋", "滅火器", "拍謝少年", "董事長樂團", "林強",
            "陳明章", "黃妃", "謝宇威", "蕭賀碩", "陳建年", "胡德夫",
            "紀曉君", "張震嶽", "李英宏", "魏如萱", "盧廣仲",
            "家家", "徐佳瑩", "艾怡良", "萬芳", "陳綺貞", "9m88"
        ]
        
        # 台語創作歌手
        hokkien_writers = [
            "李坤城", "林垂立", "陳維祥", "黃敏", "謝志峰", "陳百強",
            "廖偉志", "許景淳", "陳國華", "王夢麟", "施孝榮", "潘越雲",
            "楊弦", "胡德夫", "李建復", "趙樹海", "韓正皓", "馬兆駿"
        ]
        
        # 台語樂團
        hokkien_bands = [
            "董事長樂團", "滅火器", "茄子蛋", "拍謝少年", "血肉果汁機",
            "濁水溪公社", "四分衛", "1976", "脫拉庫", "豬頭皮",
            "黃連煜", "林強", "陳明章", "陳昇", "伍佰"
        ]
        
        # 台語女歌手
        hokkien_female = [
            "江蕙", "張秀卿", "黃乙玲", "龍千玉", "蔡秋鳳", "黃妃",
            "謝金燕", "詹雅雯", "陳盈潔", "林淑蓉", "曾心梅", "王瑞霞",
            "陳思安", "黃思婷", "張玲", "張蓉蓉", "陳小雲", "陳美鳳",
            "向蕙玲", "陳淑萍", "李亞明", "鳳飛飛", "蔡琴", "蘇芮",
            "方瑞娥", "秀蘭瑪雅", "朱海君", "陳芬蘭", "蔡幸娟"
        ]
        
        # 金曲獎台語歌手
        golden_melody_hokkien = [
            "蕭煌奇", "洪榮宏", "蔡振南", "陳建瑋", "謝銘祐", "蘇明淵",
            "許富凱", "翁立友", "羅時豐", "葉啟田", "施文彬", "陳雷",
            "王中平", "唐飛", "袁小迪", "蔡小虎"
        ]
        
        # 合併所有台語歌手
        all_hokkien = set()
        all_hokkien.update(classic_hokkien)
        all_hokkien.update(veteran_hokkien)
        all_hokkien.update(modern_hokkien)
        all_hokkien.update(hokkien_writers)
        all_hokkien.update(hokkien_bands)
        all_hokkien.update(hokkien_female)
        all_hokkien.update(golden_melody_hokkien)
        
        self.singers_database['taiwan_hokkien'].update(all_hokkien)
        
        print(f"✅ 台語歌手擴充完成：{len(all_hokkien)} 位")
    
    def add_massive_hong_kong_singers(self):
        """大幅擴充香港歌手"""
        print("🇭🇰 大幅擴充香港歌手資料庫...")
        
        # 四大天王及超級巨星
        superstars = [
            "劉德華", "張學友", "郭富城", "黎明", "陳奕迅", "容祖兒",
            "楊千嬅", "謝霆鋒", "古巨基", "陳慧琳", "鄭秀文", "關淑怡"
        ]
        
        # 經典香港歌手
        classics = [
            "張國榮", "譚咏麟", "梅艷芳", "徐小鳳", "林子祥", "羅文",
            "許冠傑", "關正傑", "陳百強", "鄭少秋", "汪明荃", "甄妮",
            "葉麗儀", "林憶蓮", "王菲", "彭羚", "黃凱芹", "呂方",
            "張明敏", "蘇永康", "李克勤", "張衛健", "鄭中基", "許志安"
        ]
        
        # 經典樂團
        classic_bands = [
            "Beyond", "黃家駒", "黃家強", "黃貫中", "葉世榮", "達明一派",
            "太極樂隊", "溫拿", "草蜢", "軟硬天師", "at17", "my little airport"
        ]
        
        # 新一代香港歌手
        new_generation = [
            "陳柏宇", "方皓玟", "謝安琪", "何韻詩", "衛蘭", "鄧紫棋",
            "吳雨霏", "李幸倪", "馮允謙", "岑寧兒", "周柏豪", "張敬軒",
            "C AllStar", "RubberBand", "Dear Jane", "麥浚龍", "王嘉爾",
            "陳卓賢", "姜濤", "盧瀚霆", "楊千嬅", "楊愛瑾"
        ]
        
        # 經典女歌手
        female_singers = [
            "梅艷芳", "徐小鳳", "汪明荃", "甄妮", "葉麗儀", "林憶蓮",
            "王菲", "彭羚", "容祖兒", "楊千嬅", "陳慧琳", "鄭秀文",
            "關淑怡", "陳慧嫻", "李蕙敏", "黃凱芹", "周慧敏", "王馨平",
            "湯寶如", "劉美君", "葉蒨文", "林姍姍", "呂珊"
        ]
        
        # 實力派歌手
        powerhouse_singers = [
            "林家謙", "陳蕾", "Serrini", "鄭欣宜", "張天賦", "馮允謙",
            "岑寧兒", "何韻詩", "謝安琪", "衛蘭", "吳雨霏", "李幸倪",
            "麥浚龍", "陳奐仁", "側田", "方大同", "24Herbs", "農夫"
        ]
        
        # 70-80年代歌手
        golden_era = [
            "許冠傑", "關正傑", "羅文", "陳百強", "張明敏", "鄭少秋",
            "汪明荃", "徐小鳳", "甄妮", "葉麗儀", "林子祥", "譚咏麟"
        ]
        
        # 90年代巨星
        nineties_stars = [
            "劉德華", "張學友", "郭富城", "黎明", "張國榮", "梅艷芳",
            "王菲", "林憶蓮", "彭羚", "陳慧嫻", "周慧敏", "李蕙敏"
        ]
        
        # 2000年代新星
        millennium_stars = [
            "陳奕迅", "容祖兒", "楊千嬅", "謝霆鋒", "古巨基", "陳慧琳",
            "鄭秀文", "關淑怡", "蘇永康", "李克勤", "張衛健", "許志安"
        ]
        
        # 合併所有香港歌手
        all_hk = set()
        all_hk.update(superstars)
        all_hk.update(classics)
        all_hk.update(classic_bands)
        all_hk.update(new_generation)
        all_hk.update(female_singers)
        all_hk.update(powerhouse_singers)
        all_hk.update(golden_era)
        all_hk.update(nineties_stars)
        all_hk.update(millennium_stars)
        
        self.singers_database['hong_kong'].update(all_hk)
        
        print(f"✅ 香港歌手擴充完成：{len(all_hk)} 位")
    
    def add_massive_mainland_china_singers(self):
        """大幅擴充大陸歌手"""
        print("🇨🇳 大幅擴充大陸歌手資料庫...")
        
        # 一線流行歌手
        top_tier = [
            "周深", "毛不易", "李健", "薛之謙", "汪蘇瀧", "胡彥斌",
            "林志炫", "韓紅", "那英", "王菲", "孫楠", "譚維維",
            "張靚穎", "華晨宇", "鄧紫棋", "李榮浩", "陳粒", "房東的貓"
        ]
        
        # 經典老牌歌手
        veteran_singers = [
            "刀郎", "鳳凰傳奇", "玖月奇蹟", "筷子兄弟", "羽泉", "水木年華",
            "縱貫線", "零點樂隊", "黑豹樂隊", "唐朝樂隊", "崔健", "竇唯",
            "何勇", "張楚", "許巍", "鄭鈞", "汪峰", "樸樹"
        ]
        
        # 新生代偶像
        new_idols = [
            "周筆暢", "李宇春", "張藝興", "易烊千璽", "王一博", "肖戰",
            "蔡徐坤", "范丞丞", "朱一龍", "王俊凱", "王源", "鹿晗",
            "吳亦凡", "黃子韜", "張碧晨", "袁婭維", "徐佳瑩", "鄧紫棋"
        ]
        
        # 實力創作歌手
        singer_songwriters = [
            "許嵩", "汪蘇泷", "徐良", "莊心妍", "金志文", "平安",
            "李代沫", "張磊", "陳楚生", "蘇醒", "王錚亮", "尚雯婕",
            "吉克雋逸", "曾軼可", "安琥", "黃征", "信", "張傑"
        ]
        
        # 民謠創作
        folk_singers = [
            "李志", "宋冬野", "趙雷", "馬頔", "陳粒", "房東的貓",
            "好妹妹樂隊", "萬曉利", "張瑪莉", "二手玫瑰", "左小祖咒",
            "謝天笑", "痛仰樂隊", "刺猬樂隊", "重塑雕像的權利"
        ]
        
        # 搖滾樂團
        rock_bands = [
            "新褲子樂隊", "萬能青年旅店", "刺猬樂隊", "重塑雕像的權利",
            "痛仰樂隊", "謝天笑", "左小祖咒", "二手玫瑰", "扭曲機器",
            "反光鏡樂隊", "子曰秋野", "P.K.14", "木馬樂隊"
        ]
        
        # 電子音樂
        electronic_artists = [
            "尚雯婕", "曾軼可", "3ASiC", "譚維維", "張靚穎", "徐夢圓",
            "薩頂頂", "朱哲琴", "龔琳娜", "常石磊"
        ]
        
        # 說唱歌手
        rap_artists = [
            "GAI", "PG One", "紅花會", "嘻哈四重奏", "AR劉夫陽",
            "王以太", "艾福傑尼", "法老", "滿舒克", "孫八一",
            "丁太昇", "OBI", "小青龍", "黃旭"
        ]
        
        # 女歌手
        female_singers = [
            "鄧紫棋", "張靚穎", "韓紅", "那英", "王菲", "譚維維",
            "周筆暢", "李宇春", "張碧晨", "袁婭維", "尚雯婕", "吉克雋逸",
            "曾軼可", "陳粒", "薩頂頂", "朱哲琴", "龔琳娜", "莊心妍"
        ]
        
        # 歌手2024參賽者
        singer_2024 = [
            "那英", "楊丞琳", "汪蘇泷", "海來阿木", "孫楠", "譚維維",
            "二手玫瑰", "Chanté Moore", "Faouzia Ouihya"
        ]
        
        # 合併所有大陸歌手
        all_mainland = set()
        all_mainland.update(top_tier)
        all_mainland.update(veteran_singers)
        all_mainland.update(new_idols)
        all_mainland.update(singer_songwriters)
        all_mainland.update(folk_singers)
        all_mainland.update(rock_bands)
        all_mainland.update(electronic_artists)
        all_mainland.update(rap_artists)
        all_mainland.update(female_singers)
        all_mainland.update(singer_2024)
        
        self.singers_database['mainland_china'].update(all_mainland)
        
        print(f"✅ 大陸歌手擴充完成：{len(all_mainland)} 位")
    
    def add_massive_bands_and_groups(self):
        """大幅擴充樂團組合"""
        print("🎸 大幅擴充樂團組合資料庫...")
        
        # 台灣樂團
        taiwan_bands = [
            "五月天", "蘇打綠", "F.I.R.", "飛兒樂團", "信樂團", "脫拉庫",
            "董事長樂團", "滅火器", "茄子蛋", "草東沒有派對", "老王樂隊",
            "宇宙人", "八十八顆芭樂籽", "閃靈", "麋先生", "四分衛",
            "1976", "濁水溪公社", "血肉果汁機", "大支", "透明雜誌",
            "椅子樂團", "告五人", "持修", "理想混蛋", "夕陽紅樂隊",
            "雞蛋蒸肉餅", "美秀集團", "珂拉琪", "淺堤", "逆流而上"
        ]
        
        # 香港樂團
        hk_bands = [
            "Beyond", "達明一派", "太極樂隊", "溫拿", "草蜢", "軟硬天師",
            "at17", "my little airport", "RubberBand", "Dear Jane",
            "C AllStar", "農夫", "24Herbs", "Mr.", "糖兄妹", "Yellow!"
        ]
        
        # 大陸樂團
        mainland_bands = [
            "零點樂隊", "黑豹樂隊", "唐朝樂隊", "新褲子樂隊", "萬能青年旅店",
            "刺猬樂隊", "重塑雕像的權利", "痛仰樂隊", "二手玫瑰", "扭曲機器",
            "反光鏡樂隊", "子曰秋野", "P.K.14", "木馬樂隊", "鳳凰傳奇",
            "水木年華", "羽泉", "筷子兄弟", "玖月奇蹟", "好妹妹樂隊"
        ]
        
        # 女子組合
        girl_groups = [
            "S.H.E", "Twins", "2moro", "By2", "Dream Girls", "Popu Lady",
            "AKB48 Team TP", "宇宙少女", "火箭少女101", "THE9", "硬糖少女303"
        ]
        
        # 男子組合  
        boy_groups = [
            "小虎隊", "優客李林", "動力火車", "F4", "飛輪海", "SpeXial",
            "EXO-M", "TFBOYS", "時代少年團", "INTO1", "NINE PERCENT"
        ]
        
        # 搖滾金屬樂團
        rock_metal = [
            "閃靈", "Chthonic", "四分衛", "濁水溪公社", "血肉果汁機",
            "黑豹樂隊", "唐朝樂隊", "痛仰樂隊", "二手玫瑰", "扭曲機器",
            "Beyond", "太極樂隊", "達明一派"
        ]
        
        # 獨立樂團
        indie_bands = [
            "草東沒有派對", "老王樂隊", "透明雜誌", "椅子樂團", "告五人",
            "理想混蛋", "夕陽紅樂隊", "雞蛋蒸肉餅", "美秀集團", "珂拉琪",
            "my little airport", "at17", "萬能青年旅店", "刺猬樂隊"
        ]
        
        # 合併所有樂團
        all_bands = set()
        all_bands.update(taiwan_bands)
        all_bands.update(hk_bands)
        all_bands.update(mainland_bands)
        all_bands.update(girl_groups)
        all_bands.update(boy_groups)
        all_bands.update(rock_metal)
        all_bands.update(indie_bands)
        
        self.singers_database['bands_groups'].update(all_bands)
        
        print(f"✅ 樂團組合擴充完成：{len(all_bands)} 個")
    
    def add_classic_and_golden_era_singers(self):
        """擴充經典和黃金年代歌手"""
        print("⭐ 擴充經典和黃金年代歌手...")
        
        # 60-70年代經典
        classic_60s_70s = [
            "鄧麗君", "白光", "姚蘇蓉", "崔苔青", "甄妮", "徐小鳳",
            "沈雁", "黃鶯鶯", "蔡琴", "蘇芮", "潘越雲", "蔡幸娟",
            "鳳飛飛", "高勝美", "林慧萍", "金智娟", "包娜娜", "林竹君",
            "許冠傑", "關正傑", "羅文", "林子祥", "譚詠麟", "陳百強",
            "文夏", "洪一峰", "楊三郎", "吳晉淮", "葉啟田", "郭金發"
        ]
        
        # 80-90年代黃金期
        golden_80s_90s = [
            "費玉清", "張雨生", "童安格", "姜育恆", "周華健", "王傑",
            "巫啟賢", "辛曉琪", "千百惠", "孟庭葦", "陳淑樺", "林憶蓮",
            "齊秦", "趙傳", "張宇", "伍思凱", "李宗盛", "羅大佑",
            "蔡琴", "蘇芮", "潘越雲", "萬芳", "黃小琥", "楊林",
            "張信哲", "劉德華", "張學友", "郭富城", "黎明", "陳奕迅",
            "王菲", "林憶蓮", "彭羚", "陳慧嫻", "周慧敏", "李蕙敏",
            "張國榮", "譚詠麟", "梅艷芳", "Beyond", "黃家駒"
        ]
        
        self.singers_database['classic_60s_70s'].update(classic_60s_70s)
        self.singers_database['golden_80s_90s'].update(golden_80s_90s)
        
        print(f"✅ 經典歌手擴充完成：60-70年代 {len(classic_60s_70s)} 位，80-90年代 {len(golden_80s_90s)} 位")
    
    def add_current_and_indie_singers(self):
        """擴充當代流行和獨立音樂歌手"""
        print("🎵 擴充當代流行和獨立音樂歌手...")
        
        # 當代流行歌手
        current_popular = [
            "告五人", "持修", "頑童MJ116", "韋禮安", "婁峻碩", "ØZI",
            "BCW", "Leo王", "Julia Wu", "魏嘉瑩", "9m88", "家家",
            "徐佳瑩", "戴愛玲", "艾怡良", "郁可唯", "楊乃文", "魏如萱",
            "周興哲", "高爾宣", "林哲熹", "鄧紫棋", "G.E.M.", "畢書盡",
            "李榮浩", "薛之謙", "毛不易", "周深", "華晨宇", "張藝興"
        ]
        
        # 獨立音樂
        indie_alternative = [
            "拍謝少年", "老王樂隊", "草東沒有派對", "透明雜誌", "椅子樂團",
            "理想混蛋", "夕陽紅樂隊", "告五人", "持修", "雞蛋蒸肉餅",
            "美秀集團", "珂拉琪", "淺堤", "縱貫線", "逆流而上",
            "血肉果汁機", "濁水溪公社", "閃靈", "Chthonic", "四分衛",
            "my little airport", "at17", "萬能青年旅店", "刺猬樂隊",
            "重塑雕像的權利", "陳粒", "房東的貓", "李志", "宋冬野"
        ]
        
        # 饒舌嘻哈
        rap_hiphop = [
            "頑童MJ116", "Leo王", "ØZI", "BCW", "大支", "熊仔",
            "國蛋", "蛋堡", "婁峻碩", "高爾宣", "OSHEN", "J.Sheon",
            "血肉果汁機", "陳珊妮", "春艷", "Barry Chen", "呂士軒",
            "GAI", "PG One", "紅花會", "AR劉夫陽", "王以太",
            "艾福傑尼", "法老", "滿舒克", "孫八一", "24Herbs", "農夫"
        ]
        
        self.singers_database['current_popular'].update(current_popular)
        self.singers_database['indie_alternative'].update(indie_alternative)
        self.singers_database['rap_hiphop'].update(rap_hiphop)
        
        print(f"✅ 當代和獨立歌手擴充完成：當代流行 {len(current_popular)} 位，獨立音樂 {len(indie_alternative)} 位，饒舌嘻哈 {len(rap_hiphop)} 位")
    
    def add_singapore_malaysia_singers(self):
        """擴充星馬歌手"""
        print("🇸🇬🇲🇾 擴充星馬歌手...")
        
        singapore_malaysia = [
            "林俊傑", "孫燕姿", "蔡健雅", "陳潔儀", "Tanya蔡健雅", "阿杜",
            "林宇中", "By2", "謝和弦", "梁靜茹", "戴佩妮", "光良",
            "品冠", "巫啟賢", "王力宏", "陶喆", "張棟樑", "溫力銘",
            "林志穎", "陳曉東", "李聖傑", "張震", "林峰", "杜德偉",
            "許美靜", "陳慧嫻", "黃湘怡", "鄭秀文", "陳松伶", "宣萱",
            "楊千樺", "容祖兒", "何韻詩", "衛蘭", "鄧紫棋", "關心妍"
        ]
        
        self.singers_database['singapore_malaysia'].update(singapore_malaysia)
        
        print(f"✅ 星馬歌手擴充完成：{len(singapore_malaysia)} 位")
    
    def add_comprehensive_taiwan_mandarin(self):
        """保持台灣華語歌手的豐富度"""
        print("🇹🇼 保持台灣華語歌手豐富度...")
        
        # 從清理後的資料庫中選取重要的台灣華語歌手
        taiwan_mandarin_essentials = [
            "周杰倫", "蔡依林", "張惠妹", "王力宏", "陶喆", "林俊傑", "蕭敬騰",
            "田馥甄", "楊丞琳", "羅志祥", "潘瑋柏", "周興哲", "高爾宣", "A-Lin",
            "陳綺貞", "張韶涵", "梁靜茹", "孫燕姿", "李玖哲", "品冠", "光良",
            "信", "伍佰", "庾澄慶", "張信哲", "彭佳慧", "林宥嘉", "盧廣仲",
            "徐佳瑩", "家家", "戴愛玲", "艾怡良", "魏如萱", "9m88", "Julia Wu",
            "告五人", "持修", "韋禮安", "婁峻碩", "BCW", "Leo王", "ØZI"
        ]
        
        self.singers_database['taiwan_mandarin'].update(taiwan_mandarin_essentials)
        
        print(f"✅ 台灣華語歌手：{len(taiwan_mandarin_essentials)} 位核心歌手")
    
    def create_comprehensive_database(self):
        """創建全面平衡的資料庫"""
        print("\n🔍 創建全面平衡的歌手資料庫...")
        
        # 合併所有歌手並去重
        all_singers = set()
        for singers in self.singers_database.values():
            all_singers.update(singers)
        
        # 創建搜尋關鍵字
        search_keywords = set(all_singers)
        
        # 添加關鍵字變體
        for singer in list(all_singers):
            if ' ' in singer:
                search_keywords.add(singer.replace(' ', ''))
            if '.' in singer:
                search_keywords.add(singer.replace('.', ''))
                search_keywords.add(singer.replace('.', ' '))
            if '&' in singer:
                search_keywords.add(singer.replace('&', ''))
        
        # 創建完整資料庫
        comprehensive_database = {
            'singers_by_category': {k: sorted(list(v)) for k, v in self.singers_database.items()},
            'all_singers': sorted(list(all_singers)),
            'search_keywords': sorted(list(search_keywords)),
            'statistics': {
                'total_singers': len(all_singers),
                'total_keywords': len(search_keywords),
                **{category: len(singers) for category, singers in self.singers_database.items()}
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
                'current_popular': '當代流行歌手',
                'indie_alternative': '獨立另類音樂',
                'rap_hiphop': '饒舌嘻哈'
            }
        }
        
        return comprehensive_database
    
    def save_database(self, database, filename):
        """儲存資料庫"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(database, f, ensure_ascii=False, indent=2)
            print(f"💾 全面歌手資料庫已保存到: {filename}")
        except Exception as e:
            print(f"❌ 儲存失敗: {e}")
    
    def print_comprehensive_statistics(self, database):
        """顯示全面統計"""
        print("\n📊 全面平衡歌手資料庫統計:")
        print("=" * 60)
        
        stats = database['statistics']
        
        print("🌏 各地區歌手分布:")
        region_stats = [
            ('taiwan_mandarin', '台灣華語', '🇹🇼'),
            ('taiwan_hokkien', '台語歌手', '🎭'),
            ('hong_kong', '香港歌手', '🇭🇰'),
            ('mainland_china', '大陸歌手', '🇨🇳'),
            ('singapore_malaysia', '星馬歌手', '🇸🇬')
        ]
        
        for category, name, emoji in region_stats:
            count = stats.get(category, 0)
            print(f"   {emoji} {name}: {count} 位")
        
        print("\n🎸 音樂類型分布:")
        type_stats = [
            ('bands_groups', '樂團組合', '🎸'),
            ('indie_alternative', '獨立音樂', '🎨'),
            ('rap_hiphop', '饒舌嘻哈', '🎤'),
            ('current_popular', '當代流行', '🎵')
        ]
        
        for category, name, emoji in type_stats:
            count = stats.get(category, 0)
            print(f"   {emoji} {name}: {count} 位")
        
        print("\n📅 年代分布:")
        era_stats = [
            ('classic_60s_70s', '60-70年代', '📻'),
            ('golden_80s_90s', '80-90年代', '💽')
        ]
        
        for category, name, emoji in era_stats:
            count = stats.get(category, 0)
            print(f"   {emoji} {name}: {count} 位")
        
        print(f"\n📝 總計:")
        print(f"   🎵 歌手總數: {stats['total_singers']} 位")
        print(f"   🔍 搜尋關鍵字: {stats['total_keywords']} 個")
        
        # 顯示平衡度分析
        counts = [stats.get(cat, 0) for cat, _, _ in region_stats + type_stats + era_stats]
        max_count = max(counts)
        min_count = min(counts)
        avg_count = sum(counts) / len(counts)
        
        print(f"\n📊 資料庫平衡度:")
        print(f"   📈 最大分類: {max_count} 位")
        print(f"   📉 最小分類: {min_count} 位")
        print(f"   📊 平均分類: {avg_count:.1f} 位")
        print(f"   🎯 平衡指數: {(min_count/max_count)*100:.1f}%")

def main():
    builder = ComprehensiveSingerDatabaseBuilder()
    
    print("🎵 開始建構全面平衡的歌手資料庫")
    print("=" * 70)
    
    # 1. 保持台灣華語歌手豐富度
    builder.add_comprehensive_taiwan_mandarin()
    
    # 2. 大幅擴充台語歌手
    builder.add_massive_taiwan_hokkien_singers()
    
    # 3. 大幅擴充香港歌手
    builder.add_massive_hong_kong_singers()
    
    # 4. 大幅擴充大陸歌手
    builder.add_massive_mainland_china_singers()
    
    # 5. 大幅擴充樂團組合
    builder.add_massive_bands_and_groups()
    
    # 6. 擴充經典和黃金年代歌手
    builder.add_classic_and_golden_era_singers()
    
    # 7. 擴充當代和獨立音樂歌手
    builder.add_current_and_indie_singers()
    
    # 8. 擴充星馬歌手
    builder.add_singapore_malaysia_singers()
    
    # 9. 創建完整資料庫
    comprehensive_database = builder.create_comprehensive_database()
    
    # 10. 儲存資料庫
    filename = f"comprehensive_balanced_singer_database_{time.strftime('%Y%m%d_%H%M%S')}.json"
    builder.save_database(comprehensive_database, filename)
    
    # 11. 顯示統計
    builder.print_comprehensive_statistics(comprehensive_database)
    
    print(f"\n🎯 全面平衡資料庫建構完成:")
    print(f"   📦 總歌手數: {comprehensive_database['statistics']['total_singers']} 位")
    print(f"   🔍 搜尋關鍵字: {comprehensive_database['statistics']['total_keywords']} 個")
    print(f"   🏷️ 涵蓋分類: {len([k for k,v in comprehensive_database['statistics'].items() if isinstance(v, int) and v > 0])} 個")
    print(f"   💾 檔案位置: {filename}")
    print(f"\n🚀 現在各個分類都有豐富的歌手資源，可以開始測試 KTV 搜尋功能！")

if __name__ == "__main__":
    main()