#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全資料庫需處理歌手分析
分析整個資料庫中有多少歌手需要達到95%基準
"""

import json
from collections import defaultdict

def check_singer_against_benchmark(singer_name, singer_info, benchmark_threshold=0.95):
    """檢查歌手是否達到95%基準標準"""
    songs = singer_info.get('歌曲清單', [])
    
    if not songs:
        return {
            'meets_benchmark': False,
            'needs_processing': True,
            'current_songs': 0,
            'benchmark_score': 0.0,
            'gaps': ['no_songs']
        }
    
    # 計算各項指標
    total_songs = len(songs)
    companies_covered = set()
    taiwan_songs = 0
    mandarin_songs = 0
    
    for song in songs:
        language = song.get('語言', '')
        if language == '台':
            taiwan_songs += 1
        elif language == '國':
            mandarin_songs += 1
        
        for code_info in song.get('編號資訊', []):
            company = code_info.get('公司', '')
            if company:
                companies_covered.add(company)
    
    # 計算基準得分（與修正版爬蟲相同的邏輯）
    lu_benchmark = {
        'total_songs': 12,
        'companies_covered': 16
    }
    
    scores = {
        'song_count': min(total_songs / lu_benchmark['total_songs'], 1.0),
        'company_coverage': len(companies_covered) / lu_benchmark['companies_covered'],
        'language_diversity': 1.0 if (taiwan_songs > 0 and mandarin_songs > 0) else 0.5
    }
    
    overall_score = sum(scores.values()) / len(scores)
    
    # 95%基準檢查
    meets_benchmark = overall_score >= benchmark_threshold
    needs_processing = overall_score < benchmark_threshold
    
    # 識別缺口
    gaps = []
    if total_songs < lu_benchmark['total_songs']:
        gaps.append(f'songs_insufficient_{total_songs}')
    if len(companies_covered) < 12:  # 至少12家KTV覆蓋
        gaps.append(f'company_coverage_low_{len(companies_covered)}')
    if taiwan_songs == 0 and mandarin_songs > 0:
        gaps.append('missing_taiwanese_songs')
    
    return {
        'meets_benchmark': meets_benchmark,
        'needs_processing': needs_processing,
        'current_songs': total_songs,
        'companies_covered': len(companies_covered),
        'benchmark_score': overall_score,
        'gaps': gaps,
        'taiwan_songs': taiwan_songs,
        'mandarin_songs': mandarin_songs
    }

def analyze_all_singers():
    """分析所有歌手的基準狀態"""
    print("🔍 全資料庫95%基準分析")
    print("=" * 60)
    
    with open('public/singers_data.json', 'r', encoding='utf-8') as f:
        singers_data = json.load(f)
    
    total_singers = len(singers_data)
    needs_processing = []
    already_meets_benchmark = []
    score_distribution = defaultdict(int)
    
    print(f"📊 分析 {total_singers:,} 位歌手...")
    
    # 移除盧廣仲（基準歌手）
    analysis_singers = {k: v for k, v in singers_data.items() if k != '盧廣仲'}
    
    for i, (singer_name, singer_info) in enumerate(analysis_singers.items(), 1):
        if i % 500 == 0:
            print(f"   進度: {i:,}/{len(analysis_singers):,}")
        
        benchmark_result = check_singer_against_benchmark(singer_name, singer_info)
        
        # 分數分布統計
        score_range = int(benchmark_result['benchmark_score'] * 10) * 10
        score_distribution[score_range] += 1
        
        if benchmark_result['needs_processing']:
            needs_processing.append({
                'name': singer_name,
                'score': benchmark_result['benchmark_score'],
                'songs': benchmark_result['current_songs'],
                'companies': benchmark_result['companies_covered'],
                'gaps': benchmark_result['gaps']
            })
        else:
            already_meets_benchmark.append({
                'name': singer_name,
                'score': benchmark_result['benchmark_score'],
                'songs': benchmark_result['current_songs']
            })
    
    print(f"\n📋 基準分析結果:")
    print(f"   總歌手數 (排除盧廣仲): {len(analysis_singers):,} 位")
    print(f"   需要處理: {len(needs_processing):,} 位 ({len(needs_processing)/len(analysis_singers)*100:.1f}%)")
    print(f"   已達標準: {len(already_meets_benchmark):,} 位 ({len(already_meets_benchmark)/len(analysis_singers)*100:.1f}%)")
    
    # 分析需要處理的歌手分布
    print(f"\n📊 需處理歌手分數分布:")
    needs_processing.sort(key=lambda x: x['score'], reverse=True)
    
    score_ranges = {
        '90-95%': [s for s in needs_processing if 0.90 <= s['score'] < 0.95],
        '80-90%': [s for s in needs_processing if 0.80 <= s['score'] < 0.90],
        '70-80%': [s for s in needs_processing if 0.70 <= s['score'] < 0.80],
        '60-70%': [s for s in needs_processing if 0.60 <= s['score'] < 0.70],
        '50-60%': [s for s in needs_processing if 0.50 <= s['score'] < 0.60],
        '<50%': [s for s in needs_processing if s['score'] < 0.50]
    }
    
    for range_name, singers in score_ranges.items():
        if singers:
            print(f"   {range_name}: {len(singers):,} 位")
            # 顯示每個範圍的前3位歌手示例
            for singer in singers[:3]:
                print(f"      {singer['name']}: {singer['score']:.1%} ({singer['songs']}首)")
    
    # 分析歌曲數量分布
    print(f"\n📈 需處理歌手歌曲數量分布:")
    song_count_ranges = {
        '0首': [s for s in needs_processing if s['songs'] == 0],
        '1首': [s for s in needs_processing if s['songs'] == 1],
        '2-5首': [s for s in needs_processing if 2 <= s['songs'] <= 5],
        '6-10首': [s for s in needs_processing if 6 <= s['songs'] <= 10],
        '11-20首': [s for s in needs_processing if 11 <= s['songs'] <= 20],
        '21+首': [s for s in needs_processing if s['songs'] >= 21]
    }
    
    for range_name, singers in song_count_ranges.items():
        if singers:
            print(f"   {range_name}: {len(singers):,} 位")
    
    # 檢查已處理的歌手
    try:
        with open('fixed_background_checkpoint.json', 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        processed_singers = set(checkpoint.get('processed_singers', []))
        
        remaining_to_process = [s for s in needs_processing if s['name'] not in processed_singers]
        
        print(f"\n🎯 處理進度:")
        print(f"   總需處理: {len(needs_processing):,} 位")
        print(f"   已處理: {len(processed_singers):,} 位")
        print(f"   剩餘待處理: {len(remaining_to_process):,} 位")
        print(f"   完成率: {len(processed_singers)/len(needs_processing)*100:.1f}%")
        
    except Exception as e:
        print(f"❌ 無法讀取檢查點: {e}")
        remaining_to_process = needs_processing
    
    # 優先級分析
    print(f"\n🏆 高優先級歌手 (分數80%以上):")
    high_priority = [s for s in needs_processing if s['score'] >= 0.8 and s['name'] not in processed_singers]
    high_priority.sort(key=lambda x: x['score'], reverse=True)
    
    for singer in high_priority[:10]:
        print(f"   {singer['name']}: {singer['score']:.1%} ({singer['songs']}首, {singer['companies']}家KTV)")
    
    return {
        'total_singers': len(analysis_singers),
        'needs_processing': len(needs_processing),
        'already_meets_benchmark': len(already_meets_benchmark),
        'remaining_to_process': len(remaining_to_process) if 'remaining_to_process' in locals() else len(needs_processing),
        'high_priority': len(high_priority) if 'high_priority' in locals() else 0,
        'score_ranges': {k: len(v) for k, v in score_ranges.items()},
        'song_count_ranges': {k: len(v) for k, v in song_count_ranges.items()}
    }

def estimate_processing_time(remaining_singers):
    """估算處理時間"""
    print(f"\n⏱️ 處理時間估算:")
    print("=" * 50)
    
    # 基於當前爬蟲速度的估算
    current_rate = 55 / 4  # 4小時處理55位 = 13.75位/小時
    
    hours_needed = remaining_singers / current_rate
    days_needed = hours_needed / 24
    
    print(f"   剩餘歌手: {remaining_singers:,} 位")
    print(f"   當前速度: {current_rate:.1f} 位/小時")
    print(f"   預估時間: {hours_needed:.1f} 小時 ({days_needed:.1f} 天)")
    
    # 分批次估算
    batch_size = 200  # 當前設定的批次大小
    batches_needed = (remaining_singers + batch_size - 1) // batch_size
    
    print(f"   需要批次: {batches_needed} 批 (每批{batch_size}位)")
    print(f"   每批預估: {batch_size/current_rate:.1f} 小時")

def main():
    result = analyze_all_singers()
    estimate_processing_time(result['remaining_to_process'])
    
    print(f"\n🎯 總結:")
    print("=" * 50)
    print(f"✅ 分析完成：共有 {result['needs_processing']:,} 位歌手需要處理")
    print(f"📊 完成率：{((result['needs_processing'] - result['remaining_to_process'])/result['needs_processing']*100):.1f}%")
    print(f"🎵 高優先級：{result['high_priority']:,} 位歌手分數在80%以上")
    print(f"⚡ 目前策略：每次處理200位，按歌曲數量排序")

if __name__ == "__main__":
    main()