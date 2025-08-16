#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增量更新和缺口補全系統
基於驗證結果進行精準的數據更新和補全
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import random
import os
from datetime import datetime
from urllib.parse import quote
from collections import defaultdict
import threading

class IncrementalUpdater:
    def __init__(self):
        self.base_url = "https://song.corp.com.tw"
        self.delay_range = (2.5, 4.0)
        
        # 載入數據
        self.singers_data = {}
        self.songs_data = []
        self.validation_report = None
        
        # 統計
        self.stats = {
            'singers_processed': 0,
            'songs_added': 0,
            'songs_updated': 0,
            'companies_added': 0,
            'language_tags_added': 0,
            'start_time': datetime.now()
        }
        self.stats_lock = threading.Lock()
        
        # 創建輸出目錄
        os.makedirs("incremental_updates", exist_ok=True)
        
        print("⚡ 增量更新系統")
        print("=" * 50)
    
    def load_data_and_validation(self):
        """載入數據和驗證報告"""
        try:
            # 載入歌手資料庫
            with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                self.singers_data = json.load(f)
            print(f"✅ 載入歌手資料庫: {len(self.singers_data):,} 位")
            
            # 載入完整歌曲資料庫
            with open('public/songs_simplified.json', 'r', encoding='utf-8') as f:
                self.songs_data = json.load(f)
            print(f"✅ 載入完整歌曲資料庫: {len(self.songs_data):,} 首")
            
            # 尋找最新的驗證報告
            validation_files = [f for f in os.listdir('.') if f.startswith('validation_report_') and f.endswith('.json')]
            if validation_files:
                latest_report = sorted(validation_files)[-1]
                with open(latest_report, 'r', encoding='utf-8') as f:
                    self.validation_report = json.load(f)
                print(f"✅ 載入驗證報告: {latest_report}")
            else:
                print("⚠️ 未找到驗證報告，將執行基本檢查")
                
            return True
            
        except Exception as e:
            print(f"❌ 載入數據失敗: {e}")
            return False
    
    def identify_update_targets(self):
        """識別需要更新的目標歌手"""
        update_targets = []
        
        if self.validation_report and 'update_suggestions' in self.validation_report:
            # 基於驗證報告的建議
            suggestions = self.validation_report['update_suggestions']
            for suggestion in suggestions:
                if suggestion['priority'] in ['high', 'medium']:
                    update_targets.append({
                        'singer': suggestion['singer'],
                        'priority': suggestion['priority'],
                        'reason': suggestion['reason'],
                        'type': 'validation_based'
                    })
        
        # 基於數據完整性的自動檢測
        for singer_name, singer_info in self.singers_data.items():
            songs = singer_info.get('歌曲清單', [])
            if not songs:
                continue
            
            # 檢查語言標記完整性
            missing_language = sum(1 for song in songs if not song.get('語言'))
            language_completeness = 1.0 - (missing_language / len(songs))
            
            # 檢查KTV公司覆蓋度
            companies = set()
            for song in songs:
                for code_info in song.get('編號資訊', []):
                    company = code_info.get('公司', '')
                    if company:
                        companies.add(company)
            
            company_completeness = len(companies) / 17  # 假設17家主要KTV
            
            # 綜合評分
            overall_score = (language_completeness + company_completeness) / 2
            
            if overall_score < 0.7:  # 完整度<70%
                priority = 'high' if overall_score < 0.5 else 'medium'
                update_targets.append({
                    'singer': singer_name,
                    'priority': priority,
                    'reason': f'完整度{overall_score:.1%} (語言{language_completeness:.1%}, 公司{company_completeness:.1%})',
                    'type': 'completeness_based',
                    'current_score': overall_score
                })
        
        # 去重並按優先級排序
        unique_targets = {}
        for target in update_targets:
            singer = target['singer']
            if singer not in unique_targets or target['priority'] == 'high':
                unique_targets[singer] = target
        
        sorted_targets = sorted(unique_targets.values(), 
                               key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], 
                               reverse=True)
        
        print(f"🎯 識別更新目標: {len(sorted_targets)} 位歌手")
        print(f"   高優先級: {sum(1 for t in sorted_targets if t['priority'] == 'high')} 位")
        print(f"   中優先級: {sum(1 for t in sorted_targets if t['priority'] == 'medium')} 位")
        
        return sorted_targets
    
    def fetch_singer_songs_incremental(self, singer_name):
        """增量獲取歌手歌曲數據"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        print(f"🔄 增量更新: {singer_name}")
        
        # 獲取現有數據作為基準
        existing_songs = {}
        if singer_name in self.singers_data:
            for song in self.singers_data[singer_name].get('歌曲清單', []):
                song_key = song.get('歌名', '')
                existing_songs[song_key] = song
        
        # 從完整歌曲資料庫獲取該歌手的所有歌曲
        singer_songs_in_db = []
        for song in self.songs_data:
            if song.get('歌手') == singer_name:
                singer_songs_in_db.append(song)
        
        # 按歌名分組完整資料庫的歌曲
        db_songs_by_title = defaultdict(list)
        for song in singer_songs_in_db:
            title = song.get('歌名', '')
            if title:
                db_songs_by_title[title].append(song)
        
        updated_songs = []
        new_songs_count = 0
        updated_songs_count = 0
        companies_added = 0
        language_tags_added = 0
        
        # 整合數據
        for song_title, db_song_entries in db_songs_by_title.items():
            if song_title in existing_songs:
                # 更新現有歌曲
                existing_song = existing_songs[song_title].copy()
                existing_codes = {(code['公司'], code['編號']) for code in existing_song.get('編號資訊', [])}
                
                # 從完整資料庫添加新的KTV編號
                for db_entry in db_song_entries:
                    company = db_entry.get('公司', '')
                    number = db_entry.get('編號', '')
                    
                    if company and number and (company, number) not in existing_codes:
                        existing_song.setdefault('編號資訊', []).append({
                            '公司': company,
                            '編號': number
                        })
                        companies_added += 1
                
                # 更新語言標記（如果缺失）
                if not existing_song.get('語言'):
                    # 嘗試從完整資料庫獲取語言資訊
                    for db_entry in db_song_entries:
                        lang = db_entry.get('語言', '')
                        if lang:
                            existing_song['語言'] = lang
                            language_tags_added += 1
                            break
                    
                    # 如果還沒有語言，使用智能檢測
                    if not existing_song.get('語言'):
                        detected_lang = self._detect_language(song_title)
                        if detected_lang:
                            existing_song['語言'] = detected_lang
                            language_tags_added += 1
                
                updated_songs.append(existing_song)
                if companies_added > 0 or language_tags_added > 0:
                    updated_songs_count += 1
                    
            else:
                # 新歌曲
                new_song = {
                    '歌名': song_title,
                    '歌手': singer_name,
                    '語言': '',
                    '編號資訊': []
                }
                
                # 收集所有KTV編號
                for db_entry in db_song_entries:
                    company = db_entry.get('公司', '')
                    number = db_entry.get('編號', '')
                    lang = db_entry.get('語言', '')
                    
                    if company and number:
                        new_song['編號資訊'].append({
                            '公司': company,
                            '編號': number
                        })
                    
                    if lang and not new_song['語言']:
                        new_song['語言'] = lang
                
                # 智能語言檢測（如果還沒有語言）
                if not new_song['語言']:
                    new_song['語言'] = self._detect_language(song_title)
                
                if new_song['編號資訊']:  # 只添加有編號的歌曲
                    updated_songs.append(new_song)
                    new_songs_count += 1
        
        # 添加完整資料庫中沒有的歌曲（保持原有數據）
        for song_title, existing_song in existing_songs.items():
            if song_title not in db_songs_by_title:
                updated_songs.append(existing_song)
        
        result = {
            'singer': singer_name,
            'updated_songs': updated_songs,
            'stats': {
                'new_songs': new_songs_count,
                'updated_songs': updated_songs_count,
                'companies_added': companies_added,
                'language_tags_added': language_tags_added,
                'total_songs': len(updated_songs)
            }
        }
        
        print(f"   ✅ 完成: +{new_songs_count}首新歌, 更新{updated_songs_count}首, +{companies_added}個編號, +{language_tags_added}個語言標記")
        
        return result
    
    def _detect_language(self, song_title):
        """智能語言檢測"""
        if not song_title:
            return ''
        
        # 統計字符類型
        chinese_chars = sum(1 for char in song_title if '\u4e00' <= char <= '\u9fff')
        english_chars = sum(1 for char in song_title if char.isalpha() and ord(char) < 128)
        total_chars = len(song_title.replace(' ', ''))
        
        if total_chars == 0:
            return ''
        
        chinese_ratio = chinese_chars / total_chars
        english_ratio = english_chars / total_chars
        
        if chinese_ratio > 0.5:
            return '國'  # 預設中文為國語
        elif english_ratio > 0.5:
            return '英'
        else:
            return ''
    
    def apply_incremental_updates(self, update_targets, max_singers=50):
        """應用增量更新"""
        print(f"\n🔄 執行增量更新 (限制: {max_singers} 位歌手)")
        
        successful_updates = []
        failed_updates = []
        
        for i, target in enumerate(update_targets[:max_singers]):
            singer_name = target['singer']
            priority = target['priority']
            
            try:
                print(f"\n[{i+1}/{min(len(update_targets), max_singers)}] {priority.upper()}: {singer_name}")
                
                # 執行增量更新
                result = self.fetch_singer_songs_incremental(singer_name)
                
                if result['updated_songs']:
                    # 更新歌手資料庫
                    self.singers_data[singer_name] = {
                        '歌手名稱': singer_name,
                        '歌曲清單': result['updated_songs']
                    }
                    
                    successful_updates.append(result)
                    
                    # 更新統計
                    with self.stats_lock:
                        self.stats['singers_processed'] += 1
                        self.stats['songs_added'] += result['stats']['new_songs']
                        self.stats['songs_updated'] += result['stats']['updated_songs']
                        self.stats['companies_added'] += result['stats']['companies_added']
                        self.stats['language_tags_added'] += result['stats']['language_tags_added']
                    
                    # 保存中間結果
                    self._save_incremental_result(result)
                    
                else:
                    print(f"   ⚠️ 無更新數據")
                    
            except Exception as e:
                print(f"   ❌ 更新失敗: {str(e)[:50]}")
                failed_updates.append({'singer': singer_name, 'error': str(e)})
            
            # 延遲避免過載
            if i < len(update_targets) - 1:
                delay = random.uniform(*self.delay_range)
                time.sleep(delay)
        
        return successful_updates, failed_updates
    
    def _save_incremental_result(self, result):
        """保存單次增量更新結果"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"incremental_updates/{result['singer']}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"   ⚠️ 保存結果失敗: {e}")
    
    def save_updated_database(self):
        """保存更新後的資料庫"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 備份原始文件
            backup_file = f"singers_data_backup_{timestamp}.json"
            if os.path.exists('public/singers_data.json'):
                import shutil
                shutil.copy2('public/singers_data.json', backup_file)
                print(f"📁 原始數據備份: {backup_file}")
            
            # 保存更新後的數據
            with open('public/singers_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.singers_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 歌手資料庫已更新")
            return True
            
        except Exception as e:
            print(f"❌ 保存失敗: {e}")
            return False
    
    def generate_update_report(self, successful_updates, failed_updates):
        """生成更新報告"""
        elapsed = datetime.now() - self.stats['start_time']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report = {
            'update_date': datetime.now().isoformat(),
            'execution_time': str(elapsed),
            'statistics': self.stats,
            'successful_updates': successful_updates,
            'failed_updates': failed_updates,
            'summary': {
                'total_singers_processed': len(successful_updates),
                'total_songs_added': sum(r['stats']['new_songs'] for r in successful_updates),
                'total_songs_updated': sum(r['stats']['updated_songs'] for r in successful_updates),
                'total_companies_added': sum(r['stats']['companies_added'] for r in successful_updates),
                'total_language_tags_added': sum(r['stats']['language_tags_added'] for r in successful_updates),
                'success_rate': len(successful_updates) / (len(successful_updates) + len(failed_updates)) * 100 if (successful_updates or failed_updates) else 0
            }
        }
        
        # 保存報告
        report_file = f"incremental_update_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 顯示摘要
        print(f"\n" + "="*70)
        print("📊 增量更新完成報告")
        print("="*70)
        print(f"⏱️  執行時間: {elapsed}")
        print(f"🎤 處理歌手: {len(successful_updates)} 位")
        print(f"🎵 新增歌曲: {report['summary']['total_songs_added']} 首")
        print(f"🔄 更新歌曲: {report['summary']['total_songs_updated']} 首")
        print(f"🏢 新增KTV編號: {report['summary']['total_companies_added']} 個")
        print(f"🌍 新增語言標記: {report['summary']['total_language_tags_added']} 個")
        print(f"✅ 成功率: {report['summary']['success_rate']:.1f}%")
        
        if failed_updates:
            print(f"❌ 失敗歌手: {len(failed_updates)} 位")
        
        print(f"\n📄 詳細報告: {report_file}")
        
        return report

def main():
    """主程序"""
    print("⚡ 增量更新和缺口補全系統")
    print("=" * 50)
    
    updater = IncrementalUpdater()
    
    try:
        # 載入數據
        if not updater.load_data_and_validation():
            return
        
        # 識別更新目標
        update_targets = updater.identify_update_targets()
        
        if not update_targets:
            print("✅ 所有數據都已是最新狀態")
            return
        
        # 執行增量更新
        successful_updates, failed_updates = updater.apply_incremental_updates(update_targets, max_singers=20)
        
        if successful_updates:
            # 保存更新後的資料庫
            if updater.save_updated_database():
                print("✅ 資料庫更新成功")
            
            # 生成報告
            updater.generate_update_report(successful_updates, failed_updates)
        else:
            print("⚠️ 沒有成功更新任何歌手")
    
    except Exception as e:
        print(f"❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()