#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速基準分析器 - 快速分析歌手基準狀態
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lu_benchmark_mass_scraper import LuBenchmarkMassScraper

def quick_analyze_sample():
    """快速分析樣本歌手"""
    print("🔍 快速基準狀態分析")
    print("=" * 30)
    
    scraper = LuBenchmarkMassScraper()
    
    # 取樣分析前100位歌手
    sample_singers = scraper.singers_to_process[:100]
    
    print(f"📊 分析樣本: 前{len(sample_singers)}位歌手")
    
    needs_work = []
    already_good = []
    
    for i, singer in enumerate(sample_singers, 1):
        if i % 20 == 0:
            print(f"   進度: {i}/{len(sample_singers)}")
        
        benchmark_check = scraper.check_singer_against_benchmark(singer)
        
        if benchmark_check['needs_processing']:
            needs_work.append({
                'singer': singer,
                'score': benchmark_check['benchmark_score'],
                'songs': benchmark_check['current_songs'],
                'companies': benchmark_check.get('companies_covered', 0)
            })
        else:
            already_good.append({
                'singer': singer,
                'score': benchmark_check['benchmark_score']
            })
    
    print(f"\n📋 樣本分析結果:")
    print(f"   需要改進: {len(needs_work)}/{len(sample_singers)} ({len(needs_work)/len(sample_singers)*100:.1f}%)")
    print(f"   已達標準: {len(already_good)}/{len(sample_singers)} ({len(already_good)/len(sample_singers)*100:.1f}%)")
    
    # 推估全體狀況
    total_singers = len(scraper.singers_to_process)
    estimated_need_work = int(total_singers * len(needs_work) / len(sample_singers))
    
    print(f"\n🎯 全體推估:")
    print(f"   預估需要改進: ~{estimated_need_work:,} 位歌手")
    print(f"   預估已達標準: ~{total_singers - estimated_need_work:,} 位歌手")
    
    if needs_work:
        print(f"\n📉 最需要改進的前10位歌手:")
        needs_work.sort(key=lambda x: x['score'])
        for i, info in enumerate(needs_work[:10], 1):
            print(f"   {i:2d}. {info['singer']:15s}: {info['score']:.1%} "
                  f"({info['songs']}首, {info['companies']}家KTV)")
    
    print(f"\n💡 建議:")
    if len(needs_work) / len(sample_singers) > 0.5:
        print("   🚀 建議執行大規模改進計畫")
        print("   📦 可分批處理，每批10-20位歌手")
    elif len(needs_work) / len(sample_singers) > 0.2:
        print("   ⚡ 建議執行中等規模改進")
        print("   🎯 重點處理評分較低的歌手")
    else:
        print("   ✅ 大部分歌手已達標準")
        print("   🔧 只需處理少數歌手")
    
    return needs_work, already_good

def analyze_lu_benchmark_status():
    """分析盧廣仲基準達成狀況"""
    print("\n🎤 盧廣仲基準標準檢查")
    print("-" * 30)
    
    try:
        with open('public/singers_data.json', 'r', encoding='utf-8') as f:
            singers_data = json.load(f)
        
        if "盧廣仲" in singers_data:
            lu_info = singers_data["盧廣仲"]
            lu_songs = lu_info.get('歌曲清單', [])
            
            print(f"✅ 盧廣仲資料狀態:")
            print(f"   總歌曲數: {len(lu_songs)} 首")
            
            # 統計語言分布
            languages = {}
            companies = set()
            ktv_entries = 0
            
            for song in lu_songs:
                lang = song.get('語言', '未知')
                languages[lang] = languages.get(lang, 0) + 1
                
                for code_info in song.get('編號資訊', []):
                    companies.add(code_info.get('公司', ''))
                    ktv_entries += 1
            
            print(f"   語言分布: {dict(languages)}")
            print(f"   KTV公司數: {len(companies)} 家")
            print(f"   KTV條目數: {ktv_entries} 筆")
            print(f"   平均每首歌: {ktv_entries/len(lu_songs):.1f} 個KTV編號")
            
            print(f"\n🎯 作為基準標準:")
            print(f"   其他歌手應至少達到: {len(lu_songs)}首歌, {len(companies)}家KTV覆蓋")
            
        else:
            print(f"❌ 找不到盧廣仲資料")
            
    except Exception as e:
        print(f"❌ 分析失敗: {e}")

def main():
    analyze_lu_benchmark_status()
    needs_work, already_good = quick_analyze_sample()
    
    if needs_work:
        print(f"\n🚀 建議下一步:")
        print(f"   可執行: python3 targeted_scraper.py")
        print(f"   處理最需要改進的 {min(len(needs_work) * 35, 500)} 位歌手")

if __name__ == "__main__":
    main()