#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌手資料驗證和重複檢查工具
確保數據品質和完整性，避免重複下載
"""

import json
import os
from datetime import datetime
from collections import defaultdict, Counter
import difflib

class SingerDataValidator:
    def __init__(self):
        self.singers_data = {}
        self.songs_data = []
        self.validation_results = {
            'duplicates': [],
            'missing_data': [],
            'inconsistencies': [],
            'quality_issues': []
        }
        
        print("🔍 歌手資料驗證工具")
        print("=" * 50)
        
    def load_data(self):
        """載入資料庫進行驗證"""
        try:
            # 載入歌手資料庫
            with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                self.singers_data = json.load(f)
            print(f"✅ 載入歌手資料庫: {len(self.singers_data):,} 位歌手")
            
            # 載入完整歌曲資料庫
            with open('public/songs_simplified.json', 'r', encoding='utf-8') as f:
                self.songs_data = json.load(f)
            print(f"✅ 載入完整歌曲資料庫: {len(self.songs_data):,} 首歌")
            
            return True
            
        except Exception as e:
            print(f"❌ 載入資料失敗: {e}")
            return False
    
    def check_singer_duplicates(self):
        """檢查歌手名稱重複和相似度"""
        print("\n🔍 檢查歌手重複...")
        
        singer_names = list(self.singers_data.keys())
        duplicates = []
        similar_pairs = []
        
        # 檢查完全重複
        name_counts = Counter(singer_names)
        for name, count in name_counts.items():
            if count > 1:
                duplicates.append((name, count))
        
        # 檢查相似名稱 (可能是不同編碼或格式)
        for i, name1 in enumerate(singer_names):
            for name2 in singer_names[i+1:]:
                similarity = difflib.SequenceMatcher(None, name1, name2).ratio()
                if similarity > 0.85 and similarity < 1.0:  # 高度相似但不完全相同
                    similar_pairs.append((name1, name2, similarity))
        
        self.validation_results['duplicates'].extend([
            {'type': 'exact_duplicate', 'singer': name, 'count': count} 
            for name, count in duplicates
        ])
        
        self.validation_results['duplicates'].extend([
            {'type': 'similar_names', 'singer1': name1, 'singer2': name2, 'similarity': sim}
            for name1, name2, sim in similar_pairs
        ])
        
        print(f"   完全重複歌手: {len(duplicates)} 組")
        print(f"   相似名稱歌手: {len(similar_pairs)} 對")
        
        return duplicates, similar_pairs
    
    def check_song_duplicates_within_singer(self):
        """檢查單一歌手內的歌曲重複"""
        print("\n🔍 檢查歌手內部歌曲重複...")
        
        duplicates_found = 0
        
        for singer_name, singer_info in self.singers_data.items():
            songs = singer_info.get('歌曲清單', [])
            song_titles = [song.get('歌名', '') for song in songs]
            
            # 檢查完全重複的歌曲名稱
            title_counts = Counter(song_titles)
            singer_duplicates = [(title, count) for title, count in title_counts.items() if count > 1]
            
            if singer_duplicates:
                duplicates_found += len(singer_duplicates)
                self.validation_results['duplicates'].append({
                    'type': 'song_duplicate_within_singer',
                    'singer': singer_name,
                    'duplicates': singer_duplicates
                })
        
        print(f"   發現重複歌曲: {duplicates_found} 組")
        return duplicates_found
    
    def check_data_completeness(self):
        """檢查數據完整性"""
        print("\n🔍 檢查數據完整性...")
        
        missing_language = 0
        missing_codes = 0
        incomplete_singers = []
        
        for singer_name, singer_info in self.singers_data.items():
            songs = singer_info.get('歌曲清單', [])
            
            if not songs:
                incomplete_singers.append(singer_name)
                continue
            
            singer_missing_lang = 0
            singer_missing_codes = 0
            
            for song in songs:
                # 檢查語言標記
                if not song.get('語言'):
                    missing_language += 1
                    singer_missing_lang += 1
                
                # 檢查KTV編號
                codes = song.get('編號資訊', [])
                if not codes:
                    missing_codes += 1
                    singer_missing_codes += 1
                else:
                    # 檢查編號完整性
                    for code in codes:
                        if not code.get('公司') or not code.get('編號'):
                            singer_missing_codes += 1
            
            # 記錄問題較多的歌手
            if singer_missing_lang / len(songs) > 0.3 or singer_missing_codes / len(songs) > 0.1:
                self.validation_results['missing_data'].append({
                    'singer': singer_name,
                    'total_songs': len(songs),
                    'missing_language': singer_missing_lang,
                    'missing_codes': singer_missing_codes
                })
        
        print(f"   缺少語言標記: {missing_language:,} 首歌")
        print(f"   缺少KTV編號: {missing_codes:,} 首歌")
        print(f"   無歌曲歌手: {len(incomplete_singers)} 位")
        
        return {
            'missing_language': missing_language,
            'missing_codes': missing_codes,
            'empty_singers': incomplete_singers
        }
    
    def check_cross_database_consistency(self):
        """檢查歌手資料庫與完整歌曲資料庫的一致性"""
        print("\n🔍 檢查跨資料庫一致性...")
        
        # 建立完整資料庫的歌手-歌曲索引
        songs_by_singer = defaultdict(set)
        for song in self.songs_data:
            singer = song.get('歌手', '')
            title = song.get('歌名', '')
            if singer and title:
                songs_by_singer[singer].add(title)
        
        inconsistencies = []
        missing_in_songs_db = 0
        missing_in_singers_db = 0
        
        # 檢查歌手資料庫中的歌曲是否在完整資料庫中
        for singer_name, singer_info in self.singers_data.items():
            singer_songs = set(song.get('歌名', '') for song in singer_info.get('歌曲清單', []))
            db_songs = songs_by_singer.get(singer_name, set())
            
            only_in_singer = singer_songs - db_songs
            only_in_db = db_songs - singer_songs
            
            if only_in_singer or only_in_db:
                inconsistency = {
                    'singer': singer_name,
                    'only_in_singer_db': list(only_in_singer),
                    'only_in_songs_db': list(only_in_db),
                    'common_songs': len(singer_songs.intersection(db_songs))
                }
                inconsistencies.append(inconsistency)
                missing_in_songs_db += len(only_in_singer)
                missing_in_singers_db += len(only_in_db)
        
        self.validation_results['inconsistencies'].extend(inconsistencies)
        
        print(f"   不一致的歌手: {len(inconsistencies)} 位")
        print(f"   歌手DB獨有歌曲: {missing_in_songs_db} 首")
        print(f"   完整DB獨有歌曲: {missing_in_singers_db} 首")
        
        return inconsistencies
    
    def check_data_quality(self):
        """檢查數據品質問題"""
        print("\n🔍 檢查數據品質...")
        
        quality_issues = []
        
        for singer_name, singer_info in self.singers_data.items():
            songs = singer_info.get('歌曲清單', [])
            
            for song in songs:
                issues = []
                
                # 檢查歌名
                title = song.get('歌名', '')
                if not title or len(title.strip()) == 0:
                    issues.append('空白歌名')
                elif len(title) > 100:
                    issues.append('歌名過長')
                
                # 檢查編號格式
                codes = song.get('編號資訊', [])
                for code in codes:
                    company = code.get('公司', '')
                    number = code.get('編號', '')
                    
                    if company and not number:
                        issues.append(f'{company}編號為空')
                    elif number and len(number) > 20:
                        issues.append(f'{company}編號過長')
                
                # 檢查語言標記
                lang = song.get('語言', '')
                if lang and lang not in ['國', '台', '英', '客', '粵', '日', '韓', '山', '兒']:
                    issues.append(f'異常語言標記: {lang}')
                
                if issues:
                    quality_issues.append({
                        'singer': singer_name,
                        'song': title,
                        'issues': issues
                    })
        
        self.validation_results['quality_issues'].extend(quality_issues)
        
        print(f"   品質問題: {len(quality_issues)} 項")
        
        return quality_issues
    
    def suggest_updates_needed(self):
        """根據驗證結果建議需要更新的歌手"""
        print("\n💡 建議更新歌手清單...")
        
        update_suggestions = []
        
        # 基於缺失數據建議更新
        for item in self.validation_results['missing_data']:
            singer = item['singer']
            total = item['total_songs']
            missing_lang = item['missing_language']
            missing_codes = item['missing_codes']
            
            priority = 'high' if missing_codes / total > 0.2 else 'medium'
            
            update_suggestions.append({
                'singer': singer,
                'priority': priority,
                'reason': f'缺少語言標記{missing_lang}首，缺少編號{missing_codes}首',
                'recommendation': '重新爬取補全資料'
            })
        
        # 基於不一致性建議更新
        for item in self.validation_results['inconsistencies']:
            if len(item['only_in_songs_db']) > 5:  # 完整資料庫有很多歌手資料庫沒有的歌曲
                update_suggestions.append({
                    'singer': item['singer'],
                    'priority': 'high',
                    'reason': f'完整資料庫有額外{len(item["only_in_songs_db"])}首歌',
                    'recommendation': '重新爬取整合資料'
                })
        
        # 按優先級排序
        update_suggestions.sort(key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
        
        print(f"   建議更新歌手: {len(update_suggestions)} 位")
        print(f"   高優先級: {sum(1 for s in update_suggestions if s['priority'] == 'high')} 位")
        print(f"   中優先級: {sum(1 for s in update_suggestions if s['priority'] == 'medium')} 位")
        
        return update_suggestions
    
    def generate_validation_report(self):
        """生成完整的驗證報告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 執行所有檢查
        if not self.load_data():
            return None
        
        print("\n🔍 執行完整數據驗證...")
        
        self.check_singer_duplicates()
        self.check_song_duplicates_within_singer()
        completeness = self.check_data_completeness()
        self.check_cross_database_consistency()
        self.check_data_quality()
        suggestions = self.suggest_updates_needed()
        
        # 生成報告
        report = {
            'validation_date': datetime.now().isoformat(),
            'database_stats': {
                'total_singers': len(self.singers_data),
                'total_songs_in_singers_db': sum(len(info.get('歌曲清單', [])) for info in self.singers_data.values()),
                'total_songs_in_songs_db': len(self.songs_data)
            },
            'validation_results': self.validation_results,
            'completeness_stats': completeness,
            'update_suggestions': suggestions,
            'summary': {
                'duplicates_found': len(self.validation_results['duplicates']),
                'missing_data_issues': len(self.validation_results['missing_data']),
                'inconsistencies_found': len(self.validation_results['inconsistencies']),
                'quality_issues': len(self.validation_results['quality_issues']),
                'singers_need_update': len(suggestions)
            }
        }
        
        # 保存報告
        report_file = f"validation_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 顯示摘要
        print(f"\n" + "="*70)
        print("📊 數據驗證報告摘要")
        print("="*70)
        print(f"📁 報告文件: {report_file}")
        print(f"🎤 總歌手數: {report['database_stats']['total_singers']:,}")
        print(f"🎵 歌手DB歌曲數: {report['database_stats']['total_songs_in_singers_db']:,}")
        print(f"🎵 完整DB歌曲數: {report['database_stats']['total_songs_in_songs_db']:,}")
        print()
        print(f"⚠️ 發現問題:")
        print(f"   重複項目: {report['summary']['duplicates_found']}")
        print(f"   缺失數據: {report['summary']['missing_data_issues']}")
        print(f"   不一致項: {report['summary']['inconsistencies_found']}")
        print(f"   品質問題: {report['summary']['quality_issues']}")
        print()
        print(f"💡 建議更新歌手: {report['summary']['singers_need_update']} 位")
        
        return report

def main():
    """主程序"""
    validator = SingerDataValidator()
    
    try:
        report = validator.generate_validation_report()
        
        if report:
            print(f"\n✅ 驗證完成！")
            print(f"📄 詳細報告已保存")
        else:
            print(f"\n❌ 驗證失敗")
    
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()