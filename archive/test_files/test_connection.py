#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試網站連接和數據提取
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import time

def test_connection():
    print("🔗 測試網站連接...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    
    company = "音圓"
    page = 6920
    
    try:
        url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
        print(f"📡 請求: {url}")
        
        response = session.get(url, timeout=15)
        response.encoding = "utf-8"
        
        print(f"📊 響應狀態: {response.status_code}")
        print(f"📏 內容長度: {len(response.text)} 字符")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            song_links = soup.select('a[href^="mv.aspx?id="]')
            
            print(f"🎵 找到歌曲: {len(song_links)} 首")
            
            if song_links:
                print("📝 前5首歌曲:")
                for i, link in enumerate(song_links[:5]):
                    try:
                        link_text = link.get_text().strip()
                        parts = link_text.split()
                        
                        if len(parts) >= 4:
                            print(f"   {i+1}. {parts[1]} - {' '.join(parts[3:])} ({parts[0]})")
                    except Exception as e:
                        print(f"   {i+1}. 解析失敗: {e}")
                
                return True
            else:
                print("❌ 沒有找到歌曲數據")
                return False
        else:
            print(f"❌ HTTP錯誤: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 連接錯誤: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    test_connection()