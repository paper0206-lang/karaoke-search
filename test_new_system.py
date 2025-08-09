#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新的智能搜尋系統
"""

import requests
import time
import json

def wait_for_api(base_url="http://localhost:5001", max_attempts=10):
    """等待API服務啟動"""
    print("⏳ 等待API服務啟動...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/api/stats", timeout=5)
            if response.status_code == 200:
                print("✅ API服務已就緒")
                return True
        except:
            pass
        
        time.sleep(2)
        print(f"   嘗試 {attempt + 1}/{max_attempts}...")
    
    print("❌ API服務啟動超時")
    return False

def test_comprehensive_search(base_url="http://localhost:5001"):
    """測試綜合搜尋"""
    print("\n🧠 測試綜合搜尋功能...")
    
    test_queries = [
        "周杰倫",
        "青花瓷", 
        "告白氣球",
        "愛情",
        "鄧紫棋"
    ]
    
    for query in test_queries:
        try:
            print(f"\n🔍 測試搜尋: {query}")
            
            response = requests.get(
                f"{base_url}/api/enhanced-search?keyword={query}",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    total = data.get('total', 0)
                    results = data.get('data', [])
                    
                    print(f"   ✅ 找到 {total} 首歌曲")
                    
                    # 顯示前3首
                    for i, song in enumerate(results[:3], 1):
                        song_name = song.get('歌名', 'N/A')
                        singer_name = song.get('歌手', 'N/A')
                        codes_count = len(song.get('編號資訊', []))
                        confidence = song.get('confidence', 0)
                        sources = song.get('sources', [])
                        
                        print(f"      {i}. {song_name} - {singer_name}")
                        print(f"         編號: {codes_count} 個 | 信心度: {confidence:.2f} | 來源: {', '.join(sources)}")
                else:
                    print(f"   ❌ 搜尋失敗: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ API請求失敗: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 測試 '{query}' 時出錯: {e}")
        
        time.sleep(1)  # 避免請求過快

def test_singer_search(base_url="http://localhost:5001"):
    """測試歌手專搜"""
    print("\n🎤 測試歌手專搜功能...")
    
    test_singers = ["周杰倫", "蔡依林", "鄧紫棋"]
    
    for singer in test_singers:
        try:
            print(f"\n👤 測試歌手: {singer}")
            
            response = requests.get(
                f"{base_url}/api/singer-search?singer={singer}",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    total = data.get('total', 0)
                    results = data.get('data', [])
                    
                    print(f"   ✅ 找到 {total} 首{singer}的歌曲")
                    
                    # 顯示前3首
                    for i, song in enumerate(results[:3], 1):
                        song_name = song.get('歌名', 'N/A')
                        codes_count = len(song.get('編號資訊', []))
                        
                        print(f"      {i}. {song_name} (編號: {codes_count} 個)")
                else:
                    print(f"   ❌ 搜尋失敗: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ API請求失敗: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 測試歌手 '{singer}' 時出錯: {e}")
        
        time.sleep(1)

def test_database_stats(base_url="http://localhost:5001"):
    """測試資料庫統計"""
    print("\n📊 測試資料庫統計...")
    
    try:
        response = requests.get(f"{base_url}/api/stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('stats', {})
                
                print("   ✅ 資料庫統計:")
                print(f"      📚 歌曲資料庫: {stats.get('songs_db_count', 'N/A'):,} 首")
                print(f"      🎤 歌手數量: {stats.get('singers_count', 'N/A')} 位")
                print(f"      🔄 統一資料庫: {stats.get('unified_db_songs', 'N/A'):,} 首")
                print(f"      🕒 更新時間: {stats.get('last_updated', 'N/A')}")
            else:
                print(f"   ❌ 取得統計失敗: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ 統計API請求失敗: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 測試統計時出錯: {e}")

def performance_test(base_url="http://localhost:5001"):
    """效能測試"""
    print("\n⚡ 效能測試...")
    
    test_queries = ["周杰倫", "愛情", "青花瓷"]
    total_time = 0
    successful_requests = 0
    
    for query in test_queries:
        try:
            start_time = time.time()
            
            response = requests.get(
                f"{base_url}/api/enhanced-search?keyword={query}",
                timeout=15
            )
            
            end_time = time.time()
            request_time = end_time - start_time
            total_time += request_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    successful_requests += 1
                    result_count = data.get('total', 0)
                    print(f"   🔍 {query}: {request_time:.2f}秒 ({result_count} 首歌)")
            
        except Exception as e:
            print(f"   ❌ {query}: 測試失敗 ({e})")
    
    if successful_requests > 0:
        avg_time = total_time / successful_requests
        print(f"\n   📈 平均回應時間: {avg_time:.2f} 秒")
        print(f"   ✅ 成功率: {successful_requests}/{len(test_queries)} ({successful_requests/len(test_queries)*100:.1f}%)")
    else:
        print("   ❌ 所有效能測試都失敗了")

def main():
    """主測試程序"""
    print("🧪 智能搜尋系統測試開始")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    # 等待API服務
    if not wait_for_api(base_url):
        print("❌ 無法連接到API服務，請確認服務已啟動")
        return
    
    # 執行各種測試
    test_database_stats(base_url)
    test_comprehensive_search(base_url)
    test_singer_search(base_url)
    performance_test(base_url)
    
    print("\n" + "=" * 50)
    print("🎉 測試完成！")
    print()
    print("💡 如果所有測試都通過，你的新搜尋系統已經準備就緒！")
    print("   可以開始使用 new_frontend.html 來體驗新功能了！")

if __name__ == "__main__":
    main()