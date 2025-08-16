#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終正確基準爬蟲
使用HAR文件洞察 + 用戶反饋優化
實現正確的5%閾值檢測和優先級排序
"""

import json
import os
import sys
import time
import logging
import signal
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

# 導入改進的台灣比較器
from improved_taiwan_comparator import ImprovedTaiwanComparator

class FinalCorrectScraper:
    def __init__(self):
        self.setup_logging()
        self.comparator = ImprovedTaiwanComparator()
        self.running = True
        self.current_batch = 0
        self.scraped_singers = 0
        self.skipped_singers = 0
        
        # 設置信號處理
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # 檢查點文件
        self.checkpoint_file = "final_scraper_checkpoint.json"
        self.results_file = "final_scraper_results.json"
        
        self.logger.info("🎯 最終正確基準爬蟲已初始化")
    
    def setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('final_correct_scraper.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('FinalCorrectScraper')
    
    def signal_handler(self, signum, frame):
        """信號處理器"""
        self.logger.info(f"🛑 收到停止信號 {signum}")
        self.running = False
    
    def save_checkpoint(self, data):
        """保存檢查點（處理datetime序列化）"""
        try:
            # 轉換datetime對象為ISO字符串
            checkpoint_data = {
                "current_batch": data.get("current_batch", 0),
                "scraped_singers": data.get("scraped_singers", 0),
                "skipped_singers": data.get("skipped_singers", 0),
                "last_update": datetime.now().isoformat(),
                "status": data.get("status", "running"),
                "processed_singers": data.get("processed_singers", [])
            }
            
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
                
            self.logger.debug("💾 檢查點已保存")
            
        except Exception as e:
            self.logger.error(f"保存檢查點失敗: {e}")
    
    def load_checkpoint(self):
        """讀取檢查點"""
        try:
            if os.path.exists(self.checkpoint_file):
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.current_batch = data.get("current_batch", 0)
                self.scraped_singers = data.get("scraped_singers", 0)
                self.skipped_singers = data.get("skipped_singers", 0)
                
                self.logger.info(f"📊 檢查點已讀取: 批次{self.current_batch}, 已處理{self.scraped_singers + self.skipped_singers}位歌手")
                return data.get("processed_singers", [])
            
        except Exception as e:
            self.logger.error(f"讀取檢查點失敗: {e}")
        
        return []
    
    def get_priority_singers(self, max_check=100):
        """獲取優先級排序的歌手（基於用戶要求）"""
        try:
            self.logger.info("🎯 分析歌手優先級...")
            
            # 獲取優先級排序列表
            priority_list = self.comparator.get_priority_sorted_singers(max_singers=max_check)
            
            # 檢查已處理的歌手
            processed_singers = self.load_checkpoint()
            
            # 過濾已處理的歌手
            remaining_singers = [
                item for item in priority_list 
                if item['singer'] not in processed_singers
            ]
            
            self.logger.info(f"📋 優先級分析完成:")
            self.logger.info(f"   候選歌手: {len(priority_list)}")
            self.logger.info(f"   已處理: {len(processed_singers)}")
            self.logger.info(f"   待處理: {len(remaining_singers)}")
            
            if remaining_singers:
                self.logger.info(f"🏆 最高優先級: {remaining_singers[0]['singer']} ({remaining_singers[0]['estimated_priority_score']:.1f}分)")
            
            return remaining_singers
            
        except Exception as e:
            self.logger.error(f"獲取優先級歌手失敗: {e}")
            return []
    
    def scrape_singer_detailed(self, singer_name):
        """詳細爬取單個歌手（檢查是否需要爬取）"""
        try:
            self.logger.info(f"🎵 開始詳細檢查: {singer_name}")
            
            # 使用改進的比較器檢查
            check_result = self.comparator.check_needs_scraping_with_priority(singer_name)
            
            if not check_result['needs_scraping']:
                self.logger.info(f"⏭️ 跳過 {singer_name}: {check_result['reason']}")
                return {
                    'singer': singer_name,
                    'action': 'skipped',
                    'reason': check_result['reason'],
                    'priority_score': check_result['priority_score'],
                    'check_result': check_result
                }
            
            self.logger.info(f"✅ 需要爬取 {singer_name}: 優先級{check_result['priority_score']:.1f}分")
            
            # 這裡可以調用實際的爬蟲邏輯
            # 目前先返回檢查結果，實際實現時可以調用現有的爬蟲
            
            return {
                'singer': singer_name,
                'action': 'scraped',
                'reason': check_result['reason'],
                'priority_score': check_result['priority_score'],
                'check_result': check_result,
                'scraped_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"爬取 {singer_name} 失敗: {e}")
            return {
                'singer': singer_name,
                'action': 'failed',
                'error': str(e)
            }
    
    def git_push_changes(self):
        """自動推送Git變更"""
        try:
            # 檢查是否有變更
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip():
                self.logger.info("📤 發現Git變更，準備推送...")
                
                # 添加所有變更
                subprocess.run(['git', 'add', '.'], check=True)
                
                # 提交變更
                commit_message = f"🎵 自動更新: 批次{self.current_batch} 完成 - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
                subprocess.run(['git', 'commit', '-m', commit_message], check=True)
                
                # 推送到遠程
                subprocess.run(['git', 'push'], check=True)
                
                self.logger.info("✅ Git變更已自動推送")
                return True
            else:
                self.logger.info("ℹ️ 沒有Git變更需要推送")
                return False
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git推送失敗: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Git操作異常: {e}")
            return False
    
    def run_batch_processing(self, batch_size=10):
        """運行批量處理"""
        try:
            self.logger.info("🚀 開始批量處理...")
            
            # 獲取優先級歌手列表
            priority_singers = self.get_priority_singers()
            
            if not priority_singers:
                self.logger.info("✅ 沒有需要處理的歌手")
                return
            
            # 處理歌手
            batch_results = []
            processed_singers = self.load_checkpoint()
            
            for i, singer_item in enumerate(priority_singers):
                if not self.running:
                    self.logger.info("🛑 收到停止信號，正在安全退出...")
                    break
                
                singer_name = singer_item['singer']
                
                self.logger.info(f"🎯 處理 {i+1}/{len(priority_singers)}: {singer_name}")
                
                # 爬取歌手
                result = self.scrape_singer_detailed(singer_name)
                batch_results.append(result)
                
                # 更新統計
                if result['action'] == 'scraped':
                    self.scraped_singers += 1
                elif result['action'] == 'skipped':
                    self.skipped_singers += 1
                
                # 記錄為已處理
                processed_singers.append(singer_name)
                
                # 保存檢查點
                self.save_checkpoint({
                    "current_batch": self.current_batch,
                    "scraped_singers": self.scraped_singers,
                    "skipped_singers": self.skipped_singers,
                    "status": "running",
                    "processed_singers": processed_singers
                })
                
                # 批量完成或達到批量大小
                if (i + 1) % batch_size == 0 or (i + 1) == len(priority_singers):
                    self.current_batch += 1
                    
                    self.logger.info(f"📊 批次 {self.current_batch} 完成:")
                    self.logger.info(f"   已爬取: {self.scraped_singers} 位歌手")
                    self.logger.info(f"   已跳過: {self.skipped_singers} 位歌手")
                    
                    # 保存結果
                    self.save_batch_results(batch_results)
                    
                    # 自動Git推送
                    if self.scraped_singers > 0:  # 只有爬取到新數據才推送
                        self.git_push_changes()
                    
                    # 重置批量結果
                    batch_results = []
                
                # 延遲避免請求過於頻繁
                time.sleep(2)
            
            self.logger.info("🎉 批量處理完成")
            
        except Exception as e:
            self.logger.error(f"批量處理失敗: {e}")
        finally:
            # 最終保存
            self.save_checkpoint({
                "current_batch": self.current_batch,
                "scraped_singers": self.scraped_singers,
                "skipped_singers": self.skipped_singers,
                "status": "completed",
                "processed_singers": processed_singers
            })
    
    def save_batch_results(self, results):
        """保存批量結果"""
        try:
            # 讀取現有結果
            all_results = []
            if os.path.exists(self.results_file):
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    all_results = json.load(f)
            
            # 添加新結果
            all_results.extend(results)
            
            # 保存
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"💾 批量結果已保存: {len(results)} 個新結果")
            
        except Exception as e:
            self.logger.error(f"保存批量結果失敗: {e}")

def main():
    """主函數"""
    scraper = FinalCorrectScraper()
    
    try:
        # 運行批量處理
        scraper.run_batch_processing(batch_size=5)
        
    except KeyboardInterrupt:
        scraper.logger.info("🛑 用戶中斷")
    except Exception as e:
        scraper.logger.error(f"運行失敗: {e}")
    finally:
        scraper.logger.info("🏁 爬蟲已停止")

if __name__ == "__main__":
    main()