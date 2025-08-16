#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試正確基準機制
"""

import logging
from taiwan_ktv_comparator import TaiwanKTVComparator

def simple_test():
    """簡單測試一個歌手"""
    
    # 設置日誌
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    comparator = TaiwanKTVComparator()
    
    # 測試一個較小的歌手以減少查詢時間
    test_singer = "盧廣仲"
    
    print(f"🧪 測試歌手: {test_singer}")
    print("=" * 50)
    
    try:
        # 先查看我們資料庫的數據
        our_data = comparator.get_our_database_ktv_count(test_singer)
        print(f"📊 我們資料庫:")
        print(f"   存在: {'是' if our_data['exists'] else '否'}")
        print(f"   KTV編號: {our_data['total_ktv_entries']} 筆")
        print(f"   歌曲數: {our_data['unique_songs']} 首")
        print(f"   KTV公司: {our_data['companies_count']} 家")
        
        # 查詢台灣點歌網數據
        print(f"\n🔍 查詢台灣點歌網...")
        website_data = comparator.get_singer_ktv_count_from_website(test_singer)
        
        if website_data['search_successful']:
            print(f"📊 台灣點歌網:")
            print(f"   KTV編號: {website_data['total_ktv_entries']} 筆")
            print(f"   歌曲數: {website_data['unique_songs']} 首")
            print(f"   KTV公司: {website_data['companies_count']} 家")
            
            # 計算5%差異
            if website_data['total_ktv_entries'] > 0:
                coverage_ratio = our_data['total_ktv_entries'] / website_data['total_ktv_entries']
                print(f"\n🎯 覆蓋率分析:")
                print(f"   我們/網站: {our_data['total_ktv_entries']}/{website_data['total_ktv_entries']}")
                print(f"   覆蓋率: {coverage_ratio:.1%}")
                print(f"   差異: {abs(1-coverage_ratio):.1%}")
                
                # 5%閾值檢查
                needs_scraping = coverage_ratio < 0.95
                print(f"   需要爬取: {'是' if needs_scraping else '否'} (5%閾值)")
                
                if needs_scraping:
                    print(f"\n🔍 檢查缺失編號...")
                    missing = comparator.find_missing_ktv_entries(test_singer)
                    print(f"   缺失編號: {len(missing)} 筆")
                    
                    if missing:
                        print(f"   前3筆示例:")
                        for i, entry in enumerate(missing[:3]):
                            print(f"     {i+1}. {entry['song_name']} - {entry['company']}:{entry['number']}")
            else:
                print("\n⚠️ 台灣點歌網沒有該歌手資料")
        else:
            print(f"❌ 台灣點歌網查詢失敗: {website_data.get('error', '未知錯誤')}")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    simple_test()