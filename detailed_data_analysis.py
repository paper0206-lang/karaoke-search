#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細數據分析工具
深入分析數據質量和不一致問題
"""

import json
import random
from collections import Counter

def analyze_singer_distribution():
    """分析歌手歌曲數量分布"""
    print("🔍 詳細歌手數據分布分析")
    print("=" * 50)
    
    with open('public/singers_data.json', 'r', encoding='utf-8') as f:
        singers_data = json.load(f)
    
    song_counts = []
    empty_singers = []
    sample_singers = {}
    
    for singer_name, singer_info in singers_data.items():
        songs = singer_info.get('歌曲清單', [])
        song_count = len(songs)
        song_counts.append(song_count)
        
        if song_count == 0:
            empty_singers.append(singer_name)
        
        # 取樣不同歌曲數量的歌手
        if song_count in [0, 1, 5, 10, 20, 50] and len(sample_singers.get(song_count, [])) < 3:
            if song_count not in sample_singers:
                sample_singers[song_count] = []
            sample_singers[song_count].append(singer_name)
    
    # 統計分布
    distribution = Counter(song_counts)
    
    print(f"📊 歌曲數量分布:")
    print(f"   0首: {distribution[0]:,} 位歌手 ({distribution[0]/len(singers_data)*100:.1f}%)")
    print(f"   1首: {distribution[1]:,} 位歌手 ({distribution[1]/len(singers_data)*100:.1f}%)")
    print(f"   2-5首: {sum(distribution[i] for i in range(2, 6)):,} 位歌手")
    print(f"   6-10首: {sum(distribution[i] for i in range(6, 11)):,} 位歌手")
    print(f"   11-20首: {sum(distribution[i] for i in range(11, 21)):,} 位歌手")
    print(f"   21-50首: {sum(distribution[i] for i in range(21, 51)):,} 位歌手")
    print(f"   50+首: {sum(distribution[i] for i in range(51, max(song_counts)+1)):,} 位歌手")
    
    print(f"\n📋 樣本歌手檢查:")
    for count in sorted(sample_singers.keys()):
        print(f"   {count}首歌歌手示例: {', '.join(sample_singers[count][:3])}")
    
    return {
        'distribution': dict(distribution),
        'empty_singers': empty_singers,
        'total_singers': len(singers_data)
    }

def check_recent_updates():
    """檢查最近的更新情況"""
    print(f"\n🔍 檢查最近更新狀況")
    print("=" * 50)
    
    # 檢查修正版檢查點中已處理的歌手
    try:
        with open('fixed_background_checkpoint.json', 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        
        processed_singers = checkpoint.get('processed_singers', [])
        print(f"✅ 已處理歌手: {len(processed_singers)} 位")
        
        # 檢查這些歌手在主資料庫中的狀況
        with open('public/singers_data.json', 'r', encoding='utf-8') as f:
            singers_data = json.load(f)
        
        print(f"\n📊 已處理歌手的歌曲數量:")
        processed_song_counts = []
        for singer in processed_singers[-10:]:  # 檢查最後10位
            if singer in singers_data:
                song_count = len(singers_data[singer].get('歌曲清單', []))
                processed_song_counts.append(song_count)
                print(f"   {singer}: {song_count} 首")
        
        if processed_song_counts:
            avg_processed = sum(processed_song_counts) / len(processed_song_counts)
            print(f"\n📈 最近處理歌手平均歌曲數: {avg_processed:.1f} 首")
        
        return processed_singers
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        return []

def find_data_inconsistencies():
    """尋找數據不一致的問題"""
    print(f"\n🔍 尋找數據不一致問題")
    print("=" * 50)
    
    with open('public/singers_data.json', 'r', encoding='utf-8') as f:
        singers_data = json.load(f)
    
    issues = []
    
    # 檢查知名歌手的歌曲數量
    famous_singers = ['周杰倫', '蔡依林', '五月天', '林俊傑', '張惠妹', '王力宏', '林宥嘉', '孫燕姿']
    
    print(f"🎤 知名歌手歌曲數量檢查:")
    for singer in famous_singers:
        if singer in singers_data:
            song_count = len(singers_data[singer].get('歌曲清單', []))
            print(f"   {singer}: {song_count} 首")
            
            # 知名歌手歌曲數量異常少可能表示數據不完整
            if song_count < 10:
                issues.append(f"{singer}歌曲數量異常少 ({song_count}首)")
        else:
            print(f"   {singer}: 未找到")
            issues.append(f"{singer}未在資料庫中")
    
    # 檢查盧廣仲（基準歌手）
    if '盧廣仲' in singers_data:
        lu_songs = len(singers_data['盧廣仲'].get('歌曲清單', []))
        print(f"\n🎯 基準歌手盧廣仲: {lu_songs} 首歌")
        if lu_songs != 12:
            issues.append(f"盧廣仲歌曲數量不是預期的12首 (實際:{lu_songs}首)")
    
    return issues

def analyze_data_growth():
    """分析數據增長模式"""
    print(f"\n🔍 分析數據增長模式")
    print("=" * 50)
    
    # 比較爬蟲報告的數字
    try:
        with open('fixed_background_checkpoint.json', 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        
        session_stats = checkpoint.get('session_stats', {})
        processed = session_stats.get('processed_singers', 0)
        successful = session_stats.get('successful_singers', 0)
        new_songs = session_stats.get('new_songs_added', 0)
        
        print(f"📈 爬蟲會話統計:")
        print(f"   處理歌手: {processed} 位")
        print(f"   成功處理: {successful} 位")
        print(f"   新增歌曲: {new_songs} 首")
        
        if successful > 0:
            avg_songs_per_successful = new_songs / successful
            print(f"   平均每位成功歌手新增: {avg_songs_per_successful:.1f} 首")
        
        # 計算理論vs實際
        print(f"\n🧮 數據一致性分析:")
        print(f"   理論上50位歌手應該增加的歌曲數: {new_songs}")
        print(f"   實際新增比例: {new_songs/12801*100:.2f}% (of total database)")
        
        return {
            'processed': processed,
            'successful': successful,
            'new_songs': new_songs
        }
        
    except Exception as e:
        print(f"❌ 分析失敗: {e}")
        return None

def main():
    print("🔍 深度數據分析報告")
    print("=" * 60)
    
    # 分析歌手分布
    distribution_analysis = analyze_singer_distribution()
    
    # 檢查最近更新
    recent_updates = check_recent_updates()
    
    # 尋找不一致問題
    inconsistencies = find_data_inconsistencies()
    
    # 分析數據增長
    growth_analysis = analyze_data_growth()
    
    print(f"\n🎯 關鍵發現總結")
    print("=" * 50)
    
    # 計算數據質量指標
    total_singers = distribution_analysis['total_singers']
    empty_singers = len(distribution_analysis['empty_singers'])
    low_quality_singers = sum(count for songs, count in distribution_analysis['distribution'].items() if songs < 5)
    
    print(f"📊 數據質量指標:")
    print(f"   總歌手數: {total_singers:,}")
    print(f"   空歌單歌手: {empty_singers:,} ({empty_singers/total_singers*100:.1f}%)")
    print(f"   低質量歌手(<5首): {low_quality_singers:,} ({low_quality_singers/total_singers*100:.1f}%)")
    print(f"   高質量歌手(≥5首): {total_singers-low_quality_singers:,} ({(total_singers-low_quality_singers)/total_singers*100:.1f}%)")
    
    if inconsistencies:
        print(f"\n⚠️ 發現的問題:")
        for issue in inconsistencies:
            print(f"   - {issue}")
    
    # 給出建議
    print(f"\n💡 建議:")
    if low_quality_singers / total_singers > 0.8:
        print("   - 大量歌手數據不完整，建議優先處理知名歌手")
        print("   - 考慮實施數據質量閾值，專注於有意義的歌手")
    
    if growth_analysis and growth_analysis['new_songs'] > 1000:
        print("   - 爬蟲系統運行良好，持續增加高質量數據")
    
    print("   - 建議建立數據質量監控機制")
    print("   - 考慮實施分層處理策略：知名歌手優先")

if __name__ == "__main__":
    main()