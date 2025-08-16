#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試版大規模爬蟲 - 僅處理前5位歌手進行驗證
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lu_benchmark_mass_scraper import LuBenchmarkMassScraper

class TestMassScraper(LuBenchmarkMassScraper):
    def __init__(self):
        super().__init__()
        
        # 限制為前5位歌手進行測試
        self.singers_to_process = self.singers_to_process[:5]
        self.batch_size = 5  # 一次處理全部
        self.total_batches = 1
        
        print(f"🧪 測試模式：僅處理前5位歌手")
        print(f"📋 測試歌手：{', '.join(self.singers_to_process)}")
        print("=" * 50)

def main():
    print("🧪 大規模爬蟲測試模式")
    print("=" * 30)
    
    scraper = TestMassScraper()
    
    try:
        results = scraper.run_mass_scraping()
        
        if results:
            print(f"\n✅ 測試完成！處理了 {len(results)} 位歌手")
            for result in results:
                status = result['status']
                singer = result['singer']
                if status == 'processed':
                    print(f"   ✅ {singer}: +{result.get('new_songs', 0)}首新歌")
                elif status == 'already_complete':
                    print(f"   📋 {singer}: 已達標準")
                else:
                    print(f"   ❌ {singer}: {status}")
        else:
            print(f"\n⚠️ 測試未能完成")
        
    except Exception as e:
        print(f"\n❌ 測試錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()