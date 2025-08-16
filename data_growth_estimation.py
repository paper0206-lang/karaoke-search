#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料庫增長預估分析器
基於當前爬蟲執行狀況預估最終資料增長
"""

import json
import os
from datetime import datetime

def analyze_current_database():
    """分析當前資料庫狀態"""
    try:
        with open('public/singers_data.json', 'r', encoding='utf-8') as f:
            singers_data = json.load(f)
        
        total_singers = len(singers_data)
        total_songs = 0
        total_ktv_entries = 0
        
        language_stats = {}
        company_stats = {}
        
        for singer, info in singers_data.items():
            songs = info.get('歌曲清單', [])
            total_songs += len(songs)
            
            for song in songs:
                # 語言統計
                lang = song.get('語言', '未知')
                language_stats[lang] = language_stats.get(lang, 0) + 1
                
                # KTV條目統計
                for code_info in song.get('編號資訊', []):
                    total_ktv_entries += 1
                    company = code_info.get('公司', '未知')
                    company_stats[company] = company_stats.get(company, 0) + 1
        
        return {
            'total_singers': total_singers,
            'total_songs': total_songs,
            'total_ktv_entries': total_ktv_entries,
            'language_stats': language_stats,
            'company_stats': company_stats,
            'avg_songs_per_singer': total_songs / total_singers if total_singers > 0 else 0,
            'avg_ktv_per_song': total_ktv_entries / total_songs if total_songs > 0 else 0
        }
        
    except Exception as e:
        print(f"❌ 分析資料庫失敗: {e}")
        return None

def analyze_background_scraper_progress():
    """分析背景爬蟲進度和成效"""
    # 從日誌分析當前進度
    log_file = None
    try:
        import glob
        log_files = glob.glob("background_logs/nohup_*.log")
        if log_files:
            log_file = max(log_files, key=os.path.getmtime)
    except:
        pass
    
    current_progress = {
        'total_target_singers': 112,  # 從日誌看到
        'total_batches': 23,
        'completed_batches': 0,
        'singers_already_meeting_standard': 0,
        'singers_needing_scraping': 0,
        'singers_with_no_data': 0
    }
    
    if log_file:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 統計各種狀況
            already_standard_count = content.count('已達基準標準')
            no_data_count = content.count('無新資料')
            batch_count = content.count('--- 批次')
            
            current_progress.update({
                'completed_batches': batch_count,
                'singers_already_meeting_standard': already_standard_count,
                'singers_with_no_data': no_data_count
            })
            
        except Exception as e:
            print(f"⚠️ 讀取日誌失敗: {e}")
    
    return current_progress

def analyze_historical_success_rate():
    """分析歷史成功率"""
    historical_data = {
        # 基於之前的測試結果
        'sample_size': 20,
        'successful_processing': 7,  # 35%
        'met_benchmark': 2,  # 28.6% of successful
        'avg_new_songs_per_successful': 237 / 7,  # ~34首
        'taiwan_song_king_hit_rate': 0.35,  # 35%找到資料
        'benchmark_achievement_rate': 0.286  # 28.6%達到基準
    }
    
    return historical_data

def estimate_final_results():
    """預估最終結果"""
    print("📊 資料庫增長預估分析")
    print("=" * 50)
    
    # 分析當前狀態
    current_db = analyze_current_database()
    if not current_db:
        return
    
    progress = analyze_background_scraper_progress()
    historical = analyze_historical_success_rate()
    
    print(f"🗄️ 當前資料庫狀態:")
    print(f"   歌手數量: {current_db['total_singers']:,} 位")
    print(f"   歌曲總數: {current_db['total_songs']:,} 首")
    print(f"   KTV條目: {current_db['total_ktv_entries']:,} 筆")
    print(f"   平均每位歌手: {current_db['avg_songs_per_singer']:.1f} 首歌")
    print(f"   平均每首歌: {current_db['avg_ktv_per_song']:.1f} 個KTV編號")
    
    print(f"\n🎯 背景爬蟲當前進度:")
    print(f"   目標歌手: {progress['total_target_singers']} 位")
    print(f"   已完成批次: {progress['completed_batches']}/{progress['total_batches']}")
    print(f"   已達標準: {progress['singers_already_meeting_standard']} 位")
    print(f"   無新資料: {progress['singers_with_no_data']} 位")
    
    # 基於當前趨勢估算
    remaining_singers = progress['total_target_singers'] - progress['singers_already_meeting_standard'] - progress['singers_with_no_data']
    estimated_progress = min(progress['completed_batches'] / progress['total_batches'], 1.0)
    
    print(f"\n📈 基於歷史數據的預估:")
    print(f"   Taiwan Song King命中率: {historical['taiwan_song_king_hit_rate']*100:.1f}%")
    print(f"   成功處理的歌手平均新增: {historical['avg_new_songs_per_successful']:.1f} 首歌")
    print(f"   基準達成率: {historical['benchmark_achievement_rate']*100:.1f}%")
    
    # 計算預估結果
    total_remaining = max(remaining_singers, progress['total_target_singers'] - progress['singers_already_meeting_standard'])
    
    # 樂觀預估 (Taiwan Song King命中率維持35%)
    optimistic_successful_singers = int(total_remaining * historical['taiwan_song_king_hit_rate'])
    optimistic_new_songs = int(optimistic_successful_singers * historical['avg_new_songs_per_successful'])
    
    # 保守預估 (考慮網路問題，命中率降到20%)
    conservative_hit_rate = 0.20
    conservative_successful_singers = int(total_remaining * conservative_hit_rate)
    conservative_new_songs = int(conservative_successful_singers * (historical['avg_new_songs_per_successful'] * 0.8))
    
    # 現實預估 (基於當前觀察到的趨勢)
    # 觀察到很多歌手已達標準，實際需要爬取的更少
    realistic_need_scraping = max(10, total_remaining - int(total_remaining * 0.6))  # 60%可能已達標
    realistic_successful = int(realistic_need_scraping * 0.3)  # 30%能找到資料
    realistic_new_songs = int(realistic_successful * 20)  # 平均每位20首 (較保守)
    
    print(f"\n🎯 最終預估結果:")
    print(f"")
    print(f"樂觀預估 (35%命中率):")
    print(f"   成功處理歌手: {optimistic_successful_singers} 位")
    print(f"   新增歌曲: {optimistic_new_songs:,} 首")
    print(f"   最終資料庫: {current_db['total_songs'] + optimistic_new_songs:,} 首歌")
    print(f"   增長幅度: {(optimistic_new_songs/current_db['total_songs'])*100:.1f}%")
    
    print(f"")
    print(f"保守預估 (20%命中率):")
    print(f"   成功處理歌手: {conservative_successful_singers} 位")
    print(f"   新增歌曲: {conservative_new_songs:,} 首")
    print(f"   最終資料庫: {current_db['total_songs'] + conservative_new_songs:,} 首歌")
    print(f"   增長幅度: {(conservative_new_songs/current_db['total_songs'])*100:.1f}%")
    
    print(f"")
    print(f"現實預估 (基於當前趨勢):")
    print(f"   實際需爬取: {realistic_need_scraping} 位")
    print(f"   成功處理歌手: {realistic_successful} 位")
    print(f"   新增歌曲: {realistic_new_songs:,} 首")
    print(f"   最終資料庫: {current_db['total_songs'] + realistic_new_songs:,} 首歌")
    print(f"   增長幅度: {(realistic_new_songs/current_db['total_songs'])*100:.1f}%")
    
    # KTV條目預估
    avg_ktv_per_song = current_db['avg_ktv_per_song']
    realistic_new_ktv_entries = int(realistic_new_songs * avg_ktv_per_song)
    
    print(f"\n📊 KTV條目預估:")
    print(f"   當前KTV條目: {current_db['total_ktv_entries']:,} 筆")
    print(f"   預估新增KTV條目: {realistic_new_ktv_entries:,} 筆")
    print(f"   最終KTV條目: {current_db['total_ktv_entries'] + realistic_new_ktv_entries:,} 筆")
    
    print(f"\n💡 結論:")
    print(f"   根據當前背景爬蟲的執行狀況，大多數歌手已達到盧廣仲基準標準")
    print(f"   預估實際增長較為溫和，但品質會顯著提升")
    print(f"   現實預估新增 {realistic_new_songs:,} 首歌曲是合理的預期")
    
    # 儲存預估報告
    estimation_data = {
        'analysis_time': datetime.now().isoformat(),
        'current_database': current_db,
        'scraper_progress': progress,
        'historical_performance': historical,
        'estimations': {
            'optimistic': {
                'successful_singers': optimistic_successful_singers,
                'new_songs': optimistic_new_songs,
                'final_total': current_db['total_songs'] + optimistic_new_songs
            },
            'conservative': {
                'successful_singers': conservative_successful_singers,
                'new_songs': conservative_new_songs,
                'final_total': current_db['total_songs'] + conservative_new_songs
            },
            'realistic': {
                'successful_singers': realistic_successful,
                'new_songs': realistic_new_songs,
                'final_total': current_db['total_songs'] + realistic_new_songs,
                'new_ktv_entries': realistic_new_ktv_entries
            }
        }
    }
    
    with open('data_growth_estimation.json', 'w', encoding='utf-8') as f:
        json.dump(estimation_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 詳細預估報告已保存: data_growth_estimation.json")

def main():
    estimate_final_results()

if __name__ == "__main__":
    main()