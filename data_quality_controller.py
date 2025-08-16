#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
數據清理和品質控制系統
確保爬蟲數據的品質、一致性和完整性
"""

import json
import re
import os
from datetime import datetime
from collections import defaultdict, Counter
import difflib

class DataQualityController:
    def __init__(self):
        self.singers_data = {}
        self.quality_rules = self._initialize_quality_rules()
        self.cleaning_stats = {
            'duplicates_removed': 0,
            'invalid_entries_removed': 0,
            'language_tags_corrected': 0,
            'company_names_normalized': 0,
            'song_names_cleaned': 0,
            'numbers_normalized': 0
        }
        
        print("🧹 數據品質控制系統")
        print("=" * 50)
    
    def _initialize_quality_rules(self):
        """初始化品質控制規則"""
        return {
            'language_mapping': {
                # 語言標準化對應表
                '中文': '國', '國語': '國', '中': '國', '華語': '國',
                '台語': '台', '台': '台', '閩南語': '台', '閩': '台',
                '英文': '英', '英語': '英', 'English': '英', 'EN': '英',
                '客家話': '客', '客語': '客', '客': '客',
                '粵語': '粵', '廣東話': '粵', '港語': '粵', '粵': '粵',
                '日語': '日', '日文': '日', '日本語': '日', 'JP': '日',
                '韓語': '韓', '韓文': '韓', '朝鮮語': '韓', 'KR': '韓',
                '兒歌': '兒', '童謠': '兒',
                '山地語': '山', '原住民語': '山'
            },
            'company_mapping': {
                # KTV公司名稱標準化對應表
                'CASHBOX': '錢櫃', 'cashbox': '錢櫃', '錢櫃KTV': '錢櫃',
                'HOLIDAY': '好樂迪', 'holiday': '好樂迪', 'HOLIDAY KTV': '好樂迪',
                '音園': '音圓', '音圓KTV': '音圓', 'MZONE': '音圓',
                '銀柜': '銀櫃', '银柜': '銀櫃',
                '星聚點': '星據點', '星聚点': '星據點',
                '金嗓公司': '金嗓', '金嗓企業': '金嗓',
                '弘音企業': '弘音', '弘音公司': '弘音'
            },
            'invalid_patterns': {
                # 無效數據模式
                'empty_song_names': [r'^\s*$', r'^-+$', r'^\.+$'],
                'invalid_numbers': [r'^\s*$', r'^-+$', r'[^\w\-\s]'],
                'suspicious_lengths': {
                    'song_name_max': 100,
                    'singer_name_max': 50,
                    'company_name_max': 20,
                    'number_max': 20
                }
            }
        }
    
    def load_data(self):
        """載入歌手資料庫"""
        try:
            with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                self.singers_data = json.load(f)
            print(f"✅ 載入歌手資料庫: {len(self.singers_data):,} 位歌手")
            return True
        except Exception as e:
            print(f"❌ 載入失敗: {e}")
            return False
    
    def normalize_language_tags(self):
        """標準化語言標籤"""
        print("🌍 標準化語言標籤...")
        
        corrected_count = 0
        
        for singer_name, singer_info in self.singers_data.items():
            songs = singer_info.get('歌曲清單', [])
            
            for song in songs:
                original_lang = song.get('語言', '')
                
                # 空白語言嘗試智能檢測
                if not original_lang or original_lang.strip() == '':
                    detected_lang = self._detect_language_advanced(song.get('歌名', ''), singer_name)
                    if detected_lang:
                        song['語言'] = detected_lang
                        corrected_count += 1
                        continue
                
                # 標準化現有語言標籤
                normalized_lang = self.quality_rules['language_mapping'].get(original_lang, original_lang)
                if normalized_lang != original_lang:
                    song['語言'] = normalized_lang
                    corrected_count += 1
        
        self.cleaning_stats['language_tags_corrected'] = corrected_count
        print(f"   ✅ 修正語言標籤: {corrected_count} 個")
    
    def _detect_language_advanced(self, song_title, singer_name):
        """進階語言檢測"""
        if not song_title:
            return ''
        
        # 字符分析
        chinese_chars = sum(1 for char in song_title if '\u4e00' <= char <= '\u9fff')
        english_chars = sum(1 for char in song_title if char.isalpha() and ord(char) < 128)
        japanese_chars = sum(1 for char in song_title if '\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff')
        korean_chars = sum(1 for char in song_title if '\uac00' <= char <= '\ud7af')
        
        total_chars = len(song_title.replace(' ', '').replace('(', '').replace(')', ''))
        
        if total_chars == 0:
            return ''
        
        # 基於字符比例判斷
        if japanese_chars / total_chars > 0.3:
            return '日'
        elif korean_chars / total_chars > 0.3:
            return '韓'
        elif english_chars / total_chars > 0.7:
            return '英'
        elif chinese_chars / total_chars > 0.5:
            # 進一步區分國語和台語 (簡化邏輯)
            if self._is_likely_taiwanese(song_title, singer_name):
                return '台'
            else:
                return '國'
        
        return ''
    
    def _is_likely_taiwanese(self, song_title, singer_name):
        """判斷是否可能是台語歌曲"""
        taiwanese_indicators = [
            '心肝', '阿母', '阿爸', '故鄉', '思念', '酒店', '查某', '查埔',
            '愛情', '海邊', '漁船', '田庄', '思君', '離別', '相思'
        ]
        
        taiwanese_singers = [
            '江蕙', '黃乙玲', '龍千玉', '詹雅雯', '秀蘭瑪雅', '袁小迪',
            '陳盈潔', '白冰冰', '蔡小虎', '江志豐', '七郎'
        ]
        
        # 歌名包含台語關鍵詞
        for indicator in taiwanese_indicators:
            if indicator in song_title:
                return True
        
        # 歌手是知名台語歌手
        for taiwanese_singer in taiwanese_singers:
            if taiwanese_singer in singer_name:
                return True
        
        return False
    
    def normalize_company_names(self):
        """標準化KTV公司名稱"""
        print("🏢 標準化KTV公司名稱...")
        
        normalized_count = 0
        
        for singer_name, singer_info in self.singers_data.items():
            songs = singer_info.get('歌曲清單', [])
            
            for song in songs:
                codes = song.get('編號資訊', [])
                
                for code_info in codes:
                    original_company = code_info.get('公司', '')
                    normalized_company = self.quality_rules['company_mapping'].get(original_company, original_company)
                    
                    if normalized_company != original_company:
                        code_info['公司'] = normalized_company
                        normalized_count += 1
        
        self.cleaning_stats['company_names_normalized'] = normalized_count
        print(f"   ✅ 標準化公司名稱: {normalized_count} 個")
    
    def clean_song_names(self):
        """清理歌曲名稱"""
        print("🎵 清理歌曲名稱...")
        
        cleaned_count = 0
        
        for singer_name, singer_info in self.singers_data.items():
            songs = singer_info.get('歌曲清單', [])
            
            for song in songs:
                original_name = song.get('歌名', '')
                
                # 清理歌名
                cleaned_name = self._clean_song_name(original_name)
                
                if cleaned_name != original_name:
                    song['歌名'] = cleaned_name
                    cleaned_count += 1
        
        self.cleaning_stats['song_names_cleaned'] = cleaned_count
        print(f"   ✅ 清理歌曲名稱: {cleaned_count} 個")
    
    def _clean_song_name(self, song_name):
        """清理單個歌曲名稱"""
        if not song_name:
            return ''
        
        # 移除前後空白
        cleaned = song_name.strip()
        
        # 移除多餘的空格
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # 移除特殊字符 (保留必要的標點)
        cleaned = re.sub(r'[^\w\s\(\)\-\+\&\.\,\!\?\'\"\:\;]', '', cleaned)
        
        # 移除重複的標點符號
        cleaned = re.sub(r'([\.]{2,})', '...', cleaned)
        cleaned = re.sub(r'([!]{2,})', '!', cleaned)
        cleaned = re.sub(r'([?]{2,})', '?', cleaned)
        
        return cleaned
    
    def normalize_ktv_numbers(self):
        """標準化KTV編號格式"""
        print("🔢 標準化KTV編號...")
        
        normalized_count = 0
        
        for singer_name, singer_info in self.singers_data.items():
            songs = singer_info.get('歌曲清單', [])
            
            for song in songs:
                codes = song.get('編號資訊', [])
                
                for code_info in codes:
                    original_number = code_info.get('編號', '')
                    normalized_number = self._normalize_number(original_number)
                    
                    if normalized_number != original_number:
                        code_info['編號'] = normalized_number
                        normalized_count += 1
        
        self.cleaning_stats['numbers_normalized'] = normalized_count
        print(f"   ✅ 標準化編號: {normalized_count} 個")
    
    def _normalize_number(self, number):
        """標準化單個編號"""
        if not number:
            return ''
        
        # 移除前後空白
        normalized = str(number).strip()
        
        # 移除非數字字母字符 (保留-和空格)
        normalized = re.sub(r'[^\w\-\s]', '', normalized)
        
        # 標準化格式 (例如：001234 -> 1234, A-001 -> A001)
        if normalized.isdigit():
            # 純數字：移除前導零但保持至少一位
            normalized = str(int(normalized))
        
        return normalized
    
    def remove_duplicates(self):
        """移除重複歌曲"""
        print("🔄 移除重複歌曲...")
        
        duplicates_removed = 0
        
        for singer_name, singer_info in self.singers_data.items():
            songs = singer_info.get('歌曲清單', [])
            
            # 建立唯一歌曲字典
            unique_songs = {}
            
            for song in songs:
                song_key = self._generate_song_key(song)
                
                if song_key in unique_songs:
                    # 合併KTV編號
                    existing_song = unique_songs[song_key]
                    existing_codes = {(code['公司'], code['編號']) for code in existing_song.get('編號資訊', [])}
                    
                    for new_code in song.get('編號資訊', []):
                        code_tuple = (new_code['公司'], new_code['編號'])
                        if code_tuple not in existing_codes:
                            existing_song.setdefault('編號資訊', []).append(new_code)
                    
                    # 更新語言資訊（選擇非空的）
                    if not existing_song.get('語言') and song.get('語言'):
                        existing_song['語言'] = song['語言']
                    
                    duplicates_removed += 1
                else:
                    unique_songs[song_key] = song
            
            # 更新歌曲清單
            singer_info['歌曲清單'] = list(unique_songs.values())
        
        self.cleaning_stats['duplicates_removed'] = duplicates_removed
        print(f"   ✅ 移除重複歌曲: {duplicates_removed} 首")
    
    def _generate_song_key(self, song):
        """生成歌曲唯一標識"""
        song_name = song.get('歌名', '').lower().strip()
        singer_name = song.get('歌手', '').lower().strip()
        
        # 移除常見的變化 (括號內容、空格等)
        song_name = re.sub(r'\([^)]*\)', '', song_name)
        song_name = re.sub(r'\s+', '', song_name)
        singer_name = re.sub(r'\s+', '', singer_name)
        
        return f"{song_name}_{singer_name}"
    
    def remove_invalid_entries(self):
        """移除無效的數據條目"""
        print("❌ 移除無效條目...")
        
        invalid_removed = 0
        
        for singer_name, singer_info in self.singers_data.items():
            songs = singer_info.get('歌曲清單', [])
            valid_songs = []
            
            for song in songs:
                if self._is_valid_song(song):
                    # 清理編號資訊
                    valid_codes = []
                    for code_info in song.get('編號資訊', []):
                        if self._is_valid_code(code_info):
                            valid_codes.append(code_info)
                        else:
                            invalid_removed += 1
                    
                    if valid_codes:  # 只保留有有效編號的歌曲
                        song['編號資訊'] = valid_codes
                        valid_songs.append(song)
                    else:
                        invalid_removed += 1
                else:
                    invalid_removed += 1
            
            singer_info['歌曲清單'] = valid_songs
        
        self.cleaning_stats['invalid_entries_removed'] = invalid_removed
        print(f"   ✅ 移除無效條目: {invalid_removed} 個")
    
    def _is_valid_song(self, song):
        """檢查歌曲是否有效"""
        song_name = song.get('歌名', '').strip()
        
        # 檢查歌名
        if not song_name:
            return False
        
        # 檢查歌名長度
        if len(song_name) > self.quality_rules['invalid_patterns']['suspicious_lengths']['song_name_max']:
            return False
        
        # 檢查是否匹配無效模式
        for pattern in self.quality_rules['invalid_patterns']['empty_song_names']:
            if re.match(pattern, song_name):
                return False
        
        return True
    
    def _is_valid_code(self, code_info):
        """檢查KTV編號是否有效"""
        company = code_info.get('公司', '').strip()
        number = code_info.get('編號', '').strip()
        
        # 必須有公司和編號
        if not company or not number:
            return False
        
        # 檢查長度
        if (len(company) > self.quality_rules['invalid_patterns']['suspicious_lengths']['company_name_max'] or
            len(number) > self.quality_rules['invalid_patterns']['suspicious_lengths']['number_max']):
            return False
        
        return True
    
    def run_quality_control(self):
        """執行完整的品質控制流程"""
        print("🧹 執行數據品質控制...")
        
        if not self.load_data():
            return False
        
        # 執行各項清理步驟
        self.remove_invalid_entries()
        self.normalize_company_names()
        self.clean_song_names()
        self.normalize_ktv_numbers()
        self.normalize_language_tags()
        self.remove_duplicates()
        
        # 生成清理報告
        self._generate_cleaning_report()
        
        # 保存清理後的數據
        return self._save_cleaned_data()
    
    def _generate_cleaning_report(self):
        """生成清理報告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 統計清理後的數據
        total_singers = len(self.singers_data)
        total_songs = sum(len(info.get('歌曲清單', [])) for info in self.singers_data.values())
        
        # 語言分布統計
        language_dist = Counter()
        company_dist = Counter()
        
        for singer_info in self.singers_data.values():
            for song in singer_info.get('歌曲清單', []):
                lang = song.get('語言', '')
                if lang:
                    language_dist[lang] += 1
                
                for code_info in song.get('編號資訊', []):
                    company = code_info.get('公司', '')
                    if company:
                        company_dist[company] += 1
        
        report = {
            'cleaning_date': datetime.now().isoformat(),
            'cleaning_stats': self.cleaning_stats,
            'database_stats_after_cleaning': {
                'total_singers': total_singers,
                'total_songs': total_songs,
                'language_distribution': dict(language_dist.most_common()),
                'company_distribution': dict(company_dist.most_common())
            },
            'quality_improvements': {
                'data_consistency': 'Improved through normalization',
                'duplicate_reduction': f"Removed {self.cleaning_stats['duplicates_removed']} duplicates",
                'language_coverage': f"Added/corrected {self.cleaning_stats['language_tags_corrected']} language tags",
                'invalid_data_removal': f"Removed {self.cleaning_stats['invalid_entries_removed']} invalid entries"
            }
        }
        
        # 保存報告
        report_file = f"data_quality_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 顯示摘要
        print(f"\n" + "="*70)
        print("📊 數據品質控制完成報告")
        print("="*70)
        print(f"🎤 處理歌手: {total_singers:,} 位")
        print(f"🎵 清理後歌曲: {total_songs:,} 首")
        print()
        print(f"🧹 清理統計:")
        print(f"   移除重複歌曲: {self.cleaning_stats['duplicates_removed']:,}")
        print(f"   移除無效條目: {self.cleaning_stats['invalid_entries_removed']:,}")
        print(f"   修正語言標籤: {self.cleaning_stats['language_tags_corrected']:,}")
        print(f"   標準化公司名稱: {self.cleaning_stats['company_names_normalized']:,}")
        print(f"   清理歌曲名稱: {self.cleaning_stats['song_names_cleaned']:,}")
        print(f"   標準化編號: {self.cleaning_stats['numbers_normalized']:,}")
        print()
        print(f"🌍 語言分布: {dict(list(language_dist.most_common(5)))}")
        print(f"🏢 主要KTV公司: {dict(list(company_dist.most_common(5)))}")
        print(f"\n📄 詳細報告: {report_file}")
        
        return report
    
    def _save_cleaned_data(self):
        """保存清理後的數據"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 備份原始文件
            backup_file = f"singers_data_before_cleaning_{timestamp}.json"
            if os.path.exists('public/singers_data.json'):
                import shutil
                shutil.copy2('public/singers_data.json', backup_file)
                print(f"📁 清理前數據備份: {backup_file}")
            
            # 保存清理後的數據
            with open('public/singers_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.singers_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 清理後數據已保存")
            return True
            
        except Exception as e:
            print(f"❌ 保存失敗: {e}")
            return False

def main():
    """主程序"""
    print("🧹 數據品質控制系統")
    print("=" * 50)
    
    controller = DataQualityController()
    
    try:
        success = controller.run_quality_control()
        
        if success:
            print("\n✅ 數據品質控制完成！")
            print("📊 數據品質得到顯著提升")
        else:
            print("\n❌ 數據品質控制失敗")
    
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()