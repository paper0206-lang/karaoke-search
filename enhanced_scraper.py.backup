# -*- coding: utf-8 -*-

import requests
import logging
import json
import time
from urllib.parse import quote
import random

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class EnhancedKaraokeScraper:
    def __init__(self):
        self.base_url = "https://song.corp.com.tw"
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://song.corp.com.tw/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
        }
        self.all_songs = {}  # 使用 dict 儲存歌曲，key 為 song_id
        
    def init_session(self):
        """初始化會話"""
        try:
            response = self.session.get(self.base_url, headers=self.headers, timeout=10)
            logging.info(f"初始化會話狀態碼: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            logging.error(f"初始化會話失敗: {str(e)}")
            return False

    def search_songs_by_keyword(self, keyword):
        """根據關鍵字搜尋歌曲"""
        try:
            # 構建搜尋 URL
            search_url = f"{self.base_url}/api/song.aspx"
            params = {
                'company': '全部',
                'cusType': 'searchList',
                'keyword': keyword
            }
            
            # 設定 Referer
            self.headers['Referer'] = f"{self.base_url}/songs.aspx?company={quote('全部')}&keyword={quote(keyword)}"
            
            response = self.session.get(search_url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        logging.info(f"關鍵字 '{keyword}' 找到 {len(data)} 首歌曲")
                        return data
                    else:
                        logging.info(f"關鍵字 '{keyword}' 沒有找到歌曲")
                        return []
                except json.JSONDecodeError as e:
                    logging.error(f"JSON 解析錯誤 '{keyword}': {e}")
                    return []
            else:
                logging.error(f"搜尋 '{keyword}' 失敗: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"搜尋 '{keyword}' 出錯: {str(e)}")
            return []

    def scrape_by_keywords(self):
        """使用多個關鍵字進行搜尋"""
        # 擴展關鍵字列表
        keywords = [
            # 常用字
            '愛', '情', '心', '夢', '你', '我', '他', '她', '的', '是', '在', '有', '就', '不', '了', '會', '要', '來', '去',
            '月', '日', '年', '天', '春', '夏', '秋', '冬', '東', '南', '西', '北', '上', '下', '中', '大', '小',
            
            # 流行歌手
            '鄧麗君', '張惠妹', '周杰倫', '蔡依林', '林俊傑', '王力宏', '陶喆', '張學友', '劉德華', '郭富城',
            '張信哲', '庾澄慶', '伍佰', '張宇', '林志炫', '童安格', '潘瑋柏', '羅志祥', '五月天', '蘇打綠',
            
            # 團體/樂團
            '黑色柳丁', 'F.I.R', '信樂團', 'S.H.E', 'Twins', '飛兒樂團', '動力火車', '優客李林',
            
            # 情感詞彙
            '思念', '想念', '孤單', '寂寞', '快樂', '傷心', '開心', '難過', '幸福', '痛苦',
            
            # 常見歌名詞彙
            '玫瑰', '茉莉', '百合', '櫻花', '流星', '彩虹', '海洋', '山川', '故鄉', '家鄉',
            '朋友', '兄弟', '姐妹', '媽媽', '爸爸', '母親', '父親', '兒子', '女兒',
            
            # 數字和時間
            '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '萬',
            '今', '昨', '明', '早', '晚', '夜', '晨',
            
            # 英文常用詞
            'love', 'baby', 'girl', 'boy', 'dream', 'fly', 'goodbye', 'hello', 'tonight', 'forever'
        ]
        
        total_found = 0
        
        for i, keyword in enumerate(keywords):
            logging.info(f"進度: {i+1}/{len(keywords)} - 搜尋關鍵字: '{keyword}'")
            
            songs = self.search_songs_by_keyword(keyword)
            
            for song in songs:
                # 創建唯一識別符
                song_id = f"{song.get('name', '')}-{song.get('singer', '')}-{song.get('code', '')}"
                if song_id not in self.all_songs:
                    song_data = {
                        '歌名': song.get('name', ''),
                        '歌手': song.get('singer', ''),
                        '編號': song.get('code', ''),
                        '公司': song.get('company', '')
                    }
                    self.all_songs[song_id] = song_data
            
            current_total = len(self.all_songs)
            new_found = current_total - total_found
            total_found = current_total
            
            if new_found > 0:
                logging.info(f"新增 {new_found} 首歌曲，目前總計: {total_found} 首")
            
            # 隨機延遲避免被封鎖
            time.sleep(random.uniform(1, 3))
            
            # 每 50 個關鍵字儲存一次進度
            if (i + 1) % 50 == 0:
                self.save_progress()
        
        return list(self.all_songs.values())

    def save_progress(self):
        """儲存進度"""
        try:
            # 轉換為列表格式
            songs_list = list(self.all_songs.values())
            
            # 儲存到文件
            with open('public/songs_simplified.json', 'w', encoding='utf-8') as f:
                json.dump(songs_list, f, ensure_ascii=False, indent=2)
            
            logging.info(f"進度已儲存，目前共 {len(songs_list)} 首歌曲")
            
        except Exception as e:
            logging.error(f"儲存進度失敗: {e}")

    def run_enhanced_scrape(self):
        """執行增強版爬取"""
        if not self.init_session():
            logging.error("無法初始化會話，退出")
            return
        
        logging.info("開始增強版歌曲爬取...")
        
        # 載入現有資料
        try:
            with open('public/songs_simplified.json', 'r', encoding='utf-8') as f:
                existing_songs = json.load(f)
            for song in existing_songs:
                song_id = f"{song.get('歌名', '')}-{song.get('歌手', '')}-{song.get('編號', '')}"
                self.all_songs[song_id] = song
            logging.info(f"載入現有歌曲: {len(existing_songs)} 首")
        except:
            logging.info("沒有找到現有歌曲資料，從空開始")
        
        # 開始爬取
        self.scrape_by_keywords()
        
        # 最終儲存
        self.save_progress()
        
        final_count = len(self.all_songs)
        logging.info(f"✅ 爬取完成！總共收集到 {final_count} 首歌曲")

if __name__ == "__main__":
    scraper = EnhancedKaraokeScraper()
    scraper.run_enhanced_scrape()