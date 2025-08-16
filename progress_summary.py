#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
進度總結報告生成器
分析當前大規模爬取的進度和成果
"""

import json
import os
from datetime import datetime
import glob

def analyze_mass_scraping_progress():
    """分析大規模爬取進度"""
    print("📊 大規模歌手爬取進度分析")
    print("=" * 40)
    
    results_dir = "mass_scraping_results"
    
    if not os.path.exists(results_dir):
        print("❌ 找不到結果目錄")
        return
    
    # 收集批次進度檔案
    batch_files = glob.glob(f"{results_dir}/batch_*_progress.json")
    batch_files.sort()
    
    print(f"📁 找到 {len(batch_files)} 個批次進度檔案")
    
    all_results = []
    overall_stats = {}
    
    for batch_file in batch_files:
        try:
            with open(batch_file, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
            
            batch_results = batch_data.get('batch_results', [])
            all_results.extend(batch_results)
            overall_stats = batch_data.get('overall_stats', {})
            
            print(f"   ✅ 批次 {batch_data.get('batch_number', '?')}: {len(batch_results)} 位歌手")
            
        except Exception as e:
            print(f"   ❌ 讀取 {batch_file} 失敗: {e}")
    
    if not all_results:
        print("⚠️ 沒有找到處理結果")
        return
    
    # 分析結果
    print(f"\n📈 總體結果分析:")
    print(f"   總處理歌手: {len(all_results)} 位")
    
    # 按狀態分類
    status_counts = {}
    successful_results = []
    benchmark_achieved = []
    total_new_songs = 0
    total_updated_songs = 0
    
    for result in all_results:
        status = result.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
        
        if status == 'processed':
            successful_results.append(result)
            total_new_songs += result.get('new_songs', 0)
            total_updated_songs += result.get('updated_songs', 0)
            
            if result.get('meets_benchmark_now', False):
                benchmark_achieved.append(result)
    
    print(f"\n🎯 處理狀態統計:")
    for status, count in status_counts.items():
        percentage = count / len(all_results) * 100
        status_emoji = {
            'processed': '✅',
            'no_data': '❌',
            'already_complete': '📋',
            'failed': '💥'
        }.get(status, '❓')
        print(f"   {status_emoji} {status:15s}: {count:3d} 位 ({percentage:5.1f}%)")
    
    print(f"\n🎵 歌曲統計:")
    print(f"   新增歌曲: {total_new_songs:,} 首")
    print(f"   更新歌曲: {total_updated_songs:,} 首")
    print(f"   總計增加: {total_new_songs + total_updated_songs:,} 首")
    
    print(f"\n🎖️ 基準達成:")
    print(f"   達到盧廣仲基準: {len(benchmark_achieved)} 位")
    if successful_results:
        achievement_rate = len(benchmark_achieved) / len(successful_results) * 100
        print(f"   基準達成率: {achievement_rate:.1f}%")
    
    # 最佳表現歌手
    if successful_results:
        print(f"\n🏆 最佳表現歌手 (按新增歌曲排序):")
        top_performers = sorted(successful_results, 
                              key=lambda x: x.get('new_songs', 0), reverse=True)
        
        for i, result in enumerate(top_performers[:10], 1):
            singer = result.get('singer', '未知')
            new_songs = result.get('new_songs', 0)
            companies = result.get('companies_found', 0)
            benchmark_before = result.get('benchmark_before', 0) * 100
            benchmark_after = result.get('benchmark_after', 0) * 100
            benchmark_icon = "🎯" if result.get('meets_benchmark_now', False) else "📈"
            
            print(f"   {i:2d}. {benchmark_icon} {singer:15s}: +{new_songs:3d}首 "
                  f"({companies}家KTV) {benchmark_before:4.1f}% → {benchmark_after:4.1f}%")
    
    # 時間統計
    if overall_stats.get('start_time'):
        try:
            start_time = datetime.fromisoformat(overall_stats['start_time'])
            elapsed = datetime.now() - start_time
            print(f"\n⏱️ 執行統計:")
            print(f"   開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   執行時長: {elapsed}")
            if successful_results:
                songs_per_hour = (total_new_songs + total_updated_songs) / (elapsed.total_seconds() / 3600)
                print(f"   效率: {songs_per_hour:.0f} 首歌/小時")
        except:
            pass
    
    # 建議下一步
    print(f"\n💡 建議下一步:")
    
    no_data_count = status_counts.get('no_data', 0)
    if no_data_count > len(all_results) * 0.3:
        print("   ⚠️ 很多歌手沒有找到Taiwan Song King資料")
        print("   🔄 可能需要嘗試其他搜尋策略或資料來源")
    
    if len(benchmark_achieved) < len(successful_results) * 0.7:
        print("   📈 部分歌手仍未達到基準標準")
        print("   🎯 可考慮再次處理或調整基準標準")
    
    if len(successful_results) > 0:
        print("   ✅ 有成功案例，系統運作正常")
        print("   🚀 可繼續處理更多歌手")
    
    # 生成詳細報告
    report_data = {
        'analysis_time': datetime.now().isoformat(),
        'total_singers_processed': len(all_results),
        'status_breakdown': status_counts,
        'song_statistics': {
            'new_songs': total_new_songs,
            'updated_songs': total_updated_songs,
            'total_additions': total_new_songs + total_updated_songs
        },
        'benchmark_achievement': {
            'achieved_count': len(benchmark_achieved),
            'achievement_rate': len(benchmark_achieved) / len(successful_results) if successful_results else 0
        },
        'top_performers': top_performers[:20] if successful_results else [],
        'overall_stats': overall_stats
    }
    
    report_file = f"{results_dir}/progress_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 詳細報告已保存: {report_file}")

def main():
    analyze_mass_scraping_progress()

if __name__ == "__main__":
    main()