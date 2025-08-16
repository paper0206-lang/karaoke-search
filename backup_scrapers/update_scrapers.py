#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬蟲更新工具 - 將所有現有爬蟲更新為統一資料庫架構
"""

import os
import glob

def update_scraper_file(file_path):
    """更新單一爬蟲檔案"""
    print(f"🔄 更新: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 記錄修改
        changes = []
        original_content = content
        
        # 1. 更新檔案路徑引用
        if 'songs_simplified.json' in content:
            # 替換載入路徑
            content = content.replace(
                "with open('public/songs_simplified.json', 'r'",
                "with open('public/unified_karaoke_db.json', 'r'"
            )
            content = content.replace(
                'with open("public/songs_simplified.json", "r"',
                'with open("public/unified_karaoke_db.json", "r"'
            )
            changes.append("更新資料庫載入路徑")
        
        # 2. 添加統一資料庫處理導入
        if 'from unified_scraper import UnifiedKaraokeScraper' not in content:
            # 在import區塊後添加
            import_lines = []
            other_lines = []
            in_imports = True
            
            for line in content.split('\n'):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    import_lines.append(line)
                elif line.strip() == '' and in_imports:
                    import_lines.append(line)
                else:
                    if in_imports and line.strip():
                        import_lines.append('from unified_scraper import UnifiedKaraokeScraper')
                        import_lines.append('')
                        in_imports = False
                    other_lines.append(line)
            
            if in_imports:  # 如果文件末尾還在imports
                import_lines.append('from unified_scraper import UnifiedKaraokeScraper')
                import_lines.append('')
            
            content = '\n'.join(import_lines + other_lines)
            changes.append("添加統一爬蟲導入")
        
        # 3. 添加兼容性注釋
        if '# 已更新為統一資料庫架構兼容' not in content:
            header_comment = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚠️ 此爬蟲已更新為統一資料庫架構兼容
建議使用 unified_scraper.py 或確保此爬蟲正確處理統一資料庫格式
"""

'''
            # 移除原有的shebang和encoding，添加新的header
            lines = content.split('\n')
            new_lines = []
            skip_header = True
            
            for line in lines:
                if skip_header:
                    if (line.startswith('#!') or 
                        line.startswith('# -*- coding:') or 
                        line.startswith('# -*- coding') or
                        line.strip().startswith('"""') or
                        line.strip() == ''):
                        continue
                    else:
                        skip_header = False
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            content = header_comment + '\n'.join(new_lines)
            changes.append("添加統一架構兼容性注釋")
        
        # 4. 檢查是否需要保存修改
        if content != original_content:
            # 創建備份
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # 保存修改
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ 已更新: {', '.join(changes)}")
            print(f"   📝 備份: {backup_path}")
            return True
        else:
            print(f"   ⏭️  無需修改")
            return False
            
    except Exception as e:
        print(f"   ❌ 更新失敗: {e}")
        return False

def main():
    print("🔧 爬蟲更新工具 - 統一資料庫架構")
    print("=" * 50)
    
    # 尋找所有Python爬蟲檔案
    scraper_patterns = [
        '*scraper*.py',
        'continuous*.py', 
        'enhanced*.py',
        'new_songs*.py',
        'search_*.py'
    ]
    
    scraper_files = []
    for pattern in scraper_patterns:
        scraper_files.extend(glob.glob(pattern))
    
    # 排除我們新創建的檔案和這個更新工具本身
    exclude_files = [
        'unified_scraper.py',
        'update_scrapers.py', 
        'database_unifier.py'
    ]
    
    scraper_files = [f for f in scraper_files if f not in exclude_files]
    scraper_files = list(set(scraper_files))  # 去重
    
    print(f"📋 發現 {len(scraper_files)} 個爬蟲檔案:")
    for i, file in enumerate(scraper_files, 1):
        print(f"   {i}. {file}")
    
    if not scraper_files:
        print("❌ 沒有找到需要更新的爬蟲檔案")
        return
    
    print()
    print("🚀 自動開始更新所有爬蟲...")
    
    print("\n🚀 開始更新...")
    updated_count = 0
    
    for file_path in scraper_files:
        if update_scraper_file(file_path):
            updated_count += 1
    
    print(f"\n🎉 更新完成!")
    print(f"   更新檔案: {updated_count}/{len(scraper_files)} 個")
    print(f"   建議: 使用 unified_scraper.py 進行新的爬取作業")
    print(f"   備份: 所有原檔案已備份為 .backup 檔案")
    
    # 建議下一步行動
    print(f"\n💡 建議操作:")
    print(f"1. 測試新的統一爬蟲: python3 unified_scraper.py")
    print(f"2. 檢查資料庫一致性: ls -la public/*.json") 
    print(f"3. 如有問題可還原: cp filename.backup filename")

if __name__ == "__main__":
    main()