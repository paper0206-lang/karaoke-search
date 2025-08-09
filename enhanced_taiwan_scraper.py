#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版台灣點歌王爬蟲 - 整合到專案架構
基於原始程式碼優化，增加錯誤處理、進度保存、自動推送等功能
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os
import csv
from datetime import datetime
from urllib.parse import quote
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import sys

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('taiwan_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class EnhancedTaiwanScraper:
    def __init__(self):
        self.companies = [
            "音圓", "弘音", "金嗓", "音圓原廠", "瑞影", "點將家", "嘉揚", "音遊",
            "音影", "美華", "金影", "金嗓/投幣", "一級棒", "錢櫃", "好樂迪", "星據點",
            "銀櫃", "享溫馨", "大唐", "MV", "金嗓/家庭"
        ]
        
        self.headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        self.all_data = []
        self.progress_file = 'scraping_progress.json'
        self.output_files = {
            'csv': 'taiwan_songking_all.csv',
            'json': 'public/taiwan_songs_raw.json',
            'unified': 'public/songs_simplified.json'
        }
        
        # 載入進度
        self.progress = self._load_progress()
    
    def _get_random_user_agent(self):
        """隨機User-Agent"""
        agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        return random.choice(agents)
    
    def _load_progress(self):
        """載入爬取進度"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                logging.info(f"載入進度: 已完成 {len(progress.get('completed_companies', []))} 家公司")
                return progress
            except:
                pass
        return {'completed_companies': [], 'total_songs': 0, 'last_update': None}
    
    def _save_progress(self):
        """保存爬取進度"""
        self.progress['last_update'] = datetime.now().isoformat()
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def _smart_delay(self):
        """智能延遲"""
        delay = random.uniform(1.5, 3.5)  # 1.5-3.5秒隨機延遲
        time.sleep(delay)
    
    def scrape_company(self, company):
        """爬取單一公司的所有歌曲"""
        if company in self.progress.get('completed_companies', []):
            logging.info(f"跳過已完成的公司: {company}")
            return []
        
        logging.info(f"開始爬取: {company}")
        company_data = []
        page = 1
        consecutive_failures = 0
        max_failures = 3
        
        while True:
            try:
                url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
                
                # 更新User-Agent
                if page % 5 == 0:  # 每5頁更換一次
                    self.session.headers['User-Agent'] = self._get_random_user_agent()
                
                response = self.session.get(url, timeout=15)
                response.encoding = "utf-8"
                
                if response.status_code != 200:
                    logging.warning(f"{company} 第{page}頁 HTTP {response.status_code}")
                    consecutive_failures += 1
                    if consecutive_failures >= max_failures:
                        break
                    self._smart_delay()
                    continue
                
                soup = BeautifulSoup(response.text, "html.parser")
                rows = soup.select("table tr")
                
                if len(rows) <= 1:  # 只有表頭，沒有資料
                    logging.info(f"{company} 第{page}頁 無更多資料，完成")
                    break
                
                page_songs = 0
                for row in rows[1:]:  # 跳過表頭
                    cols = [c.get_text().strip() for c in row.find_all("td")]
                    if cols and len(cols) >= 3:  # 確保有足夠欄位
                        # 標準化資料格式
                        song_data = {
                            '公司': company,
                            '編號': cols[0] if len(cols) > 0 else '',
                            '歌名': cols[1] if len(cols) > 1 else '',
                            '歌手': cols[2] if len(cols) > 2 else '',
                            '語言': cols[3] if len(cols) > 3 else '',
                            'raw_data': cols,  # 保留原始資料
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        company_data.append(song_data)
                        page_songs += 1
                
                if page_songs == 0:
                    logging.warning(f"{company} 第{page}頁 無有效資料")
                    consecutive_failures += 1
                    if consecutive_failures >= max_failures:
                        break
                else:
                    consecutive_failures = 0  # 重置失敗計數
                    logging.info(f"✅ {company} 第{page}頁: {page_songs} 首歌")
                
                page += 1
                self._smart_delay()
                
            except Exception as e:
                logging.error(f"{company} 第{page}頁 錯誤: {e}")
                consecutive_failures += 1
                if consecutive_failures >= max_failures:
                    logging.error(f"{company} 連續失敗 {max_failures} 次，跳過")
                    break
                self._smart_delay()
        
        # 標記公司完成
        if company not in self.progress.get('completed_companies', []):
            self.progress['completed_companies'].append(company)
        
        self.progress['total_songs'] = self.progress.get('total_songs', 0) + len(company_data)
        self._save_progress()
        
        logging.info(f"🎉 {company} 完成: {len(company_data)} 首歌")
        return company_data
    
    def scrape_all(self, max_workers=2):
        """爬取所有公司資料"""
        logging.info(f"開始爬取 {len(self.companies)} 家公司")
        start_time = time.time()
        
        # 載入現有資料
        if os.path.exists(self.output_files['json']):
            try:
                with open(self.output_files['json'], 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                self.all_data.extend(existing_data)
                logging.info(f"載入現有資料: {len(existing_data)} 首歌")
            except Exception as e:
                logging.warning(f"載入現有資料失敗: {e}")
        
        # 單線程爬取 (避免被封鎖)
        for company in self.companies:
            try:
                company_data = self.scrape_company(company)
                self.all_data.extend(company_data)
                
                # 每家公司完成後保存
                self._save_intermediate_results()
                
            except Exception as e:
                logging.error(f"爬取 {company} 時發生錯誤: {e}")
                continue
        
        end_time = time.time()
        duration = end_time - start_time
        
        logging.info(f"🎉 全部完成！")
        logging.info(f"⏱️  耗時: {duration:.2f} 秒")
        logging.info(f"📊 總計: {len(self.all_data)} 首歌")
        logging.info(f"🏢 公司: {len(self.companies)} 家")
        logging.info(f"📈 平均: {len(self.all_data)/len(self.companies):.0f} 首/公司")
        
        return self.all_data
    
    def _save_intermediate_results(self):
        """保存中間結果"""
        try:
            # 保存JSON格式
            with open(self.output_files['json'], 'w', encoding='utf-8') as f:
                json.dump(self.all_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"中間結果已保存: {len(self.all_data)} 首歌")
        except Exception as e:
            logging.error(f"保存中間結果失敗: {e}")
    
    def save_results(self):
        """保存最終結果"""
        if not self.all_data:
            logging.warning("沒有資料可保存")
            return
        
        try:
            # 1. 保存CSV格式 (原始格式)
            with open(self.output_files['csv'], 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['公司', '編號', '歌名', '歌手', '語言'])
                
                for song in self.all_data:
                    writer.writerow([
                        song.get('公司', ''),
                        song.get('編號', ''),
                        song.get('歌名', ''),
                        song.get('歌手', ''),
                        song.get('語言', '')
                    ])
            
            logging.info(f"CSV檔案已保存: {self.output_files['csv']}")
            
            # 2. 保存JSON格式
            with open(self.output_files['json'], 'w', encoding='utf-8') as f:
                json.dump(self.all_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"JSON檔案已保存: {self.output_files['json']}")
            
            # 3. 轉換為統一格式
            unified_data = self._convert_to_unified_format()
            
            # 載入現有統一資料
            existing_unified = []
            if os.path.exists(self.output_files['unified']):
                try:
                    with open(self.output_files['unified'], 'r', encoding='utf-8') as f:
                        existing_unified = json.load(f)
                except:
                    pass
            
            # 合併資料並去重
            all_unified = existing_unified + unified_data
            unique_songs = self._deduplicate_songs(all_unified)
            
            with open(self.output_files['unified'], 'w', encoding='utf-8') as f:
                json.dump(unique_songs, f, ensure_ascii=False, indent=2)
            
            logging.info(f"統一格式已保存: {self.output_files['unified']} ({len(unique_songs)} 首)")
            
            return True
            
        except Exception as e:
            logging.error(f"保存結果失敗: {e}")
            return False
    
    def _convert_to_unified_format(self):
        """轉換為統一格式"""
        unified_data = []
        
        for song in self.all_data:
            if song.get('歌名') and song.get('歌手'):
                unified_song = {
                    '歌名': song.get('歌名', '').strip(),
                    '歌手': song.get('歌手', '').strip(),
                    '編號': song.get('編號', '').strip(),
                    '公司': song.get('公司', '').strip(),
                    '語言': song.get('語言', '').strip()
                }
                unified_data.append(unified_song)
        
        return unified_data
    
    def _deduplicate_songs(self, songs):
        """去除重複歌曲"""
        seen = set()
        unique_songs = []
        
        for song in songs:
            key = f"{song.get('歌名', '')}_{song.get('歌手', '')}_{song.get('公司', '')}_{song.get('編號', '')}"
            if key not in seen:
                seen.add(key)
                unique_songs.append(song)
        
        return unique_songs
    
    def auto_push_to_github(self):
        """自動推送到GitHub"""
        try:
            logging.info("開始推送到GitHub...")
            
            # 檢查是否在Git倉庫中
            result = subprocess.run(['git', 'status'], 
                                 capture_output=True, text=True, cwd='.')
            if result.returncode != 0:
                logging.warning("不在Git倉庫中，跳過自動推送")
                return False
            
            # 添加檔案
            files_to_add = [
                self.output_files['csv'],
                self.output_files['json'],
                self.output_files['unified'],
                'taiwan_scraper.log'
            ]
            
            for file_path in files_to_add:
                if os.path.exists(file_path):
                    subprocess.run(['git', 'add', file_path], cwd='.')
            
            # 檢查是否有檔案要提交
            result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                 capture_output=True, text=True, cwd='.')
            if not result.stdout.strip():
                logging.info("沒有檔案需要提交")
                return False
            
            # 創建提交
            commit_message = f"""🎵 自動更新台灣點歌王資料庫

📊 爬取統計:
- 總歌曲數: {len(self.all_data):,} 首
- 覆蓋公司: {len(self.companies)} 家
- 更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📁 更新檔案:
- {self.output_files['csv']} (CSV原始資料)
- {self.output_files['json']} (JSON結構化資料)  
- {self.output_files['unified']} (統一格式)

🤖 Generated with Claude Code
"""
            
            result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                 capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                logging.info("提交成功")
                
                # 推送到GitHub
                result = subprocess.run(['git', 'push', 'origin', 'main'], 
                                     capture_output=True, text=True, cwd='.')
                
                if result.returncode == 0:
                    logging.info("✅ 成功推送到GitHub")
                    return True
                else:
                    logging.error(f"推送失敗: {result.stderr}")
                    return False
            else:
                logging.error(f"提交失敗: {result.stderr}")
                return False
                
        except Exception as e:
            logging.error(f"自動推送失敗: {e}")
            return False

def main():
    """主程序"""
    print("🎵 增強版台灣點歌王爬蟲")
    print("=" * 50)
    
    scraper = EnhancedTaiwanScraper()
    
    try:
        # 爬取資料
        data = scraper.scrape_all()
        
        if data:
            # 保存結果
            if scraper.save_results():
                print(f"✅ 資料保存成功: {len(data)} 首歌")
                
                # 自動推送到GitHub
                if scraper.auto_push_to_github():
                    print("✅ 自動推送到GitHub成功")
                    print("🌐 線上版本將自動更新")
                else:
                    print("⚠️ 自動推送失敗，請手動推送")
                
                # 清理進度檔案
                if os.path.exists(scraper.progress_file):
                    os.remove(scraper.progress_file)
                
                print("\n🎉 爬蟲任務完成！")
                print(f"📊 總計爬取: {len(data)} 首歌")
                print(f"📁 檔案位置:")
                for name, path in scraper.output_files.items():
                    if os.path.exists(path):
                        print(f"   {name}: {path}")
            else:
                print("❌ 資料保存失敗")
        else:
            print("❌ 沒有爬取到資料")
    
    except KeyboardInterrupt:
        print("\n⚠️ 使用者中斷，進度已保存")
        scraper._save_intermediate_results()
    except Exception as e:
        print(f"❌ 爬蟲執行失敗: {e}")
        logging.error(f"主程序錯誤: {e}")

if __name__ == "__main__":
    main()