#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌手歌曲提取器 - 小規模測試版本
從現有150萬首歌曲資料庫中提取歌手相關歌曲，創建獨立的歌手歌曲資料庫
"""

import json
import time
import re
import os
from datetime import datetime
from collections import defaultdict
import difflib

class SingerSongExtractor:
    def __init__(self):
        # 獨立的歌手歌曲資料庫
        self.singer_songs_database = {
            "metadata": {
                "created_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "extractor_version": "1.0.0",
                "database_type": "singer_songs_extraction",
                "source_database": "音圓完整數據_20250810_221337.json",
                "singer_source": "FINAL_singer_database_20250811_200210.json",
                "total_singers_processed": 0,
                "total_songs_extracted": 0
            },
            "extraction_results": {},
            "statistics": {
                "singers_with_songs": [],
                "singers_without_songs": [],
                "total_unique_songs": 0,
                "live_songs_count": 0,
                "regular_songs_count": 0
            }
        }
        
        # 測試用歌手（前5位知名歌手）
        self.test_singers = [
            "周杰倫",
            "蔡依林", 
            "林俊傑",
            "鄧紫棋",
            "五月天"
        ]
        
        # 歌手名稱變體生成
        self.singer_variants = {}
        
    def load_source_databases(self):
        """載入來源資料庫"""
        print("📥 載入來源資料庫...")
        
        # 1. 載入歌手資料庫
        singer_db_file = "FINAL_singer_database_20250811_200210.json"
        if not os.path.exists(singer_db_file):
            print(f"❌ 找不到歌手資料庫: {singer_db_file}")
            return None, None
            
        try:
            with open(singer_db_file, 'r', encoding='utf-8') as f:
                singer_database = json.load(f)
            print(f"✅ 歌手資料庫: {singer_database.get('statistics', {}).get('total_singers', 0)} 位歌手")
        except Exception as e:
            print(f"❌ 載入歌手資料庫失敗: {e}")
            return None, None
        
        # 2. 載入歌曲資料庫
        songs_db_file = "音圓完整數據_20250810_221337.json"
        if not os.path.exists(songs_db_file):
            print(f"❌ 找不到歌曲資料庫: {songs_db_file}")
            return singer_database, None
            
        try:
            with open(songs_db_file, 'r', encoding='utf-8') as f:
                songs_database = json.load(f)
            
            # 檢查歌曲資料結構
            total_songs = 0
            if isinstance(songs_database, dict):
                # 如果是字典結構，計算總歌曲數
                for key, value in songs_database.items():
                    if isinstance(value, list):
                        total_songs += len(value)
                    elif isinstance(value, dict) and 'songs' in value:
                        total_songs += len(value['songs'])
            elif isinstance(songs_database, list):
                # 如果是列表結構
                total_songs = len(songs_database)
                
            print(f"✅ 歌曲資料庫: 約 {total_songs:,} 首歌曲")
            
        except Exception as e:
            print(f"❌ 載入歌曲資料庫失敗: {e}")
            return singer_database, None
            
        return singer_database, songs_database
    
    def generate_singer_variants(self, singer_name):
        """生成歌手名稱變體"""
        variants = set([singer_name])
        
        # 1. 空格變體
        if ' ' in singer_name:
            no_space = singer_name.replace(' ', '')
            variants.add(no_space)
        else:
            # 嘗試添加空格（在中英文之間）
            spaced = re.sub(r'([\u4e00-\u9fa5])([a-zA-Z])', r'\1 \2', singer_name)
            spaced = re.sub(r'([a-zA-Z])([\u4e00-\u9fa5])', r'\1 \2', spaced)
            if spaced != singer_name:
                variants.add(spaced)
        
        # 2. 符號變體
        if '&' in singer_name:
            variants.add(singer_name.replace('&', ' & '))
            variants.add(singer_name.replace('&', ''))
        
        # 3. 樂團變體
        if singer_name.endswith('樂團'):
            variants.add(singer_name.replace('樂團', ''))
        elif singer_name.endswith('樂隊'):
            variants.add(singer_name.replace('樂隊', ''))
            
        # 4. 常見變體
        variants.add(singer_name.upper())
        variants.add(singer_name.lower())
        
        return list(variants)
    
    def process_song_title(self, title):
        """處理歌曲標題 - 將(lv)轉換為(Live版)"""
        if not title:
            return title, False
            
        is_live = False
        
        # 處理Live版本標記
        if re.search(r'\(lv\)', title, re.IGNORECASE):
            title = re.sub(r'\(lv\)', '(Live版)', title, flags=re.IGNORECASE)
            is_live = True
        elif re.search(r'\(LV\)', title):
            title = re.sub(r'\(LV\)', '(Live版)', title)
            is_live = True
        elif 'live' in title.lower() and '版' not in title:
            # 檢測其他Live標記
            if re.search(r'live', title, re.IGNORECASE) and not re.search(r'(Live版)', title):
                is_live = True
        
        # 清理多餘空格
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title, is_live
    
    def fuzzy_match_singer(self, song_singer, target_singer_variants, threshold=0.8):
        """模糊匹配歌手名稱"""
        if not song_singer or not target_singer_variants:
            return False, 0
            
        best_match = 0
        matched = False
        
        # 清理歌手名稱
        clean_song_singer = song_singer.strip()
        
        for variant in target_singer_variants:
            # 精確匹配
            if clean_song_singer == variant:
                return True, 1.0
                
            # 模糊匹配
            similarity = difflib.SequenceMatcher(None, clean_song_singer.lower(), variant.lower()).ratio()
            if similarity > best_match:
                best_match = similarity
                
            # 包含關係檢查
            if variant in clean_song_singer or clean_song_singer in variant:
                contain_ratio = min(len(variant), len(clean_song_singer)) / max(len(variant), len(clean_song_singer))
                if contain_ratio > 0.7:
                    best_match = max(best_match, contain_ratio)
        
        if best_match >= threshold:
            matched = True
            
        return matched, best_match
    
    def extract_songs_for_singer(self, singer_name, songs_database):
        """為單一歌手提取歌曲"""
        print(f"🎵 提取歌手: {singer_name}")
        
        # 生成歌手名稱變體
        singer_variants = self.generate_singer_variants(singer_name)
        self.singer_variants[singer_name] = singer_variants
        
        print(f"   📝 名稱變體: {', '.join(singer_variants[:3])}{'...' if len(singer_variants) > 3 else ''}")
        
        matched_songs = []
        
        try:
            # 處理不同的資料庫結構
            songs_to_search = []
            
            if isinstance(songs_database, dict):
                # 字典結構 - 查找歌曲列表
                for key, value in songs_database.items():
                    if isinstance(value, list):
                        # 直接是歌曲列表
                        songs_to_search.extend(value)
                    elif isinstance(value, dict):
                        # 巢狀結構
                        if 'songs' in value and isinstance(value['songs'], list):
                            songs_to_search.extend(value['songs'])
                        elif 'data' in value and isinstance(value['data'], list):
                            songs_to_search.extend(value['data'])
            elif isinstance(songs_database, list):
                # 直接是歌曲列表
                songs_to_search = songs_database
            
            print(f"   🔍 搜尋範圍: {len(songs_to_search):,} 首歌曲")
            
            # 搜尋匹配的歌曲
            for song in songs_to_search:
                if not isinstance(song, dict):
                    continue
                    
                # 提取歌手資訊（嘗試不同的欄位名稱）
                song_singer = None
                for singer_field in ['singer', 'artist', 'performer', '歌手', '演唱者']:
                    if singer_field in song:
                        song_singer = song[singer_field]
                        break
                
                if not song_singer:
                    continue
                    
                # 檢查是否匹配
                is_match, similarity = self.fuzzy_match_singer(song_singer, singer_variants)
                
                if is_match:
                    # 提取歌曲資訊
                    song_title = None
                    for title_field in ['song_name', 'title', 'name', '歌名', '歌曲名稱']:
                        if title_field in song:
                            song_title = song[title_field]
                            break
                    
                    if not song_title:
                        continue
                        
                    # 處理Live版本
                    processed_title, is_live = self.process_song_title(song_title)
                    
                    # 提取其他資訊
                    song_id = song.get('song_id', song.get('id', song.get('編號', '')))
                    
                    song_info = {
                        "song_id": str(song_id) if song_id else '',
                        "song_name": processed_title,
                        "original_song_name": song_title,
                        "singer": song_singer,
                        "target_singer": singer_name,
                        "is_live": is_live,
                        "match_similarity": round(similarity, 3),
                        "matched_variant": None,  # 找出匹配的變體
                        "extraction_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # 找出匹配的變體
                    for variant in singer_variants:
                        if variant == song_singer or variant in song_singer or song_singer in variant:
                            song_info["matched_variant"] = variant
                            break
                    
                    matched_songs.append(song_info)
            
            print(f"   ✅ 找到 {len(matched_songs)} 首歌曲")
            
            # 去重（基於歌名和歌手）
            unique_songs = []
            seen = set()
            
            for song in matched_songs:
                key = (song["song_name"].lower(), song["singer"].lower())
                if key not in seen:
                    seen.add(key)
                    unique_songs.append(song)
                    
            if len(unique_songs) != len(matched_songs):
                print(f"   🗑️ 去重後: {len(unique_songs)} 首歌曲")
            
            return unique_songs
            
        except Exception as e:
            print(f"   ❌ 提取失敗: {e}")
            return []
    
    def run_test_extraction(self):
        """執行小規模測試提取"""
        print("🧪 開始歌手歌曲提取測試")
        print("=" * 50)
        print(f"📋 測試歌手: {', '.join(self.test_singers)}")
        print()
        
        # 載入來源資料庫
        singer_database, songs_database = self.load_source_databases()
        
        if not singer_database or not songs_database:
            print("❌ 無法載入必要的資料庫")
            return
        
        # 更新元數據
        self.singer_songs_database["metadata"]["total_singers_to_process"] = len(self.test_singers)
        
        # 處理每位測試歌手
        for singer in self.test_singers:
            try:
                songs = self.extract_songs_for_singer(singer, songs_database)
                
                if songs:
                    self.singer_songs_database["extraction_results"][singer] = {
                        "status": "success",
                        "songs_count": len(songs),
                        "songs": songs,
                        "variants_used": self.singer_variants.get(singer, [])
                    }
                    
                    self.singer_songs_database["statistics"]["singers_with_songs"].append(singer)
                    self.singer_songs_database["metadata"]["total_songs_extracted"] += len(songs)
                    
                    # 統計Live版本
                    live_count = sum(1 for song in songs if song["is_live"])
                    regular_count = len(songs) - live_count
                    
                    self.singer_songs_database["statistics"]["live_songs_count"] += live_count
                    self.singer_songs_database["statistics"]["regular_songs_count"] += regular_count
                    
                    print(f"   🎤 Live版本: {live_count} 首")
                    print(f"   🎵 一般版本: {regular_count} 首")
                    
                    # 顯示前5首歌曲樣本
                    print(f"   📝 歌曲樣本:")
                    for i, song in enumerate(songs[:5], 1):
                        live_mark = " (Live版)" if song["is_live"] else ""
                        print(f"      {i}. {song['song_name']}{live_mark} - {song['singer']}")
                    
                    if len(songs) > 5:
                        print(f"      ... 還有 {len(songs) - 5} 首")
                        
                else:
                    self.singer_songs_database["extraction_results"][singer] = {
                        "status": "no_songs",
                        "songs_count": 0,
                        "songs": [],
                        "variants_used": self.singer_variants.get(singer, [])
                    }
                    
                    self.singer_songs_database["statistics"]["singers_without_songs"].append(singer)
                    print(f"   ⚪ 未找到歌曲")
                
                self.singer_songs_database["metadata"]["total_singers_processed"] += 1
                
            except Exception as e:
                print(f"   ❌ 處理失敗: {e}")
                self.singer_songs_database["extraction_results"][singer] = {
                    "status": "error",
                    "error": str(e),
                    "songs_count": 0,
                    "songs": []
                }
            
            print()  # 空行分隔
        
        # 保存測試結果
        self.save_test_results()
        self.print_test_summary()
    
    def save_test_results(self):
        """保存測試結果"""
        filename = f"test_singer_extraction_results_{time.strftime('%Y%m%d_%H%M%S')}.json"
        
        # 更新統計資訊
        self.singer_songs_database["statistics"]["total_unique_songs"] = self.singer_songs_database["metadata"]["total_songs_extracted"]
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.singer_songs_database, f, ensure_ascii=False, indent=2)
            print(f"💾 測試結果已保存到: {filename}")
            self.results_file = filename
        except Exception as e:
            print(f"❌ 保存測試結果失敗: {e}")
    
    def print_test_summary(self):
        """打印測試摘要"""
        print("=" * 60)
        print("📊 歌手歌曲提取測試結果")
        print("=" * 60)
        
        metadata = self.singer_songs_database["metadata"]
        stats = self.singer_songs_database["statistics"]
        
        print(f"🎵 測試歌手總數: {len(self.test_singers)}")
        print(f"✅ 處理完成: {metadata['total_singers_processed']}")
        print(f"🎶 有歌曲歌手: {len(stats['singers_with_songs'])}")
        print(f"⚪ 無歌曲歌手: {len(stats['singers_without_songs'])}")
        print(f"🎵 總歌曲數: {metadata['total_songs_extracted']}")
        print(f"🎤 Live版本: {stats['live_songs_count']}")
        print(f"🎵 一般版本: {stats['regular_songs_count']}")
        
        print(f"\n📋 詳細結果:")
        for singer, result in self.singer_songs_database["extraction_results"].items():
            status = result["status"]
            if status == "success":
                songs_count = result["songs_count"]
                print(f"   ✅ {singer}: {songs_count} 首歌曲")
                
                # 顯示歌曲樣本
                if result["songs"]:
                    print(f"      🎵 歌曲樣本:")
                    for song in result["songs"][:3]:
                        live_mark = " (Live版)" if song["is_live"] else ""
                        similarity = f"[{song['match_similarity']:.2f}]" if song.get('match_similarity') else ""
                        print(f"         • {song['song_name']}{live_mark} {similarity}")
                    
                    if result["songs_count"] > 3:
                        print(f"         ... 還有 {result['songs_count'] - 3} 首")
                        
            elif status == "no_songs":
                print(f"   ⚪ {singer}: 未找到歌曲")
            elif status == "error":
                error_msg = result.get("error", "未知錯誤")
                print(f"   ❌ {singer}: 處理失敗 ({error_msg})")
        
        if hasattr(self, 'results_file'):
            print(f"\n📄 完整結果請查看: {self.results_file}")
            
        print(f"\n🎯 下一步：如果測試結果符合需求，可以擴展到完整的989位歌手")

def main():
    extractor = SingerSongExtractor()
    extractor.run_test_extraction()

if __name__ == "__main__":
    main()