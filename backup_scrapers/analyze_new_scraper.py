#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析新提供的爬蟲程式
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import quote

def analyze_target_site():
    """分析目標網站結構"""
    print("🔍 分析 song.corp.com.tw 網站結構...")
    
    try:
        # 測試基本連線
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # 測試首頁
        response = requests.get("https://song.corp.com.tw/", headers=headers, timeout=10)
        print(f"   ✅ 首頁連線: HTTP {response.status_code}")
        
        # 測試歌曲頁面結構
        test_url = "https://song.corp.com.tw/songs.aspx?company=錢櫃&page=1"
        response = requests.get(test_url, headers=headers, timeout=10)
        print(f"   ✅ 歌曲頁面: HTTP {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 檢查表格結構
            tables = soup.find_all('table')
            print(f"   📊 發現 {len(tables)} 個表格")
            
            if tables:
                rows = tables[0].find_all('tr')
                print(f"   📋 第一個表格有 {len(rows)} 行")
                
                if len(rows) > 1:
                    cols = rows[1].find_all('td')
                    print(f"   📝 資料行有 {len(cols)} 欄")
                    if cols:
                        sample_data = [col.get_text().strip() for col in cols]
                        print(f"   🎵 範例資料: {sample_data}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 分析失敗: {e}")
        return False

def test_original_scraper():
    """測試原始爬蟲邏輯"""
    print("\n🧪 測試原始爬蟲邏輯...")
    
    companies = ["錢櫃", "好樂迪"]  # 測試少數公司
    data = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    for company in companies:
        print(f"   🔍 測試 {company}...")
        page = 1
        company_songs = 0
        
        while page <= 2:  # 只測試前2頁
            try:
                # URL 編碼
                url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
                
                response = requests.get(url, headers=headers, timeout=10)
                response.encoding = "utf-8"
                soup = BeautifulSoup(response.text, "html.parser")

                rows = soup.select("table tr")
                
                if len(rows) <= 1:  # 只有表頭
                    print(f"      📄 第 {page} 頁無資料，停止")
                    break

                page_songs = 0
                for row in rows[1:]:  # 跳過表頭
                    cols = [c.get_text().strip() for c in row.find_all("td")]
                    if cols and len(cols) >= 3:  # 確保有足夠欄位
                        data.append([company] + cols)
                        page_songs += 1

                company_songs += page_songs
                print(f"      ✅ 第 {page} 頁: {page_songs} 首歌")
                page += 1
                time.sleep(1)  # 延遲
                
            except Exception as e:
                print(f"      ❌ 第 {page} 頁錯誤: {e}")
                break
        
        print(f"   📊 {company} 總計: {company_songs} 首歌")
    
    print(f"\n🎉 測試完成，總共: {len(data)} 首歌")
    return len(data) > 0

def main():
    print("=" * 60)
    print("🎵 台灣點歌王爬蟲分析")
    print("=" * 60)
    
    # 分析網站
    site_ok = analyze_target_site()
    
    if site_ok:
        # 測試爬蟲邏輯
        scraper_ok = test_original_scraper()
        
        if scraper_ok:
            print("\n✅ 爬蟲程式基本可行")
            print("\n📋 分析結果:")
            print("   💯 優點:")
            print("      • 邏輯簡潔清晰")
            print("      • 涵蓋所有主要KTV公司")
            print("      • 有基本的延遲控制")
            print("      • 正確處理中文編碼")
            
            print("\n   ⚠️ 需要改進:")
            print("      • 缺少錯誤恢復機制")
            print("      • 沒有進度保存功能") 
            print("      • 請求標頭過於簡單")
            print("      • 沒有重複資料檢查")
            print("      • 固定延遲可能被偵測")
            
            print("\n💡 建議:")
            print("   1. 整合到現有專案架構")
            print("   2. 增加智能重試機制")
            print("   3. 添加進度保存功能")
            print("   4. 優化輸出格式(JSON)")
            print("   5. 增加資料驗證")
            
        else:
            print("\n❌ 爬蟲測試失敗")
    else:
        print("\n❌ 網站分析失敗")

if __name__ == "__main__":
    main()