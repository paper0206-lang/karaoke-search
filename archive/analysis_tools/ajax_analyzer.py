#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入分析：AJAX請求和隱藏分頁機制檢測
如果ViewState無效，可能存在AJAX或其他動態載入機制
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import quote, urljoin, urlparse
import time

class AjaxAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest'  # 標識為AJAX請求
        })
        
    def analyze_javascript_patterns(self, company="音圓"):
        """深度分析JavaScript中的AJAX和分頁模式"""
        print("🔍 JavaScript深度分析：尋找AJAX分頁機制")
        print("=" * 60)
        
        try:
            url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ 無法獲取頁面: HTTP {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            scripts = soup.find_all('script')
            
            analysis = {
                'ajax_patterns': [],
                'fetch_patterns': [],
                'postback_patterns': [],
                'url_construction_patterns': [],
                'pagination_functions': [],
                'event_handlers': [],
                'hidden_endpoints': []
            }
            
            print(f"📋 分析 {len(scripts)} 個JavaScript區塊...")
            
            # 關鍵字和模式定義
            ajax_keywords = [
                'XMLHttpRequest', 'xhr', '$.ajax', '$.post', '$.get', 
                'fetch(', 'axios', 'ajaxCall', 'sendRequest'
            ]
            
            pagination_keywords = [
                'changePage', 'goToPage', 'loadPage', 'nextPage', 'prevPage',
                'pageIndex', 'currentPage', 'totalPages', 'PageSize'
            ]
            
            for i, script in enumerate(scripts):
                script_content = script.string or ''
                if not script_content.strip():
                    continue
                
                print(f"\\n📄 分析腳本 {i+1}...")
                
                # 查找AJAX模式
                for keyword in ajax_keywords:
                    if keyword.lower() in script_content.lower():
                        # 提取包含該關鍵字的行
                        lines = script_content.split('\\n')
                        for line_num, line in enumerate(lines):
                            if keyword.lower() in line.lower():
                                analysis['ajax_patterns'].append({
                                    'keyword': keyword,
                                    'line': line.strip(),
                                    'script_index': i,
                                    'line_number': line_num
                                })
                                print(f"   🌐 發現AJAX模式: {keyword} → {line.strip()[:80]}...")
                
                # 查找fetch模式
                fetch_matches = re.findall(r'fetch\\s*\\([^)]+\\)', script_content, re.IGNORECASE)
                for match in fetch_matches:
                    analysis['fetch_patterns'].append({
                        'pattern': match,
                        'script_index': i
                    })
                    print(f"   🔄 發現fetch調用: {match[:60]}...")
                
                # 查找分頁相關函數
                for keyword in pagination_keywords:
                    if keyword.lower() in script_content.lower():
                        # 嘗試提取函數定義
                        func_pattern = rf'function\\s+{re.escape(keyword)}\\s*\\([^)]*\\)\\s*{{[^}}]*}}'
                        func_matches = re.findall(func_pattern, script_content, re.IGNORECASE | re.DOTALL)
                        
                        if func_matches:
                            for func in func_matches:
                                analysis['pagination_functions'].append({
                                    'function_name': keyword,
                                    'definition': func[:200] + '...' if len(func) > 200 else func,
                                    'script_index': i
                                })
                                print(f"   📄 發現分頁函數: {keyword}")
                        else:
                            # 至少記錄提及該關鍵字的行
                            lines = script_content.split('\\n')
                            for line_num, line in enumerate(lines):
                                if keyword.lower() in line.lower():
                                    analysis['pagination_functions'].append({
                                        'function_name': keyword,
                                        'line': line.strip(),
                                        'script_index': i,
                                        'line_number': line_num
                                    })
                                    break
                
                # 查找URL構造模式
                url_patterns = [
                    r'["\'][^"\']*songs\.aspx[^"\']*["\']',
                    r'["\'][^"\']*\.aspx\?[^"\']*["\']', 
                    r'location\.href\s*=\s*["\'][^"\']*["\']',
                    r'window\.open\s*\(["\'][^"\']*["\']'
                ]
                
                for pattern in url_patterns:
                    matches = re.findall(pattern, script_content, re.IGNORECASE)
                    for match in matches:
                        analysis['url_construction_patterns'].append({
                            'pattern': match,
                            'script_index': i
                        })
                        print(f"   🔗 發現URL構造: {match}")
                
                # 查找事件處理器
                event_patterns = [
                    r'onclick\s*=\s*["\'][^"\']*["\']',
                    r'addEventListener\s*\(["\']click["\'][^)]*\)',
                    r'\$\([^)]*\)\.click\([^)]*\)'
                ]
                
                for pattern in event_patterns:
                    matches = re.findall(pattern, script_content, re.IGNORECASE)
                    for match in matches:
                        if 'page' in match.lower() or 'ajax' in match.lower():
                            analysis['event_handlers'].append({
                                'pattern': match,
                                'script_index': i
                            })
                            print(f"   🖱️ 發現相關事件處理: {match[:60]}...")
            
            return analysis
            
        except Exception as e:
            print(f"❌ JavaScript分析失敗: {e}")
            return None
    
    def test_potential_ajax_endpoints(self, company="音圓"):
        """測試可能的AJAX端點"""
        print("\\n🧪 測試潛在的AJAX端點")
        print("=" * 40)
        
        # 可能的AJAX端點
        potential_endpoints = [
            f"/songs.aspx?company={quote(company)}&page=2&ajax=1",
            f"/songs.aspx?company={quote(company)}&page=2&partial=1", 
            f"/ajax/songs.aspx?company={quote(company)}&page=2",
            f"/api/songs?company={quote(company)}&page=2",
            f"/services/songs.asmx/GetSongs",
            f"/handlers/songs.ashx?company={quote(company)}&page=2",
            f"/songs.aspx/GetSongsData",
            f"/Default.aspx/GetSongs"
        ]
        
        base_url = "https://song.corp.com.tw"
        results = []
        
        for endpoint in potential_endpoints:
            print(f"\\n🔍 測試端點: {endpoint}")
            
            try:
                full_url = urljoin(base_url, endpoint)
                
                # 嘗試GET請求
                response = self.session.get(full_url, timeout=10)
                
                result = {
                    'endpoint': endpoint,
                    'method': 'GET',
                    'status_code': response.status_code,
                    'content_type': response.headers.get('Content-Type', ''),
                    'content_length': len(response.text),
                    'success': False,
                    'data_type': 'unknown'
                }
                
                if response.status_code == 200:
                    content = response.text
                    
                    # 判斷返回內容類型
                    if content.strip().startswith('{') or content.strip().startswith('['):
                        result['data_type'] = 'json'
                        try:
                            json_data = json.loads(content)
                            result['success'] = True
                            result['json_keys'] = list(json_data.keys()) if isinstance(json_data, dict) else 'array'
                            print(f"   ✅ JSON響應: {result['json_keys']}")
                        except:
                            result['data_type'] = 'text'
                    elif '<' in content and '>' in content:
                        result['data_type'] = 'html'
                        soup = BeautifulSoup(content, 'html.parser')
                        songs = soup.select('a[href^="mv.aspx?id="]')
                        if songs:
                            result['success'] = True
                            result['songs_count'] = len(songs)
                            print(f"   ✅ HTML響應: {len(songs)} 首歌")
                        else:
                            print(f"   ⚠️ HTML響應但無歌曲數據")
                    else:
                        result['data_type'] = 'text'
                        print(f"   ⚠️ 文本響應: {len(content)} 字符")
                else:
                    print(f"   ❌ HTTP {response.status_code}")
                
                results.append(result)
                time.sleep(1)
                
            except Exception as e:
                result = {
                    'endpoint': endpoint,
                    'method': 'GET',
                    'error': str(e),
                    'success': False
                }
                results.append(result)
                print(f"   ❌ 錯誤: {e}")
        
        return results
    
    def test_postback_with_ajax_headers(self, company="音圓"):
        """使用AJAX頭部測試PostBack"""
        print("\\n🔄 使用AJAX頭部測試PostBack")
        print("=" * 40)
        
        try:
            # 先獲取初始ViewState
            url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ 無法獲取初始頁面: HTTP {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            viewstate = soup.find('input', {'name': '__VIEWSTATE'}).get('value', '')
            viewstate_gen = soup.find('input', {'name': '__VIEWSTATEGENERATOR'}).get('value', '')
            event_validation = soup.find('input', {'name': '__EVENTVALIDATION'}).get('value', '')
            
            # 設置AJAX頭部
            ajax_headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }
            
            # 更新session頭部
            self.session.headers.update(ajax_headers)
            
            # 測試不同的PostBack組合
            test_data = [
                {
                    '__VIEWSTATE': viewstate,
                    '__VIEWSTATEGENERATOR': viewstate_gen,
                    '__EVENTVALIDATION': event_validation,
                    '__EVENTTARGET': '',
                    '__EVENTARGUMENT': 'Page$2'
                },
                {
                    '__VIEWSTATE': viewstate,
                    '__VIEWSTATEGENERATOR': viewstate_gen,
                    '__EVENTVALIDATION': event_validation,
                    '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$GridView1',
                    '__EVENTARGUMENT': 'Page$2'
                }
            ]
            
            results = []
            
            for i, data in enumerate(test_data):
                print(f"\\n🧪 測試AJAX PostBack組合 {i+1}")
                
                try:
                    response = self.session.post(url, data=data, timeout=15)
                    
                    result = {
                        'combination_index': i,
                        'status_code': response.status_code,
                        'content_type': response.headers.get('Content-Type', ''),
                        'content_length': len(response.text),
                        'success': False
                    }
                    
                    if response.status_code == 200:
                        content = response.text
                        
                        # 檢查是否為JSON響應
                        if content.strip().startswith('{'):
                            try:
                                json_data = json.loads(content)
                                result['data_type'] = 'json'
                                result['json_data'] = json_data
                                result['success'] = True
                                print(f"   ✅ 獲得JSON響應")
                            except:
                                result['data_type'] = 'text'
                        else:
                            # 檢查HTML響應
                            soup = BeautifulSoup(content, 'html.parser')
                            songs = soup.select('a[href^="mv.aspx?id="]')
                            
                            if songs:
                                first_song = songs[0].get_text().strip().split()
                                if len(first_song) >= 4:
                                    result['data_type'] = 'html'
                                    result['songs_count'] = len(songs)
                                    result['first_song'] = {
                                        'id': first_song[0],
                                        'name': first_song[1],
                                        'artist': ' '.join(first_song[3:])
                                    }
                                    result['success'] = True
                                    print(f"   ✅ HTML響應: {first_song[0]} - {first_song[1]}")
                    else:
                        print(f"   ❌ HTTP {response.status_code}")
                    
                    results.append(result)
                    time.sleep(2)
                    
                except Exception as e:
                    result = {
                        'combination_index': i,
                        'error': str(e),
                        'success': False
                    }
                    results.append(result)
                    print(f"   ❌ 錯誤: {e}")
            
            return results
            
        except Exception as e:
            print(f"❌ AJAX PostBack測試失敗: {e}")
            return None
    
    def analyze_network_patterns(self, company="音圓"):
        """分析網絡請求模式，尋找可能被忽略的請求"""
        print("\\n🌐 網絡請求模式分析")
        print("=" * 30)
        
        patterns_found = {
            'javascript_ajax_calls': [],
            'form_submission_patterns': [],
            'hidden_iframe_patterns': [],
            'meta_refresh_patterns': []
        }
        
        try:
            url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 檢查隱藏的iframe
                iframes = soup.find_all('iframe')
                for iframe in iframes:
                    src = iframe.get('src', '')
                    if src:
                        patterns_found['hidden_iframe_patterns'].append(src)
                        print(f"🖼️ 發現iframe: {src}")
                
                # 檢查meta refresh
                meta_refresh = soup.find_all('meta', {'http-equiv': 'refresh'})
                for meta in meta_refresh:
                    content = meta.get('content', '')
                    if content:
                        patterns_found['meta_refresh_patterns'].append(content)
                        print(f"🔄 發現meta refresh: {content}")
                
                # 檢查表單提交目標
                forms = soup.find_all('form')
                for form in forms:
                    action = form.get('action', '')
                    method = form.get('method', 'GET')
                    onsubmit = form.get('onsubmit', '')
                    
                    pattern = {
                        'action': action,
                        'method': method.upper(),
                        'onsubmit': onsubmit
                    }
                    patterns_found['form_submission_patterns'].append(pattern)
                    print(f"📝 表單模式: {method} → {action}")
                    if onsubmit:
                        print(f"   onSubmit: {onsubmit[:60]}...")
        
        except Exception as e:
            print(f"❌ 網絡模式分析失敗: {e}")
        
        return patterns_found

def main():
    analyzer = AjaxAnalyzer()
    
    print("🔬 開始AJAX和隱藏分頁機制深度分析")
    print("=" * 60)
    
    # JavaScript深度分析
    js_analysis = analyzer.analyze_javascript_patterns("音圓")
    
    # 測試AJAX端點
    ajax_endpoints = analyzer.test_potential_ajax_endpoints("音圓")
    
    # AJAX PostBack測試
    ajax_postback = analyzer.test_postback_with_ajax_headers("音圓")
    
    # 網絡模式分析
    network_patterns = analyzer.analyze_network_patterns("音圓")
    
    # 綜合分析結果
    comprehensive_analysis = {
        'javascript_analysis': js_analysis,
        'ajax_endpoints_test': ajax_endpoints,
        'ajax_postback_test': ajax_postback,
        'network_patterns': network_patterns
    }
    
    # 保存結果
    filename = "ajax_deep_analysis.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_analysis, f, ensure_ascii=False, indent=2)
        print(f"\\n💾 深度分析結果已保存到: {filename}")
    except Exception as e:
        print(f"\\n❌ 保存失敗: {e}")
    
    # 總結發現
    print("\\n🎯 深度分析總結:")
    
    ajax_found = False
    if js_analysis:
        ajax_count = len(js_analysis.get('ajax_patterns', [])) + len(js_analysis.get('fetch_patterns', []))
        if ajax_count > 0:
            print(f"  🌐 發現 {ajax_count} 個AJAX/Fetch模式")
            ajax_found = True
    
    successful_endpoints = [r for r in ajax_endpoints if r.get('success', False)] if ajax_endpoints else []
    if successful_endpoints:
        print(f"  ✅ 發現 {len(successful_endpoints)} 個有效AJAX端點")
        ajax_found = True
    
    if ajax_postback and any(r.get('success', False) for r in ajax_postback):
        print(f"  🔄 AJAX PostBack可能有效")
        ajax_found = True
    
    if not ajax_found:
        print("  😔 未發現有效的AJAX分頁機制")
        print("  💡 結論：網站可能確實沒有真實的分頁功能")
        print("     建議：接受現實，每家公司可能只有約100首真實歌曲")
    else:
        print("  🎉 發現潛在突破點！建議深入測試有效的AJAX模式")

if __name__ == "__main__":
    main()