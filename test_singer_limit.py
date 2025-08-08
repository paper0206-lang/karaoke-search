#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試歌手爬蟲的50首限制突破效果
"""

import sys
sys.path.append('.')
from singer_scraper import SingerScraper

def test_singer_limit():
    print("🧪 測試歌手爬蟲50首限制突破")
    print("="*50)
    
    # 選擇一個歌曲很多的歌手進行測試
    test_singers = ["周杰倫", "蔡依林", "林俊傑"]
    
    scraper = SingerScraper(max_workers=1)
    
    for singer in test_singers:
        print(f"\n🎤 測試歌手: {singer}")
        print("-" * 30)
        
        # 測試單一公司的搜尋效果
        company = "錢櫃"
        results = scraper.search_company_exhaustive(company, singer)
        
        print(f"\n📊 {singer} 在 {company} 的統計:")
        print(f"   總歌曲數: {len(results)}")
        
        if len(results) > 50:
            print(f"   🎉 成功突破50首限制！")
        elif len(results) == 50:
            print(f"   ⚠️  可能仍受50首限制")
        else:
            print(f"   ℹ️  歌曲數未達50首")
        
        # 顯示歌曲清單（前10首和後10首）
        if results:
            print(f"\n🎵 歌曲範例 (前5首):")
            for i, song in enumerate(results[:5], 1):
                print(f"   {i}. {song.get('name', '未知')} - {song.get('code', '未知')}")
            
            if len(results) > 10:
                print(f"   ... (中間 {len(results)-10} 首)")
                print(f"🎵 歌曲範例 (後5首):")
                for i, song in enumerate(results[-5:], len(results)-4):
                    print(f"   {i}. {song.get('name', '未知')} - {song.get('code', '未知')}")
        
        # 只測試第一個歌手，避免過度請求
        break
    
    print(f"\n✅ 測試完成!")

if __name__ == "__main__":
    test_singer_limit()