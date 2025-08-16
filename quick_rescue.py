#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速數據搶救腳本
在停止爬蟲前先搶救最新範圍的數據
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from urllib.parse import quote
import os

def quick_rescue_recent_pages():
    """快速搶救最近頁面的數據"""
    print("🚨 快速數據搶救開始")
    print("目標：搶救音圓第6750-6800頁的數據")
    print("=" * 50)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    rescue_data = []
    company = "音圓"
    start_page = 6750
    end_page = 6800
    
    print(f"⚡ 快速爬取 {company} 第{start_page}-{end_page}頁...")
    
    success_count = 0
    
    for page in range(start_page, end_page + 1):
        try:
            url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
            response = session.get(url, timeout=8)
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
                                    'scraped_at': datetime.now().isoformat(),
                                    'source': 'quick_rescue',
                                    'page_number': page
                                }
                                rescue_data.append(song_data)
                                page_songs += 1
                        except:
                            continue
                    
                    success_count += 1
                    if page % 10 == 0:
                        print(f"✅ 第{page}頁: {page_songs} 首歌")
            
            time.sleep(0.5)  # 最小延遲，加快速度
            
        except Exception as e:
            print(f"❌ 第{page}頁失敗: {e}")
            continue
    
    # 保存搶救數據
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rescued_data_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(rescue_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎉 快速搶救完成！")
        print(f"檔案: {filename}")
        print(f"成功頁面: {success_count}/{end_page-start_page+1}")
        print(f"搶救歌曲: {len(rescue_data)} 首")
        
        # 顯示樣本
        if rescue_data:
            print(f"\n📝 搶救數據樣本 (前5首):")
            for i, song in enumerate(rescue_data[:5]):
                print(f"{i+1}. {song['歌名']} - {song['歌手']} ({song['編號']})")
        
        return filename
        
    except Exception as e:
        print(f"❌ 保存搶救數據失敗: {e}")
        return None

def create_stop_script():
    """創建安全停止腳本"""
    stop_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全停止爬蟲腳本
"""

import os
import signal
import time

def stop_scraper():
    """安全停止爬蟲"""
    print("🛑 開始安全停止爬蟲...")
    
    # 查找程式PID
    result = os.popen("ps aux | grep enhanced_taiwan_scraper | grep -v grep").read()
    
    if result.strip():
        lines = result.strip().split('\\n')
        for line in lines:
            if 'enhanced_taiwan_scraper.py' in line:
                parts = line.split()
                if len(parts) >= 2:
                    pid = int(parts[1])
                    print(f"找到程式 PID: {pid}")
                    
                    try:
                        # 發送SIGTERM信號 (禮貌停止)
                        os.kill(pid, signal.SIGTERM)
                        print("✅ 發送停止信號 (SIGTERM)")
                        
                        # 等待5秒
                        time.sleep(5)
                        
                        # 檢查是否還在運行
                        try:
                            os.kill(pid, 0)  # 檢查程式是否還存在
                            print("⚠️ 程式仍在運行，發送強制停止信號")
                            os.kill(pid, signal.SIGKILL)
                            time.sleep(2)
                        except OSError:
                            print("✅ 程式已成功停止")
                            
                    except OSError as e:
                        print(f"停止程式失敗: {e}")
    else:
        print("❌ 沒有找到運行中的爬蟲程式")

if __name__ == "__main__":
    stop_scraper()
'''
    
    with open('stop_scraper.py', 'w', encoding='utf-8') as f:
        f.write(stop_script)
    
    print("✅ 安全停止腳本已創建: stop_scraper.py")

if __name__ == "__main__":
    # 快速搶救數據
    rescued_file = quick_rescue_recent_pages()
    
    # 創建停止腳本
    create_stop_script()
    
    if rescued_file:
        print(f"\n💡 下一步操作:")
        print(f"1. 已搶救數據到: {rescued_file}")
        print(f"2. 運行 'python stop_scraper.py' 安全停止爬蟲")
        print(f"3. 然後啟動最佳化版本")
    else:
        print(f"\n⚠️ 數據搶救失敗，但仍可繼續停止爬蟲")