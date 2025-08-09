#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證周杰倫搜尋修正結果
"""

import requests
import time

def verify_jay_search():
    """驗證周杰倫搜尋改善情況"""
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 驗證周杰倫搜尋修正結果...")
    
    # 等待伺服器重新啟動
    print("⏳ 等待伺服器啟動...")
    time.sleep(3)
    
    try:
        # 測試周杰倫搜尋
        response = requests.get(f"{base_url}/api/taiwan-ktv?keyword=周杰倫", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                total_found = data.get('total', 0)
                returned_count = len(data['data'])
                
                print(f"✅ 搜尋成功！")
                print(f"   📊 總共找到: {total_found} 首歌")
                print(f"   📋 回傳數量: {returned_count} 首歌")
                print(f"   📈 改善幅度: {returned_count - 50} 首 (之前只有50首)")
                
                print(f"\n🎵 周杰倫熱門歌曲 (前10首):")
                for i, song in enumerate(data['data'][:10], 1):
                    print(f"   {i:2d}. {song.get('name', 'N/A')} - {song.get('company', 'N/A')} ({song.get('code', 'N/A')})")
                
                # 統計各家KTV數量
                company_stats = {}
                for song in data['data']:
                    company = song.get('company', 'Unknown')
                    company_stats[company] = company_stats.get(company, 0) + 1
                
                print(f"\n🏢 各家KTV周杰倫歌曲統計:")
                for company, count in sorted(company_stats.items(), key=lambda x: x[1], reverse=True):
                    print(f"   {company}: {count} 首")
                    
            else:
                print("❌ 搜尋失敗或無結果")
        else:
            print(f"❌ API請求失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 測試過程出錯: {e}")
        print("💡 請確認伺服器已重新啟動 (python3 app.py)")

if __name__ == "__main__":
    verify_jay_search()