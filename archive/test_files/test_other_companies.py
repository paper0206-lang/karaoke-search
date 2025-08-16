#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試其他KTV公司的分頁重複問題
檢查是否為音圓獨有問題或網站通用問題
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
from collections import Counter

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"啟動瀏覽器失敗: {e}")
        return None

def test_company_pagination(company_name, max_pages=5):
    """測試指定公司的分頁重複情況"""
    driver = setup_driver()
    if not driver:
        return None
    
    print(f"\n🧪 測試公司: {company_name}")
    print("=" * 50)
    
    try:
        all_songs = []
        base_url = f"https://song.corp.com.tw/songs.aspx?company={company_name}"
        
        page_first_songs = []  # 記錄每頁第一首歌
        
        for page in range(1, max_pages + 1):
            print(f"正在處理第 {page} 頁...")
            
            url = f"{base_url}&page={page}"
            driver.get(url)
            
            # 等待頁面載入
            time.sleep(random.uniform(4, 7))
            
            try:
                song_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href^="mv.aspx?id="]')
                
                if not song_elements:
                    print(f"  ❌ 第 {page} 頁: 沒有找到歌曲")
                    break
                
                page_songs = []
                for element in song_elements:
                    text = element.text.strip()
                    parts = text.split()
                    
                    if len(parts) >= 4:
                        song_data = {
                            '公司': company_name,
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
                    
                    # 記錄第一首歌作為頁面唯一性標識
                    first_song_key = f"{page_songs[0]['編號']}_{page_songs[0]['歌手']}"
                    page_first_songs.append((page, first_song_key, page_songs[0]['歌名']))
                    
                    # 分析當前頁面
                    page_keys = [f"{song['編號']}_{song['歌手']}" for song in page_songs]
                    unique_page_keys = set(page_keys)
                    
                    print(f"  ✅ 第 {page} 頁: {len(page_songs)} 首歌, {len(unique_page_keys)} 首唯一")
                    print(f"     第一首: {page_songs[0]['編號']} - {page_songs[0]['歌名']} - {page_songs[0]['歌手']}")
                    
                else:
                    print(f"  ❌ 第 {page} 頁: 無法解析歌曲數據")
                    
            except Exception as e:
                print(f"  ❌ 第 {page} 頁處理錯誤: {e}")
        
        # 分析結果
        if all_songs:
            # 使用編號+歌手作為唯一標識
            all_keys = [f"{song['編號']}_{song['歌手']}" for song in all_songs]
            unique_keys = set(all_keys)
            
            # 計算重複率
            duplicate_rate = (len(all_keys) - len(unique_keys)) / len(all_keys) * 100
            
            # 分析頁面間重複
            first_song_keys = [key for _, key, _ in page_first_songs]
            unique_first_keys = set(first_song_keys)
            page_variety_rate = len(unique_first_keys) / len(first_song_keys) * 100
            
            result = {
                'company': company_name,
                'total_records': len(all_songs),
                'unique_songs': len(unique_keys),
                'duplicate_rate': duplicate_rate,
                'pages_tested': len(page_first_songs),
                'unique_first_songs': len(unique_first_keys),
                'page_variety_rate': page_variety_rate,
                'first_songs': page_first_songs
            }
            
            print(f"\n📊 {company_name} 分析結果:")
            print(f"  總記錄數: {len(all_songs)}")
            print(f"  唯一歌曲: {len(unique_keys)}")
            print(f"  跨頁面重複率: {duplicate_rate:.1f}%")
            print(f"  頁面多樣性: {page_variety_rate:.1f}% ({len(unique_first_keys)}/{len(first_song_keys)}頁不重複)")
            
            # 顯示各頁第一首歌
            print(f"  各頁第一首歌:")
            for page, key, song_name in page_first_songs:
                print(f"    第{page}頁: {song_name}")
            
            return result
        else:
            print(f"❌ {company_name}: 未收集到任何數據")
            return None
            
    finally:
        driver.quit()

def main():
    print("🔍 測試多家KTV公司分頁重複問題")
    print("=" * 60)
    
    # 測試的公司列表
    test_companies = [
        "點將家",
        "大唐",
        "金嗓",
        "東洋",
        "音圓"  # 作為對照組
    ]
    
    results = []
    
    for company in test_companies:
        try:
            result = test_company_pagination(company, max_pages=5)
            if result:
                results.append(result)
            time.sleep(3)  # 公司間間隔
        except Exception as e:
            print(f"❌ 測試 {company} 時出錯: {e}")
            continue
    
    # 總結比較
    print(f"\n📈 各公司分頁重複問題對比分析")
    print("=" * 70)
    print(f"{'公司':^8} {'總記錄':^8} {'唯一歌曲':^8} {'重複率':^8} {'頁面多樣性':^10}")
    print("-" * 70)
    
    for result in results:
        print(f"{result['company']:^8} {result['total_records']:^8} {result['unique_songs']:^8} {result['duplicate_rate']:^7.1f}% {result['page_variety_rate']:^9.1f}%")
    
    # 問題分析
    high_duplicate_companies = [r for r in results if r['duplicate_rate'] > 50]
    low_variety_companies = [r for r in results if r['page_variety_rate'] < 80]
    
    print(f"\n🔍 問題分析:")
    if high_duplicate_companies:
        print(f"高重複率公司 (>50%): {', '.join([r['company'] for r in high_duplicate_companies])}")
    if low_variety_companies:
        print(f"低頁面多樣性公司 (<80%): {', '.join([r['company'] for r in low_variety_companies])}")
    
    if len(high_duplicate_companies) == len(results):
        print("🚨 結論: 這是網站通用問題，所有公司都有分頁重複問題")
    elif len(high_duplicate_companies) > 0:
        print("⚠️ 結論: 部分公司存在分頁問題")
    else:
        print("✅ 結論: 分頁問題可能是音圓特有的")
    
    # 保存詳細結果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"company_pagination_test_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 詳細結果已保存到: {filename}")

if __name__ == "__main__":
    main()