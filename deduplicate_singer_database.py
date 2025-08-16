#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌手資料庫去重工具
檢查並清理重複的歌手名稱，產生乾淨的資料庫
"""

import json
import time
from collections import defaultdict
import difflib

class SingerDatabaseDeduplicator:
    def __init__(self, database_file):
        self.database_file = database_file
        self.database = None
        self.load_database()
        
    def load_database(self):
        """載入資料庫"""
        try:
            with open(self.database_file, 'r', encoding='utf-8') as f:
                self.database = json.load(f)
            print(f"✅ 成功載入資料庫: {self.database_file}")
        except Exception as e:
            print(f"❌ 載入資料庫失敗: {e}")
            
    def find_exact_duplicates(self):
        """找出完全重複的歌手"""
        print("\n🔍 檢查完全重複的歌手...")
        
        all_singers = []
        singer_to_categories = defaultdict(list)
        
        # 收集所有歌手及其所屬分類
        for category, singers in self.database['singers_by_category'].items():
            for singer in singers:
                all_singers.append(singer)
                singer_to_categories[singer].append(category)
        
        # 找出重複的歌手
        exact_duplicates = {}
        for singer, categories in singer_to_categories.items():
            if len(categories) > 1:
                exact_duplicates[singer] = categories
        
        print(f"🔍 找到 {len(exact_duplicates)} 個完全重複的歌手:")
        
        for singer, categories in exact_duplicates.items():
            print(f"   📋 '{singer}' 出現在: {', '.join(categories)}")
        
        return exact_duplicates
    
    def find_similar_duplicates(self, similarity_threshold=0.85):
        """找出相似的重複歌手"""
        print(f"\n🔍 檢查相似重複的歌手 (相似度 >= {similarity_threshold})...")
        
        all_singers = list(set([
            singer for singers in self.database['singers_by_category'].values() 
            for singer in singers
        ]))
        
        similar_groups = []
        processed = set()
        
        for i, singer1 in enumerate(all_singers):
            if singer1 in processed:
                continue
                
            similar_group = [singer1]
            processed.add(singer1)
            
            for j, singer2 in enumerate(all_singers[i+1:], i+1):
                if singer2 in processed:
                    continue
                
                # 計算相似度
                similarity = difflib.SequenceMatcher(None, singer1.lower(), singer2.lower()).ratio()
                
                if similarity >= similarity_threshold:
                    similar_group.append(singer2)
                    processed.add(singer2)
            
            if len(similar_group) > 1:
                similar_groups.append(similar_group)
        
        print(f"🔍 找到 {len(similar_groups)} 組相似的歌手:")
        
        for group in similar_groups:
            print(f"   📋 相似組合: {' | '.join(group)}")
        
        return similar_groups
    
    def analyze_categories_overlap(self):
        """分析分類間的重疊情況"""
        print("\n📊 分析分類間重疊情況...")
        
        category_singers = {}
        for category, singers in self.database['singers_by_category'].items():
            category_singers[category] = set(singers)
        
        overlaps = []
        categories = list(category_singers.keys())
        
        for i, cat1 in enumerate(categories):
            for cat2 in categories[i+1:]:
                common_singers = category_singers[cat1] & category_singers[cat2]
                if common_singers:
                    overlaps.append({
                        'category1': cat1,
                        'category2': cat2,
                        'common_count': len(common_singers),
                        'common_singers': sorted(list(common_singers))[:10]  # 只顯示前10個
                    })
        
        # 按重疊數量排序
        overlaps.sort(key=lambda x: x['common_count'], reverse=True)
        
        print(f"📊 發現 {len(overlaps)} 對分類有重疊:")
        
        for overlap in overlaps[:10]:  # 只顯示前10個
            print(f"   🔄 {overlap['category1']} ⟷ {overlap['category2']}: {overlap['common_count']} 位相同歌手")
            print(f"      樣本: {', '.join(overlap['common_singers'][:5])}")
            if overlap['common_count'] > 5:
                print(f"      ... 還有 {overlap['common_count'] - 5} 位")
        
        return overlaps
    
    def create_clean_database(self, remove_exact_duplicates=True, merge_similar=False):
        """創建清理後的資料庫"""
        print(f"\n🧹 創建清理後的資料庫...")
        
        clean_database = {
            'singers_by_category': {},
            'all_singers': [],
            'search_keywords': [],
            'statistics': {},
            'category_descriptions': self.database.get('category_descriptions', {}),
            'deduplication_info': {
                'original_total': sum(len(singers) for singers in self.database['singers_by_category'].values()),
                'removed_duplicates': 0,
                'merged_similar': 0,
                'final_total': 0
            }
        }
        
        # 收集所有唯一歌手
        all_unique_singers = set()
        category_unique_singers = {}
        
        if remove_exact_duplicates:
            # 去除完全重複：每個歌手只保留在第一個出現的分類中
            singer_first_category = {}
            
            # 按特定順序處理分類（確保重要分類優先）
            priority_order = [
                'taiwan_mandarin', 'taiwan_hokkien', 'hong_kong', 'mainland_china',
                'current_popular', 'bands_groups', 'classic_60s_70s', 'golden_80s_90s'
            ]
            
            # 處理優先分類
            for category in priority_order:
                if category in self.database['singers_by_category']:
                    category_unique_singers[category] = []
                    
                    for singer in self.database['singers_by_category'][category]:
                        if singer not in singer_first_category:
                            singer_first_category[singer] = category
                            category_unique_singers[category].append(singer)
                            all_unique_singers.add(singer)
                        else:
                            clean_database['deduplication_info']['removed_duplicates'] += 1
            
            # 處理剩餘分類
            for category, singers in self.database['singers_by_category'].items():
                if category not in priority_order:
                    category_unique_singers[category] = []
                    
                    for singer in singers:
                        if singer not in singer_first_category:
                            singer_first_category[singer] = category
                            category_unique_singers[category].append(singer)
                            all_unique_singers.add(singer)
                        else:
                            clean_database['deduplication_info']['removed_duplicates'] += 1
        else:
            # 不去除重複，直接複製
            for category, singers in self.database['singers_by_category'].items():
                category_unique_singers[category] = list(set(singers))
                all_unique_singers.update(singers)
        
        # 創建搜尋關鍵字
        search_keywords = set(all_unique_singers)
        
        # 添加變體
        for singer in list(all_unique_singers):
            # 空格變體
            if ' ' in singer:
                search_keywords.add(singer.replace(' ', ''))
            
            # 點號變體
            if '.' in singer:
                search_keywords.add(singer.replace('.', ''))
                search_keywords.add(singer.replace('.', ' '))
            
            # 特殊符號變體
            if '&' in singer:
                search_keywords.add(singer.replace('&', ''))
        
        # 更新資料庫
        clean_database['singers_by_category'] = {k: sorted(v) for k, v in category_unique_singers.items() if v}
        clean_database['all_singers'] = sorted(list(all_unique_singers))
        clean_database['search_keywords'] = sorted(list(search_keywords))
        
        # 更新統計
        clean_database['statistics'] = {
            'total_singers': len(all_unique_singers),
            'total_keywords': len(search_keywords),
            **{category: len(singers) for category, singers in category_unique_singers.items()}
        }
        
        clean_database['deduplication_info']['final_total'] = len(all_unique_singers)
        
        print(f"✅ 清理完成:")
        print(f"   📊 原始歌手數: {clean_database['deduplication_info']['original_total']}")
        print(f"   🗑️ 移除重複: {clean_database['deduplication_info']['removed_duplicates']}")
        print(f"   🎵 最終歌手數: {clean_database['deduplication_info']['final_total']}")
        print(f"   🔍 搜尋關鍵字: {clean_database['statistics']['total_keywords']}")
        
        return clean_database
    
    def save_clean_database(self, clean_database, filename):
        """儲存清理後的資料庫"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(clean_database, f, ensure_ascii=False, indent=2)
            print(f"💾 清理後的資料庫已保存到: {filename}")
        except Exception as e:
            print(f"❌ 儲存失敗: {e}")
    
    def print_clean_statistics(self, clean_database):
        """顯示清理後的統計"""
        print("\n📊 清理後資料庫統計:")
        print("=" * 50)
        
        stats = clean_database['statistics']
        dedup_info = clean_database['deduplication_info']
        
        print("🧹 清理結果:")
        print(f"   📥 原始歌手總數: {dedup_info['original_total']}")
        print(f"   🗑️ 移除重複歌手: {dedup_info['removed_duplicates']}")
        print(f"   📤 最終歌手總數: {dedup_info['final_total']}")
        print(f"   📈 去重效率: {dedup_info['removed_duplicates']/dedup_info['original_total']*100:.1f}%")
        
        print(f"\n🎵 分類統計:")
        important_categories = [
            ('taiwan_mandarin', '台灣華語'),
            ('taiwan_hokkien', '台語歌手'),
            ('hong_kong', '香港歌手'),
            ('mainland_china', '大陸歌手'),
            ('bands_groups', '樂團組合'),
            ('current_popular', '當代流行')
        ]
        
        for category, description in important_categories:
            if category in stats:
                print(f"   🎤 {description}: {stats[category]} 位")
        
        print(f"\n🔍 搜尋關鍵字: {stats['total_keywords']} 個")
        
        # 顯示部分清理後的歌手樣本
        print(f"\n🌟 清理後歌手樣本:")
        sample_singers = clean_database['all_singers'][:15]
        for i, singer in enumerate(sample_singers, 1):
            print(f"   {i:2d}. {singer}")
        
        if len(clean_database['all_singers']) > 15:
            print(f"   ... 還有 {len(clean_database['all_singers']) - 15} 位")

def main():
    # 載入最新的資料庫
    database_file = "enhanced_singer_keywords_database_20250811_194939.json"
    
    print("🧹 開始歌手資料庫去重處理")
    print("=" * 50)
    
    deduplicator = SingerDatabaseDeduplicator(database_file)
    
    if not deduplicator.database:
        print("❌ 無法載入資料庫，程式結束")
        return
    
    # 1. 找出完全重複的歌手
    exact_duplicates = deduplicator.find_exact_duplicates()
    
    # 2. 找出相似的重複歌手
    similar_duplicates = deduplicator.find_similar_duplicates()
    
    # 3. 分析分類間重疊
    category_overlaps = deduplicator.analyze_categories_overlap()
    
    # 4. 創建清理後的資料庫
    clean_database = deduplicator.create_clean_database(remove_exact_duplicates=True)
    
    # 5. 儲存清理後的資料庫
    clean_filename = f"clean_singer_keywords_database_{time.strftime('%Y%m%d_%H%M%S')}.json"
    deduplicator.save_clean_database(clean_database, clean_filename)
    
    # 6. 顯示清理後統計
    deduplicator.print_clean_statistics(clean_database)
    
    print(f"\n🎯 去重處理完成:")
    print(f"   🧹 已清理 {clean_database['deduplication_info']['removed_duplicates']} 個重複項目")
    print(f"   💾 清理後資料庫: {clean_filename}")
    print(f"   🎵 可用於搜尋的歌手: {clean_database['statistics']['total_singers']} 位")
    print(f"   🔍 搜尋關鍵字: {clean_database['statistics']['total_keywords']} 個")

if __name__ == "__main__":
    main()