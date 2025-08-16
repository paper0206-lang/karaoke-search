#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
優化版背景爬蟲監控工具
監控優化版背景爬蟲的執行狀態和性能指標
"""

import json
import os
import time
import glob
import subprocess
from datetime import datetime
import psutil

def check_process_status():
    """檢查優化版背景進程狀態"""
    pid_file = "optimized_scraper.pid"
    
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
    checkpoint_file = "optimized_background_checkpoint.json"
    
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
    log_files = glob.glob("optimized_logs/*.log")
    
    if not log_files:
        return "沒有找到日誌文件"
    
    # 找最新的日誌文件
    latest_log = max(log_files, key=os.path.getmtime)
    
    try:
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 取最後15行
        recent_lines = lines[-15:] if len(lines) >= 15 else lines
        return latest_log, recent_lines
        
    except Exception as e:
        return latest_log, [f"讀取日誌失敗: {e}"]

def calculate_performance_metrics(checkpoint):
    """計算性能指標"""
    session_stats = checkpoint.get('session_stats', {})
    start_time_str = session_stats.get('start_time', '')
    
    if not start_time_str:
        return None
    
    try:
        start_time = datetime.fromisoformat(start_time_str)
        current_time = datetime.now()
        elapsed_time = current_time - start_time
        
        processed = session_stats.get('processed_singers', 0)
        successful = session_stats.get('successful_singers', 0)
        new_songs = session_stats.get('new_songs_added', 0)
        
        hours_elapsed = elapsed_time.total_seconds() / 3600
        
        if hours_elapsed > 0:
            singers_per_hour = processed / hours_elapsed
            songs_per_hour = new_songs / hours_elapsed
            success_rate = (successful / processed * 100) if processed > 0 else 0
            
            return {
                'hours_elapsed': hours_elapsed,
                'singers_per_hour': singers_per_hour,
                'songs_per_hour': songs_per_hour,
                'success_rate': success_rate,
                'avg_songs_per_successful': new_songs / successful if successful > 0 else 0
            }
    except Exception as e:
        print(f"計算性能指標失敗: {e}")
        return None

def check_git_status():
    """檢查Git狀態"""
    try:
        # 檢查是否有未推送的提交
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        uncommitted = result.stdout.strip()
        
        # 檢查最近的提交
        result = subprocess.run(['git', 'log', '--oneline', '-3'], 
                              capture_output=True, text=True)
        
        recent_commits = result.stdout.strip().split('\n')
        
        return {
            'uncommitted_changes': uncommitted,
            'recent_commits': recent_commits
        }
        
    except Exception as e:
        return {'error': str(e)}

def monitor_progress():
    """監控進度"""
    print("🚀 優化版背景爬蟲監控儀表板")
    print("=" * 60)
    
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
        print(f"   基準設定: {checkpoint.get('benchmark_threshold', 0.95)*100:.0f}%")
        
        # 顯示優化配置
        opt_config = checkpoint.get('optimization_config', {})
        if opt_config:
            print(f"   優化配置:")
            print(f"     並行線程: {opt_config.get('parallel_threads', 'N/A')}")
            print(f"     延遲範圍: {opt_config.get('delay_range', 'N/A')}")
            print(f"     批次大小: {opt_config.get('batch_size', 'N/A')}")
            print(f"     Git推送間隔: {opt_config.get('git_push_interval', 'N/A')}")
        
        session_stats = checkpoint.get('session_stats', {})
        if session_stats:
            print(f"   本次會話:")
            print(f"     處理歌手: {session_stats.get('processed_singers', 0)} 位")
            print(f"     成功處理: {session_stats.get('successful_singers', 0)} 位")
            print(f"     新增歌曲: {session_stats.get('new_songs_added', 0)} 首")
            print(f"     Git推送: {session_stats.get('git_pushes', 0)} 次")
            print(f"     失敗數量: {session_stats.get('failed_singers', 0)} 位")
        
        # 計算性能指標
        performance = calculate_performance_metrics(checkpoint)
        if performance:
            print(f"\n⚡ 性能指標:")
            print(f"   運行時間: {performance['hours_elapsed']:.1f} 小時")
            print(f"   處理速度: {performance['singers_per_hour']:.1f} 位歌手/小時")
            print(f"   歌曲產出: {performance['songs_per_hour']:.1f} 首歌/小時")
            print(f"   成功率: {performance['success_rate']:.1f}%")
            print(f"   平均每位成功歌手: {performance['avg_songs_per_successful']:.1f} 首")
            
            # 預估完成時間
            total_need_processing = 3425  # 從之前分析得出
            processed = session_stats.get('processed_singers', 0)
            remaining = total_need_processing - processed
            
            if performance['singers_per_hour'] > 0:
                hours_remaining = remaining / performance['singers_per_hour']
                days_remaining = hours_remaining / 24
                print(f"   預估剩餘: {hours_remaining:.1f} 小時 ({days_remaining:.1f} 天)")
    else:
        print(f"\n❌ 沒有檢查點資訊")
    
    # 檢查Git狀態
    git_status = check_git_status()
    print(f"\n📤 Git狀態:")
    if 'error' in git_status:
        print(f"   ❌ 檢查失敗: {git_status['error']}")
    else:
        if git_status['uncommitted_changes']:
            print(f"   ⚠️ 有未提交的更改:")
            for line in git_status['uncommitted_changes'].split('\n')[:3]:
                print(f"     {line}")
        else:
            print(f"   ✅ 沒有未提交的更改")
        
        print(f"   📝 最近提交:")
        for commit in git_status['recent_commits'][:3]:
            if commit.strip():
                print(f"     {commit}")
    
    # 檢查批次結果
    batch_files = glob.glob("optimized_scraping_results/batch_*_progress.json")
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
                already_complete = sum(1 for r in batch_results if r.get('status') == 'already_complete')
                failed = sum(1 for r in batch_results if r.get('status') == 'failed')
                
                print(f"   批次結果: {successful}成功, {already_complete}已達標, {no_data}無資料, {failed}失敗")
                
        except Exception as e:
            print(f"❌ 讀取批次資訊失敗: {e}")
    
    # 顯示最新日誌
    log_info = get_latest_logs()
    if isinstance(log_info, tuple):
        log_file, recent_lines = log_info
        print(f"\n📄 最新日誌 ({os.path.basename(log_file)}):")
        print("   " + "="*50)
        for line in recent_lines:
            print(f"   {line.rstrip()}")
    else:
        print(f"\n📄 日誌狀態: {log_info}")

def continuous_monitor():
    """連續監控模式"""
    print("🔄 開始連續監控優化版爬蟲 (按 Ctrl+C 停止)")
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
        print(f"   連續監控: python3 monitor_optimized.py --continuous")
        print(f"   查看日誌: tail -f optimized_logs/*.log")
        print(f"   停止爬蟲: ./stop_optimized_scraper.sh")
        print(f"   檢查Git: git log --oneline -5")

if __name__ == "__main__":
    main()