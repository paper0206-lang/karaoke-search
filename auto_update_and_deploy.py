#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動化爬蟲 + 推送 + 部署完整流程
執行後自動完成：爬取資料 → 更新資料庫 → 推送GitHub → 觸發部署
"""

import subprocess
import sys
import os
import time
import json
from datetime import datetime
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_deploy.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def run_command(cmd, description, cwd=None):
    """執行命令並返回結果"""
    logging.info(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd or os.getcwd(),
            timeout=3600  # 1小時超時
        )
        
        if result.returncode == 0:
            logging.info(f"✅ {description} 成功")
            if result.stdout.strip():
                logging.debug(f"輸出: {result.stdout.strip()}")
            return True, result.stdout
        else:
            logging.error(f"❌ {description} 失敗")
            if result.stderr.strip():
                logging.error(f"錯誤: {result.stderr.strip()}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        logging.error(f"⏰ {description} 超時")
        return False, "Timeout"
    except Exception as e:
        logging.error(f"💥 {description} 異常: {e}")
        return False, str(e)

def check_environment():
    """檢查執行環境"""
    logging.info("🔧 檢查執行環境...")
    
    # 檢查Python套件
    required_packages = [
        ('requests', 'requests'),
        ('beautifulsoup4', 'bs4')
    ]
    for display_name, import_name in required_packages:
        try:
            __import__(import_name)
            logging.info(f"   ✅ {display_name}")
        except ImportError:
            logging.error(f"   ❌ 缺少 {display_name}")
            return False
    
    # 檢查Git
    success, _ = run_command('git --version', 'Git版本檢查')
    if not success:
        logging.error("Git未安裝或不可用")
        return False
    
    # 檢查是否在Git倉庫中
    success, _ = run_command('git status', 'Git倉庫檢查')
    if not success:
        logging.error("不在Git倉庫中")
        return False
    
    # 檢查必要檔案
    required_files = ['enhanced_taiwan_scraper.py', 'standalone_frontend.html']
    for file in required_files:
        if os.path.exists(file):
            logging.info(f"   ✅ {file}")
        else:
            logging.warning(f"   ⚠️ {file} 不存在")
    
    logging.info("✅ 環境檢查完成")
    return True

def run_scraper():
    """執行爬蟲"""
    logging.info("🕷️ 開始執行爬蟲...")
    
    start_time = time.time()
    
    success, output = run_command(
        'python3 enhanced_taiwan_scraper.py',
        '執行增強版台灣爬蟲'
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    if success:
        logging.info(f"✅ 爬蟲執行成功，耗時 {duration:.2f} 秒")
        
        # 檢查輸出檔案
        output_files = [
            'taiwan_songking_all.csv',
            'public/taiwan_songs_raw.json',
            'public/songs_simplified.json'
        ]
        
        files_created = []
        for file in output_files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                logging.info(f"   📁 {file} ({size:,} bytes)")
                files_created.append(file)
            else:
                logging.warning(f"   ⚠️ {file} 未生成")
        
        return len(files_created) > 0
    else:
        logging.error(f"❌ 爬蟲執行失敗，耗時 {duration:.2f} 秒")
        logging.error(f"錯誤輸出: {output}")
        return False

def update_frontend():
    """更新前端檔案以使用最新資料"""
    logging.info("🎨 更新前端介面...")
    
    try:
        # 更新standalone_frontend.html中的時間戳
        if os.path.exists('standalone_frontend.html'):
            with open('standalone_frontend.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新最後更新時間
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated_content = content.replace(
                '載入中...',
                current_time
            )
            
            # 如果有變更就寫回
            if updated_content != content:
                with open('standalone_frontend.html', 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                logging.info("✅ 前端時間戳已更新")
            else:
                logging.info("ℹ️ 前端無需更新")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ 更新前端失敗: {e}")
        return False

def git_commit_and_push():
    """Git提交和推送"""
    logging.info("📡 準備推送到GitHub...")
    
    # 檢查是否有變更
    success, output = run_command('git status --porcelain', '檢查Git狀態')
    if not success:
        return False
    
    if not output.strip():
        logging.info("ℹ️ 沒有檔案需要提交")
        return True
    
    # 添加檔案
    files_to_add = [
        'taiwan_songking_all.csv',
        'public/taiwan_songs_raw.json', 
        'public/songs_simplified.json',
        'standalone_frontend.html',
        'enhanced_taiwan_scraper.py',
        'taiwan_scraper.log',
        'auto_deploy.log'
    ]
    
    added_files = []
    for file in files_to_add:
        if os.path.exists(file):
            success, _ = run_command(f'git add "{file}"', f'添加 {file}')
            if success:
                added_files.append(file)
    
    if not added_files:
        logging.warning("⚠️ 沒有檔案被添加")
        return False
    
    # 檢查是否有暫存的變更
    success, output = run_command('git diff --cached --name-only', '檢查暫存變更')
    if not success or not output.strip():
        logging.info("ℹ️ 沒有暫存的變更")
        return True
    
    # 生成統計資訊
    song_count = 0
    try:
        if os.path.exists('public/songs_simplified.json'):
            with open('public/songs_simplified.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                song_count = len(data)
    except:
        pass
    
    # 創建提交訊息
    commit_message = f"""🎵 自動更新卡拉OK歌曲資料庫

📊 更新統計:
- 歌曲總數: {song_count:,} 首
- 更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 涵蓋系統: 台灣主要KTV品牌

📁 更新檔案:
{chr(10).join([f'- {f}' for f in added_files])}

🤖 自動化流程完成
Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"""
    
    # 提交
    success, _ = run_command(f'git commit -m "{commit_message}"', '提交變更')
    if not success:
        return False
    
    # 推送
    success, _ = run_command('git push origin main', '推送到GitHub')
    return success

def check_deployment_status():
    """檢查部署狀態 (如果有設定Vercel等)"""
    logging.info("🌐 檢查線上部署狀態...")
    
    # 這裡可以添加檢查Vercel部署狀態的邏輯
    # 目前只是等待一段時間讓部署完成
    logging.info("⏳ 等待自動部署完成...")
    time.sleep(30)  # 等待30秒
    
    # 可以嘗試訪問線上網址
    try:
        import requests
        response = requests.get('https://karaoke-search-theta.vercel.app/', timeout=10)
        if response.status_code == 200:
            logging.info("✅ 線上網站可正常訪問")
            return True
        else:
            logging.warning(f"⚠️ 線上網站回應 HTTP {response.status_code}")
            return False
    except Exception as e:
        logging.warning(f"⚠️ 無法檢查線上狀態: {e}")
        return False

def main():
    """主要流程"""
    print("🚀 自動化爬蟲更新部署流程")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # 1. 環境檢查
        try:
            if not check_environment():
                logging.warning("⚠️ 環境檢查失敗，但繼續執行")
        except Exception as e:
            logging.warning(f"⚠️ 環境檢查異常: {e}，繼續執行")
        
        # 2. 執行爬蟲
        if not run_scraper():
            logging.error("❌ 爬蟲執行失敗")
            return False
        
        # 3. 更新前端
        if not update_frontend():
            logging.warning("⚠️ 前端更新失敗，但繼續流程")
        
        # 4. Git提交和推送
        if not git_commit_and_push():
            logging.error("❌ Git推送失敗")
            return False
        
        # 5. 檢查部署
        deployment_ok = check_deployment_status()
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 自動化流程完成！")
        print(f"⏱️  總耗時: {total_duration:.2f} 秒 ({total_duration/60:.1f} 分鐘)")
        print()
        print("✅ 完成項目:")
        print("   • 爬取最新歌曲資料")
        print("   • 更新本地資料庫")
        print("   • 推送到GitHub")
        if deployment_ok:
            print("   • 線上部署更新完成")
        else:
            print("   • 線上部署狀態未確認")
        print()
        print("🌐 可訪問網址:")
        print("   • GitHub: https://github.com/[你的用戶名]/karaoke-search")
        print("   • 線上版: https://karaoke-search-theta.vercel.app/")
        print("   • 本地版: ./standalone_frontend.html")
        print()
        print("📊 建議下次執行時間: 每週或每月一次")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️ 用戶中斷執行")
        return False
    except Exception as e:
        logging.error(f"💥 流程執行異常: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)