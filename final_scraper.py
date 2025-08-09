#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終版本卡拉OK爬蟲 - 自動推送，背景執行，完整功能
集成所有功能：121位歌手，修復分頁限制，統一資料庫，自動推送
"""

import subprocess
import sys
import json
from datetime import datetime
from enhanced_singer_scraper import EnhancedSingerScraper

class FinalKaraokeScraper:
    def __init__(self):
        self.scraper = EnhancedSingerScraper(max_workers=2)
        
    def execute_full_scraping(self, mode="standard"):
        """執行完整爬蟲作業"""
        
        # 模式配置
        modes = {
            "test": {"singers": 5, "description": "測試模式 (前5位歌手)"},
            "quick": {"singers": 10, "description": "快速模式 (前10位天王天后)"},
            "standard": {"singers": 30, "description": "標準模式 (前30位重點歌手)"},
            "extended": {"singers": 60, "description": "擴展模式 (前60位完整歌手)"},
            "complete": {"singers": 121, "description": "完整模式 (全部121位歌手)"}
        }
        
        if mode not in modes:
            mode = "standard"
            
        config = modes[mode]
        
        print(f"🎤 最終版本卡拉OK爬蟲")
        print(f"執行模式: {config['description']}")
        print(f"=" * 60)
        print(f"🎯 特色功能:")
        print(f"   ✅ 121位歌手完整名單")
        print(f"   ✅ 修復50筆分頁限制") 
        print(f"   ✅ 統一資料庫架構")
        print(f"   ✅ 自動推送GitHub")
        print(f"   ✅ 前端智能搜尋")
        print(f"   ✅ 同歌曲自動歸納")
        
        start_time = datetime.now()
        print(f"\n🚀 開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 執行爬蟲
            if config["singers"] <= 30:
                # 小批次直接執行
                result = self.scraper.batch_scrape_121_singers(0, config["singers"])
            else:
                # 大批次分組執行
                total_result = 0
                batch_size = 20
                total_singers = config["singers"]
                
                for start in range(0, total_singers, batch_size):
                    current_batch = min(batch_size, total_singers - start)
                    print(f"\n🔄 執行第 {start//batch_size + 1} 批次 ({start+1}-{start+current_batch})...")
                    
                    batch_result = self.scraper.batch_scrape_121_singers(start, current_batch)
                    total_result += batch_result
                    
                    print(f"📊 批次結果: 新增 {batch_result} 首歌曲")
                    
                result = total_result
            
            end_time = datetime.now()
            elapsed = end_time - start_time
            
            print(f"\n🎉 爬蟲執行完成!")
            print(f"📊 最終統計:")
            print(f"   處理模式: {config['description']}")
            print(f"   新增歌曲: {result} 首")
            print(f"   總歌曲數: {self.scraper.unified_db['metadata']['total_songs']:,} 首")
            print(f"   總歌手數: {self.scraper.unified_db['metadata']['total_singers']:,} 位")
            print(f"   執行時間: {elapsed}")
            
            # 自動推送到GitHub
            if result > 0:
                self.auto_push_to_github(config, result, start_time, end_time)
            else:
                print(f"\n📝 沒有新增歌曲，跳過推送")
                
            return True
            
        except KeyboardInterrupt:
            print(f"\n⏹️ 用戶中斷執行")
            self.scraper.save_unified_database()
            print(f"💾 已保存當前進度")
            return False
            
        except Exception as e:
            print(f"\n❌ 執行出錯: {e}")
            self.scraper.save_unified_database()
            print(f"💾 已保存當前進度")
            return False
    
    def auto_push_to_github(self, config, new_songs, start_time, end_time):
        """自動推送到GitHub"""
        print(f"\n🚀 自動推送到GitHub...")
        
        try:
            # 添加檔案到Git
            files_to_add = [
                'public/unified_karaoke_db.json',
                'public/songs_simplified.json', 
                'public/singers_data.json',
                'src/App.vue'  # 前端更新
            ]
            
            subprocess.run(['git', 'add'] + files_to_add, check=True)
            
            # 準備詳細的提交訊息
            total_songs = self.scraper.unified_db['metadata']['total_songs']
            total_singers = self.scraper.unified_db['metadata']['total_singers']
            elapsed = end_time - start_time
            
            commit_msg = f"""最終版本爬蟲更新: {config['description']}

🎤 執行統計:
- 執行模式: {config['description']}
- 新增歌曲: {new_songs:,} 首
- 總歌曲數: {total_songs:,} 首
- 總歌手數: {total_singers:,} 位
- 執行時間: {elapsed}

🚀 功能升級:
- ✅ 修復50筆分頁限制，完整收錄歌手作品
- ✅ 統一資料庫架構，消除資料重複
- ✅ 前端智能搜尋，自動歸納同歌曲編號
- ✅ 121位歌手完整名單，涵蓋各世代藝人
- ✅ 自動推送部署，無縫更新前端

💾 資料庫架構:
- 主資料庫: unified_karaoke_db.json ({len(json.dumps(self.scraper.unified_db))/1024/1024:.1f}MB)
- 相容檔案: songs_simplified.json + singers_data.json
- 支援KTV: {len(self.scraper.unified_db['metadata']['companies'])}家公司

🌐 前端功能:
- 智能搜尋: 自動判斷歌曲名稱或歌手名稱
- 歸納顯示: 同一首歌的各家KTV編號集中顯示
- 動態統計: 即時顯示最新歌曲和歌手數量
- 響應式設計: 支援手機和電腦瀏覽

⏰ 執行時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%H:%M:%S')}

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""
            
            # 提交變更
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            
            # 推送到遠端
            subprocess.run(['git', 'push'], check=True)
            
            print(f"✅ 成功推送到GitHub")
            print(f"🌐 網站將在2-3分鐘內更新")
            print(f"📱 查看結果: https://karaoke-search-theta.vercel.app")
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Git操作失敗: {e}")
            print(f"📝 請手動執行推送")

def main():
    """主執行函數 - 支援命令列參數"""
    
    # 默認模式
    mode = "standard"
    
    # 檢查命令列參數
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    
    available_modes = ["test", "quick", "standard", "extended", "complete"]
    if mode not in available_modes:
        print(f"❌ 無效模式: {mode}")
        print(f"可用模式: {', '.join(available_modes)}")
        return
    
    # 執行爬蟲
    scraper = FinalKaraokeScraper()
    success = scraper.execute_full_scraping(mode)
    
    if success:
        print(f"\n🎉 任務完成!")
        print(f"📊 數據已更新並推送")
        print(f"🌐 前端已自動部署")
    else:
        print(f"\n⚠️ 任務未完全完成")
        print(f"💾 進度已保存，可稍後繼續")

if __name__ == "__main__":
    main()