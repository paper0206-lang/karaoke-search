#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
樣本數據搶救腳本
快速獲取一些樣本數據供查看
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
from urllib.parse import quote

def get_sample_data(company="音圓", pages=5):
    """獲取樣本數據"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    sample_data = []
    print(f"🎯 獲取 {company} 前 {pages} 頁數據作為樣本...")
    
    for page in range(1, pages + 1):
        try:
            url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
            response = session.get(url, timeout=10)
            response.encoding = "utf-8"
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                song_links = soup.select('a[href^="mv.aspx?id="]')
                
                page_songs = 0
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
                                '語言': '',
                                'scraped_at': datetime.now().isoformat(),
                                'source': 'sample_rescue'
                            }
                            sample_data.append(song_data)
                            page_songs += 1
                    except Exception as e:
                        print(f"解析失敗: {e}")
                
                print(f"✅ 第{page}頁: {page_songs} 首歌")
            
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"❌ 第{page}頁失敗: {e}")
    
    # 保存樣本數據
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sample_data_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 樣本數據已保存: {filename}")
    print(f"📊 樣本歌曲數: {len(sample_data)} 首")
    
    # 顯示前幾首歌
    print(f"\n📝 樣本數據預覽 (前5首):")
    for i, song in enumerate(sample_data[:5]):
        print(f"{i+1}. {song['歌名']} - {song['歌手']} ({song['編號']})")
    
    return sample_data

if __name__ == "__main__":
    get_sample_data()
