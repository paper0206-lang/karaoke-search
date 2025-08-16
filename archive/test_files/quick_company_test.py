#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速測試其他公司分頁問題 - 簡化版
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.common.by import By
import time
import random

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"瀏覽器啟動失敗: {e}")
        return None

def quick_test_company(company_name):
    """快速測試一家公司的前3頁"""
    driver = setup_driver()
    if not driver:
        return None
    
    print(f"\n🧪 快速測試: {company_name}")
    
    try:
        first_songs = []  # 每頁第一首歌
        
        for page in [1, 2, 3]:
            url = f"https://song.corp.com.tw/songs.aspx?company={company_name}&page={page}"
            print(f"  檢查第{page}頁...")
            
            driver.get(url)
            time.sleep(5)  # 等待載入
            
            try:
                song_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href^="mv.aspx?id="]')
                
                if song_elements and len(song_elements) > 0:
                    first_song_text = song_elements[0].text.strip()
                    parts = first_song_text.split()
                    
                    if len(parts) >= 4:
                        song_info = {
                            'page': page,
                            'id': parts[0],
                            'name': parts[1],
                            'artist': ' '.join(parts[3:])
                        }
                        first_songs.append(song_info)
                        print(f"    第一首: {parts[0]} - {parts[1]} - {' '.join(parts[3:])}")
                    else:
                        print(f"    解析失敗: {first_song_text}")
                else:
                    print(f"    ❌ 沒有找到歌曲")
                    break
                    
            except Exception as e:
                print(f"    ❌ 頁面處理錯誤: {e}")
        
        # 分析結果
        if len(first_songs) >= 2:
            # 檢查第一首歌是否相同
            unique_first_ids = set(song['id'] for song in first_songs)
            unique_first_names = set(f"{song['name']}_{song['artist']}" for song in first_songs)
            
            result = {
                'company': company_name,
                'pages_tested': len(first_songs),
                'unique_ids': len(unique_first_ids),
                'unique_name_artist': len(unique_first_names),
                'has_variety': len(unique_first_ids) > 1,
                'first_songs': first_songs
            }
            
            if len(unique_first_ids) == 1:
                print(f"  🚨 {company_name}: 所有頁面第一首歌相同 - 可能有重複問題")
            else:
                print(f"  ✅ {company_name}: 頁面有不同內容 - 分頁正常")
                
            return result
        else:
            print(f"  ❌ {company_name}: 測試失敗，數據不足")
            return None
            
    finally:
        driver.quit()

def main():
    print("🚀 快速測試各KTV公司分頁問題")
    print("=" * 50)
    
    companies = ["點將家", "大唐", "金嗓", "東洋", "音圓"]
    results = []
    
    for company in companies:
        try:
            result = quick_test_company(company)
            if result:
                results.append(result)
            time.sleep(2)  # 間隔
        except KeyboardInterrupt:
            print("\\n用戶中斷測試")
            break
        except Exception as e:
            print(f"測試 {company} 時出錯: {e}")
            continue
    
    # 總結
    print(f"\\n📊 測試結果總結:")
    print("=" * 50)
    
    problem_companies = []
    good_companies = []
    
    for result in results:
        company = result['company']
        if result['has_variety']:
            good_companies.append(company)
            print(f"✅ {company}: 分頁正常")
        else:
            problem_companies.append(company)
            print(f"❌ {company}: 疑似有重複問題")
    
    print(f"\\n🔍 結論:")
    if len(problem_companies) == len(results) and len(results) > 0:
        print("🚨 所有測試的公司都有分頁重複問題 - 這是網站通用問題")
    elif len(problem_companies) > 0:
        print(f"⚠️ 部分公司有問題: {', '.join(problem_companies)}")
        print(f"✅ 正常公司: {', '.join(good_companies)}")
    else:
        print("✅ 所有公司分頁都正常")

if __name__ == "__main__":
    main()