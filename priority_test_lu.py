#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
優先測試盧廣仲爬取
直接爬取盧廣仲完整資料並立即推送
"""

import json
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import random
import time
from datetime import datetime
from collections import defaultdict
import subprocess

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('PriorityTestLu')

def scrape_lu_guangzhong_complete():
    """完整爬取盧廣仲資料"""
    logger.info("🎯 開始優先測試盧廣仲完整爬取")
    
    # 創建Session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    })
    
    singer_name = "盧廣仲"
    all_songs = []
    page = 1
    consecutive_empty = 0
    max_empty = 3
    
    logger.info(f"🎵 開始爬取 {singer_name}")
    start_time = time.time()
    
    try:
        while consecutive_empty < max_empty:
            try:
                # 智能延遲
                if page > 1:
                    delay = random.uniform(1.5, 3.0)
                    time.sleep(delay)
                
                # 構建URL
                url = f"https://song.corp.com.tw/songs.aspx?company=全部&keyword={quote(singer_name)}&page={page}"
                
                logger.info(f"📡 正在爬取第{page}頁...")
                response = session.get(url, timeout=20)
                response.encoding = "utf-8"
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    song_links = soup.select('a[href^="mv.aspx?id="]')
                    
                    if song_links:
                        consecutive_empty = 0
                        page_songs = []
                        
                        for link in song_links:
                            try:
                                raw_text = link.get_text().strip()
                                lines = raw_text.split('\\n')
                                
                                if len(lines) >= 2:
                                    # 基本信息
                                    line1 = lines[0].strip()  # 通常是編號
                                    line2 = lines[1].strip()  # 通常是歌名
                                    line3 = lines[2].strip() if len(lines) > 2 else ""  # 歌手信息
                                    
                                    # 檢查是否真的包含盧廣仲
                                    if singer_name in raw_text:
                                        # 解析編號和歌名
                                        song_data = {
                                            'raw_line1': line1,
                                            'raw_line2': line2, 
                                            'raw_line3': line3,
                                            'singer': singer_name,
                                            'page': page,
                                            'raw_text': raw_text,
                                            'scraped_at': datetime.now().isoformat()
                                        }
                                        
                                        page_songs.append(song_data)
                                        
                            except Exception as e:
                                logger.debug(f"解析歌曲失敗: {e}")
                                continue
                        
                        all_songs.extend(page_songs)
                        logger.info(f"   第{page}頁: {len(page_songs)} 首相關歌曲")
                        
                    else:
                        consecutive_empty += 1
                        logger.info(f"   第{page}頁: 無資料 ({consecutive_empty}/{max_empty})")
                        
                else:
                    logger.warning(f"第{page}頁 HTTP {response.status_code}")
                    
                page += 1
                
            except Exception as e:
                logger.error(f"第{page}頁異常: {e}")
                consecutive_empty += 1
                page += 1
                continue
        
    finally:
        session.close()
    
    elapsed_time = time.time() - start_time
    logger.info(f"🎉 {singer_name} 爬取完成!")
    logger.info(f"   耗時: {elapsed_time:.1f}秒")
    logger.info(f"   總頁數: {page-1}頁")
    logger.info(f"   總歌曲: {len(all_songs)}首")
    
    return all_songs

def analyze_lu_data(songs_data):
    """分析盧廣仲資料"""
    logger.info("📊 分析盧廣仲資料結構...")
    
    if not songs_data:
        logger.warning("沒有找到資料")
        return
    
    # 分析資料格式
    logger.info(f"📋 資料樣本分析:")
    for i, song in enumerate(songs_data[:5]):
        logger.info(f"   樣本{i+1}:")
        logger.info(f"     Line1: {song['raw_line1']}")
        logger.info(f"     Line2: {song['raw_line2']}")
        logger.info(f"     Line3: {song['raw_line3']}")
        logger.info(f"     Raw: {song['raw_text'][:100]}...")
        logger.info("")
    
    # 統計
    total_songs = len(songs_data)
    unique_line2 = len(set(song['raw_line2'] for song in songs_data))
    pages_used = len(set(song['page'] for song in songs_data))
    
    logger.info(f"📈 統計結果:")
    logger.info(f"   總條目: {total_songs}")
    logger.info(f"   獨特歌名: {unique_line2}")
    logger.info(f"   爬取頁數: {pages_used}")
    logger.info(f"   平均每頁: {total_songs/pages_used:.1f}條")

def save_lu_data(songs_data):
    """保存盧廣仲資料"""
    try:
        # 保存原始資料
        output_file = f"lu_guangzhong_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(songs_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 盧廣仲完整資料已保存: {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"保存資料失敗: {e}")
        return None

def git_push_lu_data():
    """推送盧廣仲資料"""
    try:
        logger.info("📤 準備推送盧廣仲資料到Git...")
        
        # 檢查變更
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            subprocess.run(['git', 'add', '.'], check=True)
            
            commit_message = f"🎵 盧廣仲完整資料爬取完成: {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            subprocess.run(['git', 'push'], check=True)
            
            logger.info("✅ 盧廣仲資料已推送到Git")
            return True
        else:
            logger.info("ℹ️ 沒有變更需要推送")
            return False
            
    except Exception as e:
        logger.error(f"Git推送失敗: {e}")
        return False

def main():
    """主函數"""
    try:
        # 爬取盧廣仲完整資料
        songs_data = scrape_lu_guangzhong_complete()
        
        if songs_data:
            # 分析資料
            analyze_lu_data(songs_data)
            
            # 保存資料
            output_file = save_lu_data(songs_data)
            
            if output_file:
                # 推送到Git
                git_push_lu_data()
                
                logger.info("🎉 盧廣仲測試完成！請檢查前台搜尋結果")
                logger.info(f"📁 資料檔案: {output_file}")
            else:
                logger.error("保存失敗")
        else:
            logger.error("爬取失敗")
            
    except Exception as e:
        logger.error(f"執行失敗: {e}")

if __name__ == "__main__":
    main()