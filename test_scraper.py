#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統一爬蟲測試腳本 - 快速驗證新架構
"""

from unified_scraper import UnifiedKaraokeScraper
import time

def test_unified_scraper():
    """測試統一爬蟲功能"""
    print("🧪 統一爬蟲測試")
    print("=" * 30)
    
    # 初始化爬蟲
    scraper = UnifiedKaraokeScraper(max_workers=2)
    
    # 測試用少量關鍵字
    test_keywords = [
        "周杰倫",    # 知名歌手
        "愛情",      # 熱門主題
        "2025",      # 年份
        "新歌",      # 類型
        "快樂"       # 情感
    ]
    
    print(f"📋 測試關鍵字: {', '.join(test_keywords)}")
    print(f"🔧 並行線程: {scraper.max_workers}")
    print()
    
    # 記錄開始狀態
    start_songs = scraper.unified_db["metadata"]["total_songs"]
    start_time = time.time()
    
    print(f"📊 開始狀態:")
    print(f"   歌曲數: {start_songs:,} 首")
    print()
    
    # 執行測試爬取
    try:
        print("🚀 開始測試爬取...")
        added_count = scraper.scrape_with_keywords(test_keywords)
        
        # 記錄結束狀態
        end_time = time.time()
        elapsed = end_time - start_time
        end_songs = scraper.unified_db["metadata"]["total_songs"]
        
        print(f"\n🎉 測試完成!")
        print(f"=" * 30)
        print(f"📊 結果統計:")
        print(f"   執行時間: {elapsed:.1f} 秒")
        print(f"   新增歌曲: {added_count} 首")
        print(f"   總歌曲數: {end_songs:,} 首")
        print(f"   平均速度: {added_count/elapsed:.2f} 首/秒")
        
        # 檢查檔案是否正確更新
        import os
        files_to_check = [
            'public/unified_karaoke_db.json',
            'public/songs_simplified.json', 
            'public/singers_data.json'
        ]
        
        print(f"\n📁 檔案更新檢查:")
        for file_path in files_to_check:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path) / 1024 / 1024  # MB
                print(f"   ✅ {file_path}: {size:.2f} MB")
            else:
                print(f"   ❌ {file_path}: 不存在")
                
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        return False

def main():
    """主函數"""
    success = test_unified_scraper()
    
    print(f"\n💡 測試結果: {'✅ 通過' if success else '❌ 失敗'}")
    
    if success:
        print(f"\n🎯 下一步建議:")
        print(f"1. 執行完整爬取: ./auto_scraper.sh")
        print(f"2. 檢查進度: ./check_progress.sh") 
        print(f"3. 監控執行: watch -n 5 ./check_progress.sh")
    else:
        print(f"\n🔧 除錯建議:")
        print(f"1. 檢查網路連線: ping song.corp.com.tw")
        print(f"2. 檢查資料庫: python3 database_unifier.py")
        print(f"3. 查看錯誤日誌: tail scraper.log")

if __name__ == "__main__":
    main()