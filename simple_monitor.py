#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版監控腳本 - 不依賴psutil
"""

import time
import json
import os
import re
from datetime import datetime

def monitor_progress():
    """監控爬蟲進度"""
    print("🎵 台灣爬蟲狀態監控")
    print("=" * 50)
    
    # 檢查程式是否在運行
    try:
        result = os.popen("ps aux | grep enhanced_taiwan_scraper | grep -v grep").read()
        if result.strip():
            print("✅ 爬蟲程式正在運行")
            lines = result.strip().split('\n')
            for line in lines:
                if 'enhanced_taiwan_scraper.py' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        pid = parts[1]
                        print(f"   PID: {pid}")
        else:
            print("❌ 爬蟲程式未運行")
    except Exception as e:
        print(f"檢查程式狀態失敗: {e}")
    
    print()
    
    # 分析日誌文件
    log_file = 'taiwan_scraper.log'
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 獲取最後幾條記錄
            recent_lines = lines[-10:] if len(lines) >= 10 else lines
            
            print("📊 最近進度 (最後10條記錄):")
            for line in recent_lines:
                if "✅" in line and "首歌" in line:
                    print(f"   {line.strip()}")
            
            print()
            
            # 統計總進度
            success_lines = [line for line in lines if "✅" in line and "首歌" in line]
            if success_lines:
                last_line = success_lines[-1]
                match = re.search(r'第(\d+)頁:\s*(\d+)\s*首歌', last_line)
                if match:
                    page_num = int(match.group(1))
                    songs_per_page = int(match.group(2))
                    total_estimated = page_num * songs_per_page
                    
                    print(f"📈 統計信息:")
                    print(f"   當前頁面: 第 {page_num:,} 頁")
                    print(f"   每頁歌曲: {songs_per_page} 首")
                    print(f"   估算總數: {total_estimated:,} 首歌")
                    print(f"   成功記錄: {len(success_lines):,} 次")
                    
                    # 計算近期速度 (最後100次記錄)
                    if len(success_lines) >= 100:
                        recent_100 = success_lines[-100:]
                        first_time_str = recent_100[0].split(' - ')[0]
                        last_time_str = recent_100[-1].split(' - ')[0]
                        
                        try:
                            first_time = datetime.strptime(first_time_str, '%Y-%m-%d %H:%M:%S,%f')
                            last_time = datetime.strptime(last_time_str, '%Y-%m-%d %H:%M:%S,%f')
                            time_diff = (last_time - first_time).total_seconds() / 60  # 分鐘
                            
                            if time_diff > 0:
                                pages_per_min = 100 / time_diff
                                songs_per_min = pages_per_min * songs_per_page
                                
                                print(f"⚡ 近期速度:")
                                print(f"   {pages_per_min:.1f} 頁/分鐘")
                                print(f"   {songs_per_min:.0f} 首歌/分鐘")
                                print(f"   {songs_per_min * 60:.0f} 首歌/小時")
                        except Exception as e:
                            print(f"   速度計算失敗: {e}")
                    
                    print()
                    
                    # 數據體量評估
                    if total_estimated >= 100000:
                        print("🚨 數據體量警告:")
                        print(f"   目前數據量已達到 {total_estimated:,} 首歌")
                        print("   這是一個非常大的數據集！")
                        print("   建議考慮:")
                        print("   - 檢查是否所有數據都是需要的")
                        print("   - 考慮分批保存避免記憶體不足")
                        print("   - 準備足夠的存儲空間")
        
        except Exception as e:
            print(f"分析日誌失敗: {e}")
    else:
        print("❌ 找不到日誌文件: taiwan_scraper.log")
    
    # 檢查輸出文件
    print("\n📁 檢查輸出文件:")
    output_files = [
        'public/taiwan_songs_raw.json',
        'taiwan_songking_all.csv',
        'public/songs_simplified.json'
    ]
    
    for file_path in output_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            if size > 0:
                if size > 1024 * 1024:  # MB
                    size_str = f"{size / 1024 / 1024:.1f} MB"
                elif size > 1024:  # KB
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size} bytes"
                print(f"   ✅ {file_path}: {size_str}")
            else:
                print(f"   ⚠️ {file_path}: 空文件")
        else:
            print(f"   ❌ {file_path}: 不存在")

def create_sample_rescue():
    """創建樣本數據搶救腳本"""
    print("\n🔧 創建樣本數據搶救腳本...")
    
    sample_script = '''#!/usr/bin/env python3
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
    
    print(f"\\n🎉 樣本數據已保存: {filename}")
    print(f"📊 樣本歌曲數: {len(sample_data)} 首")
    
    # 顯示前幾首歌
    print(f"\\n📝 樣本數據預覽 (前5首):")
    for i, song in enumerate(sample_data[:5]):
        print(f"{i+1}. {song['歌名']} - {song['歌手']} ({song['編號']})")
    
    return sample_data

if __name__ == "__main__":
    get_sample_data()
'''
    
    with open('get_sample_data.py', 'w', encoding='utf-8') as f:
        f.write(sample_script)
    
    print("✅ 樣本搶救腳本已創建: get_sample_data.py")
    print("💡 運行 'python get_sample_data.py' 可獲取樣本數據")

if __name__ == "__main__":
    monitor_progress()
    create_sample_rescue()