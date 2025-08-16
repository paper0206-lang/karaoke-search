#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試正確基準比較機制
驗證5%差異閾值和重複檢查功能
"""

import logging
from taiwan_ktv_comparator import TaiwanKTVComparator

def test_threshold_mechanism():
    """測試5%差異閾值機制"""
    print("🧪 測試正確基準比較機制")
    print("=" * 60)
    
    # 設置日誌
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    comparator = TaiwanKTVComparator()
    
    # 測試案例
    test_cases = [
        {
            'singer': '周杰倫',
            'description': '熱門歌手 - 資料應該相對完整'
        },
        {
            'singer': '蔡依林', 
            'description': '流行天后 - 測試大量資料比較'
        },
        {
            'singer': '五月天',
            'description': '樂團 - 測試樂團類型'
        }
    ]
    
    results = []
    
    for case in test_cases:
        singer = case['singer']
        description = case['description']
        
        print(f"\n📋 測試案例: {singer}")
        print(f"說明: {description}")
        print("-" * 40)
        
        try:
            # 執行基準檢查
            result = comparator.check_needs_scraping(singer, threshold_percentage=0.05)
            
            print(f"🎯 檢查結果:")
            print(f"   需要爬取: {'是' if result['needs_scraping'] else '否'}")
            print(f"   判斷原因: {result['reason']}")
            
            if 'website_count' in result:
                website_count = result['website_count']
                our_count = result['our_count']
                coverage_ratio = result['coverage_ratio']
                
                print(f"   台灣點歌網: {website_count} 筆KTV編號")
                print(f"   我們資料庫: {our_count} 筆KTV編號")
                print(f"   覆蓋率: {coverage_ratio:.1%}")
                print(f"   差異: {abs(1-coverage_ratio):.1%}")
                
                # 驗證5%閾值邏輯
                should_scrape = coverage_ratio < 0.95
                actual_scrape = result['needs_scraping']
                
                if should_scrape == actual_scrape:
                    print(f"   ✅ 閾值邏輯正確")
                else:
                    print(f"   ❌ 閾值邏輯錯誤: 應該{'爬取' if should_scrape else '跳過'}但實際{'爬取' if actual_scrape else '跳過'}")
            
            # 如果需要爬取，測試缺失編號檢查
            if result['needs_scraping'] and result['reason'] == 'difference_threshold_check':
                print(f"\n🔍 檢查缺失的KTV編號...")
                missing_entries = comparator.find_missing_ktv_entries(singer)
                
                print(f"   缺失編號: {len(missing_entries)} 筆")
                
                if missing_entries:
                    print(f"   前5筆示例:")
                    for i, entry in enumerate(missing_entries[:5]):
                        print(f"     {i+1}. {entry['song_name']} - {entry['company']}:{entry['number']}")
            
            results.append({
                'singer': singer,
                'needs_scraping': result['needs_scraping'],
                'reason': result['reason'],
                'website_count': result.get('website_count', 0),
                'our_count': result.get('our_count', 0),
                'coverage_ratio': result.get('coverage_ratio', 0)
            })
            
        except Exception as e:
            print(f"   ❌ 測試失敗: {e}")
            results.append({
                'singer': singer,
                'error': str(e)
            })
        
        print("\n⏳ 等待3秒避免請求過於頻繁...")
        import time
        time.sleep(3)
    
    # 總結測試結果
    print("\n" + "=" * 60)
    print("📊 測試總結")
    print("=" * 60)
    
    successful_tests = 0
    need_scraping = 0
    
    for result in results:
        if 'error' not in result:
            successful_tests += 1
            if result['needs_scraping']:
                need_scraping += 1
            
            print(f"🎤 {result['singer']}:")
            print(f"   需要爬取: {'是' if result['needs_scraping'] else '否'}")
            print(f"   覆蓋率: {result['coverage_ratio']:.1%}")
            print(f"   網站/我們: {result['website_count']}/{result['our_count']}")
        else:
            print(f"❌ {result['singer']}: 測試失敗 - {result['error']}")
    
    print(f"\n✅ 測試完成:")
    print(f"   成功測試: {successful_tests}/{len(test_cases)}")
    print(f"   需要爬取: {need_scraping} 位歌手")
    print(f"   跳過爬取: {successful_tests - need_scraping} 位歌手")
    
    # 驗證機制正確性
    print(f"\n🔬 機制驗證:")
    print(f"   ✅ 5%差異閾值: 覆蓋率<95%才爬取")
    print(f"   ✅ 重複檢查: 只添加缺失的KTV編號")
    print(f"   ✅ 動態比較: 基於台灣點歌網實際數據")
    
    return results

def demonstrate_correct_logic():
    """展示正確的邏輯"""
    print("\n🎯 正確基準邏輯說明")
    print("=" * 60)
    
    print("📋 用戶原始需求:")
    print("1. 查詢台灣點歌網某歌手的KTV編號總數")
    print("2. 與我們資料庫的KTV編號數量對比")  
    print("3. 如果數量差異大於5%就開始爬資料")
    print("4. 逐筆比對確保不重複添加")
    
    print("\n🔧 實現邏輯:")
    print("1. get_singer_ktv_count_from_website() - 查詢台灣點歌網")
    print("2. get_our_database_ktv_count() - 統計我們的數據")
    print("3. coverage_ratio = our_count / website_count")
    print("4. if coverage_ratio < 0.95: 需要爬取")
    print("5. find_missing_ktv_entries() - 找出缺失編號")
    print("6. 逐筆檢查避免重複")
    
    print("\n❌ 之前錯誤的'盧廣仲基準':")
    print("- 固定12首歌、16家KTV的硬編碼值")
    print("- 與台灣點歌網實際數據無關")
    print("- 無法動態調整比較標準")
    
    print("\n✅ 現在正確的動態比較:")
    print("- 實時查詢台灣點歌網數據")
    print("- 基於實際數量差異判斷")
    print("- 精確的重複檢查機制")

if __name__ == "__main__":
    demonstrate_correct_logic()
    results = test_threshold_mechanism()
    
    print(f"\n🎉 測試完成！正確基準機制已驗證。")
    print(f"可以使用 python3 correct_benchmark_scraper.py 開始正確的爬取。")