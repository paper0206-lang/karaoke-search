#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高級多線程卡拉OK歌曲爬蟲
使用智能關鍵字生成和多線程並行搜尋
"""

import requests
import json
import time
import random
from urllib.parse import quote
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from collections import defaultdict
import string
import itertools

class AdvancedKaraokeScraper:
    def __init__(self, max_workers=3, max_songs=15000):
        self.max_workers = max_workers
        self.max_songs = max_songs
        self.session_pool = []
        self.all_songs = {}
        self.search_stats = defaultdict(int)
        self.lock = threading.Lock()
        self.base_url = "https://song.corp.com.tw"
        
        # 初始化session池
        for _ in range(max_workers):
            session = requests.Session()
            session.headers.update({
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://song.corp.com.tw/',
                'X-Requested-With': 'XMLHttpRequest',
            })
            self.session_pool.append(session)
    
    def _get_random_user_agent(self):
        """獲取隨機User-Agent"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/605.1.15',
        ]
        return random.choice(agents)
    
    def generate_smart_keywords(self):
        """生成智能關鍵字列表 - 2025年優化版"""
        keywords = []
        
        # 0. 2025年熱門關鍵字 (優先搜尋)
        keywords_2025 = {
            "2025新歌": [
                "2025", "新歌", "熱門", "最新", "流行", "爆紅", "夯歌", "當紅", "熱播",
                "排行榜", "冠軍", "單曲", "專輯", "首發", "新專輯", "新作", "話題"
            ],
            "2025熱門藝人": [
                "告五人", "茄子蛋", "持修", "ØZI", "高爾宣", "LEO王", "9m88", "吳卓源",
                "血肉果汁機", "理想混蛋", "康士坦的變化球", "傷心欲絕", "壞特", "孫盛希",
                "陳零九", "顏人中", "宋念宇", "Crispy脆樂團", "deca joins", "原子邦妮"
            ],
            "2025音樂風格": [
                "療癒系", "治癒系", "放鬆", "chill", "lofi", "indie", "民謠", "搖滾",
                "電音", "嘻哈", "R&B", "爵士", "藍調", "古風", "國風", "城市民謠"
            ],
            "2025音樂主題": [
                "夏日", "海邊", "公路", "旅行", "青春", "校園", "畢業", "告白",
                "分手", "療傷", "勵志", "正能量", "夜晚", "星空", "月光", "日落"
            ]
        }
        
        # 優先加入2025年關鍵字
        for category, words in keywords_2025.items():
            keywords.extend(words)
        
        # 1. 歌手數據庫 - 大幅擴展
        singers = {
            "華語巨星": [
                "周杰倫", "蔡依林", "林俊傑", "張惠妹", "王力宏", "陶喆", "孫燕姿", "梁靜茹",
                "田馥甄", "楊丞琳", "蕭亞軒", "張韶涵", "鄧紫棋", "林宥嘉", "蘇打綠", "五月天",
                "S.H.E", "飛輪海", "F.I.R", "信樂團", "動力火車", "張信哲", "劉德華", "張學友",
                "郭富城", "黎明", "張國榮", "梅艷芳", "鄧麗君", "蔡琴", "鳳飛飛", "費玉清"
            ],
            "新生代藝人": [
                "告五人", "ØZI", "吳卓源", "9m88", "持修", "血肉果汁機", "康士坦的變化球",
                "理想混蛋", "Crispy脆樂團", "deca joins", "傷心欲絕", "高爾宣", "LEO王",
                "壞特", "孫盛希", "陳零九", "顏人中", "宋念宇", "草東沒有派對", "老王樂隊",
                "原子邦妮", "漂流出口", "落日飛車", "透明雜誌", "巨獸搖滾", "麵包車"
            ],
            "經典歌手": [
                "李宗盛", "羅大佑", "伍佰", "張宇", "庾澄慶", "齊秦", "張雨生", "黃品源",
                "黃小琥", "辛曉琪", "萬芳", "林憶蓮", "齊豫", "蘇芮", "潘越雲", "黃乙玲",
                "江蕙", "張清芳", "王菲", "那英", "毛阿敏", "韓紅", "李玟", "容祖兒"
            ],
            "樂團組合": [
                "蘇打綠", "五月天", "信樂團", "F.I.R", "飛兒樂團", "八三夭", "茄子蛋",
                "滅火器", "四分衛", "黑色柳丁", "董事長樂團", "脫拉庫", "1976", "回聲樂團"
            ]
        }
        
        # 2. 歌曲類型和情感關鍵字
        song_themes = {
            "情感主題": [
                "愛情", "思念", "想念", "回憶", "青春", "夢想", "希望", "孤單", "寂寞",
                "快樂", "傷心", "幸福", "痛苦", "離別", "重逢", "承諾", "背叛", "原諒"
            ],
            "生活主題": [
                "朋友", "家人", "媽媽", "爸爸", "故鄉", "家鄉", "學校", "工作", "旅行",
                "下雨", "晴天", "星空", "月亮", "太陽", "海邊", "山上", "城市", "鄉村"
            ],
            "時代關鍵字": [
                "2025", "新歌", "熱門", "最新", "2024", "2023", "2022", "經典", "懷舊", "復古",
                "流行", "搖滾", "民謠", "R&B", "嘻哈", "電子", "爵士", "藍調", "話題歌曲", "病毒式"
            ]
        }
        
        # 3. 數字和符號組合
        numbers_symbols = {
            "數字": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            "中文數字": ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"],
            "符號": ["心", "星", "夜", "天", "地", "風", "雨", "雪", "花", "樹"]
        }
        
        # 4. 地名和文化關鍵字
        locations_culture = {
            "地名": [
                "台北", "高雄", "台中", "台南", "桃園", "新竹", "嘉義", "台東", "花蓮",
                "宜蘭", "基隆", "彰化", "雲林", "屏東", "澎湖", "金門", "馬祖"
            ],
            "文化詞彙": [
                "夜市", "老街", "廟會", "節日", "春節", "中秋", "端午", "七夕", "元宵",
                "生日", "畢業", "結婚", "相遇", "告白", "分手", "重逢"
            ]
        }
        
        # 組合所有關鍵字
        for category in [singers, song_themes, locations_culture]:
            for subcategory, words in category.items():
                keywords.extend(words)
        
        # 5. 生成組合關鍵字
        combinations = []
        
        # 數字組合
        for num in numbers_symbols["數字"] + numbers_symbols["中文數字"]:
            for symbol in numbers_symbols["符號"]:
                combinations.append(f"{num}{symbol}")
                combinations.append(f"{symbol}{num}")
        
        # 情感+時間組合
        emotions = song_themes["情感主題"][:10]
        times = ["夜", "日", "春", "夏", "秋", "冬", "晨", "晚"]
        for emotion in emotions:
            for time in times:
                combinations.append(f"{emotion}{time}")
                combinations.append(f"{time}{emotion}")
        
        keywords.extend(combinations)
        
        # 6. 常用單字（高頻詞）
        common_chars = [
            "愛", "心", "夢", "情", "想", "念", "思", "憶", "淚", "笑", "歌", "舞",
            "風", "雨", "雪", "花", "月", "星", "天", "地", "水", "火", "山", "海",
            "紅", "藍", "白", "黑", "金", "銀", "綠", "紫", "黃", "粉", "橙", "灰"
        ]
        keywords.extend(common_chars)
        
        # 7. 英文關鍵字
        english_words = [
            "love", "heart", "dream", "night", "day", "star", "moon", "sun", "sky",
            "sea", "fire", "wind", "rain", "snow", "flower", "tree", "home", "way",
            "time", "life", "song", "music", "dance", "baby", "girl", "boy", "you", "me"
        ]
        keywords.extend(english_words)
        
        # 去重並隨機排序
        keywords = list(set(keywords))
        random.shuffle(keywords)
        
        print(f"🎯 生成 {len(keywords)} 個關鍵字")
        return keywords
    
    def search_single_keyword(self, keyword, session_id):
        """單個關鍵字搜尋 - 支援多頁結果"""
        try:
            session = self.session_pool[session_id % len(self.session_pool)]
            all_results = []
            total_new_songs = 0
            
            # 嘗試多種搜尋方式以獲取更多結果
            search_methods = [
                {'company': '全部', 'cusType': 'searchList', 'keyword': keyword},
                {'company': '錢櫃', 'cusType': 'searchList', 'keyword': keyword},
                {'company': '好樂迪', 'cusType': 'searchList', 'keyword': keyword},
                {'company': '音圓', 'cusType': 'searchList', 'keyword': keyword},
                {'company': '金嗓', 'cusType': 'searchList', 'keyword': keyword}
            ]
            
            for method_params in search_methods:
                try:
                    url = f"{self.base_url}/api/song.aspx"
                    
                    # 隨機延遲避免被封鎖
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    response = session.get(url, params=method_params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if isinstance(data, list) and data:
                            all_results.extend(data)
                            
                except Exception as e:
                    continue  # 如果某個方法失敗，繼續嘗試其他方法
            
            # 去重並處理所有結果
            seen_songs = set()
            unique_results = []
            for song in all_results:
                song_key = f"{song.get('name', '')}-{song.get('singer', '')}-{song.get('code', '')}"
                if song_key not in seen_songs:
                    seen_songs.add(song_key)
                    unique_results.append(song)
            
            # 加入到總資料庫
            with self.lock:
                for song in unique_results:
                    song_id = f"{song.get('name', '')}-{song.get('singer', '')}-{song.get('code', '')}"
                    if song_id not in self.all_songs and song.get('name'):
                        self.all_songs[song_id] = {
                            '歌名': song.get('name', ''),
                            '歌手': song.get('singer', ''),
                            '編號': song.get('code', ''),
                            '公司': song.get('company', ''),
                            '語言': song.get('lang', ''),
                            '性別': song.get('sex', '')
                        }
                        total_new_songs += 1
                
                self.search_stats[keyword] = len(unique_results)
            
            if unique_results:
                return f"🔍 {keyword}: 找到 {len(unique_results)} 首，新增 {total_new_songs} 首 (總計: {len(self.all_songs)})"
            else:
                return f"⚠️ {keyword}: 無結果"
                
        except Exception as e:
            return f"💥 {keyword}: {str(e)}"
    
    def save_progress(self):
        """儲存進度"""
        try:
            songs_list = list(self.all_songs.values())
            with open('public/songs_simplified.json', 'w', encoding='utf-8') as f:
                json.dump(songs_list, f, ensure_ascii=False, indent=2)
            
            return len(songs_list)
        except Exception as e:
            print(f"❌ 儲存失敗: {e}")
            return 0
    
    def run_scraper(self):
        """執行多線程爬蟲"""
        # 載入現有資料
        try:
            with open('public/songs_simplified.json', 'r', encoding='utf-8') as f:
                existing_songs = json.load(f)
            self.all_songs = {f"{s['歌名']}-{s['歌手']}-{s['編號']}": s for s in existing_songs}
            print(f"📚 載入現有歌曲: {len(self.all_songs)} 首")
        except:
            print("📚 從空開始建立資料庫")
        
        # 生成關鍵字
        keywords = self.generate_smart_keywords()
        
        start_time = datetime.now()
        print(f"🚀 開始多線程爬蟲，目標: {self.max_songs} 首歌曲")
        print(f"👥 並行線程數: {self.max_workers}")
        print(f"📅 開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        completed_searches = 0
        
        # 使用線程池執行
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交任務
            futures = []
            for i, keyword in enumerate(keywords):
                if len(self.all_songs) >= self.max_songs:
                    break
                
                future = executor.submit(self.search_single_keyword, keyword, i)
                futures.append(future)
            
            # 處理結果
            for future in as_completed(futures):
                if len(self.all_songs) >= self.max_songs:
                    break
                
                try:
                    result = future.result()
                    print(result)
                    completed_searches += 1
                    
                    # 每50次搜尋儲存一次
                    if completed_searches % 50 == 0:
                        saved_count = self.save_progress()
                        print(f"💾 已儲存 {saved_count} 首歌曲到資料庫")
                        
                        # 顯示統計
                        elapsed = datetime.now() - start_time
                        print(f"📊 進度: {completed_searches} 次搜尋，{len(self.all_songs)} 首歌曲，耗時 {elapsed}")
                    
                except Exception as e:
                    print(f"❌ 任務執行錯誤: {e}")
        
        # 最終儲存
        final_count = self.save_progress()
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        
        print(f"\n🎉 爬蟲完成！")
        print(f"📈 最終歌曲數: {final_count} 首")
        print(f"🔍 總搜尋次數: {completed_searches}")
        print(f"⏱️ 總耗時: {elapsed_time}")
        print(f"⚡ 平均每首歌耗時: {elapsed_time.total_seconds()/final_count:.2f} 秒")
        
        # 顯示效果最好的關鍵字
        print(f"\n🏆 效果最佳的關鍵字:")
        top_keywords = sorted(self.search_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        for keyword, count in top_keywords:
            print(f"   {keyword}: {count} 首")

def main():
    print("🎤 高級多線程卡拉OK歌曲爬蟲")
    print("=" * 60)
    
    # 設定參數
    max_workers = int(input("請輸入並行線程數 (建議1-5，預設3): ") or "3")
    target_songs = int(input("請輸入目標歌曲數量 (預設15000): ") or "15000")
    
    print(f"\n⚙️ 設定:")
    print(f"   並行線程數: {max_workers}")
    print(f"   目標歌曲數: {target_songs}")
    
    confirm = input("\n確定開始嗎？(y/n): ")
    if confirm.lower() == 'y':
        scraper = AdvancedKaraokeScraper(max_workers=max_workers, max_songs=target_songs)
        scraper.run_scraper()
    else:
        print("❌ 已取消")

if __name__ == "__main__":
    main()