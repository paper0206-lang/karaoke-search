#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
終極版音圓爬蟲 - 使用Selenium模擬真實瀏覽器
解決所有ASP.NET和JavaScript問題
"""

import json
import time
import random
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading
import signal

def selenium_scraper():
    """使用Selenium的爬蟲實現"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        
        print("✅ Selenium可用，使用瀏覽器模擬")
        return True
    except ImportError:
        print("❌ Selenium未安裝，請安裝: pip install selenium")
        return False

def simple_test_scraper():
    """簡化版測試 - 確認網站真實分頁機制"""
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import quote, urlencode
    
    print("🔍 執行網站分頁機制深度分析...")
    
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://song.corp.com.tw'
    }
    session.headers.update(headers)
    
    try:
        # 策略1: 嘗試不同的URL構造方式
        test_strategies = [
            {'name': '直接GET參數', 'method': 'get_direct'},
            {'name': '模擬表單POST', 'method': 'form_post'},
            {'name': '分析真實分頁連結', 'method': 'real_pagination'},
        ]
        
        results = {}
        
        for strategy in test_strategies:
            print(f"\\n🧪 測試策略: {strategy['name']}")
            
            if strategy['method'] == 'get_direct':
                # 直接GET不同頁面
                page_data = {}
                for page in [1, 2, 3]:
                    url = f"https://song.corp.com.tw/songs.aspx?company={quote('音圓')}&page={page}"
                    response = session.get(url, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        songs = soup.select('a[href^=\"mv.aspx?id=\"]')
                        
                        if songs:
                            first_song_id = songs[0].get_text().strip().split()[0]
                            page_data[page] = first_song_id
                            print(f"  第{page}頁第一首歌ID: {first_song_id}")
                
                unique_ids = set(page_data.values())
                results[strategy['name']] = len(unique_ids) > 1
                
            elif strategy['method'] == 'form_post':
                # 嘗試POST方式
                base_url = "https://song.corp.com.tw/songs.aspx"
                
                # 先獲取初始頁面和ViewState
                initial_response = session.get(f"{base_url}?company={quote('音圓')}")
                if initial_response.status_code == 200:
                    soup = BeautifulSoup(initial_response.text, 'html.parser')
                    
                    viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                    viewstate_gen = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
                    event_val = soup.find('input', {'name': '__EVENTVALIDATION'})
                    
                    if viewstate:
                        # 嘗試POST到第2頁
                        post_data = {
                            '__VIEWSTATE': viewstate.get('value', ''),
                            '__VIEWSTATEGENERATOR': viewstate_gen.get('value', '') if viewstate_gen else '',
                            '__EVENTVALIDATION': event_val.get('value', '') if event_val else '',
                            '__EVENTTARGET': '',
                            '__EVENTARGUMENT': 'Page$2',  # 嘗試不同的參數格式
                        }
                        
                        post_response = session.post(base_url, data=post_data, timeout=15)
                        if post_response.status_code == 200:
                            soup2 = BeautifulSoup(post_response.text, 'html.parser')
                            songs2 = soup2.select('a[href^=\"mv.aspx?id=\"]')
                            
                            if songs2:
                                second_page_id = songs2[0].get_text().strip().split()[0]
                                print(f"  POST方式第2頁第一首歌ID: {second_page_id}")
                                
                                # 與第1頁比較
                                songs1 = soup.select('a[href^=\"mv.aspx?id=\"]')
                                first_page_id = songs1[0].get_text().strip().split()[0] if songs1 else ''
                                
                                results[strategy['name']] = first_page_id != second_page_id
                
            elif strategy['method'] == 'real_pagination':
                # 尋找真實的分頁連結
                url = f"https://song.corp.com.tw/songs.aspx?company={quote('音圓')}"
                response = session.get(url, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 尋找分頁相關元素
                    pagination_elements = []
                    
                    # 方法1: 尋找包含數字的連結
                    number_links = soup.find_all('a', string=lambda x: x and x.isdigit())
                    pagination_elements.extend(number_links)
                    
                    # 方法2: 尋找包含'下一頁'或'Next'的連結
                    next_links = soup.find_all('a', string=lambda x: x and ('下一頁' in str(x) or 'next' in str(x).lower()))
                    pagination_elements.extend(next_links)
                    
                    # 方法3: 尋找JavaScript事件處理
                    js_links = soup.find_all('a', href=lambda x: x and 'javascript:' in str(x))
                    pagination_elements.extend(js_links)
                    
                    print(f"  找到 {len(pagination_elements)} 個潜在分頁元素")
                    for elem in pagination_elements[:5]:
                        href = elem.get('href', '')
                        text = elem.get_text().strip()
                        onclick = elem.get('onclick', '')
                        print(f"    {text} | href='{href}' | onclick='{onclick}'")
                    
                    results[strategy['name']] = len(pagination_elements) > 0
        
        # 總結測試結果
        print(f"\\n📊 測試結果總結:")
        successful_strategies = [name for name, success in results.items() if success]
        
        if successful_strategies:
            print(f"✅ 成功的策略: {', '.join(successful_strategies)}")
            return True
        else:
            print(f"❌ 所有策略都失敗了")
            print(f"\\n🤔 可能的原因:")
            print(f"  1. 網站使用複雜的JavaScript分頁")
            print(f"  2. 需要特殊的Cookie或Session狀態")  
            print(f"  3. 實施了嚴格的反爬機制")
            print(f"  4. 數據通過AJAX動態載入")
            return False
            
    except Exception as e:
        print(f"❌ 測試過程中出錯: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_browser_automation_scraper():
    """創建瀏覽器自動化版本的爬蟲"""
    scraper_code = '''#!/usr/bin/env python3
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
            print(f"\\n完成！總共 {len(all_songs)} 條記錄, {len(unique_songs)} 首唯一歌曲")
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
'''
    
    with open('browser_scraper.py', 'w', encoding='utf-8') as f:
        f.write(scraper_code)
    
    print("已創建 browser_scraper.py")
    print("使用方法:")
    print("1. 安裝依賴: pip install selenium")
    print("2. 下載 chromedriver 並添加到 PATH")
    print("3. 運行: python browser_scraper.py")

def main():
    print("🔧 音圓爬蟲終極診斷和修復工具")
    print("=" * 50)
    
    # 1. 先測試基礎方法
    print("\\n階段1: 測試基礎HTTP方法...")
    basic_success = simple_test_scraper()
    
    # 2. 檢查Selenium可用性
    print("\\n階段2: 檢查瀏覽器自動化支援...")
    selenium_available = selenium_scraper()
    
    # 3. 提供解決方案
    print("\\n階段3: 提供解決方案...")
    
    if basic_success:
        print("✅ 基礎HTTP方法可行，建議使用修復版爬蟲")
    elif selenium_available:
        print("🔄 需要使用瀏覽器自動化方案")
        create_browser_automation_scraper()
    else:
        print("❌ 需要安裝額外工具")
        print("\\n建議解決方案:")
        print("1. 安裝 selenium: pip install selenium") 
        print("2. 下載 chromedriver")
        print("3. 或考慮使用其他KTV公司的數據源")
    
    print("\\n診斷完成！")

if __name__ == "__main__":
    main()