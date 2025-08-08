#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌手名單發現系統 - 從多個來源獲取華語歌手名單
"""

import requests
import json
import time
import random
from datetime import datetime
import re

class SingerDiscovery:
    def __init__(self):
        self.discovered_singers = set()
        self.singer_sources = {}
        
    def get_taiwanese_popular_singers(self):
        """台灣流行歌手名單 - 手工整理的高品質清單"""
        return {
            "天王天后級": [
                "周杰倫", "蔡依林", "林俊傑", "張惠妹", "王力宏", "陶喆", "孫燕姿", "梁靜茹",
                "田馥甄", "楊丞琳", "蕭亞軒", "張韶涵", "鄧紫棋", "林宥嘉", "張學友", "劉德華",
                "郭富城", "黎明", "張國榮", "梅艷芳", "鄧麗君", "蔡琴", "鳳飛飛", "費玉清"
            ],
            "五月天世代": [
                "五月天", "蘇打綠", "信樂團", "動力火車", "F.I.R", "飛兒樂團", "S.H.E", "飛輪海",
                "八三夭", "茄子蛋", "滅火器", "四分衛", "黑色柳丁", "董事長樂團", "脫拉庫", "1976"
            ],
            "新生代藝人": [
                "告五人", "茄子蛋", "持修", "ØZI", "高爾宣", "LEO王", "9m88", "吳卓源", "血肉果汁機",
                "理想混蛋", "康士坦的變化球", "傷心欲絕", "壞特", "孫盛希", "陳零九", "顏人中",
                "宋念宇", "Crispy脆樂團", "deca joins", "原子邦妮", "漂流出口", "落日飛車",
                "透明雜誌", "巨獸搖滾", "麵包車", "老王樂隊", "草東沒有派對"
            ],
            "創作歌手": [
                "李宗盛", "羅大佑", "伍佰", "張宇", "庾澄慶", "齊秦", "張雨生", "黃品源",
                "黃小琥", "辛曉琪", "萬芳", "林憶蓮", "齊豫", "蘇芮", "潘越雲", "黃乙玲", "江蕙"
            ],
            "港星經典": [
                "張國榮", "梅艷芳", "陳百強", "譚詠麟", "張學友", "劉德華", "郭富城", "黎明",
                "王菲", "容祖兒", "陳奕迅", "古巨基", "李克勤", "Beyond", "達明一派"
            ],
            "大陸歌手": [
                "那英", "毛阿敏", "韓紅", "李玟", "刀郎", "庾澄慶", "孫楠", "韋唯", "屠洪剛",
                "騰格爾", "朴樹", "許巍", "汪峰", "羽泉", "水木年華", "零點樂隊"
            ],
            "2024-2025新星": [
                "告五人", "茄子蛋", "持修", "ØZI", "高爾宣", "血肉果汁機", "理想混蛋", "康士坦的變化球",
                "9m88", "吳卓源", "壞特", "孫盛希", "陳零九", "顏人中", "宋念宇", "李友廷",
                "婁峻碩", "呂士軒", "謝震廷", "晨悠", "許含光", "柯智棠", "魏如萱", "盧廣仲"
            ]
        }
    
    def get_singers_from_music_charts(self):
        """從音樂排行榜獲取歌手名單"""
        # 這裡可以擴展為真實的API調用
        chart_singers = [
            # KKBOX 熱門
            "告五人", "茄子蛋", "持修", "ØZI", "高爾宣", "韋禮安", "李友廷", "婁峻碩",
            "謝震廷", "晨悠", "許含光", "柯智棠", "魏如萱", "盧廣仲", "蘇明淵", "徐佳瑩",
            
            # Apple Music 華語熱門
            "周杰倫", "蔡依林", "林俊傑", "張惠妹", "鄧紫棋", "林宥嘉", "田馥甄", "楊丞琳",
            "孫燕姿", "梁靜茹", "蕭亞軒", "張韶涵", "王力宏", "陶喆", "五月天", "蘇打綠",
            
            # Spotify 華語
            "告五人", "茄子蛋", "持修", "血肉果汁機", "理想混蛋", "9m88", "吳卓源", "壞特",
            "孫盛希", "陳零九", "顏人中", "宋念宇", "LEO王", "高爾宣", "ØZI", "康士坦的變化球"
        ]
        return list(set(chart_singers))
    
    def get_singers_from_genres(self):
        """按音樂類型獲取歌手"""
        genre_singers = {
            "華語流行": [
                "周杰倫", "蔡依林", "林俊傑", "張惠妹", "王力宏", "陶喆", "孫燕姿", "梁靜茹",
                "田馥甄", "楊丞琳", "蕭亞軒", "張韶涵", "鄧紫棋", "林宥嘉", "徐佳瑩", "韋禮安"
            ],
            "華語搖滾": [
                "五月天", "蘇打綠", "信樂團", "動力火車", "F.I.R", "飛兒樂團", "八三夭", "茄子蛋",
                "滅火器", "四分衛", "黑色柳丁", "董事長樂團", "血肉果汁機", "理想混蛋", "草東沒有派對"
            ],
            "華語民謠": [
                "盧廣仲", "魏如萱", "柯智棠", "許含光", "晨悠", "謝震廷", "李友廷", "蘇明淵",
                "持修", "告五人", "老王樂隊", "原子邦妮", "漂流出口", "落日飛車", "透明雜誌"
            ],
            "華語嘻哈": [
                "LEO王", "高爾宣", "ØZI", "壞特", "婁峻碩", "呂士軒", "9m88", "康士坦的變化球",
                "血肉果汁機", "理想混蛋", "傷心欲絕", "deca joins"
            ],
            "華語R&B": [
                "陶喆", "王力宏", "林俊傑", "韋禮安", "李友廷", "9m88", "吳卓源", "孫盛希",
                "陳零九", "顏人中", "宋念宇", "ØZI", "持修"
            ]
        }
        
        all_genre_singers = []
        for genre, singers in genre_singers.items():
            all_genre_singers.extend(singers)
        
        return list(set(all_genre_singers))
    
    def get_singers_by_decades(self):
        """按年代獲取歌手"""
        decade_singers = {
            "1980年代": [
                "鄧麗君", "鳳飛飛", "蔡琴", "齊豫", "蘇芮", "潘越雲", "黃乙玲", "江蕙",
                "張國榮", "梅艷芳", "陳百強", "譚詠麟", "羅文", "徐小鳳"
            ],
            "1990年代": [
                "張學友", "劉德華", "郭富城", "黎明", "王菲", "那英", "毛阿敏", "韓紅",
                "李宗盛", "羅大佑", "伍佰", "張宇", "庾澄慶", "齊秦", "張雨生", "黃品源"
            ],
            "2000年代": [
                "周杰倫", "蔡依林", "林俊傑", "張惠妹", "王力宏", "陶喆", "孫燕姿", "梁靜茹",
                "五月天", "蘇打綠", "S.H.E", "飛輪海", "F.I.R", "信樂團", "動力火車"
            ],
            "2010年代": [
                "田馥甄", "楊丞琳", "蕭亞軒", "張韶涵", "鄧紫棋", "林宥嘉", "徐佳瑩", "韋禮安",
                "八三夭", "茄子蛋", "滅火器", "四分衛", "黑色柳丁", "董事長樂團"
            ],
            "2020年代": [
                "告五人", "持修", "ØZI", "高爾宣", "LEO王", "9m88", "吳卓源", "血肉果汁機",
                "理想混蛋", "康士坦的變化球", "壞特", "孫盛希", "陳零九", "顏人中", "宋念宇"
            ]
        }
        
        all_decade_singers = []
        for decade, singers in decade_singers.items():
            all_decade_singers.extend(singers)
        
        return list(set(all_decade_singers))
    
    def discover_all_singers(self):
        """綜合所有來源發現歌手"""
        print("🎤 開始歌手名單發現...")
        
        # 收集所有來源的歌手
        all_singers = set()
        
        # 1. 台灣流行歌手
        taiwanese_singers = self.get_taiwanese_popular_singers()
        for category, singers in taiwanese_singers.items():
            print(f"  📋 {category}: {len(singers)} 位歌手")
            all_singers.update(singers)
            self.singer_sources.update({singer: f"台灣流行-{category}" for singer in singers})
        
        # 2. 音樂排行榜
        chart_singers = self.get_singers_from_music_charts()
        print(f"  📊 音樂排行榜: {len(chart_singers)} 位歌手")
        all_singers.update(chart_singers)
        for singer in chart_singers:
            if singer not in self.singer_sources:
                self.singer_sources[singer] = "音樂排行榜"
        
        # 3. 音樂類型分類
        genre_singers = self.get_singers_from_genres()
        print(f"  🎵 音樂類型: {len(genre_singers)} 位歌手")
        all_singers.update(genre_singers)
        for singer in genre_singers:
            if singer not in self.singer_sources:
                self.singer_sources[singer] = "音樂類型分類"
        
        # 4. 年代分類
        decade_singers = self.get_singers_by_decades()
        print(f"  📅 年代分類: {len(decade_singers)} 位歌手")
        all_singers.update(decade_singers)
        for singer in decade_singers:
            if singer not in self.singer_sources:
                self.singer_sources[singer] = "年代分類"
        
        print(f"\n🎉 總共發現 {len(all_singers)} 位不重複歌手")
        return sorted(list(all_singers))
    
    def save_singer_list(self, singers):
        """儲存歌手名單"""
        singer_data = {
            "發現時間": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "歌手總數": len(singers),
            "歌手清單": []
        }
        
        for singer in singers:
            singer_data["歌手清單"].append({
                "歌手名稱": singer,
                "來源": self.singer_sources.get(singer, "未知"),
                "收錄狀態": "待爬蟲"
            })
        
        with open('discovered_singers.json', 'w', encoding='utf-8') as f:
            json.dump(singer_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 歌手名單已儲存到 discovered_singers.json")
        return singer_data
    
    def generate_priority_list(self, singers):
        """生成優先爬蟲清單"""
        # 按照重要性排序
        priority_categories = [
            "天王天后級", "五月天世代", "新生代藝人", "2024-2025新星",
            "創作歌手", "華語流行", "華語搖滾", "音樂排行榜"
        ]
        
        priority_singers = []
        processed = set()
        
        for category in priority_categories:
            for singer in singers:
                source = self.singer_sources.get(singer, "")
                if category in source and singer not in processed:
                    priority_singers.append(singer)
                    processed.add(singer)
        
        # 加入剩餘歌手
        for singer in singers:
            if singer not in processed:
                priority_singers.append(singer)
        
        return priority_singers

def main():
    print("🔍 歌手名單發現系統")
    print("=" * 50)
    
    discovery = SingerDiscovery()
    
    # 發現所有歌手
    all_singers = discovery.discover_all_singers()
    
    # 儲存歌手名單
    singer_data = discovery.save_singer_list(all_singers)
    
    # 生成優先清單
    priority_list = discovery.generate_priority_list(all_singers)
    
    print(f"\n📋 優先爬蟲清單 (前20位):")
    for i, singer in enumerate(priority_list[:20], 1):
        source = discovery.singer_sources.get(singer, "未知")
        print(f"  {i:2d}. {singer:8s} ({source})")
    
    # 儲存優先清單
    with open('priority_singers.txt', 'w', encoding='utf-8') as f:
        for singer in priority_list:
            f.write(f"{singer}\n")
    
    print(f"\n💡 使用建議:")
    print(f"1. 查看完整清單: cat discovered_singers.json")
    print(f"2. 開始爬蟲: ./run_singer_scraper.sh")
    print(f"3. 優先清單: cat priority_singers.txt")
    
    return all_singers

if __name__ == "__main__":
    main()