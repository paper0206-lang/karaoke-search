#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真實用戶搜尋行為分析器
測試網站對真實搜尋關鍵字（歌名、歌手）的回應
vs 公司名稱搜尋的差異性
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import quote, urlencode
import random

class RealSearchAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        
    def analyze_search_mechanism(self):
        """分析網站的搜尋機制"""
        print("🔍 分析網站搜尋機制")
        print("=" * 40)
        
        try:
            # 獲取主頁面
            response = self.session.get("https://song.corp.com.tw/", timeout=15)
            if response.status_code != 200:
                print(f"❌ 無法訪問首頁: HTTP {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有搜尋相關的表單和輸入框
            search_forms = []
            search_inputs = []
            
            # 分析表單
            forms = soup.find_all('form')
            for i, form in enumerate(forms):
                action = form.get('action', '')
                method = form.get('method', 'GET')
                
                # 查找輸入框
                inputs = form.find_all(['input', 'select', 'textarea'])
                form_inputs = []
                
                for inp in inputs:
                    input_type = inp.get('type', 'text')
                    name = inp.get('name', '')
                    placeholder = inp.get('placeholder', '')
                    value = inp.get('value', '')
                    
                    form_inputs.append({
                        'type': input_type,
                        'name': name,
                        'placeholder': placeholder,
                        'value': value
                    })
                
                search_forms.append({
                    'index': i,
                    'action': action,
                    'method': method,
                    'inputs': form_inputs
                })
                
                print(f"📝 表單 {i+1}: {method} → {action}")
                for inp in form_inputs:
                    if inp['placeholder'] or 'search' in inp['name'].lower():
                        print(f"   🔍 搜尋框: {inp['name']} | {inp['placeholder']}")
            
            # 查找所有輸入框（不限於表單內）
            all_inputs = soup.find_all(['input'], type='text')
            for inp in all_inputs:
                name = inp.get('name', '')
                placeholder = inp.get('placeholder', '')
                if placeholder and ('搜' in placeholder or 'search' in placeholder.lower()):
                    search_inputs.append({
                        'name': name,
                        'placeholder': placeholder,
                        'parent_form': inp.find_parent('form')
                    })
            
            return {
                'search_forms': search_forms,
                'search_inputs': search_inputs,
                'page_title': soup.title.string if soup.title else 'No title'
            }
            
        except Exception as e:
            print(f"❌ 搜尋機制分析失敗: {e}")
            return None
    
    def test_real_search_queries(self):
        """測試真實的搜尋查詢"""
        print("\n🎵 測試真實搜尋查詢")
        print("=" * 30)
        
        # 真實用戶會搜尋的關鍵字
        real_queries = [
            # 熱門歌手
            "周杰倫", "蔡依林", "張惠妹", "五月天", "林俊傑",
            # 經典歌曲
            "月亮代表我的心", "童話", "聽海", "愛你", "小幸運",
            # 台語歌手
            "江蕙", "張秀卿", "陳雷", "黃乙玲", "龍千玉",
            # 台語經典
            "家後", "心事誰人知", "愛人", "月光", "酒後的心聲"
        ]
        
        results = []
        
        for query in real_queries[:10]:  # 測試前10個
            print(f"\n🔍 測試搜尋: '{query}'")
            
            result = {
                'query': query,
                'success': False,
                'songs_found': 0,
                'first_song': None,
                'search_url': '',
                'error': None
            }
            
            try:
                # 方法1: 直接搜尋URL (如果存在搜尋端點)
                search_url = f"https://song.corp.com.tw/search.aspx?q={quote(query)}"
                response = self.session.get(search_url, timeout=15)
                
                result['search_url'] = search_url
                result['status_code'] = response.status_code
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    songs = soup.select('a[href^="mv.aspx?id="]')
                    
                    if songs:
                        result['success'] = True
                        result['songs_found'] = len(songs)
                        
                        # 解析第一首歌
                        first_song_text = songs[0].get_text().strip()
                        song_parts = first_song_text.split()
                        if len(song_parts) >= 3:
                            result['first_song'] = {
                                'text': first_song_text,
                                'id': song_parts[0],
                                'title': song_parts[1],
                                'artist': ' '.join(song_parts[2:])
                            }
                        
                        print(f"   ✅ 找到 {len(songs)} 首歌")
                        print(f"   🎵 第一首: {first_song_text[:50]}...")
                    else:
                        print(f"   ❌ 無搜尋結果")
                        # 檢查是否有錯誤訊息
                        error_msgs = soup.find_all(text=lambda t: t and ('沒有' in t or '找不到' in t or '無結果' in t))
                        if error_msgs:
                            result['error'] = error_msgs[0].strip()
                else:
                    print(f"   ❌ HTTP {response.status_code}")
                    result['error'] = f'HTTP {response.status_code}'
                
            except Exception as e:
                print(f"   ❌ 搜尋失敗: {e}")
                result['error'] = str(e)
            
            results.append(result)
            time.sleep(random.uniform(2, 4))  # 避免被檢測
        
        return results
    
    def test_post_search(self):
        """測試POST方式的搜尋"""
        print("\n📡 測試POST搜尋")
        print("=" * 20)
        
        # 先獲取可能的搜尋表單
        try:
            response = self.session.get("https://song.corp.com.tw/", timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找搜尋表單
            search_form = None
            forms = soup.find_all('form')
            
            for form in forms:
                inputs = form.find_all('input')
                for inp in inputs:
                    placeholder = inp.get('placeholder', '')
                    if '搜' in placeholder or 'search' in placeholder.lower():
                        search_form = {
                            'action': form.get('action', './'),
                            'method': form.get('method', 'POST'),
                            'search_input_name': inp.get('name', 'q')
                        }
                        break
                if search_form:
                    break
            
            if not search_form:
                print("❌ 未找到搜尋表單")
                return None
            
            print(f"📝 找到搜尋表單: {search_form}")
            
            # 測試POST搜尋
            test_queries = ["周杰倫", "月光", "愛你"]
            results = []
            
            for query in test_queries:
                print(f"\n🔍 POST搜尋: '{query}'")
                
                try:
                    # 準備POST數據
                    post_data = {search_form['search_input_name']: query}
                    
                    # 如果需要ViewState等ASP.NET字段
                    if 'aspx' in search_form['action']:
                        # 獲取ViewState
                        viewstate_input = soup.find('input', {'name': '__VIEWSTATE'})
                        if viewstate_input:
                            post_data['__VIEWSTATE'] = viewstate_input.get('value', '')
                    
                    search_url = f"https://song.corp.com.tw{search_form['action']}"
                    response = self.session.post(search_url, data=post_data, timeout=15)
                    
                    result = {
                        'query': query,
                        'method': 'POST',
                        'status_code': response.status_code,
                        'success': False,
                        'songs_found': 0
                    }
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        songs = soup.select('a[href^="mv.aspx?id="]')
                        
                        if songs:
                            result['success'] = True
                            result['songs_found'] = len(songs)
                            print(f"   ✅ 找到 {len(songs)} 首歌")
                        else:
                            print(f"   ❌ 無搜尋結果")
                    else:
                        print(f"   ❌ HTTP {response.status_code}")
                    
                    results.append(result)
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"   ❌ POST搜尋失敗: {e}")
                    results.append({
                        'query': query,
                        'method': 'POST',
                        'error': str(e),
                        'success': False
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ POST搜尋測試失敗: {e}")
            return None
    
    def compare_company_vs_real_search(self):
        """比較公司搜尋 vs 真實搜尋的結果差異"""
        print("\n⚖️ 公司搜尋 vs 真實搜尋比較")
        print("=" * 40)
        
        comparison = {
            'company_search': None,
            'real_search': None,
            'analysis': {}
        }
        
        try:
            # 公司搜尋結果（我們已知的）
            print("📊 獲取公司搜尋結果...")
            company_url = "https://song.corp.com.tw/songs.aspx?company=音圓"
            response = self.session.get(company_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                company_songs = soup.select('a[href^="mv.aspx?id="]')
                
                comparison['company_search'] = {
                    'url': company_url,
                    'songs_count': len(company_songs),
                    'first_song': company_songs[0].get_text().strip() if company_songs else None,
                    'success': len(company_songs) > 0
                }
                
                print(f"   ✅ 公司搜尋: {len(company_songs)} 首歌")
                if company_songs:
                    print(f"   🎵 第一首: {company_songs[0].get_text().strip()}")
            
            # 真實搜尋結果（測試"音圓"作為搜尋關鍵字）
            print("\n🔍 測試'音圓'作為搜尋關鍵字...")
            real_search_url = f"https://song.corp.com.tw/search.aspx?q={quote('音圓')}"
            response = self.session.get(real_search_url, timeout=15)
            
            comparison['real_search'] = {
                'url': real_search_url,
                'status_code': response.status_code,
                'songs_count': 0,
                'success': False
            }
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                real_songs = soup.select('a[href^="mv.aspx?id="]')
                
                comparison['real_search']['songs_count'] = len(real_songs)
                comparison['real_search']['success'] = len(real_songs) > 0
                comparison['real_search']['first_song'] = real_songs[0].get_text().strip() if real_songs else None
                
                print(f"   📊 真實搜尋: {len(real_songs)} 首歌")
                if real_songs:
                    print(f"   🎵 第一首: {real_songs[0].get_text().strip()}")
            else:
                print(f"   ❌ 真實搜尋失敗: HTTP {response.status_code}")
            
            # 分析差異
            if comparison['company_search'] and comparison['real_search']:
                company_success = comparison['company_search']['success']
                real_success = comparison['real_search']['success']
                
                comparison['analysis'] = {
                    'company_works': company_success,
                    'real_search_works': real_success,
                    'different_mechanisms': company_success != real_success,
                    'conclusion': None
                }
                
                if company_success and not real_success:
                    comparison['analysis']['conclusion'] = "公司搜尋是特殊瀏覽模式，真實搜尋機制不同或無效"
                elif not company_success and real_success:
                    comparison['analysis']['conclusion'] = "真實搜尋有效，公司瀏覽模式失效"
                elif company_success and real_success:
                    # 比較結果是否相同
                    same_results = (
                        comparison['company_search']['first_song'] == 
                        comparison['real_search']['first_song']
                    )
                    comparison['analysis']['same_results'] = same_results
                    if same_results:
                        comparison['analysis']['conclusion'] = "兩種方式返回相同結果"
                    else:
                        comparison['analysis']['conclusion'] = "兩種方式返回不同結果！"
                else:
                    comparison['analysis']['conclusion'] = "兩種方式都無效"
                
                print(f"\n💡 結論: {comparison['analysis']['conclusion']}")
            
        except Exception as e:
            print(f"❌ 比較分析失敗: {e}")
        
        return comparison

def main():
    analyzer = RealSearchAnalyzer()
    
    print("🔬 真實用戶搜尋行為分析")
    print("=" * 50)
    
    # 分析搜尋機制
    search_mechanism = analyzer.analyze_search_mechanism()
    
    # 測試真實搜尋查詢
    real_search_results = analyzer.test_real_search_queries()
    
    # 測試POST搜尋
    post_search_results = analyzer.test_post_search()
    
    # 比較公司搜尋 vs 真實搜尋
    comparison = analyzer.compare_company_vs_real_search()
    
    # 綜合結果
    comprehensive_analysis = {
        'search_mechanism': search_mechanism,
        'real_search_results': real_search_results,
        'post_search_results': post_search_results,
        'company_vs_real_comparison': comparison,
        'analysis_timestamp': time.strftime('%Y%m%d_%H%M%S')
    }
    
    # 保存結果
    filename = f"real_search_analysis_{comprehensive_analysis['analysis_timestamp']}.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_analysis, f, ensure_ascii=False, indent=2)
        print(f"\n💾 分析結果已保存到: {filename}")
    except Exception as e:
        print(f"\n❌ 保存失敗: {e}")
    
    # 分析總結
    print("\n🎯 真實搜尋分析總結:")
    
    if real_search_results:
        successful_searches = [r for r in real_search_results if r['success']]
        print(f"  🔍 真實搜尋成功率: {len(successful_searches)}/{len(real_search_results)}")
        
        if successful_searches:
            print(f"  ✅ 有效搜尋發現！建議使用真實搜尋策略")
            for result in successful_searches[:3]:
                print(f"     '{result['query']}' → {result['songs_found']} 首歌")
        else:
            print(f"  😔 真實搜尋全部失效")
    
    if comparison and comparison.get('analysis'):
        analysis = comparison['analysis']
        if analysis.get('different_mechanisms'):
            print(f"  🎯 確認：公司瀏覽 ≠ 真實搜尋機制")
            print(f"  💡 結論: {analysis.get('conclusion', '未知')}")
        
    print(f"\n📈 建議下一步:")
    if successful_searches:
        print(f"     1. 使用有效的真實搜尋關鍵字重新設計爬蟲")
        print(f"     2. 測試搜尋結果的分頁機制")
        print(f"     3. 分析搜尋結果與公司瀏覽的數據差異")
    else:
        print(f"     1. 網站搜尋功能可能已關閉或需要特殊參數")
        print(f"     2. 考慮其他突破策略或接受現有數據規模")

if __name__ == "__main__":
    main()