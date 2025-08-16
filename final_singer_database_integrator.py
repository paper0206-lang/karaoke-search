#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終歌手資料庫整合器
整合所有資料庫，徹底去重，產生最終完整的歌手資料庫
"""

import json
import time
import re
from collections import defaultdict
import difflib
import os

class FinalSingerDatabaseIntegrator:
    def __init__(self):
        self.all_databases = []
        self.integrated_database = {
            'taiwan_mandarin': set(),
            'taiwan_hokkien': set(),
            'hong_kong': set(),
            'mainland_china': set(),
            'singapore_malaysia': set(),
            'bands_groups': set(),
            'classic_60s_70s': set(),
            'golden_80s_90s': set(),
            'current_popular': set(),
            'indie_alternative': set(),
            'rap_hiphop': set()
        }
        
    def load_all_databases(self):
        """載入所有已建立的資料庫"""
        print("📥 載入所有歌手資料庫...")
        
        # 尋找所有歌手資料庫檔案
        database_files = [
            "clean_singer_keywords_database_20250811_195244.json",
            "comprehensive_balanced_singer_database_20250811_195902.json"
        ]
        
        loaded_count = 0
        
        for filename in database_files:
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        database = json.load(f)
                    
                    self.all_databases.append({
                        'filename': filename,
                        'data': database,
                        'singer_count': database.get('statistics', {}).get('total_singers', 0)
                    })
                    
                    print(f"✅ 載入 {filename}: {database.get('statistics', {}).get('total_singers', 0)} 位歌手")
                    loaded_count += 1
                    
                except Exception as e:
                    print(f"❌ 載入 {filename} 失敗: {e}")
            else:
                print(f"⚠️ 找不到檔案: {filename}")
        
        print(f"📊 總共載入 {loaded_count} 個資料庫")
        return loaded_count > 0
    
    def merge_all_singers(self):
        """合併所有資料庫的歌手"""
        print("\n🔄 合併所有資料庫的歌手...")
        
        total_before_merge = 0
        
        for db_info in self.all_databases:
            database = db_info['data']
            filename = db_info['filename']
            
            print(f"\n📋 處理 {filename}...")
            
            if 'singers_by_category' in database:
                for category, singers in database['singers_by_category'].items():
                    if category in self.integrated_database:
                        before_count = len(self.integrated_database[category])
                        self.integrated_database[category].update(singers)
                        after_count = len(self.integrated_database[category])
                        added = after_count - before_count
                        
                        if added > 0:
                            print(f"   🎵 {category}: +{added} 位歌手")
                        
                        total_before_merge += len(singers)
        
        # 統計合併結果
        total_after_merge = sum(len(singers) for singers in self.integrated_database.values())
        
        print(f"\n📊 合併統計:")
        print(f"   📥 合併前總數: {total_before_merge} 位歌手")
        print(f"   📤 合併後總數: {total_after_merge} 位歌手")
        print(f"   🗑️ 自動去重: {total_before_merge - total_after_merge} 位")
        
        return total_before_merge, total_after_merge
    
    def deep_duplicate_analysis(self):
        """深度重複分析"""
        print("\n🔍 進行深度重複分析...")
        
        # 收集所有歌手及其出現位置
        singer_locations = defaultdict(list)
        
        for category, singers in self.integrated_database.items():
            for singer in singers:
                singer_locations[singer].append(category)
        
        # 找出跨分類重複
        cross_category_duplicates = {}
        for singer, locations in singer_locations.items():
            if len(locations) > 1:
                cross_category_duplicates[singer] = locations
        
        print(f"🔍 發現 {len(cross_category_duplicates)} 位歌手跨分類重複:")
        
        # 顯示前20個重複項目
        count = 0
        for singer, locations in cross_category_duplicates.items():
            if count < 20:
                print(f"   📋 '{singer}' → {', '.join(locations)}")
                count += 1
            else:
                break
        
        if len(cross_category_duplicates) > 20:
            print(f"   ... 還有 {len(cross_category_duplicates) - 20} 位重複歌手")
        
        return cross_category_duplicates
    
    def smart_deduplication(self, cross_category_duplicates):
        """智能去重 - 為每位歌手選擇最適合的分類"""
        print("\n🧠 執行智能去重...")
        
        # 分類優先順序規則
        category_priority = {
            # 地區優先規則
            'taiwan_mandarin': 10,    # 台灣華語歌手優先保留在此
            'taiwan_hokkien': 9,      # 台語歌手優先
            'hong_kong': 8,           # 香港歌手
            'mainland_china': 7,      # 大陸歌手
            'singapore_malaysia': 6,  # 星馬歌手
            
            # 類型分類次要
            'classic_60s_70s': 5,
            'golden_80s_90s': 4,
            'current_popular': 3,
            'bands_groups': 2,
            'indie_alternative': 1,
            'rap_hiphop': 0
        }
        
        removed_count = 0
        
        for singer, locations in cross_category_duplicates.items():
            # 找出最高優先級的分類
            best_category = max(locations, key=lambda cat: category_priority.get(cat, -1))
            
            # 從其他分類中移除
            for category in locations:
                if category != best_category and category in self.integrated_database:
                    if singer in self.integrated_database[category]:
                        self.integrated_database[category].remove(singer)
                        removed_count += 1
        
        print(f"✅ 智能去重完成，移除 {removed_count} 個重複項目")
        
        return removed_count
    
    def similar_name_analysis(self, similarity_threshold=0.9):
        """相似名稱分析"""
        print(f"\n🔍 分析相似歌手名稱 (相似度 >= {similarity_threshold})...")
        
        all_singers = []
        for singers in self.integrated_database.values():
            all_singers.extend(singers)
        
        similar_groups = []
        processed = set()
        
        for i, singer1 in enumerate(all_singers):
            if singer1 in processed:
                continue
                
            similar_group = [singer1]
            processed.add(singer1)
            
            for singer2 in all_singers[i+1:]:
                if singer2 in processed:
                    continue
                
                # 計算相似度
                similarity = difflib.SequenceMatcher(None, singer1.lower(), singer2.lower()).ratio()
                
                if similarity >= similarity_threshold:
                    similar_group.append(singer2)
                    processed.add(singer2)
            
            if len(similar_group) > 1:
                similar_groups.append(similar_group)
        
        print(f"🔍 發現 {len(similar_groups)} 組相似名稱:")
        
        for group in similar_groups:
            print(f"   📋 相似組: {' | '.join(group)}")
        
        return similar_groups
    
    def create_final_database(self):
        """創建最終資料庫"""
        print("\n🔨 創建最終整合資料庫...")
        
        # 合併所有唯一歌手
        all_unique_singers = set()
        for singers in self.integrated_database.values():
            all_unique_singers.update(singers)
        
        # 創建搜尋關鍵字（包含變體）
        search_keywords = set(all_unique_singers)
        
        # 添加關鍵字變體
        for singer in list(all_unique_singers):
            # 空格變體
            if ' ' in singer:
                no_space = singer.replace(' ', '')
                search_keywords.add(no_space)
            
            # 點號變體
            if '.' in singer:
                no_dot = singer.replace('.', '')
                with_space = singer.replace('.', ' ')
                search_keywords.add(no_dot)
                search_keywords.add(with_space)
            
            # 符號變體
            if '&' in singer:
                no_ampersand = singer.replace('&', '')
                with_and = singer.replace('&', 'and')
                search_keywords.add(no_ampersand)
                search_keywords.add(with_and)
            
            # 樂團變體
            if singer.endswith('樂團'):
                no_band = singer.replace('樂團', '')
                search_keywords.add(no_band)
            
            if singer.endswith('樂隊'):
                no_band = singer.replace('樂隊', '')
                search_keywords.add(no_band)
        
        # 創建最終資料庫
        final_database = {
            'singers_by_category': {
                k: sorted(list(v)) for k, v in self.integrated_database.items() if v
            },
            'all_singers': sorted(list(all_unique_singers)),
            'search_keywords': sorted(list(search_keywords)),
            'statistics': {
                'total_singers': len(all_unique_singers),
                'total_keywords': len(search_keywords),
                **{category: len(singers) for category, singers in self.integrated_database.items()}
            },
            'category_descriptions': {
                'taiwan_mandarin': '台灣華語流行歌手',
                'taiwan_hokkien': '台語/閩南語歌手',
                'hong_kong': '香港歌手',
                'mainland_china': '中國大陸歌手',
                'singapore_malaysia': '新加坡馬來西亞歌手',
                'bands_groups': '樂團組合',
                'classic_60s_70s': '60-70年代經典歌手',
                'golden_80s_90s': '80-90年代黃金期歌手',
                'current_popular': '當代流行歌手',
                'indie_alternative': '獨立另類音樂',
                'rap_hiphop': '饒舌嘻哈'
            },
            'integration_info': {
                'created_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'source_databases': len(self.all_databases),
                'deduplication_method': 'smart_priority_based',
                'keyword_variants_included': True
            }
        }
        
        return final_database
    
    def save_final_database(self, database, filename):
        """儲存最終資料庫"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(database, f, ensure_ascii=False, indent=2)
            print(f"💾 最終資料庫已保存到: {filename}")
        except Exception as e:
            print(f"❌ 儲存失敗: {e}")
    
    def print_final_statistics(self, database):
        """顯示最終統計"""
        print("\n📊 最終整合歌手資料庫統計:")
        print("=" * 60)
        
        stats = database['statistics']
        descriptions = database['category_descriptions']
        
        print("🌏 各地區歌手分布:")
        region_data = [
            ('taiwan_mandarin', '台灣華語', '🇹🇼'),
            ('taiwan_hokkien', '台語歌手', '🎭'),
            ('hong_kong', '香港歌手', '🇭🇰'),
            ('mainland_china', '大陸歌手', '🇨🇳'),
            ('singapore_malaysia', '星馬歌手', '🇸🇬')
        ]
        
        region_total = 0
        for category, name, emoji in region_data:
            count = stats.get(category, 0)
            region_total += count
            print(f"   {emoji} {name}: {count:>3} 位")
        
        print(f"   📊 地區小計: {region_total} 位")
        
        print("\n🎸 音樂類型分布:")
        type_data = [
            ('bands_groups', '樂團組合', '🎸'),
            ('indie_alternative', '獨立音樂', '🎨'),
            ('rap_hiphop', '饒舌嘻哈', '🎤'),
            ('current_popular', '當代流行', '🎵')
        ]
        
        type_total = 0
        for category, name, emoji in type_data:
            count = stats.get(category, 0)
            type_total += count
            print(f"   {emoji} {name}: {count:>3} 位")
        
        print(f"   📊 類型小計: {type_total} 位")
        
        print("\n📅 年代分布:")
        era_data = [
            ('classic_60s_70s', '60-70年代', '📻'),
            ('golden_80s_90s', '80-90年代', '💽')
        ]
        
        era_total = 0
        for category, name, emoji in era_data:
            count = stats.get(category, 0)
            era_total += count
            print(f"   {emoji} {name}: {count:>3} 位")
        
        print(f"   📊 年代小計: {era_total} 位")
        
        print(f"\n📝 總計:")
        print(f"   🎵 歌手總數: {stats['total_singers']:>4} 位")
        print(f"   🔍 搜尋關鍵字: {stats['total_keywords']:>4} 個")
        print(f"   🏷️ 有效分類: {len([k for k,v in stats.items() if isinstance(v, int) and v > 0 and k not in ['total_singers', 'total_keywords']]):>4} 個")
        
        # 計算平衡指數
        category_counts = [stats.get(cat, 0) for cat, _, _ in region_data + type_data + era_data]
        non_zero_counts = [count for count in category_counts if count > 0]
        
        if non_zero_counts:
            max_count = max(non_zero_counts)
            min_count = min(non_zero_counts)
            avg_count = sum(non_zero_counts) / len(non_zero_counts)
            balance_index = (min_count / max_count) * 100 if max_count > 0 else 0
            
            print(f"\n📊 資料庫品質分析:")
            print(f"   📈 最大分類: {max_count} 位")
            print(f"   📉 最小分類: {min_count} 位")
            print(f"   📊 平均分類: {avg_count:.1f} 位")
            print(f"   🎯 平衡指數: {balance_index:.1f}%")
        
        # 顯示部分歌手樣本
        print(f"\n🌟 歌手樣本展示:")
        
        sample_categories = ['taiwan_mandarin', 'taiwan_hokkien', 'hong_kong', 'mainland_china', 'bands_groups']
        
        for category in sample_categories:
            if category in database['singers_by_category'] and database['singers_by_category'][category]:
                singers = database['singers_by_category'][category]
                description = descriptions.get(category, category)
                print(f"\n   📂 {description} (共{len(singers)}位):")
                
                # 顯示前8位作為樣本
                for i, singer in enumerate(singers[:8], 1):
                    print(f"      {i}. {singer}")
                
                if len(singers) > 8:
                    print(f"      ... 還有 {len(singers) - 8} 位")
    
    def create_search_test_sample(self, database, sample_size=50):
        """創建搜尋測試樣本"""
        print(f"\n🧪 創建搜尋測試樣本 (隨機選取 {sample_size} 位歌手)...")
        
        import random
        
        all_singers = database['all_singers']
        
        if len(all_singers) >= sample_size:
            test_sample = random.sample(all_singers, sample_size)
        else:
            test_sample = all_singers.copy()
        
        # 確保包含各分類的代表性歌手
        category_representatives = []
        for category, singers in database['singers_by_category'].items():
            if singers:
                category_representatives.append(singers[0])  # 每個分類取第一位
        
        # 合併測試樣本
        final_test_sample = list(set(test_sample + category_representatives))
        
        print(f"✅ 測試樣本準備完成: {len(final_test_sample)} 位歌手")
        
        # 顯示測試樣本
        print("🎯 搜尋測試樣本:")
        for i, singer in enumerate(final_test_sample[:20], 1):
            print(f"   {i:2d}. {singer}")
        
        if len(final_test_sample) > 20:
            print(f"   ... 還有 {len(final_test_sample) - 20} 位")
        
        return final_test_sample

def main():
    integrator = FinalSingerDatabaseIntegrator()
    
    print("🔧 最終歌手資料庫整合器")
    print("=" * 60)
    
    # 1. 載入所有資料庫
    if not integrator.load_all_databases():
        print("❌ 沒有找到可載入的資料庫")
        return
    
    # 2. 合併所有歌手
    total_before, total_after = integrator.merge_all_singers()
    
    # 3. 深度重複分析
    cross_duplicates = integrator.deep_duplicate_analysis()
    
    # 4. 智能去重
    removed = integrator.smart_deduplication(cross_duplicates)
    
    # 5. 相似名稱分析
    similar_groups = integrator.similar_name_analysis()
    
    # 6. 創建最終資料庫
    final_database = integrator.create_final_database()
    
    # 7. 儲存最終資料庫
    final_filename = f"FINAL_singer_database_{time.strftime('%Y%m%d_%H%M%S')}.json"
    integrator.save_final_database(final_database, final_filename)
    
    # 8. 顯示最終統計
    integrator.print_final_statistics(final_database)
    
    # 9. 創建搜尋測試樣本
    test_sample = integrator.create_search_test_sample(final_database)
    
    print(f"\n🎯 最終整合完成:")
    print(f"   📦 最終歌手總數: {final_database['statistics']['total_singers']} 位")
    print(f"   🔍 搜尋關鍵字總數: {final_database['statistics']['total_keywords']} 個")
    print(f"   🧹 去重移除項目: {removed} 個")
    print(f"   💾 最終資料庫: {final_filename}")
    print(f"   🧪 測試樣本: {len(test_sample)} 位歌手")
    print(f"\n🚀 現在可以用這個完整且無重複的資料庫測試 KTV 搜尋功能！")

if __name__ == "__main__":
    main()