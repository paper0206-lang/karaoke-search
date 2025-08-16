#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全停止爬蟲腳本
"""

import os
import signal
import time

def stop_scraper():
    """安全停止爬蟲"""
    print("🛑 開始安全停止爬蟲...")
    
    # 查找程式PID
    result = os.popen("ps aux | grep enhanced_taiwan_scraper | grep -v grep").read()
    
    if result.strip():
        lines = result.strip().split('\n')
        for line in lines:
            if 'enhanced_taiwan_scraper.py' in line:
                parts = line.split()
                if len(parts) >= 2:
                    pid = int(parts[1])
                    print(f"找到程式 PID: {pid}")
                    
                    try:
                        # 發送SIGTERM信號 (禮貌停止)
                        os.kill(pid, signal.SIGTERM)
                        print("✅ 發送停止信號 (SIGTERM)")
                        
                        # 等待5秒
                        time.sleep(5)
                        
                        # 檢查是否還在運行
                        try:
                            os.kill(pid, 0)  # 檢查程式是否還存在
                            print("⚠️ 程式仍在運行，發送強制停止信號")
                            os.kill(pid, signal.SIGKILL)
                            time.sleep(2)
                        except OSError:
                            print("✅ 程式已成功停止")
                            
                    except OSError as e:
                        print(f"停止程式失敗: {e}")
    else:
        print("❌ 沒有找到運行中的爬蟲程式")

if __name__ == "__main__":
    stop_scraper()
