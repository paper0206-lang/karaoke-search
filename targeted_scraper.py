#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
針對性爬蟲 - 專門處理需要改進的歌手
基於快速分析結果，重點處理評分較低的歌手
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lu_benchmark_mass_scraper import LuBenchmarkMassScraper
import time

class TargetedScraper(LuBenchmarkMassScraper):
    def __init__(self, max_singers=100):
        super().__init__()
        
        # 限制處理數量避免過長時間
        self.max_singers_to_process = max_singers
        
        print(f"🎯 針對性改進模式")
        print(f"📊 快速掃描所有歌手，找出最需要改進的 {max_singers} 位...")
        
        # 快速找出需要改進的歌手
        self.target_singers = self._find_target_singers()
        
        # 更新處理清單
        self.singers_to_process = self.target_singers
        self.batch_size = 10  # 每批10位歌手
        self.total_batches = (len(self.singers_to_process) + self.batch_size - 1) // self.batch_size
        
        # 更新統計
        self.stats['total_singers'] = len(self.singers_to_process)
        
        print(f"🎯 目標確定:")
        print(f"   需要改進的歌手: {len(self.target_singers)} 位")
        print(f"   處理批次: {self.total_batches} 批")
        print(f"   預估時間: {self.total_batches * 5:.0f} 分鐘")
        print("=" * 50)
    
    def _find_target_singers(self):
        """快速找出需要改進的歌手"""
        print("🔍 掃描歌手基準狀態...")
        
        candidates = []
        total_singers = len(self.singers_to_process)
        checked = 0
        
        # 分批檢查避免記憶體問題
        batch_size = 200
        for batch_start in range(0, total_singers, batch_size):
            batch_end = min(batch_start + batch_size, total_singers)
            batch_singers = self.singers_to_process[batch_start:batch_end]
            
            for singer in batch_singers:
                checked += 1
                
                if checked % 100 == 0:
                    print(f"   進度: {checked}/{total_singers} ({checked/total_singers*100:.1f}%)")
                
                benchmark_check = self.check_singer_against_benchmark(singer)
                
                if benchmark_check['needs_processing']:
                    candidates.append({
                        'singer': singer,
                        'score': benchmark_check['benchmark_score'],
                        'songs': benchmark_check['current_songs'],
                        'companies': benchmark_check.get('companies_covered', 0),
                        'gaps': benchmark_check.get('gaps', [])
                    })
                
                # 如果已經找到足夠的候選者就停止
                if len(candidates) >= self.max_singers_to_process * 2:
                    break
            
            if len(candidates) >= self.max_singers_to_process * 2:
                break
        
        print(f"   完成掃描: {checked} 位歌手")
        print(f"   找到候選: {len(candidates)} 位需要改進")
        
        # 按基準分數排序，優先處理分數最低的
        candidates.sort(key=lambda x: x['score'])
        
        # 取前N位
        selected = candidates[:self.max_singers_to_process]
        
        if selected:
            print(f"\n🎯 選定處理的前10位歌手:")
            for i, info in enumerate(selected[:10], 1):
                print(f"   {i:2d}. {info['singer']:15s}: {info['score']:.1%} "
                      f"({info['songs']}首, {info['companies']}家KTV)")
        
        return [info['singer'] for info in selected]

def main():
    print("🎯 針對性歌手改進系統")
    print("=" * 35)
    
    # 詢問處理數量
    try:
        max_singers = int(input("請輸入要處理的歌手數量 (建議50-200，預設100): ") or "100")
        max_singers = max(10, min(max_singers, 500))  # 限制在合理範圍
    except:
        max_singers = 100
    
    print(f"🎯 將處理最需要改進的 {max_singers} 位歌手")
    
    scraper = TargetedScraper(max_singers)
    
    if not scraper.singers_to_process:
        print("\n🎉 沒有找到需要改進的歌手！")
        print("✅ 所有檢查的歌手都已達到基準標準")
        return
    
    print(f"\n🚀 開始針對性處理...")
    
    try:
        results = scraper.run_mass_scraping()
        
        if results:
            successful_count = sum(1 for r in results if r['status'] == 'processed')
            improved_count = sum(1 for r in results 
                               if r['status'] == 'processed' and r.get('meets_benchmark_now', False))
            total_new_songs = sum(r.get('new_songs', 0) for r in results if r['status'] == 'processed')
            
            print(f"\n🎉 針對性處理完成！")
            print(f"✅ 成功處理: {successful_count}/{len(results)} 位歌手")
            print(f"🎯 達到基準: {improved_count} 位歌手")
            print(f"🎵 新增歌曲: {total_new_songs} 首")
            print(f"📊 成功率: {successful_count/len(results)*100:.1f}%")
            print(f"🎖️ 基準達成率: {improved_count/successful_count*100:.1f}%" if successful_count > 0 else "")
            
            print(f"\n📁 詳細結果保存在 mass_scraping_results/ 目錄")
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