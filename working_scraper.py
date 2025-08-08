#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作版爬蟲 - 基於現有統一資料庫的增量更新策略
由於原始API不再可用，採用多來源策略維護資料庫
"""

import json
import os
import time
import random
from datetime import datetime
import subprocess

class WorkingScraper:
    def __init__(self):
        self.unified_db_path = 'public/unified_karaoke_db.json'
        self.load_existing_database()
        
    def load_existing_database(self):
        """載入現有的統一資料庫"""
        if os.path.exists(self.unified_db_path):
            with open(self.unified_db_path, 'r', encoding='utf-8') as f:
                self.unified_db = json.load(f)
            print(f"📚 載入現有資料庫: {self.unified_db['metadata']['total_songs']:,} 首歌曲")
        else:
            print("❌ 找不到統一資料庫檔案")
            return False
        return True
    
    def analyze_database_growth_potential(self):
        """分析資料庫成長潛力"""
        print("📊 資料庫分析:")
        print(f"   總歌曲數: {self.unified_db['metadata']['total_songs']:,}")
        print(f"   總歌手數: {self.unified_db['metadata']['total_singers']:,}") 
        print(f"   KTV公司: {len(self.unified_db['metadata']['companies'])} 家")
        
        # 分析歌手分布
        singer_song_count = {}
        for song_id, song_data in self.unified_db['songs'].items():
            singer = song_data['歌手']
            if singer not in singer_song_count:
                singer_song_count[singer] = 0
            singer_song_count[singer] += len(song_data['編號資訊'])
        
        # 找出歌曲數量少於5首的歌手 (可能需要補充)
        low_count_singers = {k: v for k, v in singer_song_count.items() if v < 5}
        print(f"   需要補充的歌手: {len(low_count_singers)} 位")
        
        # 顯示前10大歌手
        top_singers = sorted(singer_song_count.items(), key=lambda x: x[1], reverse=True)[:10]
        print(f"   前10大歌手:")
        for singer, count in top_singers:
            print(f"      {singer}: {count} 首")
            
        return low_count_singers
    
    def simulate_scraper_update(self):
        """模擬爬蟲更新過程 - 實際使用時可替換為真實爬蟲"""
        print("\n🔄 模擬資料庫更新...")
        
        # 模擬新增幾首歌曲 (實際場景中這裡會是真實的網路爬蟲)
        new_songs = [
            {
                '歌名': '測試新歌1',
                '歌手': '測試歌手',
                '編號': 'TEST001',
                '公司': '測試KTV',
                '語言': '華語'
            },
            {
                '歌名': '測試新歌2', 
                '歌手': '測試歌手',
                '編號': 'TEST002',
                '公司': '測試KTV2',
                '語言': '華語'
            }
        ]
        
        added_count = 0
        for song in new_songs:
            if self.add_song_to_database(song):
                added_count += 1
                
        print(f"✅ 模擬新增: {added_count} 首歌曲")
        return added_count > 0
    
    def add_song_to_database(self, song_data):
        """添加歌曲到統一資料庫"""
        song_key = f"{song_data['歌名']}_{song_data['歌手']}"
        
        # 檢查是否已存在
        if song_key in self.unified_db['songs']:
            # 檢查是否有新的編號資訊
            existing_codes = {(code['公司'], code['編號']) for code in self.unified_db['songs'][song_key]['編號資訊']}
            new_code = (song_data['公司'], song_data['編號'])
            
            if new_code not in existing_codes:
                # 添加新編號
                self.unified_db['songs'][song_key]['編號資訊'].append({
                    '公司': song_data['公司'],
                    '編號': song_data['編號']
                })
                return True
        else:
            # 新增歌曲
            self.unified_db['songs'][song_key] = {
                '歌名': song_data['歌名'],
                '歌手': song_data['歌手'], 
                '語言': song_data.get('語言', ''),
                '編號資訊': [{
                    '公司': song_data['公司'],
                    '編號': song_data['編號']
                }]
            }
            
            # 更新統計
            self.unified_db['metadata']['total_songs'] += 1
            if song_data['歌手'] not in self.unified_db['metadata']['singers']:
                self.unified_db['metadata']['singers'].append(song_data['歌手'])
                self.unified_db['metadata']['total_singers'] += 1
                
            if song_data['公司'] not in self.unified_db['metadata']['companies']:
                self.unified_db['metadata']['companies'].append(song_data['公司'])
                
            return True
            
        return False
    
    def save_database(self):
        """保存統一資料庫"""
        self.unified_db['metadata']['最後更新時間'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.unified_db_path, 'w', encoding='utf-8') as f:
            json.dump(self.unified_db, f, ensure_ascii=False, indent=2)
        
        # 生成前端相容檔案
        self.generate_frontend_files()
        
        print(f"💾 資料庫已保存: {self.unified_db['metadata']['total_songs']:,} 首歌曲")
        return True
    
    def generate_frontend_files(self):
        """生成前端相容檔案"""
        # 生成 songs_simplified.json
        songs_simplified = []
        singers_data = {}
        
        for song_key, song_data in self.unified_db['songs'].items():
            singer = song_data['歌手']
            
            # 為每個編號創建記錄 (前端相容格式)
            for code_info in song_data['編號資訊']:
                songs_simplified.append({
                    '歌名': song_data['歌名'],
                    '歌手': singer,
                    '編號': code_info['編號'],
                    '公司': code_info['公司'],
                    '語言': song_data.get('語言', '')
                })
            
            # 歌手資料
            if singer not in singers_data:
                singers_data[singer] = {
                    '歌手名稱': singer,
                    '歌曲清單': []
                }
            
            # 避免重複添加相同歌曲
            existing_songs = {song['歌名'] for song in singers_data[singer]['歌曲清單']}
            if song_data['歌名'] not in existing_songs:
                singers_data[singer]['歌曲清單'].append({
                    '歌名': song_data['歌名'],
                    '歌手': singer,
                    '語言': song_data.get('語言', ''),
                    '編號資訊': song_data['編號資訊'].copy()
                })
        
        # 保存檔案
        with open('public/songs_simplified.json', 'w', encoding='utf-8') as f:
            json.dump(songs_simplified, f, ensure_ascii=False, indent=2)
            
        with open('public/singers_data.json', 'w', encoding='utf-8') as f:
            json.dump(singers_data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 前端檔案已更新:")
        print(f"   songs_simplified.json: {len(songs_simplified):,} 筆記錄")
        print(f"   singers_data.json: {len(singers_data)} 位歌手")
    
    def auto_push_updates(self):
        """自動推送更新到GitHub"""
        try:
            # 添加檔案
            files_to_add = [
                'public/unified_karaoke_db.json',
                'public/songs_simplified.json',
                'public/singers_data.json'
            ]
            
            subprocess.run(['git', 'add'] + files_to_add, check=True)
            
            # 提交
            commit_msg = f"""資料庫維護更新

📊 統計資訊:
- 總歌曲數: {self.unified_db['metadata']['total_songs']:,} 首
- 總歌手數: {self.unified_db['metadata']['total_singers']:,} 位  
- KTV公司: {len(self.unified_db['metadata']['companies'])} 家

🔄 更新內容:
- 維護現有資料庫完整性
- 更新前端相容檔案
- 確保搜尋功能正常運作

💾 檔案更新:
- unified_karaoke_db.json (主資料庫)
- songs_simplified.json (歌曲搜尋)
- singers_data.json (歌手搜尋)

⏰ 更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""
            
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            subprocess.run(['git', 'push'], check=True)
            
            print("🚀 成功推送到GitHub")
            print("🌐 網站將在2-3分鐘內更新")
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Git推送失敗: {e}")

def main():
    print("🎵 工作版爬蟲系統")
    print("=" * 50)
    print("⚠️  注意: 由於原始API不再可用，目前採用資料庫維護模式")
    print("")
    
    scraper = WorkingScraper()
    
    # 分析現有資料庫
    low_count_singers = scraper.analyze_database_growth_potential()
    
    print(f"\n🔧 可用操作:")
    print(f"1. 維護現有資料庫 (重新生成前端檔案)")
    print(f"2. 模擬新增資料 (測試功能)")
    print(f"3. 推送到GitHub (更新線上版本)")
    print(f"4. 完整維護流程")
    
    try:
        choice = input("\n請選擇操作 (1-4): ").strip()
        
        if choice == '1':
            scraper.generate_frontend_files()
            scraper.save_database()
            
        elif choice == '2':
            if scraper.simulate_scraper_update():
                scraper.save_database()
            
        elif choice == '3':
            scraper.auto_push_updates()
            
        elif choice == '4':
            print("\n🔄 執行完整維護流程...")
            scraper.generate_frontend_files()
            scraper.save_database()
            scraper.auto_push_updates()
            print("\n✅ 維護完成！")
            
        else:
            print("❌ 無效選擇")
            
    except KeyboardInterrupt:
        print("\n⏹️ 操作已取消")
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")

if __name__ == "__main__":
    main()