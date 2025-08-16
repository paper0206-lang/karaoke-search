#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
緊急備份腳本 - 獲取當前範圍的數據並保存
避免等待完整爬蟲可能的記憶體問題
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
from urllib.parse import quote
import os

def create_emergency_backup(start_page=6700, end_page=6800, company="音圓"):
    """創建緊急備份"""
    print(f"🚨 緊急備份開始")
    print(f"公司: {company}")
    print(f"頁面範圍: {start_page} - {end_page}")
    print("=" * 50)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    backup_data = []
    success_count = 0
    error_count = 0
    
    for page in range(start_page, end_page + 1):
        try:
            url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
            response = session.get(url, timeout=15)
            response.encoding = "utf-8"
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                song_links = soup.select('a[href^="mv.aspx?id="]')
                
                if len(song_links) > 0:
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
                                    'link_url': link.get('href', ''),
                                    'scraped_at': datetime.now().isoformat(),
                                    'backup_source': 'emergency_backup',
                                    'page_number': page
                                }
                                backup_data.append(song_data)
                                page_songs += 1
                        except Exception as e:
                            print(f"解析歌曲失敗: {e}")
                    
                    success_count += 1
                    if page % 10 == 0:
                        print(f"✅ 第{page}頁: {page_songs} 首歌 (累計: {len(backup_data)} 首)")
                else:
                    print(f"⚠️ 第{page}頁無數據")
            else:
                print(f"❌ 第{page}頁 HTTP {response.status_code}")
                error_count += 1
            
            # 禮貌延遲
            time.sleep(random.uniform(1.5, 2.5))
            
        except Exception as e:
            print(f"❌ 第{page}頁錯誤: {e}")
            error_count += 1
            if error_count > 10:
                print("錯誤過多，停止備份")
                break
    
    # 保存備份數據
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"emergency_backup_{company}_{start_page}-{end_page}_{timestamp}.json"
    
    # 確保目錄存在
    os.makedirs('backup', exist_ok=True)
    filepath = f"backup/{filename}"
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎉 緊急備份完成！")
        print(f"檔案: {filepath}")
        print(f"📊 統計:")
        print(f"   成功頁面: {success_count}")
        print(f"   錯誤頁面: {error_count}")
        print(f"   總歌曲數: {len(backup_data)}")
        
        # 顯示樣本
        print(f"\n📝 樣本數據 (前5首):")
        for i, song in enumerate(backup_data[:5]):
            print(f"{i+1}. {song['歌名']} - {song['歌手']} ({song['編號']})")
        
        return filepath
        
    except Exception as e:
        print(f"❌ 保存備份失敗: {e}")
        return None

def create_comprehensive_sample():
    """創建全面的樣本數據"""
    print("\n🎯 創建全面樣本數據...")
    
    # 獲取不同範圍的樣本
    samples = [
        (1, 50, "開頭樣本"),      # 前50頁
        (3000, 3050, "中段樣本"),  # 中段50頁  
        (6700, 6750, "當前樣本")   # 當前50頁
    ]
    
    all_samples = []
    
    for start, end, description in samples:
        print(f"\n📍 {description}: 第{start}-{end}頁")
        try:
            sample_file = create_emergency_backup(start, end, "音圓")
            if sample_file:
                print(f"✅ {description} 完成")
            else:
                print(f"❌ {description} 失敗")
        except Exception as e:
            print(f"❌ {description} 錯誤: {e}")
        
        # 防止被限制
        time.sleep(5)

def monitor_and_suggest():
    """監控並提出建議"""
    print("\n💡 建議和警告:")
    print("=" * 30)
    
    # 檢查當前爬蟲狀態
    try:
        result = os.popen("ps aux | grep enhanced_taiwan_scraper | grep -v grep").read()
        if result.strip():
            print("✅ 原爬蟲仍在運行")
            
            # 檢查記憶體使用
            print("\n⚠️ 記憶體風險警告:")
            print("   - 目前數據量: 33萬+ 首歌")
            print("   - 預計最終: 75萬首歌 (僅音圓)")
            print("   - 記憶體需求: 2GB+")
            print("   - 風險: 程式可能因記憶體不足而崩潰")
            
            print("\n💡 建議行動:")
            print("   1. 立即創建緊急備份")
            print("   2. 考慮停止當前爬蟲，改用多線程分批版本")
            print("   3. 定期保存中間結果")
            print("   4. 監控系統資源使用")
            
        else:
            print("❌ 原爬蟲已停止，可能是記憶體問題")
            print("💡 建議使用多線程分批爬蟲")
            
    except Exception as e:
        print(f"檢查爬蟲狀態失敗: {e}")

if __name__ == "__main__":
    print("🚨 緊急備份和樣本創建工具")
    print("=" * 50)
    
    # 創建當前範圍的備份
    create_emergency_backup(6700, 6800, "音圓")
    
    # 創建全面樣本
    # create_comprehensive_sample()  # 取消註釋以運行
    
    # 監控和建議
    monitor_and_suggest()