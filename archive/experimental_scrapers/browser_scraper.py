#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
瀏覽器自動化爬蟲 - 需要安裝 selenium 和 chromedriver
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import random
from datetime import datetime

def setup_driver():
    options = Options()
    options.add_argument('--headless')  # 無頭模式
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"啟動瀏覽器失敗: {e}")
        print("請確保已安裝 chromedriver")
        return None

def scrape_with_browser(max_pages=10):
    driver = setup_driver()
    if not driver:
        return False
    
    try:
        all_songs = []
        base_url = "https://song.corp.com.tw/songs.aspx?company=音圓"
        
        for page in range(1, max_pages + 1):
            print(f"正在處理第 {page} 頁...")
            
            # 構造URL
            url = f"{base_url}&page={page}"
            driver.get(url)
            
            # 等待頁面載入
            time.sleep(random.uniform(3, 6))
            
            # 尋找歌曲連結
            try:
                song_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href^="mv.aspx?id="]')
                
                page_songs = []
                for element in song_elements:
                    text = element.text.strip()
                    parts = text.split()
                    
                    if len(parts) >= 4:
                        song_data = {
                            '公司': '音圓',
                            '編號': parts[0],
                            '歌名': parts[1], 
                            '期別': parts[2],
                            '歌手': ' '.join(parts[3:]),
                            'page': page,
                            'scraped_at': datetime.now().isoformat()
                        }
                        page_songs.append(song_data)
                
                if page_songs:
                    all_songs.extend(page_songs)
                    unique_ids = set(song['編號'] for song in page_songs)
                    print(f"第 {page} 頁: {len(page_songs)} 首歌, {len(unique_ids)} 個唯一ID")
                    
                    if len(unique_ids) == 1:
                        print("警告: 該頁所有歌曲ID相同，可能仍有問題")
                else:
                    print(f"第 {page} 頁: 無數據")
                    
            except Exception as e:
                print(f"第 {page} 頁處理錯誤: {e}")
        
        # 保存結果
        if all_songs:
            filename = f"browser_scraper_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_songs, f, ensure_ascii=False, indent=2)
            
            unique_songs = set(song['編號'] for song in all_songs)
            print(f"\n完成！總共 {len(all_songs)} 條記錄, {len(unique_songs)} 首唯一歌曲")
            print(f"結果保存到: {filename}")
            return True
        else:
            print("未收集到任何數據")
            return False
            
    finally:
        driver.quit()

if __name__ == "__main__":
    success = scrape_with_browser(10)
    if success:
        print("瀏覽器自動化爬取成功！")
    else:
        print("瀏覽器自動化爬取失敗")
