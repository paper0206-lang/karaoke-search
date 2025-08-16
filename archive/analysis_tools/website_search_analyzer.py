#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
網站搜尋機制深度分析
分析 https://song.corp.com.tw 的真實搜尋功能
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import quote, urlencode

class WebsiteSearchAnalyzer:
    def __init__(self):
        self.base_url = "https://song.corp.com.tw"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://song.corp.com.tw/'
        })
        
    def analyze_homepage_structure(self):
        """分析首頁結構"""
        print("🔍 分析首頁搜尋結構...")
        
        try:
            response = self.session.get(f"{self.base_url}/index.aspx", timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 保存首頁HTML用於分析
            with open("homepage_analysis.html", "w", encoding='utf-8') as f:
                f.write(response.text)
            
            analysis = {
                "forms": [],
                "search_inputs": [],
                "search_buttons": [],
                "viewstate": None,
                "eventvalidation": None,
                "possible_search_endpoints": []
            }
            
            # 分析表單
            forms = soup.find_all('form')
            for i, form in enumerate(forms):
                form_info = {
                    "index": i,
                    "action": form.get('action', ''),
                    "method": form.get('method', 'GET'),
                    "id": form.get('id', ''),
                    "inputs": []
                }
                
                # 分析表單內的輸入框
                inputs = form.find_all(['input', 'select', 'textarea'])
                for inp in inputs:
                    input_info = {
                        "type": inp.get('type', inp.name),
                        "name": inp.get('name', ''),
                        "id": inp.get('id', ''),
                        "value": inp.get('value', ''),
                        "placeholder": inp.get('placeholder', '')
                    }
                    form_info["inputs"].append(input_info)
                
                analysis["forms"].append(form_info)
            
            # 查找ViewState
            viewstate = soup.find('input', {'name': '__VIEWSTATE'})
            if viewstate:
                analysis["viewstate"] = viewstate.get('value', '')[:100] + "..."
                
            eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
            if eventvalidation:
                analysis["eventvalidation"] = eventvalidation.get('value', '')[:100] + "..."
            
            # 查找搜尋相關的JavaScript
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and ('search' in script.string.lower() or 'keyword' in script.string.lower()):
                    analysis["possible_search_endpoints"].append({
                        "type": "javascript",
                        "content_preview": script.string[:200] + "..."
                    })
            
            print(f"✅ 找到 {len(analysis['forms'])} 個表單")
            print(f"✅ ViewState: {'存在' if analysis['viewstate'] else '不存在'}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ 分析首頁失敗: {e}")
            return None
    
    def test_search_methods(self):
        """測試各種搜尋方式"""
        print("\n🎵 測試各種搜尋方式...")
        
        # 從989位歌手中選擇測試歌手
        test_keywords = ["周杰倫", "蔡依林", "A-Lin", "鄧紫棋", "五月天"]
        
        search_results = {}
        
        for keyword in test_keywords:
            print(f"   🔍 測試關鍵字: {keyword}")
            keyword_results = {}
            
            # 方法1: GET搜尋
            try:
                get_url = f"{self.base_url}/index.aspx?keyword={quote(keyword)}"
                response = self.session.get(get_url, timeout=30)
                
                keyword_results["GET_search"] = {
                    "status_code": response.status_code,
                    "url": get_url,
                    "content_length": len(response.text),
                    "contains_keyword": keyword in response.text,
                    "contains_mv_links": "mv.aspx" in response.text,
                    "redirect_url": response.url if response.url != get_url else None
                }
                
                # 保存搜尋結果頁面
                with open(f"search_result_GET_{keyword}.html", "w", encoding='utf-8') as f:
                    f.write(response.text)
                    
            except Exception as e:
                keyword_results["GET_search"] = {"error": str(e)}
            
            # 方法2: POST搜尋 (使用ViewState)
            try:
                # 先獲取首頁的ViewState
                homepage = self.session.get(f"{self.base_url}/index.aspx", timeout=30)
                soup = BeautifulSoup(homepage.text, 'html.parser')
                
                viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
                
                if viewstate:
                    post_data = {
                        '__VIEWSTATE': viewstate.get('value', ''),
                        '__EVENTTARGET': '',
                        '__EVENTARGUMENT': '',
                        'keyword': keyword
                    }
                    
                    if eventvalidation:
                        post_data['__EVENTVALIDATION'] = eventvalidation.get('value', '')
                    
                    # 嘗試不同的POST參數組合
                    post_variations = [
                        {'ctl00$ContentPlaceHolder1$txt_keyword': keyword, 'ctl00$ContentPlaceHolder1$but_sel': '查詢'},
                        {'txt_keyword': keyword, 'but_sel': '查詢'},
                        {'keyword': keyword, 'search': '搜尋'},
                        {'q': keyword}
                    ]
                    
                    for i, variation in enumerate(post_variations):
                        try:
                            post_data.update(variation)
                            response = self.session.post(f"{self.base_url}/index.aspx", data=post_data, timeout=30)
                            
                            keyword_results[f"POST_search_{i+1}"] = {
                                "status_code": response.status_code,
                                "post_data_keys": list(variation.keys()),
                                "content_length": len(response.text),
                                "contains_keyword": keyword in response.text,
                                "contains_mv_links": "mv.aspx" in response.text,
                                "redirect_url": response.url if response.url != f"{self.base_url}/index.aspx" else None
                            }
                            
                            # 保存第一個POST結果
                            if i == 0:
                                with open(f"search_result_POST_{keyword}.html", "w", encoding='utf-8') as f:
                                    f.write(response.text)
                            
                            break  # 如果成功就停止嘗試其他變體
                            
                        except Exception as e:
                            keyword_results[f"POST_search_{i+1}"] = {"error": str(e)}
                            
            except Exception as e:
                keyword_results["POST_search"] = {"error": str(e)}
            
            # 方法3: 檢查是否有其他搜尋端點
            possible_endpoints = [
                "/search.aspx",
                "/songs.aspx",
                "/api/search"
            ]
            
            for endpoint in possible_endpoints:
                try:
                    url = f"{self.base_url}{endpoint}?q={quote(keyword)}"
                    response = self.session.get(url, timeout=30)
                    
                    keyword_results[f"endpoint_{endpoint.replace('/', '_')}"] = {
                        "status_code": response.status_code,
                        "url": url,
                        "content_length": len(response.text),
                        "contains_keyword": keyword in response.text,
                        "contains_mv_links": "mv.aspx" in response.text
                    }
                    
                except Exception as e:
                    keyword_results[f"endpoint_{endpoint.replace('/', '_')}"] = {"error": str(e)}
            
            search_results[keyword] = keyword_results
            print(f"      ✅ 完成測試: {keyword}")
            time.sleep(2)  # 防止過快請求
        
        return search_results
    
    def analyze_search_results(self, search_results):
        """分析搜尋結果"""
        print("\n📊 分析搜尋結果...")
        
        analysis = {
            "working_methods": [],
            "failed_methods": [],
            "keywords_with_results": [],
            "keywords_without_results": [],
            "recommended_approach": None
        }
        
        for keyword, methods in search_results.items():
            keyword_has_results = False
            
            for method_name, result in methods.items():
                if "error" not in result:
                    if result.get("contains_mv_links", False) or result.get("contains_keyword", False):
                        analysis["working_methods"].append({
                            "method": method_name,
                            "keyword": keyword,
                            "evidence": "contains_mv_links" if result.get("contains_mv_links") else "contains_keyword"
                        })
                        keyword_has_results = True
                    else:
                        analysis["failed_methods"].append({
                            "method": method_name,
                            "keyword": keyword,
                            "reason": "no_relevant_content"
                        })
                else:
                    analysis["failed_methods"].append({
                        "method": method_name,
                        "keyword": keyword,
                        "reason": result["error"]
                    })
            
            if keyword_has_results:
                analysis["keywords_with_results"].append(keyword)
            else:
                analysis["keywords_without_results"].append(keyword)
        
        # 決定推薦方法
        if len(analysis["working_methods"]) > 0:
            # 統計最成功的方法
            method_success = {}
            for method in analysis["working_methods"]:
                method_name = method["method"].split("_")[0]  # GET, POST等
                method_success[method_name] = method_success.get(method_name, 0) + 1
            
            best_method = max(method_success.items(), key=lambda x: x[1])
            analysis["recommended_approach"] = {
                "method": best_method[0],
                "success_rate": f"{best_method[1]}/{len(search_results)} keywords",
                "confidence": "high" if best_method[1] >= 3 else "medium"
            }
        else:
            analysis["recommended_approach"] = {
                "method": "none_working",
                "reason": "搜尋功能可能不可用或需要其他方法",
                "confidence": "low"
            }
        
        return analysis
    
    def run_complete_analysis(self):
        """執行完整分析"""
        print("🔬 開始網站搜尋機制深度分析")
        print("=" * 60)
        
        # 1. 分析首頁結構
        homepage_analysis = self.analyze_homepage_structure()
        
        # 2. 測試搜尋方法
        search_results = self.test_search_methods()
        
        # 3. 分析結果
        result_analysis = self.analyze_search_results(search_results)
        
        # 4. 生成完整報告
        complete_report = {
            "analysis_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "website": self.base_url,
            "homepage_structure": homepage_analysis,
            "search_method_tests": search_results,
            "analysis_summary": result_analysis
        }
        
        # 5. 保存報告
        report_filename = f"website_search_analysis_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, "w", encoding='utf-8') as f:
            json.dump(complete_report, f, ensure_ascii=False, indent=2)
        
        print(f"💾 分析報告已保存: {report_filename}")
        
        # 6. 打印摘要
        self.print_analysis_summary(result_analysis)
        
        return complete_report
    
    def print_analysis_summary(self, analysis):
        """打印分析摘要"""
        print("\n" + "=" * 60)
        print("📋 搜尋機制分析摘要")
        print("=" * 60)
        
        print(f"✅ 有效方法數量: {len(analysis['working_methods'])}")
        print(f"❌ 無效方法數量: {len(analysis['failed_methods'])}")
        print(f"🎵 有結果關鍵字: {len(analysis['keywords_with_results'])}")
        print(f"⚪ 無結果關鍵字: {len(analysis['keywords_without_results'])}")
        
        if analysis["keywords_with_results"]:
            print(f"\n✅ 有結果的關鍵字: {', '.join(analysis['keywords_with_results'])}")
        
        if analysis["keywords_without_results"]:
            print(f"\n❌ 無結果的關鍵字: {', '.join(analysis['keywords_without_results'])}")
        
        recommendation = analysis["recommended_approach"]
        print(f"\n🎯 推薦方法: {recommendation['method']}")
        if recommendation.get("success_rate"):
            print(f"📊 成功率: {recommendation['success_rate']}")
        print(f"🔮 信心度: {recommendation['confidence']}")
        
        if recommendation["method"] != "none_working":
            print(f"\n💡 建議: 可以使用{recommendation['method']}方法進行歌手搜尋")
        else:
            print(f"\n⚠️ 建議: {recommendation.get('reason', '需要尋找其他技術方案')}")

def main():
    analyzer = WebsiteSearchAnalyzer()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()