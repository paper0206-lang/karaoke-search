#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASP.NET ViewState 深度分析工具
階段一：HTML源碼和JavaScript分析
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import base64
from urllib.parse import quote, unquote
import time

class ViewStateAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def extract_page_analysis(self, company="音圓", page=1):
        """提取並分析頁面的完整HTML結構"""
        print(f"🔍 階段一：分析 {company} 第{page}頁的HTML結構")
        print("=" * 60)
        
        try:
            url = f"https://song.corp.com.tw/songs.aspx?company={quote(company)}&page={page}"
            print(f"請求URL: {url}")
            
            response = self.session.get(url, timeout=15)
            print(f"HTTP狀態: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                analysis = {
                    'url': url,
                    'company': company,
                    'page': page,
                    'html_analysis': self.analyze_html_structure(soup),
                    'viewstate_analysis': self.analyze_viewstate(soup),
                    'form_analysis': self.analyze_forms(soup),
                    'javascript_analysis': self.analyze_javascript(soup),
                    'postback_analysis': self.analyze_postback_mechanism(soup),
                    'pagination_analysis': self.analyze_pagination_elements(soup)
                }
                
                return analysis
            else:
                print(f"❌ HTTP請求失敗: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 分析過程出錯: {e}")
            return None
    
    def analyze_html_structure(self, soup):
        """分析HTML基本結構"""
        print("\\n📋 HTML結構分析:")
        
        analysis = {
            'title': soup.title.string if soup.title else 'No title',
            'forms_count': len(soup.find_all('form')),
            'scripts_count': len(soup.find_all('script')),
            'hidden_inputs_count': len(soup.find_all('input', {'type': 'hidden'})),
            'links_count': len(soup.find_all('a')),
            'song_links_count': len(soup.select('a[href^="mv.aspx?id="]'))
        }
        
        for key, value in analysis.items():
            print(f"  {key}: {value}")
            
        return analysis
    
    def analyze_viewstate(self, soup):
        """分析ViewState相關字段"""
        print("\\n🔐 ViewState字段分析:")
        
        viewstate_fields = [
            '__VIEWSTATE',
            '__VIEWSTATEGENERATOR', 
            '__EVENTVALIDATION',
            '__EVENTTARGET',
            '__EVENTARGUMENT',
            '__LASTFOCUS',
            '__SCROLLPOSITIONX',
            '__SCROLLPOSITIONY'
        ]
        
        analysis = {}
        for field in viewstate_fields:
            element = soup.find('input', {'name': field})
            if element:
                value = element.get('value', '')
                analysis[field] = {
                    'exists': True,
                    'value_length': len(value),
                    'value_preview': value[:100] + '...' if len(value) > 100 else value
                }
                print(f"  ✅ {field}: 長度={len(value)}, 預覽={value[:50]}...")
            else:
                analysis[field] = {'exists': False}
                print(f"  ❌ {field}: 不存在")
        
        # 嘗試解碼ViewState
        if analysis.get('__VIEWSTATE', {}).get('exists'):
            viewstate_value = soup.find('input', {'name': '__VIEWSTATE'}).get('value', '')
            analysis['viewstate_decode'] = self.try_decode_viewstate(viewstate_value)
        
        return analysis
    
    def try_decode_viewstate(self, viewstate):
        """嘗試解碼ViewState內容"""
        print("\\n🔓 嘗試解碼ViewState:")
        
        decode_info = {
            'original_length': len(viewstate),
            'base64_valid': False,
            'decoded_length': 0,
            'decoded_preview': '',
            'structure_hints': []
        }
        
        try:
            # 嘗試Base64解碼
            decoded = base64.b64decode(viewstate)
            decode_info['base64_valid'] = True
            decode_info['decoded_length'] = len(decoded)
            
            # 分析解碼後的內容
            decoded_text = decoded[:200]  # 取前200字節分析
            decode_info['decoded_preview'] = str(decoded_text)
            
            # 尋找可能的結構提示
            if b'page' in decoded.lower():
                decode_info['structure_hints'].append('Contains "page" reference')
            if b'grid' in decoded.lower():
                decode_info['structure_hints'].append('Contains "grid" reference') 
            if b'control' in decoded.lower():
                decode_info['structure_hints'].append('Contains "control" reference')
                
            print(f"  ✅ Base64解碼成功, 長度: {len(decoded)}")
            print(f"  📄 內容預覽: {decoded_text}")
            
        except Exception as e:
            print(f"  ❌ Base64解碼失敗: {e}")
            
        return decode_info
    
    def analyze_forms(self, soup):
        """分析表單結構"""
        print("\\n📝 表單結構分析:")
        
        forms = soup.find_all('form')
        analysis = {
            'forms_count': len(forms),
            'forms_details': []
        }
        
        for i, form in enumerate(forms):
            form_info = {
                'index': i,
                'id': form.get('id', 'No ID'),
                'name': form.get('name', 'No name'),
                'method': form.get('method', 'GET').upper(),
                'action': form.get('action', ''),
                'inputs_count': len(form.find_all('input')),
                'hidden_inputs': len(form.find_all('input', {'type': 'hidden'})),
                'buttons_count': len(form.find_all(['input', 'button'], {'type': ['submit', 'button']}))
            }
            
            analysis['forms_details'].append(form_info)
            
            print(f"  📋 表單 {i+1}:")
            print(f"     ID: {form_info['id']}")
            print(f"     方法: {form_info['method']}")
            print(f"     動作: {form_info['action']}")
            print(f"     輸入欄位: {form_info['inputs_count']} (隱藏: {form_info['hidden_inputs']})")
            
        return analysis
    
    def analyze_javascript(self, soup):
        """分析JavaScript代碼"""
        print("\\n⚙️ JavaScript分析:")
        
        scripts = soup.find_all('script')
        analysis = {
            'scripts_count': len(scripts),
            'postback_functions': [],
            'pagination_functions': [],
            'ajax_patterns': [],
            'interesting_code': []
        }
        
        # 關鍵字搜索
        postback_keywords = ['__doPostBack', 'postback', 'Page$', 'PageIndexChange']
        pagination_keywords = ['page', 'next', 'prev', 'pagination', 'grid']
        ajax_keywords = ['XMLHttpRequest', 'ajax', 'fetch', '$.post', '$.get']
        
        for script in scripts:
            script_content = script.string or ''
            
            # 搜索PostBack相關代碼
            for keyword in postback_keywords:
                if keyword.lower() in script_content.lower():
                    matches = re.findall(rf'.*{re.escape(keyword)}.*', script_content, re.IGNORECASE)
                    analysis['postback_functions'].extend(matches[:3])  # 最多保存3個匹配
            
            # 搜索分頁相關代碼
            for keyword in pagination_keywords:
                if keyword.lower() in script_content.lower():
                    matches = re.findall(rf'.*{re.escape(keyword)}.*', script_content, re.IGNORECASE)
                    analysis['pagination_functions'].extend(matches[:2])
            
            # 搜索AJAX模式
            for keyword in ajax_keywords:
                if keyword.lower() in script_content.lower():
                    matches = re.findall(rf'.*{re.escape(keyword)}.*', script_content, re.IGNORECASE)
                    analysis['ajax_patterns'].extend(matches[:2])
        
        # 打印發現的重要代碼
        if analysis['postback_functions']:
            print("  🎯 發現PostBack相關代碼:")
            for code in analysis['postback_functions'][:5]:
                print(f"     {code.strip()}")
                
        if analysis['pagination_functions']:
            print("  📄 發現分頁相關代碼:")
            for code in analysis['pagination_functions'][:5]:
                print(f"     {code.strip()}")
                
        if analysis['ajax_patterns']:
            print("  🌐 發現AJAX相關代碼:")
            for code in analysis['ajax_patterns'][:3]:
                print(f"     {code.strip()}")
        
        return analysis
    
    def analyze_postback_mechanism(self, soup):
        """分析PostBack機制"""
        print("\\n🔄 PostBack機制分析:")
        
        analysis = {
            'dopostback_function_exists': False,
            'event_target_field_exists': False,
            'event_argument_field_exists': False,
            'possible_targets': [],
            'form_submit_method': 'Unknown'
        }
        
        # 檢查__doPostBack函數
        scripts = soup.find_all('script')
        for script in scripts:
            content = script.string or ''
            if '__doPostBack' in content:
                analysis['dopostback_function_exists'] = True
                print("  ✅ 發現__doPostBack函數")
                
                # 提取函數定義
                dopostback_match = re.search(r'function __doPostBack.*?{.*?}', content, re.DOTALL)
                if dopostback_match:
                    print(f"  📝 函數定義: {dopostback_match.group()[:200]}...")
        
        # 檢查事件字段
        if soup.find('input', {'name': '__EVENTTARGET'}):
            analysis['event_target_field_exists'] = True
            print("  ✅ 發現__EVENTTARGET字段")
            
        if soup.find('input', {'name': '__EVENTARGUMENT'}):
            analysis['event_argument_field_exists'] = True
            print("  ✅ 發現__EVENTARGUMENT字段")
        
        # 尋找可能的事件目標
        # 查找具有onclick或其他事件的元素
        clickable_elements = soup.find_all(['a', 'input', 'button'], href=True) + \
                           soup.find_all(['a', 'input', 'button'], onclick=True)
        
        for element in clickable_elements:
            onclick = element.get('onclick', '')
            href = element.get('href', '')
            
            if '__doPostBack' in onclick:
                # 提取PostBack參數
                match = re.search(r"__doPostBack\('([^']*)',\s*'([^']*)'\)", onclick)
                if match:
                    target, argument = match.groups()
                    analysis['possible_targets'].append({
                        'target': target,
                        'argument': argument,
                        'element': str(element)[:100]
                    })
            
            if 'javascript:' in href and '__doPostBack' in href:
                match = re.search(r"__doPostBack\('([^']*)',\s*'([^']*)'\)", href)
                if match:
                    target, argument = match.groups()
                    analysis['possible_targets'].append({
                        'target': target,
                        'argument': argument,
                        'element': str(element)[:100]
                    })
        
        if analysis['possible_targets']:
            print("  🎯 發現可能的PostBack目標:")
            for target_info in analysis['possible_targets'][:5]:
                print(f"     目標: {target_info['target']}")
                print(f"     參數: {target_info['argument']}")
                print(f"     元素: {target_info['element']}")
                print()
        
        return analysis
    
    def analyze_pagination_elements(self, soup):
        """分析分頁元素"""
        print("\\n📄 分頁元素分析:")
        
        analysis = {
            'pagination_controls': [],
            'page_numbers': [],
            'next_prev_buttons': [],
            'hidden_pagination': []
        }
        
        # 尋找分頁相關的連結和按鈕
        all_links = soup.find_all('a')
        for link in all_links:
            text = link.get_text().strip()
            href = link.get('href', '')
            onclick = link.get('onclick', '')
            
            # 檢查是否為頁碼
            if text.isdigit():
                analysis['page_numbers'].append({
                    'text': text,
                    'href': href,
                    'onclick': onclick
                })
            
            # 檢查是否為上一頁/下一頁
            if any(word in text.lower() for word in ['next', 'prev', '下一頁', '上一頁', '>', '<']):
                analysis['next_prev_buttons'].append({
                    'text': text,
                    'href': href, 
                    'onclick': onclick
                })
            
            # 檢查是否包含分頁相關的PostBack
            if 'Page$' in onclick or 'page' in onclick.lower():
                analysis['pagination_controls'].append({
                    'text': text,
                    'onclick': onclick,
                    'type': 'postback'
                })
        
        # 尋找隱藏的分頁控件
        hidden_inputs = soup.find_all('input', {'type': 'hidden'})
        for hidden in hidden_inputs:
            name = hidden.get('name', '')
            if 'page' in name.lower() or 'grid' in name.lower():
                analysis['hidden_pagination'].append({
                    'name': name,
                    'value': hidden.get('value', '')
                })
        
        # 打印發現的分頁元素
        if analysis['page_numbers']:
            print("  🔢 發現頁碼連結:")
            for page_info in analysis['page_numbers'][:5]:
                print(f"     頁碼: {page_info['text']}, onClick: {page_info['onclick'][:50]}...")
        
        if analysis['next_prev_buttons']:
            print("  ⬅️➡️ 發現導航按鈕:")
            for nav_info in analysis['next_prev_buttons']:
                print(f"     按鈕: {nav_info['text']}, onClick: {nav_info['onclick'][:50]}...")
        
        if analysis['pagination_controls']:
            print("  🎮 發現分頁控件:")
            for ctrl_info in analysis['pagination_controls']:
                print(f"     控件: {ctrl_info['text']}, onClick: {ctrl_info['onclick'][:50]}...")
        
        if analysis['hidden_pagination']:
            print("  🔒 發現隱藏分頁字段:")
            for hidden_info in analysis['hidden_pagination']:
                print(f"     字段: {hidden_info['name']} = {hidden_info['value']}")
        
        return analysis
    
    def save_analysis(self, analysis, filename):
        """保存分析結果到JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            print(f"\\n💾 分析結果已保存到: {filename}")
        except Exception as e:
            print(f"\\n❌ 保存失敗: {e}")

def main():
    analyzer = ViewStateAnalyzer()
    
    print("🚀 開始ASP.NET ViewState深度分析")
    print("=" * 60)
    
    # 分析音圓第1頁
    analysis = analyzer.extract_page_analysis("音圓", 1)
    
    if analysis:
        # 保存詳細分析結果
        filename = f"viewstate_analysis_音圓_page1.json"
        analyzer.save_analysis(analysis, filename)
        
        print("\\n📊 階段一分析完成!")
        print("主要發現:")
        
        # 總結關鍵發現
        viewstate = analysis['viewstate_analysis']
        postback = analysis['postback_analysis']
        pagination = analysis['pagination_analysis']
        
        if viewstate.get('__VIEWSTATE', {}).get('exists'):
            print("  ✅ 發現ViewState字段")
        if postback.get('dopostback_function_exists'):
            print("  ✅ 發現PostBack機制")
        if postback.get('possible_targets'):
            print(f"  🎯 發現 {len(postback['possible_targets'])} 個可能的PostBack目標")
        if pagination.get('pagination_controls'):
            print(f"  📄 發現 {len(pagination['pagination_controls'])} 個分頁控件")
            
        print("\\n下一步: 開始ViewState解碼分析...")
    else:
        print("❌ 階段一分析失敗")

if __name__ == "__main__":
    main()