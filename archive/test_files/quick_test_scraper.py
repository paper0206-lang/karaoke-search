#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速測試爬蟲 - 只爬取2-3頁驗證功能
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

def scrape_test_pages():
    print("🧪 快速測試爬蟲功能")
    print("=" * 40)
    
    company = "音圓"
    test_pages = [6920, 6921, 6922]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    all_songs = []
    
    def scrape_single_page(page):
        try:
            print(f"🔍 爬取第{page}頁...")
            url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
            
            response = session.get(url, timeout=15)
            response.encoding = "utf-8"
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                song_links = soup.select('a[href^="mv.aspx?id="]')
                
                page_data = []
                for link in song_links:
                    try:
                        link_text = link.get_text().strip()
                        parts = link_text.split()
                        
                        if len(parts) >= 4:
                            song_data = {
                                '公司': company,
                                '編號': parts[0],
                                '歌名': parts[1],
                                '期別': parts[2],
                                '歌手': ' '.join(parts[3:]),
                                'page': page,
                                'scraped_at': datetime.now().isoformat()
                            }
                            page_data.append(song_data)
                    except:
                        continue
                
                print(f"✅ 第{page}頁: {len(page_data)} 首歌")
                return page_data
            else:
                print(f"❌ 第{page}頁: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 第{page}頁錯誤: {e}")
            return []
    
    # 串行測試
    print("📝 串行測試:")
    for page in test_pages:
        page_data = scrape_single_page(page)
        all_songs.extend(page_data)
        time.sleep(2)
    
    print(f"\n📊 測試結果:")
    print(f"   總頁面: {len(test_pages)}")
    print(f"   總歌曲: {len(all_songs)}")
    
    if all_songs:
        # 保存測試數據
        test_file = f"test_scraper_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(all_songs, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 測試數據保存: {test_file}")
        print(f"📝 前3首歌曲:")
        for i, song in enumerate(all_songs[:3]):
            print(f"   {i+1}. {song['歌名']} - {song['歌手']} ({song['編號']})")
        
        return True
    else:
        print("❌ 沒有收集到數據")
        return False

if __name__ == "__main__":
    success = scrape_test_pages()
    if success:
        print("\n✅ 測試成功！爬蟲功能正常")
    else:
        print("\n❌ 測試失敗！需要檢查問題")