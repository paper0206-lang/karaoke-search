#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能基準爬蟲 - 只處理未達到盧廣仲基準的歌手
先分析所有歌手，找出需要改進的，然後批次處理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lu_benchmark_mass_scraper import LuBenchmarkMassScraper

class SmartBenchmarkScraper(LuBenchmarkMassScraper):
    def __init__(self):
        super().__init__()
        
        print(f"🧠 智能模式：分析所有歌手的基準狀態...")
        
        # 分析所有歌手，找出需要處理的
        self.singers_needing_work = self._analyze_all_singers()
        
        # 更新處理清單
        self.singers_to_process = self.singers_needing_work
        self.batch_size = 10  # 每批10位歌手
        self.total_batches = (len(self.singers_to_process) + self.batch_size - 1) // self.batch_size
        
        # 更新統計
        self.stats['total_singers'] = len(self.singers_to_process)
        
        print(f"📊 分析結果：")
        print(f"   需要處理的歌手: {len(self.singers_needing_work)} 位")
        print(f"   已達標準的歌手: {len(self.singers_to_process) + len(self.singers_needing_work) - len(self.singers_to_process)} 位")
        print(f"   處理批次: {self.total_batches} 批")
        print("=" * 50)
    
    def _analyze_all_singers(self):
        """分析所有歌手，找出需要改進的"""
        print("🔍 正在分析所有歌手的基準狀態...")
        
        needs_work = []
        already_good = []
        
        total_singers = len(self.singers_to_process)
        
        for i, singer in enumerate(self.singers_to_process, 1):
            if i % 100 == 0 or i == total_singers:
                print(f"   進度: {i}/{total_singers} ({i/total_singers*100:.1f}%)")
            
            benchmark_check = self.check_singer_against_benchmark(singer)
            
            if benchmark_check['needs_processing']:
                needs_work.append({
                    'singer': singer,
                    'current_score': benchmark_check['benchmark_score'],
                    'current_songs': benchmark_check['current_songs'],
                    'gaps': benchmark_check.get('gaps', [])
                })
            else:
                already_good.append({
                    'singer': singer,
                    'score': benchmark_check['benchmark_score']
                })
        
        print(f"\n📋 分析完成:")
        print(f"   需要改進: {len(needs_work)} 位")
        print(f"   已達標準: {len(already_good)} 位")
        
        # 按基準分數排序，優先處理分數較低的
        needs_work.sort(key=lambda x: x['current_score'])
        
        if needs_work:
            print(f"\n🎯 最需要改進的前10位歌手:")
            for i, info in enumerate(needs_work[:10], 1):
                print(f"   {i:2d}. {info['singer']:15s}: {info['current_score']:.1%} "
                      f"({info['current_songs']}首歌)")
        
        return [info['singer'] for info in needs_work]

def main():
    print("🧠 智能基準爬蟲系統")
    print("=" * 30)
    
    scraper = SmartBenchmarkScraper()
    
    if not scraper.singers_to_process:
        print("\n🎉 所有歌手都已達到盧廣仲基準標準！")
        print("✅ 無需進一步處理")
        return
    
    print(f"\n🚀 開始處理 {len(scraper.singers_to_process)} 位需要改進的歌手")
    
    try:
        results = scraper.run_mass_scraping()
        
        if results:
            successful_count = sum(1 for r in results if r['status'] == 'processed')
            improved_count = sum(1 for r in results 
                               if r['status'] == 'processed' and r.get('meets_benchmark_now', False))
            
            print(f"\n🎉 智能處理完成！")
            print(f"✅ 成功處理: {successful_count}/{len(results)} 位歌手")
            print(f"🎯 達到基準: {improved_count} 位歌手")
            print(f"📊 建議查看detailed_report了解完整結果")
        else:
            print(f"\n⚠️ 未能完成預期的處理任務")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ 用戶中斷，已保存完成的數據")
        
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()