#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復JSON格式錯誤
"""

import json
import re

def fix_json_file():
    """修復singers_data.json中的格式錯誤"""
    
    print("🔧 開始修復JSON格式錯誤...")
    
    # 讀取原始文件
    try:
        with open('public/singers_data.json', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 原始文件大小: {len(content):,} 字符")
        
        # 備份原始文件
        with open('public/singers_data.json.backup', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("💾 已創建備份文件: singers_data.json.backup")
        
        # 修復常見的JSON格式問題
        fixes_applied = []
        
        # 1. 移除行首的感嘆號
        if re.search(r'^\s*!', content, re.MULTILINE):
            content = re.sub(r'^\s*!', '', content, flags=re.MULTILINE)
            fixes_applied.append("移除行首感嘆號")
        
        # 2. 修復雙引號問題
        if '""' in content:
            content = content.replace('""', '"')
            fixes_applied.append("修復雙引號")
        
        # 3. 移除多餘的逗號
        if re.search(r',\s*}', content):
            content = re.sub(r',(\s*})', r'\1', content)
            fixes_applied.append("移除多餘逗號")
        
        # 4. 修復換行問題
        if re.search(r'"\s*\n\s*"', content):
            content = re.sub(r'"\s*\n\s*"', '""', content)
            fixes_applied.append("修復換行問題")
        
        print(f"🔧 應用的修復: {', '.join(fixes_applied) if fixes_applied else '無需修復'}")
        
        # 嘗試解析修復後的JSON
        try:
            data = json.loads(content)
            print("✅ JSON格式驗證通過")
            
            # 統計信息
            total_singers = len(data)
            total_songs = sum(len(singer_info.get('歌曲清單', [])) for singer_info in data.values())
            
            print(f"📊 資料庫統計:")
            print(f"   歌手總數: {total_singers:,} 位")
            print(f"   歌曲總數: {total_songs:,} 首")
            
            # 寫入修復後的文件
            with open('public/singers_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print("💾 已保存修復後的文件")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失敗: {e}")
            print(f"錯誤位置: 第 {e.lineno} 行, 第 {e.colno} 列")
            
            # 恢復備份
            with open('public/singers_data.json.backup', 'r', encoding='utf-8') as f:
                original_content = f.read()
            with open('public/singers_data.json', 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            print("🔄 已恢復原始文件")
            return False
            
    except Exception as e:
        print(f"❌ 文件處理失敗: {e}")
        return False

def main():
    if fix_json_file():
        print("\n🎉 JSON修復完成！")
        print("💡 可以重新運行資料庫分析工具")
    else:
        print("\n❌ JSON修復失敗")
        print("💡 可能需要手動檢查文件格式")

if __name__ == "__main__":
    main()