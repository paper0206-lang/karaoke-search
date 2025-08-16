#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
繼續爬取腳本 - 從第6920頁開始
使用5線程 + 增強安全性
"""

import sys
import os

# 匯入優化爬蟲
from optimized_scraper import OptimizedTaiwanScraper

def continue_from_last_position():
    """從上次停止的位置繼續爬取"""
    print("🔄 繼續模式啟動")
    print("=" * 50)
    
    # 從第6920頁開始（上次停在6919頁）
    start_page = 6920
    estimated_total = 15000  # 根據之前的分析
    
    print(f"📍 繼續爬取設置:")
    print(f"   起始頁面: 第{start_page}頁")
    print(f"   預估總頁: 第{estimated_total}頁")
    print(f"   剩餘頁數: {estimated_total - start_page + 1:,} 頁")
    print(f"   預估歌曲: {(estimated_total - start_page + 1) * 50:,} 首")
    print()
    
    # 創建自定義的繼續版本爬蟲
    class ContinueScraper(OptimizedTaiwanScraper):
        def scrape_company_from_page(self, company, start_page, total_pages_estimate=15000):
            """從指定頁面開始爬取公司"""
            print(f"🎯 從第{start_page}頁開始爬取: {company}")
            print(f"   線程數: {self.max_workers}")
            print(f"   批次大小: {self.batch_size} 首歌")
            print(f"   安全延遲: 1.5-4.0秒 + 智能重試")
            
            # 計算剩餘頁面
            remaining_pages = total_pages_estimate - start_page + 1
            pages_per_thread = 150  # 每個線程處理150頁
            page_ranges = []
            
            current_page = start_page
            while current_page <= total_pages_estimate:
                end_page = min(current_page + pages_per_thread - 1, total_pages_estimate)
                page_ranges.append((current_page, end_page))
                current_page = end_page + 1
            
            print(f"📊 分配策略: {len(page_ranges)} 個任務")
            
            # 使用父類的分批爬取邏輯
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            completed_tasks = 0
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_range = {
                    executor.submit(self.scrape_page_range, company, start, end): (start, end)
                    for start, end in page_ranges
                }
                
                for future in as_completed(future_to_range):
                    if self.shutdown_event.is_set():
                        break
                        
                    start, end = future_to_range[future]
                    
                    try:
                        page_data = future.result()
                        
                        # 添加到批次數據
                        with self.data_lock:
                            self.batch_data.extend(page_data)
                            
                            # 檢查是否需要保存批次
                            if len(self.batch_data) >= self.batch_size:
                                self._save_batch()
                        
                        completed_tasks += 1
                        print(f"🎉 任務完成 {completed_tasks}/{len(page_ranges)}: 第{start}-{end}頁 ({len(page_data)} 首歌)")
                        
                    except Exception as e:
                        print(f"❌ 任務失敗 第{start}-{end}頁: {e}")
            
            # 保存剩餘數據
            with self.data_lock:
                if self.batch_data:
                    self._save_batch()
            
            print(f"🎉 {company} 繼續爬取完成！總共保存: {self.total_saved} 首歌")
    
    # 創建繼續爬蟲實例
    scraper = ContinueScraper(max_workers=5, batch_size=1000)
    
    try:
        print("🚀 開始繼續爬取...")
        print("⚠️ 按 Ctrl+C 可隨時安全停止")
        print()
        
        # 從指定頁面開始爬取音圓
        scraper.scrape_company_from_page("音圓", start_page, estimated_total)
        
        # 合併批次文件
        merged_file = scraper.merge_batches()
        
        if merged_file:
            print(f"\n✅ 繼續爬取任務完成！")
            print(f"📁 合併文件: {merged_file}")
            print(f"📊 總歌曲數: {scraper.total_saved}")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用戶中斷，正在安全關閉...")
        scraper.shutdown_event.set()
        
        # 保存當前批次
        with scraper.data_lock:
            if scraper.batch_data:
                scraper._save_batch()
        
        print("✅ 已安全停止，數據已保存")
        
    except Exception as e:
        print(f"\n❌ 繼續爬取失敗: {e}")
    finally:
        # 清理會話
        for session in scraper.sessions.values():
            session.close()
        
        print("\n📊 最終統計:")
        print(f"   保存批次數: {scraper.batch_count}")
        print(f"   總歌曲數: {scraper.total_saved}")

if __name__ == "__main__":
    continue_from_last_position()