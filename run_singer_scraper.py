#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌手優先爬蟲 - 背景執行版本
直接執行，無需互動輸入
"""

import sys
from singer_focused_scraper import SingerFocusedScraper

def main():
    # 預設執行模式：標準歌手爬取 (前20位)
    mode = "standard"  # 可改為: quick(10位), standard(20位), deep(40位)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    
    # 優先歌手列表
    priority_singers = [
        # 天王天后級 (前10位)
        "周杰倫", "蔡依林", "林俊傑", "張惠妹", "五月天",
        "孫燕姿", "梁靜茹", "王力宏", "陶喆", "鄧紫棋",
        
        # 經典歌手 (11-20位)
        "張學友", "劉德華", "郭富城", "黎明", "張國榮",
        "梅艷芳", "鄧麗君", "蔡琴", "鳳飛飛", "費玉清",
        
        # 新生代熱門 (21-30位)
        "告五人", "茄子蛋", "持修", "ØZI", "高爾宣",
        "LEO王", "9m88", "吳卓源", "血肉果汁機", "理想混蛋",
        
        # 搖滾樂團 (31-40位)
        "蘇打綠", "信樂團", "F.I.R", "八三夭", "滅火器",
        "四分衛", "黑色柳丁", "董事長樂團", "脫拉庫", "1976"
    ]
    
    # 根據模式選擇歌手數量
    if mode == "quick":
        target_singers = priority_singers[:10]
        description = "快速模式 (前10位天王天后)"
    elif mode == "deep":
        target_singers = priority_singers[:40]
        description = "深度模式 (前40位精選歌手)"
    else:  # standard
        target_singers = priority_singers[:20]
        description = "標準模式 (前20位優先歌手)"
    
    print("🎤 歌手優先爬蟲 - 背景執行版")
    print("突破50首限制，完整收錄歌手作品")
    print("=" * 50)
    print(f"📋 執行模式: {description}")
    print(f"🎯 目標歌手: {len(target_singers)} 位")
    print(f"⏱️  預估時間: {len(target_singers) * 3} 分鐘")
    print(f"📊 使用5種策略突破50首限制")
    
    # 顯示目標歌手
    print(f"\n🎤 目標歌手列表:")
    for i, singer in enumerate(target_singers, 1):
        print(f"   {i:2d}. {singer}")
    
    print(f"\n🚀 開始執行...")
    
    # 執行爬蟲
    scraper = SingerFocusedScraper(max_workers=2)
    
    try:
        result = scraper.scrape_singers_batch(target_singers, save_frequency=3)
        
        print(f"\n🎉 執行完成!")
        print(f"📊 最終結果:")
        print(f"   新增歌曲: {result} 首")
        print(f"   總歌曲數: {scraper.unified_db['metadata']['total_songs']:,} 首")
        print(f"   總歌手數: {scraper.unified_db['metadata']['total_singers']:,} 位")
        
        # 自動推送到GitHub
        if result > 0:
            print(f"\n🚀 自動推送到GitHub...")
            import subprocess
            from datetime import datetime
            
            try:
                # 添加檔案到Git
                subprocess.run(['git', 'add', 'public/unified_karaoke_db.json', 'public/songs_simplified.json', 'public/singers_data.json'], check=True)
                
                # 準備提交訊息
                commit_msg = f"""歌手優先爬蟲更新: {description}

📊 執行統計:
- 處理歌手: {len(target_singers)} 位
- 新增歌曲: {result} 首
- 總歌曲數: {scraper.unified_db['metadata']['total_songs']:,} 首
- 總歌手數: {scraper.unified_db['metadata']['total_singers']:,} 位

🎯 處理歌手: {', '.join(target_singers[:10])}{'...' if len(target_singers) > 10 else ''}

🚀 歌手優先策略:
- 使用5種搜尋策略突破50首限制
- 每位歌手平均收錄 {result//len(target_singers) if len(target_singers) > 0 else 0} 首新歌曲
- 自動整合到統一資料庫架構

⏰ 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""
                
                # 提交變更
                subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
                
                # 推送到遠端
                subprocess.run(['git', 'push'], check=True)
                
                print(f"✅ 成功推送到GitHub")
                print(f"🌐 網站將在2-3分鐘內更新")
                print(f"📱 查看結果: https://karaoke-search-theta.vercel.app")
                
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Git操作失敗: {e}")
                print(f"📝 請手動執行: git add . && git commit && git push")
        else:
            print(f"\n📝 沒有新增歌曲，跳過推送")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ 用戶中斷執行")
        scraper.save_unified_database()
        print(f"💾 已保存當前進度")
        
    except Exception as e:
        print(f"\n❌ 執行出錯: {e}")
        scraper.save_unified_database()
        print(f"💾 已保存當前進度")

if __name__ == "__main__":
    main()