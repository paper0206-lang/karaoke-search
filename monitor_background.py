#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
背景爬蟲監控工具
實時監控背景爬蟲的執行狀態和進度
"""

import json
import os
import time
import glob
from datetime import datetime
import psutil

def check_process_status():
    """檢查背景進程狀態"""
    pid_file = "background_scraper.pid"
    
    if not os.path.exists(pid_file):
        return None, "沒有PID文件"
    
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        if psutil.pid_exists(pid):
            process = psutil.Process(pid)
            return pid, f"運行中 - CPU: {process.cpu_percent():.1f}%, 記憶體: {process.memory_info().rss/1024/1024:.1f}MB"
        else:
            return pid, "進程不存在"
            
    except Exception as e:
        return None, f"檢查失敗: {e}"

def get_latest_checkpoint():
    """獲取最新檢查點資訊"""
    checkpoint_file = "background_checkpoint.json"
    
    if not os.path.exists(checkpoint_file):
        return None
    
    try:
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 讀取檢查點失敗: {e}")
        return None

def get_latest_logs():
    """獲取最新日誌信息"""
    log_files = glob.glob("background_logs/*.log")
    
    if not log_files:
        return "沒有找到日誌文件"
    
    # 找最新的日誌文件
    latest_log = max(log_files, key=os.path.getmtime)
    
    try:
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 取最後10行
        recent_lines = lines[-10:] if len(lines) >= 10 else lines
        return latest_log, recent_lines
        
    except Exception as e:
        return latest_log, [f"讀取日誌失敗: {e}"]

def monitor_progress():
    """監控進度"""
    print("📊 背景爬蟲監控儀表板")
    print("=" * 50)
    
    # 檢查進程狀態
    pid, status = check_process_status()
    print(f"🔄 進程狀態: {status}")
    if pid:
        print(f"📊 進程 PID: {pid}")
    
    # 檢查檢查點
    checkpoint = get_latest_checkpoint()
    if checkpoint:
        print(f"\n📋 檢查點資訊:")
        print(f"   最後更新: {checkpoint.get('last_updated', '未知')}")
        print(f"   已處理歌手: {checkpoint.get('total_processed', 0)} 位")
        
        session_stats = checkpoint.get('session_stats', {})
        if session_stats:
            print(f"   本次會話:")
            print(f"     處理歌手: {session_stats.get('processed_singers', 0)} 位")
            print(f"     成功處理: {session_stats.get('successful_singers', 0)} 位")
            print(f"     新增歌曲: {session_stats.get('new_songs_added', 0)} 首")
            print(f"     失敗數量: {session_stats.get('failed_singers', 0)} 位")
    else:
        print(f"\n❌ 沒有檢查點資訊")
    
    # 檢查批次結果
    batch_files = glob.glob("mass_scraping_results/batch_*_progress.json")
    if batch_files:
        latest_batch = max(batch_files, key=os.path.getmtime)
        try:
            with open(latest_batch, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
            
            print(f"\n📦 最新批次:")
            print(f"   批次編號: {batch_data.get('batch_number', '?')}")
            print(f"   完成時間: {batch_data.get('completed_at', '未知')}")
            
            batch_results = batch_data.get('batch_results', [])
            if batch_results:
                successful = sum(1 for r in batch_results if r.get('status') == 'processed')
                no_data = sum(1 for r in batch_results if r.get('status') == 'no_data')
                failed = sum(1 for r in batch_results if r.get('status') == 'failed')
                
                print(f"   批次結果: {successful}成功, {no_data}無資料, {failed}失敗")
                
        except Exception as e:
            print(f"❌ 讀取批次資訊失敗: {e}")
    
    # 顯示最新日誌
    log_info = get_latest_logs()
    if isinstance(log_info, tuple):
        log_file, recent_lines = log_info
        print(f"\n📄 最新日誌 ({os.path.basename(log_file)}):")
        print("   " + "="*40)
        for line in recent_lines:
            print(f"   {line.rstrip()}")
    else:
        print(f"\n📄 日誌狀態: {log_info}")

def continuous_monitor():
    """連續監控模式"""
    print("🔄 開始連續監控 (按 Ctrl+C 停止)")
    print("每30秒更新一次...")
    
    try:
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')  # 清屏
            print(f"🕐 監控時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            monitor_progress()
            print(f"\n⏳ 下次更新: 30秒後...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print(f"\n👋 監控已停止")

def main():
    """主程序"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        continuous_monitor()
    else:
        monitor_progress()
        print(f"\n💡 提示:")
        print(f"   連續監控: python3 monitor_background.py --continuous")
        print(f"   查看日誌: tail -f background_logs/*.log")
        print(f"   停止爬蟲: ./stop_background_scraper.sh")

if __name__ == "__main__":
    main()