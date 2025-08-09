#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正周杰倫搜尋問題 - 專用爬蟲
"""

from singer_scraper import SingerScraper
import json
import time

def scrape_jay_chou_comprehensive():
    """全面爬取周杰倫的歌曲"""
    scraper = SingerScraper(max_workers=2)
    
    print("🎤 開始全面收集周杰倫歌曲...")
    
    # 多種搜尋策略
    search_terms = [
        "周杰倫",
        "Jay Chou", 
        "Jay",
        "杰伦",
        "周董"
    ]
    
    all_jay_songs = []
    
    for term in search_terms:
        print(f"\n🔍 使用關鍵字: {term}")
        try:
            songs = scraper.scrape_singer_exhaustive(term)
            if songs:
                print(f"   找到 {len(songs)} 首歌曲")
                all_jay_songs.extend(songs)
            time.sleep(2)  # 避免請求過頻
        except Exception as e:
            print(f"   ❌ 搜尋 {term} 時出錯: {e}")
    
    # 去重並整理
    unique_songs = {}
    for song in all_jay_songs:
        song_key = f"{song.get('歌名', '')}_{song.get('歌手', '')}"
        if song_key not in unique_songs:
            unique_songs[song_key] = song
    
    print(f"\n🎉 總共找到 {len(unique_songs)} 首周杰倫的歌曲")
    
    # 保存結果
    with open('jay_chou_songs.json', 'w', encoding='utf-8') as f:
        json.dump(list(unique_songs.values()), f, ensure_ascii=False, indent=2)
    
    # 顯示部分結果
    print(f"\n📋 部分歌曲清單:")
    for i, song in enumerate(list(unique_songs.values())[:20], 1):
        print(f"   {i:2d}. {song.get('歌名', 'N/A')} - {song.get('歌手', 'N/A')}")
        if song.get('編號資訊'):
            print(f"       編號: {len(song['編號資訊'])} 個")
    
    return list(unique_songs.values())

if __name__ == "__main__":
    songs = scrape_jay_chou_comprehensive()
    print(f"\n✅ 完成！共收集 {len(songs)} 首周杰倫歌曲")