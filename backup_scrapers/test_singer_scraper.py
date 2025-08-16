#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌手優先爬蟲測試 - 驗證突破50首限制功能
"""

from singer_focused_scraper import SingerFocusedScraper

def test_single_singer(singer_name="周杰倫"):
    """測試單一歌手的深度爬取"""
    print(f"🧪 測試歌手優先爬蟲: {singer_name}")
    print("=" * 40)
    
    scraper = SingerFocusedScraper(max_workers=2)
    
    # 記錄開始狀態
    start_songs = scraper.unified_db["metadata"]["total_songs"]
    print(f"📊 開始狀態: {start_songs:,} 首歌曲")
    
    # 測試深度搜尋
    songs = scraper.search_singer_comprehensive(singer_name)
    
    if songs:
        print(f"\n📈 搜尋結果分析:")
        print(f"   找到歌曲: {len(songs)} 首")
        
        # 按公司統計
        company_stats = {}
        for song in songs:
            company = song.get('公司', '未知')
            company_stats[company] = company_stats.get(company, 0) + 1
        
        print(f"\n🏢 公司分布:")
        for company, count in sorted(company_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"   {company:8s}: {count:3d} 首")
        
        # 顯示部分歌曲樣本
        print(f"\n🎵 歌曲樣本 (前10首):")
        for i, song in enumerate(songs[:10], 1):
            print(f"   {i:2d}. {song['歌名']:20s} - {song['公司']:6s} ({song['編號']})")
        
        # 加入統一資料庫
        added = scraper.add_songs_to_database(songs)
        print(f"\n💾 統一資料庫:")
        print(f"   新增歌曲: {added} 首")
        print(f"   總歌曲數: {scraper.unified_db['metadata']['total_songs']:,} 首")
        
        # 保存測試結果
        if scraper.save_unified_database():
            print(f"   ✅ 已保存到統一資料庫")
        
        return len(songs)
    else:
        print(f"   ❌ 沒有找到 {singer_name} 的歌曲")
        return 0

def test_batch_singers():
    """測試批次歌手爬取"""
    test_singers = ["告五人", "茄子蛋", "持修"]
    
    print(f"🧪 測試批次歌手爬取: {', '.join(test_singers)}")
    print("=" * 50)
    
    scraper = SingerFocusedScraper(max_workers=2)
    result = scraper.scrape_singers_batch(test_singers, save_frequency=1)
    
    print(f"\n🎉 批次測試完成，總計新增: {result} 首歌曲")
    return result

def main():
    print("🎤 歌手優先爬蟲測試系統")
    print("測試突破50首限制的多策略搜尋")
    print("=" * 50)
    
    choice = input("選擇測試模式:\n1. 測試單一歌手 (周杰倫)\n2. 測試批次歌手 (告五人,茄子蛋,持修)\n3. 自訂歌手測試\n請選擇 (1-3): ")
    
    if choice == '1':
        result = test_single_singer("周杰倫")
        print(f"\n🎯 測試結果: 找到 {result} 首歌曲")
        
    elif choice == '2':
        result = test_batch_singers()
        print(f"\n🎯 測試結果: 新增 {result} 首歌曲")
        
    elif choice == '3':
        singer_name = input("請輸入要測試的歌手名稱: ").strip()
        if singer_name:
            result = test_single_singer(singer_name)
            print(f"\n🎯 測試結果: 找到 {result} 首歌曲")
        else:
            print("❌ 沒有輸入歌手名稱")
    else:
        print("❌ 無效選擇")

if __name__ == "__main__":
    main()