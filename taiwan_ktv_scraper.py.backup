#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣點歌王搜尋爬蟲
使用方法: python taiwan_ktv_scraper.py "搜尋關鍵字"
"""

import requests
import json
import sys
import time
from urllib.parse import quote

def search_taiwan_ktv(keyword):
    """搜尋台灣點歌王"""
    
    if not keyword.strip():
        print("請提供搜尋關鍵字")
        return []
    
    try:
        # 設定請求標頭，模擬正常瀏覽器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://song.corp.com.tw/',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        # 建立session以保持連接
        session = requests.Session()
        session.headers.update(headers)
        
        print(f"🔍 搜尋台灣點歌王: {keyword}")
        
        # 台灣點歌王API URL
        api_url = 'https://song.corp.com.tw/api/song.aspx'
        params = {
            'company': '全部',
            'cusType': 'searchList',
            'keyword': keyword
        }
        
        # 發送請求
        response = session.get(api_url, params=params, timeout=15)
        
        print(f"📄 回應狀態: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            try:
                # 解析JSON回應
                data = response.json()
                
                if isinstance(data, list):
                    print(f"✅ 搜尋成功: 找到 {len(data)} 首歌曲")
                    
                    # 轉換資料格式
                    results = []
                    for song in data:
                        result = {
                            'name': song.get('name', ''),
                            'singer': song.get('singer', ''),
                            'code': song.get('code', ''),
                            'company': song.get('company', ''),
                            'lang': song.get('lang', ''),
                            'sex': song.get('sex', ''),
                        }
                        results.append(result)
                    
                    return results
                else:
                    print(f"⚠️ 回傳資料不是陣列格式: {type(data)}")
                    return []
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失敗: {e}")
                print(f"📄 原始回應: {response.text[:200]}...")
                return []
                
        else:
            print(f"❌ API請求失敗: HTTP {response.status_code}")
            print(f"📄 錯誤回應: {response.text[:200]}...")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 網路請求錯誤: {e}")
        return []
        
    except Exception as e:
        print(f"❌ 未知錯誤: {e}")
        return []

def main():
    """主程式"""
    if len(sys.argv) != 2:
        print("使用方法: python taiwan_ktv_scraper.py \"搜尋關鍵字\"")
        sys.exit(1)
    
    keyword = sys.argv[1]
    results = search_taiwan_ktv(keyword)
    
    if results:
        # 輸出JSON格式結果
        print("\n📊 搜尋結果:")
        print(json.dumps(results, ensure_ascii=False, indent=2))
        
        # 輸出簡化表格
        print(f"\n📝 找到 {len(results)} 首歌曲:")
        print("-" * 80)
        print(f"{'歌名':<20} {'歌手':<15} {'編號':<10} {'公司':<10}")
        print("-" * 80)
        
        for song in results[:10]:  # 只顯示前10首
            name = song['name'][:18] if len(song['name']) > 18 else song['name']
            singer = song['singer'][:13] if len(song['singer']) > 13 else song['singer']
            print(f"{name:<20} {singer:<15} {song['code']:<10} {song['company']:<10}")
            
        if len(results) > 10:
            print(f"... 還有 {len(results) - 10} 首歌曲")
            
    else:
        print("😔 沒有找到相關歌曲")

if __name__ == "__main__":
    main()