#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
背景大規模爬蟲系統
適合長時間背景執行，處理所有需要改進的歌手
具備自動恢復、進度保存、日誌記錄等功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lu_benchmark_mass_scraper import LuBenchmarkMassScraper
import time
import signal
import logging
from datetime import datetime
import json

class BackgroundMassScraper(LuBenchmarkMassScraper):
    def __init__(self, resume_from_checkpoint=True):
        # 設置日誌
        self.setup_logging()
        self.logger = logging.getLogger('BackgroundScraper')
        
        # 初始化父類
        super().__init__()
        
        # 背景執行配置
        self.resume_from_checkpoint = resume_from_checkpoint
        self.checkpoint_file = "background_checkpoint.json"
        self.max_singers_per_session = 200  # 每次會話最多處理200位歌手
        self.batch_size = 5  # 減小批次避免長時間阻塞
        self.longer_delays = (4.0, 7.0)  # 更長延遲確保穩定性
        
        # 覆蓋延遲設置
        self.delay_range = self.longer_delays
        
        # 載入檢查點
        self.processed_singers_set = self.load_checkpoint()
        
        # 過濾已處理的歌手
        self.filter_unprocessed_singers()
        
        self.logger.info(f"背景爬蟲初始化完成")
        self.logger.info(f"待處理歌手: {len(self.singers_to_process)} 位")
        self.logger.info(f"本次會話上限: {self.max_singers_per_session} 位")
        
    def setup_logging(self):
        """設置日誌系統"""
        log_dir = "background_logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = f"{log_dir}/background_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
    def load_checkpoint(self):
        """載入檢查點"""
        if not self.resume_from_checkpoint or not os.path.exists(self.checkpoint_file):
            self.logger.info("沒有檢查點文件，從頭開始")
            return set()
        
        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            processed_set = set(checkpoint_data.get('processed_singers', []))
            self.logger.info(f"載入檢查點: 已處理 {len(processed_set)} 位歌手")
            
            return processed_set
            
        except Exception as e:
            self.logger.error(f"載入檢查點失敗: {e}")
            return set()
    
    def save_checkpoint(self, additional_processed=None):
        """保存檢查點"""
        if additional_processed:
            self.processed_singers_set.update(additional_processed)
        
        # 準備可序列化的統計資料
        serializable_stats = self.stats.copy()
        if 'start_time' in serializable_stats and hasattr(serializable_stats['start_time'], 'isoformat'):
            serializable_stats['start_time'] = serializable_stats['start_time'].isoformat()
        
        checkpoint_data = {
            'last_updated': datetime.now().isoformat(),
            'processed_singers': list(self.processed_singers_set),
            'total_processed': len(self.processed_singers_set),
            'session_stats': serializable_stats
        }
        
        try:
            # 寫入臨時文件然後重命名，確保原子性
            temp_file = self.checkpoint_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
            
            os.rename(temp_file, self.checkpoint_file)
            self.logger.info(f"檢查點已保存: {len(self.processed_singers_set)} 位歌手已處理")
            
        except Exception as e:
            self.logger.error(f"保存檢查點失敗: {e}")
    
    def filter_unprocessed_singers(self):
        """過濾未處理的歌手"""
        original_count = len(self.singers_to_process)
        
        # 移除已處理的歌手
        self.singers_to_process = [
            singer for singer in self.singers_to_process 
            if singer not in self.processed_singers_set
        ]
        
        # 限制本次會話的處理數量
        if len(self.singers_to_process) > self.max_singers_per_session:
            self.logger.info(f"限制本次會話處理數量: {self.max_singers_per_session}")
            self.singers_to_process = self.singers_to_process[:self.max_singers_per_session]
        
        # 重新計算批次
        self.total_batches = (len(self.singers_to_process) + self.batch_size - 1) // self.batch_size
        self.stats['total_singers'] = len(self.singers_to_process)
        
        self.logger.info(f"歌手過濾完成: {original_count} → {len(self.singers_to_process)} 位")
    
    def quick_filter_needing_improvement(self):
        """快速過濾需要改進的歌手"""
        self.logger.info("快速篩選需要改進的歌手...")
        
        needs_improvement = []
        checked = 0
        
        for singer in self.singers_to_process:
            if self.shutdown_requested:
                break
                
            checked += 1
            if checked % 50 == 0:
                self.logger.info(f"篩選進度: {checked}/{len(self.singers_to_process)}")
            
            benchmark_check = self.check_singer_against_benchmark(singer)
            
            if benchmark_check['needs_processing']:
                needs_improvement.append(singer)
        
        # 更新處理清單為真正需要改進的歌手
        self.singers_to_process = needs_improvement
        self.total_batches = (len(self.singers_to_process) + self.batch_size - 1) // self.batch_size
        self.stats['total_singers'] = len(self.singers_to_process)
        
        self.logger.info(f"篩選完成: {len(needs_improvement)} 位歌手需要改進")
    
    def enhanced_process_singer(self, singer_name):
        """增強版歌手處理，包含更多日誌和錯誤處理"""
        try:
            self.logger.info(f"開始處理: {singer_name}")
            
            # 檢查基準
            benchmark_check = self.check_singer_against_benchmark(singer_name)
            
            if benchmark_check['meets_benchmark']:
                self.logger.info(f"{singer_name}: 已達基準標準 ({benchmark_check['benchmark_score']:.1%})")
                return {
                    'singer': singer_name,
                    'status': 'already_complete',
                    'benchmark_score': benchmark_check['benchmark_score']
                }
            
            self.logger.info(f"{singer_name}: 當前基準 {benchmark_check['benchmark_score']:.1%}, 開始搜尋...")
            
            # 搜索Taiwan Song King資料
            session = self.create_session()
            new_songs, companies_found, raw_data = self.search_taiwan_songking_data(singer_name, session)
            session.close()
            
            if new_songs:
                # 整合資料
                new_count, updated_count = self.integrate_singer_data(singer_name, new_songs)
                
                # 保存個別結果
                self._save_singer_result(singer_name, new_songs, companies_found, raw_data)
                
                # 重新檢查基準
                updated_benchmark = self.check_singer_against_benchmark(singer_name)
                
                result = {
                    'singer': singer_name,
                    'status': 'processed',
                    'new_songs': new_count,
                    'updated_songs': updated_count,
                    'total_new_songs': len(new_songs),
                    'companies_found': len(companies_found),
                    'benchmark_before': benchmark_check['benchmark_score'],
                    'benchmark_after': updated_benchmark['benchmark_score'],
                    'meets_benchmark_now': updated_benchmark['meets_benchmark']
                }
                
                self.logger.info(f"{singer_name}: 完成 +{new_count}首新歌, 基準 {benchmark_check['benchmark_score']:.1%} → {updated_benchmark['benchmark_score']:.1%}")
                return result
            else:
                self.logger.warning(f"{singer_name}: 無新資料")
                return {
                    'singer': singer_name,
                    'status': 'no_data',
                    'benchmark_score': benchmark_check['benchmark_score']
                }
                
        except Exception as e:
            self.logger.error(f"{singer_name}: 處理失敗 - {str(e)}")
            return {
                'singer': singer_name,
                'status': 'failed',
                'error': str(e)
            }
    
    def create_session(self):
        """創建會話，增加重試機制"""
        import requests
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # 設置重試策略
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def process_batch_with_checkpoint(self, batch_singers):
        """處理批次並定期保存檢查點"""
        batch_results = []
        processed_in_batch = []
        
        self.logger.info(f"開始處理批次: {len(batch_singers)} 位歌手")
        
        for i, singer in enumerate(batch_singers, 1):
            if self.shutdown_requested:
                self.logger.info("收到關閉信號，停止處理")
                break
            
            self.logger.info(f"[{i:2d}/{len(batch_singers)}] 處理中: {singer}")
            
            result = self.enhanced_process_singer(singer)
            batch_results.append(result)
            processed_in_batch.append(singer)
            
            # 更新統計
            with self.stats_lock:
                self.stats['processed_singers'] += 1
                if result['status'] == 'processed':
                    self.stats['successful_singers'] += 1
                    self.stats['new_songs_added'] += result.get('new_songs', 0)
                    self.stats['updated_singers'] += 1
                elif result['status'] == 'failed':
                    self.stats['failed_singers'] += 1
            
            # 每處理5個歌手保存一次檢查點
            if i % 5 == 0:
                self.save_checkpoint(processed_in_batch[-5:])
        
        # 批次結束保存檢查點
        self.save_checkpoint(processed_in_batch)
        
        return batch_results
    
    def run_background_scraping(self):
        """執行背景爬取"""
        self.logger.info("=" * 60)
        self.logger.info("背景大規模爬蟲開始執行")
        self.logger.info("=" * 60)
        
        # 快速篩選需要改進的歌手
        if len(self.singers_to_process) > 100:
            self.quick_filter_needing_improvement()
        
        if not self.singers_to_process:
            self.logger.info("沒有歌手需要處理")
            return []
        
        self.logger.info(f"開始處理 {len(self.singers_to_process)} 位歌手")
        self.logger.info(f"分為 {self.total_batches} 批次，每批 {self.batch_size} 位")
        
        all_results = []
        
        # 分批處理
        for batch_start in range(0, len(self.singers_to_process), self.batch_size):
            if self.shutdown_requested:
                self.logger.info("收到關閉信號，停止執行")
                break
                
            batch_end = min(batch_start + self.batch_size, len(self.singers_to_process))
            batch_singers = self.singers_to_process[batch_start:batch_end]
            
            batch_num = batch_start // self.batch_size
            self.logger.info(f"\n--- 批次 {batch_num + 1}/{self.total_batches} ---")
            
            batch_results = self.process_batch_with_checkpoint(batch_singers)
            all_results.extend(batch_results)
            
            # 批次間休息
            if not self.shutdown_requested and batch_num < self.total_batches - 1:
                self.logger.info("批次間休息45秒...")
                time.sleep(45)
        
        # 生成最終報告
        self.logger.info("生成最終報告...")
        self._generate_final_report(all_results)
        
        self.logger.info("背景爬蟲執行完成")
        return all_results

def main():
    """主程序 - 背景執行版本"""
    print("🔄 背景大規模爬蟲系統")
    print("=" * 40)
    
    # 檢查是否要恢復
    resume = True
    if len(sys.argv) > 1 and sys.argv[1] == '--fresh':
        resume = False
        print("🆕 重新開始（忽略檢查點）")
    
    scraper = BackgroundMassScraper(resume_from_checkpoint=resume)
    
    try:
        results = scraper.run_background_scraping()
        
        if results:
            successful_count = sum(1 for r in results if r['status'] == 'processed')
            improved_count = sum(1 for r in results 
                               if r['status'] == 'processed' and r.get('meets_benchmark_now', False))
            total_new_songs = sum(r.get('new_songs', 0) for r in results if r['status'] == 'processed')
            
            print(f"\n🎉 背景執行完成！")
            print(f"✅ 成功處理: {successful_count}/{len(results)} 位歌手")
            print(f"🎯 達到基準: {improved_count} 位歌手")
            print(f"🎵 新增歌曲: {total_new_songs} 首")
            print(f"📊 詳細日誌: background_logs/ 目錄")
        else:
            print(f"\n⚠️ 本次會話沒有處理任何歌手")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ 用戶中斷，檢查點已保存")
        scraper.logger.info("用戶中斷，數據已保存")
        
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
        scraper.logger.error(f"執行錯誤: {e}", exc_info=True)

if __name__ == "__main__":
    main()