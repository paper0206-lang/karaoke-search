#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌手資料刷新系統 - 重新爬取現有歌手，不重複儲存
"""

import sys
sys.path.append('.')
from singer_scraper import SingerScraper
import json
import time
from datetime import datetime

class SingerRefresher:
    def __init__(self):
        self.scraper = SingerScraper(max_workers=2)
        self.existing_data = {}
        self.load_existing_data()
    
    def load_existing_data(self):
        """載入現有歌手資料"""
        try:
            with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                self.existing_data = json.load(f)
            print(f"📚 載入現有歌手資料: {len(self.existing_data)} 位歌手")
        except:
            print("📚 沒有現有歌手資料")
            self.existing_data = {}
    
    def analyze_existing_singers(self):
        """分析現有歌手資料的完整性"""
        analysis = []
        
        for singer_name, singer_data in self.existing_data.items():
            song_count = len(singer_data.get('歌曲清單', []))
            update_time = singer_data.get('更新時間', '未知')
            
            # 判斷是否可能不完整 (基於歌曲數量和歌手知名度)
            needs_refresh = False
            reason = []
            
            # 知名歌手歌曲數太少
            famous_singers = ['周杰倫', '蔡依林', '林俊傑', '張惠妹', '五月天', '孫燕姿', '梁靜茹']
            if singer_name in famous_singers and song_count < 100:
                needs_refresh = True
                reason.append(f"知名歌手歌曲數偏少 ({song_count}首)")
            
            # 一般歌手歌曲數太少
            elif song_count < 30:
                needs_refresh = True
                reason.append(f"歌曲數偏少 ({song_count}首)")
            
            # 更新時間太舊 (如果有的話)
            if '2024-08-08' not in update_time:
                needs_refresh = True
                reason.append("更新時間較舊")
            
            analysis.append({
                'singer': singer_name,
                'song_count': song_count,
                'update_time': update_time,
                'needs_refresh': needs_refresh,
                'reasons': reason
            })
        
        return analysis
    
    def refresh_singer(self, singer_name, force_refresh=False):
        """刷新單一歌手資料"""
        print(f"\n🔄 刷新歌手: {singer_name}")
        
        # 獲取現有歌曲數
        old_count = 0
        if singer_name in self.existing_data:
            old_count = len(self.existing_data[singer_name].get('歌曲清單', []))
            print(f"   原有歌曲: {old_count} 首")
        
        try:
            # 重新爬取
            new_songs = self.scraper.search_singer_comprehensive(singer_name)
            new_count = len(new_songs)
            
            print(f"   重新爬取: {new_count} 首")
            
            # 比較結果
            if new_count > old_count:
                print(f"   📈 發現更多歌曲: +{new_count - old_count} 首")
                
                # 儲存新資料
                if self.scraper.save_singer_data(singer_name, new_songs):
                    # 重新載入更新後的資料
                    self.load_existing_data()
                    return {
                        'success': True,
                        'old_count': old_count,
                        'new_count': new_count,
                        'added': new_count - old_count
                    }
                else:
                    return {'success': False, 'error': '儲存失敗'}
                    
            elif new_count == old_count:
                print(f"   ✅ 歌曲數相同，資料已是最新")
                # 即使數量相同，也更新時間戳記
                self.scraper.save_singer_data(singer_name, new_songs)
                return {
                    'success': True,
                    'old_count': old_count,
                    'new_count': new_count,
                    'added': 0,
                    'status': 'already_complete'
                }
            else:
                print(f"   ⚠️ 新爬取數量較少: -{old_count - new_count} 首")
                if force_refresh:
                    print(f"   🔄 強制更新...")
                    self.scraper.save_singer_data(singer_name, new_songs)
                    return {
                        'success': True,
                        'old_count': old_count,
                        'new_count': new_count,
                        'added': new_count - old_count,
                        'status': 'forced_update'
                    }
                else:
                    print(f"   ⏭️ 保持原資料不變")
                    return {
                        'success': True,
                        'old_count': old_count,
                        'new_count': new_count,
                        'added': 0,
                        'status': 'kept_original'
                    }
                    
        except Exception as e:
            print(f"   ❌ 刷新失敗: {e}")
            return {'success': False, 'error': str(e)}
    
    def batch_refresh(self, singers_to_refresh, force_refresh=False):
        """批次刷新歌手資料"""
        print(f"🔄 開始批次刷新 {len(singers_to_refresh)} 位歌手")
        
        results = {
            'success': 0,
            'failed': 0,
            'total_added': 0,
            'details': []
        }
        
        for i, singer_name in enumerate(singers_to_refresh, 1):
            print(f"\n[{i}/{len(singers_to_refresh)}] 處理: {singer_name}")
            
            result = self.refresh_singer(singer_name, force_refresh)
            
            if result['success']:
                results['success'] += 1
                if 'added' in result:
                    results['total_added'] += result['added']
            else:
                results['failed'] += 1
            
            results['details'].append({
                'singer': singer_name,
                **result
            })
            
            # 避免被封鎖
            if i < len(singers_to_refresh):
                print("😴 休息 3 秒...")
                time.sleep(3)
        
        return results

def main():
    print("🔄 歌手資料刷新系統")
    print("="*50)
    
    refresher = SingerRefresher()
    
    # 分析現有歌手
    analysis = refresher.analyze_existing_singers()
    
    # 顯示需要刷新的歌手
    needs_refresh = [item for item in analysis if item['needs_refresh']]
    complete_singers = [item for item in analysis if not item['needs_refresh']]
    
    print(f"\n📊 歌手資料分析:")
    print(f"   需要刷新: {len(needs_refresh)} 位")
    print(f"   資料完整: {len(complete_singers)} 位")
    
    if needs_refresh:
        print(f"\n🔄 建議刷新的歌手:")
        for item in sorted(needs_refresh, key=lambda x: x['song_count']):
            reasons = ', '.join(item['reasons'])
            print(f"   {item['singer']:8s} - {item['song_count']:3d} 首 ({reasons})")
    
    print(f"\n✅ 資料完整的歌手:")
    for item in sorted(complete_singers, key=lambda x: x['song_count'], reverse=True)[:10]:
        print(f"   {item['singer']:8s} - {item['song_count']:3d} 首")
    
    print(f"\n🔧 刷新選項:")
    print(f"1. 刷新建議的 {len(needs_refresh)} 位歌手")
    print(f"2. 刷新所有 {len(analysis)} 位歌手")
    print(f"3. 刷新指定歌手")
    print(f"4. 只分析不執行")
    
    choice = input("請選擇 (1-4): ").strip()
    
    if choice == '1':
        singers_to_refresh = [item['singer'] for item in needs_refresh]
    elif choice == '2':
        singers_to_refresh = [item['singer'] for item in analysis]
    elif choice == '3':
        singer_input = input("請輸入歌手名稱 (用逗號分隔): ").strip()
        singers_to_refresh = [s.strip() for s in singer_input.split(',') if s.strip()]
    elif choice == '4':
        print("✅ 分析完成，未執行刷新")
        return
    else:
        print("❌ 無效選擇")
        return
    
    if not singers_to_refresh:
        print("❌ 沒有要刷新的歌手")
        return
    
    # 詢問是否強制更新
    force_refresh = False
    if choice in ['2', '3']:
        force_input = input("是否強制更新 (即使新數量較少)? (y/n): ").strip().lower()
        force_refresh = force_input == 'y'
    
    print(f"\n準備刷新 {len(singers_to_refresh)} 位歌手...")
    confirm = input("確定開始? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ 已取消")
        return
    
    # 開始批次刷新
    start_time = datetime.now()
    results = refresher.batch_refresh(singers_to_refresh, force_refresh)
    end_time = datetime.now()
    
    # 顯示結果
    print(f"\n🎉 刷新完成!")
    print(f"📊 執行結果:")
    print(f"   成功: {results['success']} 位")
    print(f"   失敗: {results['failed']} 位") 
    print(f"   新增歌曲: {results['total_added']} 首")
    print(f"   耗時: {end_time - start_time}")
    
    # 顯示詳細結果
    if results['total_added'] > 0:
        print(f"\n📈 新增歌曲詳情:")
        for detail in results['details']:
            if detail['success'] and detail.get('added', 0) > 0:
                print(f"   {detail['singer']:8s}: +{detail['added']} 首 ({detail['old_count']} → {detail['new_count']})")

if __name__ == "__main__":
    main()