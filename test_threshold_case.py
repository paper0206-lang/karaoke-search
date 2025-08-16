#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試需要爬取的案例（覆蓋率低於95%）
"""

import logging
from taiwan_ktv_comparator import TaiwanKTVComparator

def test_low_coverage_singer():
    """測試一個覆蓋率較低的歌手"""
    
    # 設置日誌
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    comparator = TaiwanKTVComparator()
    
    # 尋找一個資料較少的歌手來測試
    test_singer = "張艾莉"  # 之前日誌中看到的歌手
    
    print(f"🧪 測試低覆蓋率歌手: {test_singer}")
    print("=" * 50)
    
    try:
        # 執行完整的基準檢查
        result = comparator.check_needs_scraping(test_singer, threshold_percentage=0.05)
        
        print(f"🎯 完整檢查結果:")
        print(f"   需要爬取: {'是' if result['needs_scraping'] else '否'}")
        print(f"   判斷原因: {result['reason']}")
        
        if 'website_count' in result:
            print(f"   台灣點歌網: {result['website_count']} 筆")
            print(f"   我們資料庫: {result['our_count']} 筆")
            print(f"   覆蓋率: {result['coverage_ratio']:.1%}")
            print(f"   差異: {result['difference_percentage']:.1%}")
            print(f"   閾值: {result['threshold']:.1%}")
            
            # 驗證5%邏輯
            expected_scraping = result['coverage_ratio'] < 0.95
            actual_scraping = result['needs_scraping']
            
            if expected_scraping == actual_scraping:
                print(f"   ✅ 5%閾值邏輯正確")
            else:
                print(f"   ❌ 5%閾值邏輯錯誤")
        
        # 如果需要爬取，展示正確的作業流程
        if result['needs_scraping'] and result['reason'] == 'difference_threshold_check':
            print(f"\n🔧 正確爬取流程:")
            print(f"1. ✅ 檢查台灣點歌網數據")
            print(f"2. ✅ 比較我們的資料庫")
            print(f"3. ✅ 發現覆蓋率 < 95%")
            print(f"4. 🔍 查找缺失的KTV編號...")
            
            missing_entries = comparator.find_missing_ktv_entries(test_singer)
            print(f"5. 📋 找到 {len(missing_entries)} 筆缺失編號")
            
            if missing_entries:
                print(f"6. 📝 缺失編號示例:")
                for i, entry in enumerate(missing_entries[:5]):
                    print(f"   {i+1}. {entry['song_name']} - {entry['company']}:{entry['number']}")
                
                print(f"\n💡 這些就是需要添加到資料庫的新KTV編號")
                print(f"   避免重複: 只添加我們資料庫沒有的編號")
                print(f"   逐筆檢查: 確保每個編號都不重複")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    test_low_coverage_singer()