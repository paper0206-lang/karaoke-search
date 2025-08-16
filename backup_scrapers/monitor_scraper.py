#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
監控漸進式10線程爬蟲狀況
"""

import os
import time
import subprocess
import glob
from datetime import datetime

def monitor_scraper():
    print("🔍 漸進式10線程爬蟲監控")
    print("=" * 50)
    
    while True:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n⏰ {current_time}")
        
        # 檢查進程狀態
        try:
            result = subprocess.run(
                ["pgrep", "-f", "progressive_10thread_scraper"], 
                capture_output=True, text=True
            )
            if result.returncode == 0:
                pid = result.stdout.strip()
                print(f"✅ 爬蟲運行中 (PID: {pid})")
            else:
                print("❌ 爬蟲未運行")
                break
        except Exception as e:
            print(f"❌ 檢查進程失敗: {e}")
        
        # 檢查批次文件
        batch_files = glob.glob("batches/*.json")
        print(f"📁 批次文件: {len(batch_files)} 個")
        
        if batch_files:
            latest_batch = max(batch_files, key=os.path.getmtime)
            file_size = os.path.getsize(latest_batch)
            mod_time = datetime.fromtimestamp(os.path.getmtime(latest_batch))
            print(f"   最新: {os.path.basename(latest_batch)} ({file_size:,} bytes)")
            print(f"   時間: {mod_time.strftime('%H:%M:%S')}")
        
        # 檢查總文件
        json_files = [f for f in glob.glob("*.json") if "taiwan" in f or "音圓" in f]
        if json_files:
            total_file = max(json_files, key=os.path.getmtime)
            file_size = os.path.getsize(total_file)
            print(f"📊 總文件: {os.path.basename(total_file)} ({file_size:,} bytes)")
        
        print("-" * 30)
        time.sleep(10)  # 每10秒檢查一次

if __name__ == "__main__":
    try:
        monitor_scraper()
    except KeyboardInterrupt:
        print("\n⚠️ 監控停止")