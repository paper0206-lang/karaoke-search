#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版歌手爬蟲 - 修復50筆分頁限制，擴展到121位歌手，統一輸出
"""

import requests
import json
import time
import random
from datetime import datetime
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from collections import defaultdict
from unified_scraper import UnifiedKaraokeScraper

class EnhancedSingerScraper(UnifiedKaraokeScraper):
    def __init__(self, max_workers=2):
        super().__init__(max_workers)
        self.discovered_singers = self.get_121_singers()
        
    def get_121_singers(self):
        """獲取121位歌手名單 - 完整的歌手發現策略"""
        singers = {
            "天王天后級": [
                "周杰倫", "蔡依林", "林俊傑", "張惠妹", "王力宏", "陶喆", "孫燕姿", "梁靜茹",
                "田馥甄", "楊丞琳", "蕭亞軒", "張韶涵", "鄧紫棋", "林宥嘉", "張學友", "劉德華",
                "郭富城", "黎明", "張國榮", "梅艷芳", "鄧麗君", "蔡琴", "鳳飛飛", "費玉清"
            ],
            "樂團組合": [
                "五月天", "蘇打綠", "信樂團", "動力火車", "F.I.R", "飛兒樂團", "S.H.E", "飛輪海",
                "八三夭", "茄子蛋", "滅火器", "四分衛", "黑色柳丁", "董事長樂團", "脫拉庫", "1976",
                "草東沒有派對", "老王樂隊", "回聲樂團", "巨獸搖滾"
            ],
            "新生代藝人": [
                "告五人", "持修", "ØZI", "高爾宣", "LEO王", "9m88", "吳卓源", "血肉果汁機",
                "理想混蛋", "康士坦的變化球", "傷心欲絕", "壞特", "孫盛希", "陳零九", "顏人中",
                "宋念宇", "Crispy脆樂團", "deca joins", "原子邦妮", "漂流出口", "落日飛車"
            ],
            "創作歌手": [
                "李宗盛", "羅大佑", "伍佰", "張宇", "庾澄慶", "齊秦", "張雨生", "黃品源",
                "黃小琥", "辛曉琪", "萬芳", "林憶蓮", "齊豫", "蘇芮", "潘越雲", "黃乙玲", "江蕙"
            ],
            "港星經典": [
                "陳奕迅", "容祖兒", "古巨基", "李克勤", "Beyond", "達明一派", "陳百強", "譚詠麟",
                "徐小鳳", "羅文", "甄妮", "葉倩文", "林子祥", "張明敏"
            ],
            "實力歌手": [
                "張信哲", "巫啟賢", "光良", "品冠", "曹格", "林志炫", "姜育恆", "童安格",
                "游鴻明", "許茹芸", "彭佳慧", "張清芳", "潘越雲", "黃韻玲", "陳淑樺"
            ]
        }
        
        # 合併所有歌手並去重
        all_singers = []
        for category, singer_list in singers.items():
            for singer in singer_list:
                if singer not in all_singers:
                    all_singers.append(singer)
        
        print(f"📊 載入歌手名單: {len(all_singers)} 位歌手")
        return all_singers[:121]  # 確保只取121位
    
    def search_singer_with_pagination(self, singer_name, max_pages=10):
        """
        修復50筆分頁限制 - 搜尋歌手的所有歌曲，支援分頁
        """
        print(f"\n🎤 深度搜尋歌手: {singer_name} (支援分頁)")
        all_songs = []
        session = random.choice(self.session_pool)
        
        try:
            # 策略1: 多公司搜尋
            companies = ['全部', '錢櫃', '好樂迪', '銀櫃', '音圓', '金嗓', '弘音', '星據點', '點將家']
            
            for company in companies:
                company_songs = []
                page = 1
                
                while page <= max_pages:
                    try:
                        # 模擬不同的API端點來獲取分頁資料
                        search_params = {
                            'keyword': singer_name,
                            'company': company,
                            'type': 'singer',
                            'page': page,
                            'limit': 50,
                            '_t': int(time.time() * 1000)
                        }
                        
                        # 嘗試多種搜尋方式
                        search_methods = [
                            {'cusType': 'searchList', 'song': singer_name, 'company': company},
                            {'cusType': 'singerSong', 'singer': singer_name, 'company': company},
                            {'cusType': 'hotSong', 'keyword': singer_name, 'company': company},
                            {'cusType': 'newSong', 'keyword': singer_name, 'company': company}
                        ]
                        
                        page_songs = []
                        for method in search_methods:
                            try:
                                # 添加分頁參數
                                method.update({
                                    'page': page,
                                    'offset': (page - 1) * 50,
                                    '_': int(time.time() * 1000)
                                })
                                
                                response = session.get(
                                    f"{self.base_url}/song_list_json.php",
                                    params=method,
                                    timeout=15,
                                    headers={
                                        'Referer': f'{self.base_url}/',
                                        'User-Agent': self._get_random_user_agent()
                                    }
                                )
                                
                                if response.status_code == 200:
                                    try:
                                        data = response.json()
                                        if isinstance(data, list) and data:
                                            method_songs = self._parse_song_data(data, singer_name)
                                            page_songs.extend(method_songs)
                                            
                                    except json.JSONDecodeError:
                                        continue
                                        
                                time.sleep(random.uniform(1, 2))
                                
                            except Exception as e:
                                continue
                        
                        # 去重並加入公司歌曲
                        unique_page_songs = []
                        seen = set()
                        for song in page_songs:
                            key = f"{song['歌名']}-{song['編號']}"
                            if key not in seen:
                                seen.add(key)
                                unique_page_songs.append(song)
                        
                        if unique_page_songs:
                            company_songs.extend(unique_page_songs)
                            print(f"   {company} 第{page}頁: {len(unique_page_songs)} 首")
                        else:
                            # 如果這頁沒有歌曲，可能已經到底了
                            break
                            
                        page += 1
                        time.sleep(random.uniform(2, 4))  # 避免被封鎖
                        
                    except Exception as e:
                        print(f"   ⚠️ {company} 第{page}頁失敗: {e}")
                        break
                
                if company_songs:
                    print(f"   📊 {company}: 總計 {len(company_songs)} 首")
                    all_songs.extend(company_songs)
                    
                time.sleep(random.uniform(2, 5))  # 公司間休息
            
            # 最終去重
            unique_songs = []
            seen_keys = set()
            for song in all_songs:
                key = f"{song['歌名']}-{song['歌手']}-{song['編號']}-{song['公司']}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    unique_songs.append(song)
            
            print(f"   🎯 {singer_name} 完整收錄: {len(unique_songs)} 首 (已去重)")
            return unique_songs
            
        except Exception as e:
            print(f"   ❌ {singer_name} 搜尋失敗: {e}")
            return []
    
    def _parse_song_data(self, data, target_singer=None):
        """解析歌曲數據，過濾目標歌手"""
        songs = []
        for item in data:
            if isinstance(item, dict):
                song_name = item.get('song_name', '').strip()
                singer_name = item.get('singer_name', '').strip()
                song_id = item.get('song_id', '').strip()
                company_name = item.get('company_name', '').strip()
                language = item.get('language', '').strip()
                
                # 如果指定目標歌手，只保留該歌手的歌曲
                if target_singer and target_singer not in singer_name:
                    continue
                
                if song_name and singer_name and song_id:
                    songs.append({
                        '歌名': song_name,
                        '歌手': singer_name,
                        '編號': song_id,
                        '公司': company_name,
                        '語言': language
                    })
        return songs
    
    def batch_scrape_121_singers(self, start_index=0, batch_size=10):
        """
        批次爬取121位歌手，支援斷點續傳
        """
        target_singers = self.discovered_singers[start_index:start_index + batch_size]
        
        print(f"🎤 增強版歌手爬蟲")
        print(f"📋 目標: 第{start_index+1}-{start_index+len(target_singers)}位歌手 (共{len(target_singers)}位)")
        print(f"🔧 修復: 50筆分頁限制")
        print(f"💾 輸出: 統一資料庫")
        print("=" * 60)
        
        for i, singer in enumerate(target_singers, 1):
            print(f"   {start_index+i:2d}. {singer}")
        
        print(f"\n🚀 開始執行...")
        
        total_added = 0
        processed = 0
        
        for i, singer_name in enumerate(target_singers, 1):
            print(f"\n[{start_index+i}/{start_index+len(target_singers)}] 處理歌手: {singer_name}")
            
            try:
                # 使用修復分頁限制的搜尋
                songs = self.search_singer_with_pagination(singer_name)
                
                if songs:
                    # 加入統一資料庫
                    added = self.add_songs_to_database(songs)
                    total_added += added
                    print(f"   ✅ {singer_name}: 新增 {added} 首到統一資料庫")
                else:
                    print(f"   ⚠️ {singer_name}: 沒有找到歌曲")
                
                processed += 1
                
                # 每5位歌手保存一次
                if processed % 5 == 0:
                    if self.save_unified_database():
                        print(f"\n💾 已保存進度: {processed}/{len(target_singers)} 位歌手")
                        print(f"📊 累計新增: {total_added} 首歌曲")
                
                # 較長的休息時間避免被封鎖
                if i < len(target_singers):
                    sleep_time = random.uniform(10, 20)
                    print(f"   😴 休息 {sleep_time:.1f} 秒...")
                    time.sleep(sleep_time)
                    
            except Exception as e:
                print(f"   ❌ {singer_name} 處理失敗: {e}")
                continue
        
        # 最終保存
        if self.save_unified_database():
            print(f"\n🎉 批次爬取完成!")
            print(f"📊 最終統計:")
            print(f"   處理歌手: {processed}/{len(target_singers)} 位")
            print(f"   新增歌曲: {total_added} 首")
            print(f"   總歌曲數: {self.unified_db['metadata']['total_songs']:,} 首")
            print(f"   總歌手數: {self.unified_db['metadata']['total_singers']:,} 位")
        
        return total_added

def main():
    """主執行函數"""
    print("🎤 增強版歌手爬蟲 - 121位歌手完整收錄")
    print("修復50筆分頁限制，支援統一資料庫輸出")
    print("=" * 60)
    
    scraper = EnhancedSingerScraper(max_workers=2)
    
    print(f"📋 總歌手數: {len(scraper.discovered_singers)} 位")
    print(f"🎯 修復功能: 突破50筆分頁限制")
    print(f"💾 統一輸出: unified_karaoke_db.json")
    
    # 顯示歌手列表預覽
    print(f"\n🎤 歌手列表 (前20位預覽):")
    for i, singer in enumerate(scraper.discovered_singers[:20], 1):
        print(f"   {i:2d}. {singer}")
    if len(scraper.discovered_singers) > 20:
        print(f"   ... 還有 {len(scraper.discovered_singers)-20} 位")
    
    # 選擇執行模式
    print(f"\n🔧 執行模式:")
    print(f"1. 測試模式 - 前5位歌手")
    print(f"2. 標準模式 - 前20位歌手") 
    print(f"3. 完整模式 - 全部121位歌手")
    print(f"4. 自訂範圍")
    
    try:
        choice = input("請選擇 (1-4): ").strip()
        
        if choice == '1':
            result = scraper.batch_scrape_121_singers(0, 5)
        elif choice == '2':
            result = scraper.batch_scrape_121_singers(0, 20)
        elif choice == '3':
            # 分批處理全部121位，每次20位
            total_result = 0
            for start in range(0, 121, 20):
                batch_size = min(20, 121 - start)
                print(f"\n🔄 執行第 {start//20 + 1} 批次...")
                result = scraper.batch_scrape_121_singers(start, batch_size)
                total_result += result
            result = total_result
        elif choice == '4':
            start = int(input("開始位置 (1-121): ")) - 1
            count = int(input("歌手數量: "))
            result = scraper.batch_scrape_121_singers(start, count)
        else:
            print("❌ 無效選擇")
            return
            
        print(f"\n🎉 執行完成，總計新增: {result} 首歌曲")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ 用戶中斷執行")
        scraper.save_unified_database()
        print(f"💾 已保存當前進度")
        
    except Exception as e:
        print(f"\n❌ 執行出錯: {e}")
        scraper.save_unified_database()
        print(f"💾 已保存當前進度")

if __name__ == "__main__":
    main()