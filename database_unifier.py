#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料庫統一系統 - 合併歌曲和歌手資料庫為統一架構
"""

import json
import time
from datetime import datetime
from collections import defaultdict

class DatabaseUnifier:
    def __init__(self):
        self.songs_db = []
        self.singers_db = {}
        self.unified_db = {
            "metadata": {
                "version": "2.0",
                "created": datetime.now().isoformat(),
                "total_songs": 0,
                "total_singers": 0,
                "companies": set()
            },
            "songs": {},
            "indexes": {
                "by_singer": defaultdict(list),
                "by_company": defaultdict(list),
                "by_song_name": defaultdict(list),
                "by_language": defaultdict(list)
            },
            "singer_metadata": {}
        }
        
    def load_existing_databases(self):
        """載入現有的兩個資料庫"""
        print("📚 載入現有資料庫...")
        
        # 載入歌曲搜尋資料庫
        try:
            with open('public/songs_simplified.json', 'r', encoding='utf-8') as f:
                self.songs_db = json.load(f)
            print(f"  ✅ 歌曲資料庫: {len(self.songs_db):,} 首歌曲")
        except Exception as e:
            print(f"  ❌ 載入歌曲資料庫失敗: {e}")
            return False
            
        # 載入歌手搜尋資料庫
        try:
            with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                self.singers_db = json.load(f)
            singer_song_count = sum(len(singer['歌曲清單']) for singer in self.singers_db.values())
            print(f"  ✅ 歌手資料庫: {len(self.singers_db)} 位歌手, {singer_song_count:,} 首歌曲")
        except Exception as e:
            print(f"  ❌ 載入歌手資料庫失敗: {e}")
            self.singers_db = {}
            
        return True
    
    def generate_song_id(self, song_name, singer_name):
        """產生唯一的歌曲ID"""
        # 清理字串，移除特殊字符
        clean_song = ''.join(c for c in song_name if c.isalnum() or c in '中文')[:20]
        clean_singer = ''.join(c for c in singer_name if c.isalnum() or c in '中文')[:10]
        
        base_id = f"{clean_singer}_{clean_song}".replace(' ', '_')
        
        # 確保ID唯一
        counter = 1
        song_id = base_id
        while song_id in self.unified_db["songs"]:
            song_id = f"{base_id}_{counter}"
            counter += 1
            
        return song_id
    
    def merge_song_codes(self, song_entries):
        """合併相同歌曲的不同編號"""
        merged_codes = []
        seen_codes = set()
        
        for entry in song_entries:
            company = entry.get('公司', entry.get('company', ''))
            code = entry.get('編號', entry.get('code', ''))
            
            if company and code:
                code_key = f"{company}:{code}"
                if code_key not in seen_codes:
                    merged_codes.append({
                        "公司": company,
                        "編號": code
                    })
                    seen_codes.add(code_key)
                    
        # 按公司優先順序排序
        company_priority = ['錢櫃', '好樂迪', '銀櫃', '音圓', '金嗓', '弘音', '星據點', '音霸', '大東', '點將家']
        merged_codes.sort(key=lambda x: (
            company_priority.index(x['公司']) if x['公司'] in company_priority else 999,
            x['公司'],
            x['編號']
        ))
        
        return merged_codes
    
    def process_songs_database(self):
        """處理歌曲搜尋資料庫"""
        print("🔄 處理歌曲搜尋資料庫...")
        
        # 按歌名+歌手分組
        song_groups = defaultdict(list)
        
        for song in self.songs_db:
            song_name = song.get('歌名', '').strip()
            singer_name = song.get('歌手', '').strip()
            
            if song_name and singer_name:
                key = f"{song_name}||{singer_name}"
                song_groups[key].append(song)
        
        processed_count = 0
        for group_key, song_entries in song_groups.items():
            song_name, singer_name = group_key.split('||')
            song_id = self.generate_song_id(song_name, singer_name)
            
            # 合併編號資訊
            merged_codes = self.merge_song_codes(song_entries)
            
            # 取得其他資訊
            language = ''
            for entry in song_entries:
                if entry.get('語言'):
                    language = entry['語言']
                    break
            
            # 建立統一歌曲資料
            self.unified_db["songs"][song_id] = {
                "歌名": song_name,
                "歌手": singer_name,
                "語言": language,
                "編號資訊": merged_codes,
                "來源": "歌曲資料庫",
                "創建時間": datetime.now().date().isoformat(),
                "更新時間": datetime.now().isoformat()
            }
            
            # 建立索引
            self.unified_db["indexes"]["by_singer"][singer_name].append(song_id)
            self.unified_db["indexes"]["by_song_name"][song_name].append(song_id)
            if language:
                self.unified_db["indexes"]["by_language"][language].append(song_id)
            
            for code_info in merged_codes:
                company = code_info['公司']
                self.unified_db["indexes"]["by_company"][company].append(song_id)
                self.unified_db["metadata"]["companies"].add(company)
            
            processed_count += 1
            
            if processed_count % 5000 == 0:
                print(f"  進度: {processed_count:,} 首歌曲已處理")
        
        print(f"  ✅ 完成: {processed_count:,} 首歌曲")
        return processed_count
    
    def integrate_singers_database(self):
        """整合歌手搜尋資料庫"""
        print("🔄 整合歌手搜尋資料庫...")
        
        enhanced_count = 0
        new_songs_count = 0
        
        for singer_name, singer_data in self.singers_db.items():
            singer_songs = singer_data.get('歌曲清單', [])
            
            # 建立歌手統計資料
            self.unified_db["singer_metadata"][singer_name] = {
                "總歌曲數": len(singer_songs),
                "最後更新": singer_data.get('更新時間', ''),
                "來源": "歌手資料庫",
                "語言分布": defaultdict(int),
                "公司分布": defaultdict(int)
            }
            
            for song_info in singer_songs:
                song_name = song_info.get('歌名', '').strip()
                if not song_name:
                    continue
                    
                song_id = self.generate_song_id(song_name, singer_name)
                
                # 檢查是否已存在
                if song_id in self.unified_db["songs"]:
                    # 合併編號資訊
                    existing_song = self.unified_db["songs"][song_id]
                    existing_codes = existing_song.get('編號資訊', [])
                    new_codes = song_info.get('編號資訊', [])
                    
                    # 合併所有編號
                    all_codes = existing_codes + new_codes
                    merged_codes = self.merge_song_codes(all_codes)
                    
                    # 更新歌曲資訊
                    existing_song['編號資訊'] = merged_codes
                    existing_song['來源'] = "歌曲+歌手資料庫"
                    existing_song['更新時間'] = datetime.now().isoformat()
                    
                    # 更新語言資訊
                    if song_info.get('語言') and not existing_song.get('語言'):
                        existing_song['語言'] = song_info['語言']
                    
                    enhanced_count += 1
                else:
                    # 新歌曲
                    self.unified_db["songs"][song_id] = {
                        "歌名": song_name,
                        "歌手": singer_name,
                        "語言": song_info.get('語言', ''),
                        "編號資訊": song_info.get('編號資訊', []),
                        "來源": "歌手資料庫",
                        "創建時間": datetime.now().date().isoformat(),
                        "更新時間": datetime.now().isoformat()
                    }
                    
                    # 建立索引
                    self.unified_db["indexes"]["by_singer"][singer_name].append(song_id)
                    self.unified_db["indexes"]["by_song_name"][song_name].append(song_id)
                    
                    language = song_info.get('語言', '')
                    if language:
                        self.unified_db["indexes"]["by_language"][language].append(song_id)
                    
                    for code_info in song_info.get('編號資訊', []):
                        company = code_info.get('公司', '')
                        if company:
                            self.unified_db["indexes"]["by_company"][company].append(song_id)
                            self.unified_db["metadata"]["companies"].add(company)
                    
                    new_songs_count += 1
                
                # 更新歌手統計
                language = song_info.get('語言', '')
                if language:
                    self.unified_db["singer_metadata"][singer_name]["語言分布"][language] += 1
                
                for code_info in song_info.get('編號資訊', []):
                    company = code_info.get('公司', '')
                    if company:
                        self.unified_db["singer_metadata"][singer_name]["公司分布"][company] += 1
        
        print(f"  ✅ 強化現有歌曲: {enhanced_count:,} 首")
        print(f"  ✅ 新增歌曲: {new_songs_count:,} 首")
        return enhanced_count, new_songs_count
    
    def finalize_metadata(self):
        """完成統計資料"""
        total_songs = len(self.unified_db["songs"])
        total_singers = len(self.unified_db["indexes"]["by_singer"])
        
        self.unified_db["metadata"].update({
            "total_songs": total_songs,
            "total_singers": total_singers,
            "companies": sorted(list(self.unified_db["metadata"]["companies"])),
            "completed": datetime.now().isoformat()
        })
        
        # 清理空的索引
        for index_type in self.unified_db["indexes"]:
            self.unified_db["indexes"][index_type] = dict(self.unified_db["indexes"][index_type])
            
        # 轉換歌手統計中的defaultdict
        for singer_name in self.unified_db["singer_metadata"]:
            metadata = self.unified_db["singer_metadata"][singer_name]
            metadata["語言分布"] = dict(metadata["語言分布"])
            metadata["公司分布"] = dict(metadata["公司分布"])
    
    def save_unified_database(self, filename="public/unified_karaoke_db.json"):
        """儲存統一資料庫"""
        print(f"💾 儲存統一資料庫到 {filename}...")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.unified_db, f, ensure_ascii=False, indent=2)
            
            file_size = len(json.dumps(self.unified_db, ensure_ascii=False)) / 1024 / 1024
            print(f"  ✅ 儲存成功")
            print(f"  📁 檔案大小: {file_size:.2f} MB")
            
            return True
        except Exception as e:
            print(f"  ❌ 儲存失敗: {e}")
            return False
    
    def create_compatibility_files(self):
        """創建相容性檔案 (維持舊格式供過渡期使用)"""
        print("🔄 創建相容性檔案...")
        
        # 創建新的 songs_simplified.json
        new_songs = []
        for song_id, song_data in self.unified_db["songs"].items():
            for code_info in song_data.get('編號資訊', []):
                new_songs.append({
                    "歌名": song_data["歌名"],
                    "歌手": song_data["歌手"],
                    "編號": code_info["編號"],
                    "公司": code_info["公司"],
                    "語言": song_data.get("語言", "")
                })
        
        with open('public/songs_simplified_v2.json', 'w', encoding='utf-8') as f:
            json.dump(new_songs, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 新版歌曲檔案: {len(new_songs):,} 筆記錄")
        
        # 創建新的 singers_data.json - 計算實際歌曲數量
        new_singers = {}
        for singer_name in self.unified_db["indexes"]["by_singer"]:
            song_ids = self.unified_db["indexes"]["by_singer"][singer_name]
            singer_songs = []
            
            for song_id in song_ids:
                song_data = self.unified_db["songs"][song_id]
                singer_songs.append({
                    "歌名": song_data["歌名"],
                    "歌手": song_data["歌手"],
                    "語言": song_data.get("語言", ""),
                    "編號資訊": song_data.get("編號資訊", [])
                })
            
            # 使用實際歌曲清單長度而非統計資料
            actual_song_count = len(singer_songs)
            metadata = self.unified_db["singer_metadata"].get(singer_name, {})
            new_singers[singer_name] = {
                "歌手名稱": singer_name,
                "歌曲數量": actual_song_count,  # 使用實際數量
                "更新時間": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "歌曲清單": singer_songs
            }
        
        with open('public/singers_data_v2.json', 'w', encoding='utf-8') as f:
            json.dump(new_singers, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 新版歌手檔案: {len(new_singers)} 位歌手")
    
    def run_unification(self):
        """執行完整的資料庫統一流程"""
        print("🚀 資料庫統一系統啟動")
        print("="*50)
        
        start_time = time.time()
        
        # 1. 載入現有資料庫
        if not self.load_existing_databases():
            return False
        
        # 2. 處理歌曲資料庫
        songs_processed = self.process_songs_database()
        
        # 3. 整合歌手資料庫
        enhanced_count, new_songs_count = self.integrate_singers_database()
        
        # 4. 完成統計資料
        self.finalize_metadata()
        
        # 5. 儲存統一資料庫
        if not self.save_unified_database():
            return False
        
        # 6. 創建相容性檔案
        self.create_compatibility_files()
        
        end_time = time.time()
        
        # 顯示完成統計
        print(f"\n🎉 資料庫統一完成！")
        print(f"="*50)
        print(f"📊 統計資料:")
        print(f"  總歌曲數: {self.unified_db['metadata']['total_songs']:,} 首")
        print(f"  總歌手數: {self.unified_db['metadata']['total_singers']:,} 位")
        print(f"  卡拉OK公司: {len(self.unified_db['metadata']['companies'])} 家")
        print(f"  強化歌曲: {enhanced_count:,} 首")
        print(f"  新增歌曲: {new_songs_count:,} 首")
        print(f"  處理時間: {end_time - start_time:.1f} 秒")
        print(f"\n📁 產生檔案:")
        print(f"  主資料庫: public/unified_karaoke_db.json")
        print(f"  相容歌曲: public/songs_simplified_v2.json")
        print(f"  相容歌手: public/singers_data_v2.json")
        
        return True

def main():
    unifier = DatabaseUnifier()
    success = unifier.run_unification()
    
    if success:
        print(f"\n💡 下一步建議:")
        print(f"1. 檢查統一資料庫: head public/unified_karaoke_db.json")
        print(f"2. 比較檔案大小: ls -lh public/*json")
        print(f"3. 測試相容性: 確認前端仍可正常運作")
        print(f"4. 部署新架構: 更新前端程式碼使用新資料庫")
    else:
        print(f"\n❌ 統一過程失敗，請檢查錯誤訊息")

if __name__ == "__main__":
    main()