# -*- coding: utf-8 -*-

import requests
import logging
import json
import os
from urllib.parse import quote
import uuid
import time
from datetime import datetime
from pathlib import Path

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class KaraokeScraper:
    def __init__(self):
        self.base_url = "https://song.corp.com.tw"
        self.session = requests.Session()  # 使用 session 來保持 cookie
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'dnt': '1',
            'priority': 'u=0, i'
        }
        self.uuid = str(uuid.uuid4())  # 生成唯一識別碼
        self.all_songs = []
        self.checkpoint_file = "scrape_checkpoint.json"
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

    def init_session(self):
        """初始化會話，訪問首頁獲取必要的 cookie"""
        try:
            response = self.session.get(self.base_url, headers=self.headers)
            logging.info(f"初始化會話狀態碼: {response.status_code}")
            return True
        except Exception as e:
            logging.error(f"初始化會話失敗: {str(e)}")
            return False

    def format_song_info(self, song):
        """格式化歌曲信息，只顯示指定字段"""
        important_fields = {
            'name': '歌名',
            'singer': '歌手',
            'code': '編號',
            'company': '公司'
        }
        
        formatted = []
        for key, label in important_fields.items():
            if key in song and song[key]:
                # 移除字符串中的多餘空格
                value = ' '.join(str(song[key]).split())
                formatted.append(f"{label}: {value}")
        
        # 使用換行而不是分隔符來顯示
        return "\n    ".join(formatted)

    def search_song(self, keyword):
        try:
            url = (f"{self.base_url}/api/song.aspx"
                  f"?company={quote('全部')}"
                  f"&cusType=searchList"
                  f"&keyword={quote(keyword)}")
            
            self.headers['Referer'] = f"{self.base_url}/songs.aspx?company={quote('全部')}&keyword={quote(keyword)}"
            
            logging.info(f"正在搜尋: {keyword}")
            
            response = self.session.get(url, headers=self.headers)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else 0
                    logging.info(f"找到 {count} 條結果")
                    
                    if count > 0:
                        logging.info("\n搜尋結果:")
                        for i, song in enumerate(data[:5], 1):  # 只顯示前5首
                            logging.info(f"\n[{i}] {'-'*50}")
                            logging.info(self.format_song_info(song))
                    
                    return data
                except json.JSONDecodeError:
                    logging.error("響應格式錯誤")
                    return None
            else:
                logging.error(f"請求失敗: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"搜尋出錯: {str(e)}")
            return None

    def load_checkpoint(self):
        """載入上次的進度"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                self.all_songs = checkpoint.get('songs', [])
                logging.info(f"已載入上次進度，當前已有 {len(self.all_songs)} 首歌曲")
                return checkpoint.get('last_offset', 0), checkpoint.get('last_char_index', 0)
            except Exception as e:
                logging.error(f"載入進度失敗: {e}")
        return 0, 0

    def save_checkpoint(self, offset=0, char_index=0):
        """保存當前進度"""
        checkpoint = {
            'songs': self.all_songs,
            'last_offset': offset,
            'last_char_index': char_index,
            'timestamp': datetime.now().isoformat()
        }
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, ensure_ascii=False)
        logging.info("進度已保存")

    def sanitize_filename(self, filename):
        """處理文件名，移除或替換非法字符"""
        # 替換 Windows 和 Unix 系統都不允許的字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename

    def scrape_by_company(self, company='全部', batch_size=100, start_offset=0):
        """通過公司批次抓取歌曲"""
        offset = start_offset
        retry_count = 0
        max_retries = 3

        while True:
            try:
                url = (f"{self.base_url}/api/song.aspx"
                      f"?company={quote(company)}"
                      f"&cusType=searchList"
                      f"&offset={offset}"
                      f"&limit={batch_size}")
                
                response = self.session.get(url, headers=self.headers)
                
                # 檢查響應內容
                try:
                    response_text = response.text.strip()
                    if not response_text:
                        logging.warning(f"收到空響應，offset: {offset}")
                        break
                    
                    data = response.json()
                    if not data:
                        break
                    
                    if isinstance(data, list):
                        new_songs = [song for song in data if song['code'] not in {s['code'] for s in self.all_songs}]
                        self.all_songs.extend(new_songs)
                        logging.info(f"已抓取 {len(self.all_songs)} 首歌曲 (新增 {len(new_songs)} 首)")
                    else:
                        logging.warning(f"意外的響應格式: {response_text[:100]}")
                        break
                    
                    # 每100首歌保存一次進度
                    if len(self.all_songs) % 100 == 0:
                        self.save_checkpoint(offset)
                    
                    offset += batch_size
                    time.sleep(1)
                    retry_count = 0

                except json.JSONDecodeError as e:
                    logging.error(f"JSON 解析錯誤: {e}")
                    logging.debug(f"響應內容: {response_text[:100]}")
                    if retry_count < max_retries:
                        retry_count += 1
                        time.sleep(5)
                        continue
                    break

            except Exception as e:
                logging.error(f"抓取出錯: {e}")
                if retry_count < max_retries:
                    retry_count += 1
                    time.sleep(5)
                    continue
                break

    def scrape_by_letter(self, start_index=0):
        """通過字母和數字遍歷搜索"""
        characters = list("一二三四五六七八九十月年日天春夏秋冬愛情")
        retry_count = 0
        max_retries = 3

        for i, char in enumerate(characters[start_index:], start_index):
            try:
                url = (f"{self.base_url}/api/song.aspx"
                      f"?company=全部"
                      f"&cusType=searchList"
                      f"&keyword={quote(char)}")
                
                response = self.session.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        new_songs = [song for song in data if song['code'] not in {s['code'] for s in self.all_songs}]
                        self.all_songs.extend(new_songs)
                        logging.info(f"搜索 '{char}' 找到 {len(new_songs)} 首新歌曲")
                        
                        # 每個字符處理完後保存進度
                        self.save_checkpoint(char_index=i)
                
                time.sleep(1)
                retry_count = 0

            except Exception as e:
                logging.error(f"搜索 '{char}' 時出錯: {e}")
                if retry_count < max_retries:
                    retry_count += 1
                    time.sleep(5)
                    continue

    def save_results(self):
        """保存所有結果"""
        if not self.all_songs:
            logging.warning("沒有找到任何歌曲")
            return
            
        # 去重
        unique_songs = {song['code']: song for song in self.all_songs}.values()
        self.all_songs = list(unique_songs)
        
        # 按公司分類保存
        songs_by_company = {}
        for song in self.all_songs:
            company = song.get('company', '其他')
            if company not in songs_by_company:
                songs_by_company[company] = []
            songs_by_company[company].append(song)

        # 保存分類結果
        for company, songs in songs_by_company.items():
            # 處理公司名稱，確保是合法的文件名
            safe_company = self.sanitize_filename(company)
            company_dir = self.data_dir / safe_company
            company_dir.mkdir(exist_ok=True)
            
            company_file = company_dir / "songs.json"
            try:
                with open(company_file, "w", encoding="utf-8") as f:
                    json.dump(songs, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logging.error(f"保存 {company} 的數據時出錯: {e}")

        # 保存完整數據
        try:
            with open(self.data_dir / "all_songs.json", "w", encoding="utf-8") as f:
                json.dump(self.all_songs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存完整數據時出錯: {e}")
            
        # 保存簡化版本
        try:
            simplified_songs = []
            for song in self.all_songs:
                simplified_song = {
                    '歌名': song.get('name', ''),
                    '歌手': song.get('singer', ''),
                    '編號': song.get('code', ''),
                    '公司': song.get('company', '')
                }
                simplified_songs.append(simplified_song)
            
            with open(self.data_dir / "songs_simplified.json", "w", encoding="utf-8") as f:
                json.dump(simplified_songs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存簡化數據時出錯: {e}")
            
        logging.info(f"\n總共收集到 {len(self.all_songs)} 首歌曲")
        logging.info(f"完整數據已保存到: {self.data_dir}/all_songs.json")
        logging.info(f"簡化數據已保存到: {self.data_dir}/songs_simplified.json")
        logging.info(f"各公司數據已分別保存到 {self.data_dir} 目錄下的子文件夾中")

    def run_full_scrape(self):
        """執行完整的抓取過程"""
        if not self.init_session():
            return
            
        logging.info("開始抓取所有歌曲數據...")
        
        # 載入上次進度
        start_offset, start_char_index = self.load_checkpoint()
        
        # 方法1：通過公司抓取
        self.scrape_by_company(start_offset=start_offset)
        
        # 方法2：通過常用字搜索補充
        self.scrape_by_letter(start_index=start_char_index)
        
        # 保存結果
        self.save_results()
        
        # 清理checkpoint文件
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)

if __name__ == "__main__":
    scraper = KaraokeScraper()
    scraper.run_full_scrape()
