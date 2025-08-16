#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
階段二：ViewState深度解碼分析工具
嘗試理解ViewState結構並測試不同的PostBack組合
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import base64
from urllib.parse import quote, unquote, urlencode
import time
import struct

class ViewStateDecoder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://song.corp.com.tw/'
        })
        
    def get_initial_state(self, company="音圓"):
        """獲取初始頁面狀態"""
        print(f"🔍 階段二：獲取 {company} 初始ViewState")
        print("=" * 50)
        
        try:
            url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                state = {
                    'viewstate': soup.find('input', {'name': '__VIEWSTATE'}).get('value', ''),
                    'viewstate_generator': soup.find('input', {'name': '__VIEWSTATEGENERATOR'}).get('value', ''),
                    'event_validation': soup.find('input', {'name': '__EVENTVALIDATION'}).get('value', ''),
                    'url': url,
                    'cookies': dict(self.session.cookies)
                }
                
                print(f"✅ 成功獲取初始狀態")
                print(f"   ViewState長度: {len(state['viewstate'])}")
                print(f"   Generator: {state['viewstate_generator']}")
                print(f"   Cookies: {len(state['cookies'])} 個")
                
                return state
            else:
                print(f"❌ 獲取失敗: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 獲取初始狀態失敗: {e}")
            return None
    
    def analyze_viewstate_structure(self, viewstate):
        """分析ViewState的詳細結構"""
        print("\\n🔬 ViewState結構深度分析:")
        
        try:
            decoded = base64.b64decode(viewstate)
            print(f"  解碼後長度: {len(decoded)} 字節")
            
            # 分析前100字節的結構
            hex_preview = decoded[:100].hex()
            print(f"  十六進制預覽: {hex_preview[:100]}...")
            
            # 嘗試解析ASP.NET ViewState格式
            analysis = {
                'total_length': len(decoded),
                'hex_preview': hex_preview,
                'possible_structures': [],
                'string_patterns': [],
                'control_patterns': []
            }
            
            # 查找可能的字符串模式
            try:
                text = decoded.decode('utf-8', errors='ignore')
                # 查找可能的控件名稱或頁面相關字符串
                control_patterns = re.findall(r'ctl\\d+\\$\\w+', text)
                if control_patterns:
                    analysis['control_patterns'] = control_patterns[:10]
                    print(f"  🎯 發現控件模式: {control_patterns[:5]}")
                    
                page_patterns = re.findall(r'[Pp]age\\w*', text) 
                if page_patterns:
                    analysis['string_patterns'].extend(page_patterns[:5])
                    print(f"  📄 發現頁面模式: {page_patterns[:3]}")
                    
            except:
                print("  ⚠️ 無法以UTF-8解碼字符串")
            
            # 嘗試查找結構標記
            if decoded[:4] == b'\\x00\\x01\\x00\\x00':
                analysis['possible_structures'].append('Standard .NET ViewState header')
            
            # 查找可能的長度字段
            for i in range(0, min(20, len(decoded)-4), 4):
                value = struct.unpack('<I', decoded[i:i+4])[0]  # Little-endian 32-bit int
                if 100 <= value <= len(decoded):
                    analysis['possible_structures'].append(f'Length field at offset {i}: {value}')
            
            return analysis
            
        except Exception as e:
            print(f"  ❌ ViewState結構分析失敗: {e}")
            return None
    
    def test_postback_combinations(self, initial_state, company="音圓"):
        """測試不同的PostBack參數組合"""
        print("\\n🧪 PostBack參數組合測試:")
        
        # 可能的PostBack目標和參數組合
        test_combinations = [
            # 標準分頁模式
            {'target': '', 'argument': 'Page$2'},
            {'target': '', 'argument': 'Page$Next'},  
            {'target': 'ctl00$ContentPlaceHolder1$GridView1', 'argument': 'Page$2'},
            {'target': 'ctl00$MainContent$GridView1', 'argument': 'Page$2'},
            {'target': 'GridView1', 'argument': 'Page$2'},
            
            # DataList/Repeater模式
            {'target': 'ctl00$ContentPlaceHolder1$DataList1', 'argument': 'Page$2'},
            {'target': 'ctl00$MainContent$DataList1', 'argument': 'Page$2'},
            
            # 自定義分頁控件模式  
            {'target': 'ctl00$ContentPlaceHolder1$PagingControl', 'argument': '2'},
            {'target': 'ctl00$MainContent$PagingControl', 'argument': '2'},
            
            # 分頁按鈕模式
            {'target': 'ctl00$ContentPlaceHolder1$btnNext', 'argument': ''},
            {'target': 'ctl00$MainContent$btnNext', 'argument': ''},
            
            # 其他可能的組合
            {'target': 'PageIndexChanged', 'argument': '2'},
            {'target': 'ChangePage', 'argument': '2'},
            {'target': 'GoToPage', 'argument': '2'}
        ]
        
        results = []
        
        for i, combo in enumerate(test_combinations[:8]):  # 限制測試數量
            print(f"\\n  🧪 測試組合 {i+1}: {combo}")
            
            try:
                # 構造POST數據
                post_data = {
                    '__VIEWSTATE': initial_state['viewstate'],
                    '__VIEWSTATEGENERATOR': initial_state['viewstate_generator'], 
                    '__EVENTVALIDATION': initial_state['event_validation'],
                    '__EVENTTARGET': combo['target'],
                    '__EVENTARGUMENT': combo['argument']
                }
                
                # 發送POST請求
                url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}"
                response = self.session.post(url, data=post_data, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    song_links = soup.select('a[href^="mv.aspx?id="]')
                    
                    if song_links:
                        first_song = song_links[0].get_text().strip().split()
                        if len(first_song) >= 4:
                            song_id = first_song[0]
                            song_name = first_song[1]
                            artist = ' '.join(first_song[3:])
                            
                            result = {
                                'combination': combo,
                                'success': True,
                                'first_song_id': song_id,
                                'first_song_name': song_name,
                                'first_song_artist': artist,
                                'total_songs': len(song_links),
                                'response_url': response.url
                            }
                            
                            print(f"     ✅ 成功: {song_id} - {song_name} - {artist}")
                            print(f"     📊 歌曲數: {len(song_links)}")
                        else:
                            result = {
                                'combination': combo,
                                'success': False,
                                'error': 'Cannot parse first song',
                                'total_songs': len(song_links)
                            }
                            print(f"     ❌ 無法解析第一首歌")
                    else:
                        result = {
                            'combination': combo,
                            'success': False,
                            'error': 'No songs found',
                            'total_songs': 0
                        }
                        print(f"     ❌ 沒有找到歌曲")
                else:
                    result = {
                        'combination': combo,
                        'success': False,
                        'error': f'HTTP {response.status_code}',
                        'total_songs': 0
                    }
                    print(f"     ❌ HTTP錯誤: {response.status_code}")
                
                results.append(result)
                time.sleep(2)  # 延遲避免被檢測
                
            except Exception as e:
                result = {
                    'combination': combo,
                    'success': False,
                    'error': str(e),
                    'total_songs': 0
                }
                results.append(result)
                print(f"     ❌ 異常: {e}")
        
        return results
    
    def analyze_differences(self, results):
        """分析不同PostBack結果的差異"""
        print("\\n📊 PostBack結果差異分析:")
        
        # 統計成功的組合
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        print(f"  ✅ 成功組合: {len(successful_results)}")
        print(f"  ❌ 失敗組合: {len(failed_results)}")
        
        if successful_results:
            # 檢查是否有不同的第一首歌
            unique_first_songs = set()
            for result in successful_results:
                if 'first_song_id' in result:
                    unique_first_songs.add(f"{result['first_song_id']}_{result['first_song_artist']}")
            
            print(f"  🎵 不同的第一首歌: {len(unique_first_songs)}")
            
            if len(unique_first_songs) > 1:
                print("  🎉 發現不同內容！成功的組合:")
                for result in successful_results:
                    if 'first_song_id' in result:
                        combo = result['combination']
                        print(f"     🎯 {combo['target']} | {combo['argument']} → {result['first_song_id']} - {result['first_song_name']}")
                return True
            else:
                print("  😔 所有成功組合都返回相同內容")
                if successful_results:
                    first_result = successful_results[0]
                    print(f"     都返回: {first_result.get('first_song_id', 'Unknown')} - {first_result.get('first_song_name', 'Unknown')}")
        
        # 分析失敗原因
        if failed_results:
            print("  📋 失敗原因統計:")
            error_counts = {}
            for result in failed_results:
                error = result.get('error', 'Unknown')
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in error_counts.items():
                print(f"     {error}: {count} 次")
        
        return False
    
    def test_url_parameter_vs_postback(self, initial_state, company="音圓"):
        """對比URL參數和PostBack的效果"""
        print("\\n🔄 URL參數 vs PostBack效果對比:")
        
        comparison = {
            'url_method': None,
            'postback_method': None,
            'are_different': False
        }
        
        try:
            # 方法1: URL參數
            print("  📝 測試URL參數方法...")
            url_with_page = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page=2"
            response1 = self.session.get(url_with_page, timeout=15)
            
            if response1.status_code == 200:
                soup1 = BeautifulSoup(response1.text, 'html.parser')
                songs1 = soup1.select('a[href^="mv.aspx?id="]')
                if songs1:
                    first1 = songs1[0].get_text().strip().split()
                    if len(first1) >= 4:
                        comparison['url_method'] = {
                            'id': first1[0],
                            'name': first1[1], 
                            'artist': ' '.join(first1[3:]),
                            'total': len(songs1)
                        }
                        print(f"     URL方法結果: {first1[0]} - {first1[1]}")
            
            time.sleep(2)
            
            # 方法2: PostBack (使用最有希望的組合)
            print("  📝 測試PostBack方法...")
            post_data = {
                '__VIEWSTATE': initial_state['viewstate'],
                '__VIEWSTATEGENERATOR': initial_state['viewstate_generator'],
                '__EVENTVALIDATION': initial_state['event_validation'],
                '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$GridView1',
                '__EVENTARGUMENT': 'Page$2'
            }
            
            url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}"
            response2 = self.session.post(url, data=post_data, timeout=15)
            
            if response2.status_code == 200:
                soup2 = BeautifulSoup(response2.text, 'html.parser')
                songs2 = soup2.select('a[href^="mv.aspx?id="]')
                if songs2:
                    first2 = songs2[0].get_text().strip().split()
                    if len(first2) >= 4:
                        comparison['postback_method'] = {
                            'id': first2[0],
                            'name': first2[1],
                            'artist': ' '.join(first2[3:]),
                            'total': len(songs2)
                        }
                        print(f"     PostBack方法結果: {first2[0]} - {first2[1]}")
            
            # 比較結果
            if comparison['url_method'] and comparison['postback_method']:
                url_song = f"{comparison['url_method']['id']}_{comparison['url_method']['artist']}"
                postback_song = f"{comparison['postback_method']['id']}_{comparison['postback_method']['artist']}"
                
                if url_song != postback_song:
                    comparison['are_different'] = True
                    print("  🎉 發現差異！URL和PostBack返回不同內容")
                else:
                    print("  😔 URL和PostBack返回相同內容")
            
        except Exception as e:
            print(f"  ❌ 比較測試失敗: {e}")
        
        return comparison

def main():
    decoder = ViewStateDecoder()
    
    print("🔬 開始ViewState深度解碼分析")
    print("=" * 60)
    
    # 獲取初始狀態
    initial_state = decoder.get_initial_state("音圓")
    if not initial_state:
        print("❌ 無法獲取初始狀態")
        return
    
    # 分析ViewState結構
    viewstate_structure = decoder.analyze_viewstate_structure(initial_state['viewstate'])
    
    # 測試PostBack組合
    postback_results = decoder.test_postback_combinations(initial_state, "音圓")
    
    # 分析結果差異
    has_differences = decoder.analyze_differences(postback_results)
    
    # URL vs PostBack 對比
    comparison = decoder.test_url_parameter_vs_postback(initial_state, "音圓")
    
    # 保存詳細結果
    analysis_result = {
        'initial_state': {
            'viewstate_length': len(initial_state['viewstate']),
            'generator': initial_state['viewstate_generator'],
            'cookies_count': len(initial_state['cookies'])
        },
        'viewstate_structure': viewstate_structure,
        'postback_results': postback_results,
        'has_breakthrough': has_differences,
        'url_vs_postback_comparison': comparison
    }
    
    filename = "viewstate_decode_analysis.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        print(f"\\n💾 詳細分析結果已保存到: {filename}")
    except Exception as e:
        print(f"\\n❌ 保存失敗: {e}")
    
    # 總結
    print("\\n🎯 階段二總結:")
    if has_differences or comparison['are_different']:
        print("  🎉 發現突破點！某些PostBack組合或方法能返回不同內容")
        print("  📈 建議進入階段三：深入測試有效組合")
    else:
        print("  😔 未找到有效的PostBack組合")
        print("  🤔 可能需要嘗試其他策略：")
        print("     - 分析更多頁面尋找隱藏控件")
        print("     - 檢查AJAX請求")
        print("     - 嘗試修改ViewState內容")

if __name__ == "__main__":
    main()