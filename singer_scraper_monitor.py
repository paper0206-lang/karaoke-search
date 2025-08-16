#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌手關鍵字爬蟲監控工具
監控歌手搜尋爬蟲的進度和狀態
"""

import json
import os
import time
import glob
from datetime import datetime

class SingerScraperMonitor:
    def __init__(self):
        self.progress_file = "singer_search_progress.json"
        self.database_pattern = "singer_search_database_*.json"
        
    def load_progress(self):
        """載入進度資訊"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"completed_singers": [], "failed_singers": []}
        return {"completed_singers": [], "failed_singers": []}
    
    def find_latest_database(self):
        """找到最新的資料庫檔案"""
        db_files = glob.glob(self.database_pattern)
        if not db_files:
            return None
        return max(db_files, key=os.path.getmtime)
    
    def load_database(self, db_file):
        """載入資料庫"""
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def get_singer_database_stats(self):
        """獲取歌手資料庫統計"""
        singer_file = "FINAL_singer_database_20250811_200210.json"
        if os.path.exists(singer_file):
            try:
                with open(singer_file, 'r', encoding='utf-8') as f:
                    database = json.load(f)
                return {
                    'total_keywords': len(database.get('search_keywords', [])),
                    'total_singers': database.get('statistics', {}).get('total_singers', 0)
                }
            except:
                pass
        return {'total_keywords': 0, 'total_singers': 0}
    
    def print_status(self):
        """打印當前狀態"""
        print("🎵 歌手關鍵字爬蟲狀態監控")
        print("=" * 50)
        print(f"📅 檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 基礎統計
        singer_stats = self.get_singer_database_stats()
        print(f"\n📚 歌手資料庫:")
        print(f"   🎤 總歌手數: {singer_stats['total_singers']}")
        print(f"   🔍 搜尋關鍵字: {singer_stats['total_keywords']}")
        
        # 進度統計
        progress = self.load_progress()
        completed = progress.get('completed_singers', [])
        failed = progress.get('failed_singers', [])
        
        total_to_search = singer_stats['total_keywords']
        searched_count = len(completed) + len(failed)
        remaining = total_to_search - searched_count
        
        if total_to_search > 0:
            progress_percent = (searched_count / total_to_search) * 100
        else:
            progress_percent = 0
            
        print(f"\n📊 搜尋進度:")
        print(f"   ✅ 已完成: {len(completed)}")
        print(f"   ❌ 已失敗: {len(failed)}")
        print(f"   ⏳ 待處理: {remaining}")
        print(f"   📈 完成度: {progress_percent:.1f}%")
        
        # 資料庫統計
        latest_db = self.find_latest_database()
        if latest_db:
            database = self.load_database(latest_db)
            if database:
                metadata = database.get('metadata', {})
                stats = database.get('search_statistics', {})
                
                print(f"\n💾 最新資料庫: {latest_db}")
                print(f"   📅 建立時間: {metadata.get('created_time', '未知')}")
                print(f"   🎶 總歌曲數: {metadata.get('total_songs_found', 0)}")
                print(f"   👥 有歌曲歌手: {len(stats.get('singers_with_songs', []))}")
                print(f"   ⚪ 無歌曲歌手: {len(stats.get('singers_without_songs', []))}")
                
                # 檔案大小
                file_size = os.path.getsize(latest_db) / (1024 * 1024)  # MB
                print(f"   📁 檔案大小: {file_size:.1f} MB")
                
                # 最後更新時間
                last_updated = metadata.get('last_updated')
                if last_updated:
                    print(f"   🔄 最後更新: {last_updated}")
                
        else:
            print(f"\n💾 尚未找到資料庫檔案")
            
        # 最近失敗的歌手
        if failed:
            print(f"\n❌ 最近失敗的歌手 (最多顯示10位):")
            for singer in failed[-10:]:
                print(f"   • {singer}")
                
        # 估算剩餘時間
        if remaining > 0 and len(completed) > 0:
            # 簡單估算：假設每個歌手平均處理時間
            if latest_db:
                db_stat = os.path.stat(latest_db)
                creation_time = db_stat.st_ctime
                current_time = time.time()
                elapsed_hours = (current_time - creation_time) / 3600
                
                if elapsed_hours > 0 and len(completed) > 0:
                    avg_time_per_singer = elapsed_hours / len(completed)
                    estimated_remaining_hours = avg_time_per_singer * remaining
                    
                    print(f"\n⏱️ 時間估算:")
                    print(f"   ⌛ 已運行: {elapsed_hours:.1f} 小時")
                    print(f"   🎯 預估剩餘: {estimated_remaining_hours:.1f} 小時")
                    
        print("\n" + "=" * 50)
    
    def monitor_loop(self, interval=30):
        """持續監控模式"""
        print("🔄 開始持續監控模式 (每30秒更新)")
        print("按 Ctrl+C 退出")
        
        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                self.print_status()
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n👋 監控結束")

def main():
    import sys
    
    monitor = SingerScraperMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--monitor':
        monitor.monitor_loop()
    else:
        monitor.print_status()

if __name__ == "__main__":
    main()