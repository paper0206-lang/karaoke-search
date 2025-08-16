#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料庫一致性分析工具
分析不同來源的歌手和歌曲數量差異
"""

import json
import os
from datetime import datetime
from collections import defaultdict

class DatabaseConsistencyAnalyzer:
    def __init__(self):
        self.main_db_path = 'public/singers_data.json'
        self.checkpoint_path = 'fixed_background_checkpoint.json'
        self.old_checkpoint_path = 'background_checkpoint.json'
        
    def analyze_main_database(self):
        """分析主資料庫"""
        print("🔍 分析主資料庫 (public/singers_data.json)")
        print("=" * 50)
        
        try:
            with open(self.main_db_path, 'r', encoding='utf-8') as f:
                singers_data = json.load(f)
            
            total_singers = len(singers_data)
            total_songs = 0
            total_ktv_entries = 0
            language_stats = defaultdict(int)
            company_stats = defaultdict(int)
            songs_per_singer = []
            
            for singer_name, singer_info in singers_data.items():
                songs = singer_info.get('歌曲清單', [])
                singer_song_count = len(songs)
                songs_per_singer.append(singer_song_count)
                total_songs += singer_song_count
                
                for song in songs:
                    language = song.get('語言', '未知')
                    language_stats[language] += 1
                    
                    for code_info in song.get('編號資訊', []):
                        company = code_info.get('公司', '未知')
                        company_stats[company] += 1
                        total_ktv_entries += 1
            
            # 統計分析
            avg_songs = total_songs / total_singers if total_singers > 0 else 0
            max_songs = max(songs_per_singer) if songs_per_singer else 0
            min_songs = min(songs_per_singer) if songs_per_singer else 0
            
            print(f"📊 基本統計:")
            print(f"   總歌手數: {total_singers:,} 位")
            print(f"   總歌曲數: {total_songs:,} 首")
            print(f"   總KTV條目: {total_ktv_entries:,} 筆")
            print(f"   平均每位歌手: {avg_songs:.1f} 首歌")
            print(f"   最多歌曲歌手: {max_songs} 首")
            print(f"   最少歌曲歌手: {min_songs} 首")
            
            print(f"\n🎵 語言分布:")
            for lang, count in sorted(language_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_songs * 100) if total_songs > 0 else 0
                print(f"   {lang}: {count:,} 首 ({percentage:.1f}%)")
            
            print(f"\n🏢 KTV公司分布 (前10名):")
            for company, count in sorted(company_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                percentage = (count / total_ktv_entries * 100) if total_ktv_entries > 0 else 0
                print(f"   {company}: {count:,} 筆 ({percentage:.1f}%)")
                
            return {
                'total_singers': total_singers,
                'total_songs': total_songs,
                'total_ktv_entries': total_ktv_entries,
                'avg_songs_per_singer': avg_songs,
                'language_stats': dict(language_stats),
                'company_stats': dict(company_stats)
            }
            
        except Exception as e:
            print(f"❌ 分析主資料庫失敗: {e}")
            return None
    
    def analyze_checkpoint_data(self):
        """分析檢查點數據"""
        print(f"\n🔍 分析檢查點數據")
        print("=" * 50)
        
        checkpoint_data = {}
        
        # 分析修正版檢查點
        if os.path.exists(self.checkpoint_path):
            try:
                with open(self.checkpoint_path, 'r', encoding='utf-8') as f:
                    fixed_checkpoint = json.load(f)
                
                print(f"📋 修正版檢查點:")
                print(f"   已處理歌手: {fixed_checkpoint.get('total_processed', 0)} 位")
                
                session_stats = fixed_checkpoint.get('session_stats', {})
                print(f"   本次會話統計:")
                print(f"     處理歌手: {session_stats.get('processed_singers', 0)} 位")
                print(f"     成功處理: {session_stats.get('successful_singers', 0)} 位") 
                print(f"     新增歌曲: {session_stats.get('new_songs_added', 0)} 首")
                print(f"     Git推送: {session_stats.get('git_pushes', 0)} 次")
                
                checkpoint_data['fixed'] = fixed_checkpoint
                
            except Exception as e:
                print(f"❌ 讀取修正版檢查點失敗: {e}")
        
        # 分析舊版檢查點
        if os.path.exists(self.old_checkpoint_path):
            try:
                with open(self.old_checkpoint_path, 'r', encoding='utf-8') as f:
                    old_checkpoint = json.load(f)
                
                print(f"\n📋 舊版檢查點:")
                print(f"   已處理歌手: {old_checkpoint.get('total_processed', 0)} 位")
                
                checkpoint_data['old'] = old_checkpoint
                
            except Exception as e:
                print(f"❌ 讀取舊版檢查點失敗: {e}")
        
        return checkpoint_data
    
    def analyze_frontend_data(self):
        """分析前端相關數據"""
        print(f"\n🔍 檢查前端配置")
        print("=" * 50)
        
        # 檢查 app.py 中的統計
        if os.path.exists('app.py'):
            with open('app.py', 'r', encoding='utf-8') as f:
                app_content = f.read()
                if 'len(singers_data)' in app_content:
                    print("✅ 前端會動態計算歌手數量")
                else:
                    print("⚠️ 前端可能使用固定數量")
    
    def check_data_integrity(self, main_db_stats):
        """檢查數據完整性"""
        print(f"\n🔍 數據完整性檢查")
        print("=" * 50)
        
        issues = []
        
        try:
            with open(self.main_db_path, 'r', encoding='utf-8') as f:
                singers_data = json.load(f)
            
            # 檢查空歌單歌手
            empty_singers = []
            incomplete_singers = []
            
            for singer_name, singer_info in singers_data.items():
                songs = singer_info.get('歌曲清單', [])
                
                if len(songs) == 0:
                    empty_singers.append(singer_name)
                elif len(songs) < 5:  # 歌曲數量過少可能表示數據不完整
                    incomplete_singers.append((singer_name, len(songs)))
            
            if empty_singers:
                issues.append(f"發現 {len(empty_singers)} 位歌手沒有歌曲")
                print(f"⚠️ 空歌單歌手: {len(empty_singers)} 位")
                if len(empty_singers) <= 10:
                    print(f"   示例: {', '.join(empty_singers[:5])}")
            
            if incomplete_singers:
                issues.append(f"發現 {len(incomplete_singers)} 位歌手歌曲數量過少")
                print(f"⚠️ 歌曲數量過少歌手: {len(incomplete_singers)} 位")
                incomplete_singers.sort(key=lambda x: x[1])
                if len(incomplete_singers) <= 10:
                    for singer, count in incomplete_singers[:5]:
                        print(f"   {singer}: {count} 首")
            
            # 檢查重複歌曲
            all_songs = {}
            duplicate_songs = []
            
            for singer_name, singer_info in singers_data.items():
                for song in singer_info.get('歌曲清單', []):
                    song_key = f"{song.get('歌名', '')}_{song.get('歌手', '')}"
                    if song_key in all_songs:
                        duplicate_songs.append(song_key)
                    else:
                        all_songs[song_key] = singer_name
            
            if duplicate_songs:
                issues.append(f"發現 {len(duplicate_songs)} 首重複歌曲")
                print(f"⚠️ 重複歌曲: {len(duplicate_songs)} 首")
            
            if not issues:
                print("✅ 未發現明顯的數據完整性問題")
            
            return issues
            
        except Exception as e:
            error_msg = f"數據完整性檢查失敗: {e}"
            issues.append(error_msg)
            print(f"❌ {error_msg}")
            return issues
    
    def compare_data_sources(self, main_db_stats, checkpoint_data):
        """比較不同數據來源的差異"""
        print(f"\n🔍 數據來源比較")
        print("=" * 50)
        
        inconsistencies = []
        
        if main_db_stats and 'fixed' in checkpoint_data:
            fixed_stats = checkpoint_data['fixed'].get('session_stats', {})
            
            print(f"📊 主資料庫 vs 修正版檢查點:")
            print(f"   主資料庫歌手數: {main_db_stats['total_singers']:,}")
            print(f"   檢查點處理數: {fixed_stats.get('processed_singers', 0):,}")
            print(f"   檢查點新增歌曲: {fixed_stats.get('new_songs_added', 0):,}")
            
            # 檢查邏輯一致性
            if fixed_stats.get('new_songs_added', 0) > main_db_stats['total_songs'] * 0.5:
                inconsistencies.append("檢查點顯示的新增歌曲數量異常高")
        
        return inconsistencies
    
    def generate_report(self):
        """生成完整的一致性報告"""
        print("🔍 資料庫一致性分析報告")
        print("=" * 60)
        print(f"分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 主資料庫分析
        main_db_stats = self.analyze_main_database()
        
        # 檢查點分析
        checkpoint_data = self.analyze_checkpoint_data()
        
        # 前端數據檢查
        self.analyze_frontend_data()
        
        # 數據完整性檢查
        integrity_issues = self.check_data_integrity(main_db_stats) if main_db_stats else []
        
        # 數據來源比較
        inconsistencies = self.compare_data_sources(main_db_stats, checkpoint_data)
        
        # 生成總結
        print(f"\n📋 分析總結")
        print("=" * 50)
        
        if main_db_stats:
            print(f"✅ 主資料庫狀態良好")
            print(f"   - {main_db_stats['total_singers']:,} 位歌手")
            print(f"   - {main_db_stats['total_songs']:,} 首歌曲")
            print(f"   - {main_db_stats['total_ktv_entries']:,} 筆KTV資料")
        
        if integrity_issues:
            print(f"\n⚠️ 發現 {len(integrity_issues)} 個數據完整性問題:")
            for issue in integrity_issues:
                print(f"   - {issue}")
        
        if inconsistencies:
            print(f"\n⚠️ 發現 {len(inconsistencies)} 個數據一致性問題:")
            for issue in inconsistencies:
                print(f"   - {issue}")
        
        if not integrity_issues and not inconsistencies:
            print(f"\n✅ 數據一致性良好，未發現重大問題")
        
        return {
            'main_db_stats': main_db_stats,
            'checkpoint_data': checkpoint_data,
            'integrity_issues': integrity_issues,
            'inconsistencies': inconsistencies
        }

def main():
    analyzer = DatabaseConsistencyAnalyzer()
    report = analyzer.generate_report()
    
    # 保存報告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"database_consistency_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 詳細報告已保存至: {report_file}")

if __name__ == "__main__":
    main()