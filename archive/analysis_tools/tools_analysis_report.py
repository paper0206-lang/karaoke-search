#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KTV專案工具分析報告
分析所有現有工具的特色、功能和適用性
"""

import os
import json
import time
from datetime import datetime

class ToolsAnalyzer:
    def __init__(self):
        self.project_path = "/Users/paper/karaoke-search"
        self.tools_analysis = {
            'scrapers': {},
            'frontend': {},
            'database': {},
            'monitoring': {},
            'analysis': {},
            'deployment': {}
        }
    
    def analyze_scrapers(self):
        """分析爬蟲工具"""
        print("🕷️ 分析爬蟲工具...")
        
        scrapers = {
            'auto_scraper.py': {
                'description': '主要爬蟲工具 - 10線程自動爬取',
                'features': [
                    '10線程並行爬取',
                    '智能延遲機制 (1.5-5秒)',
                    'User-Agent輪換防檢測',
                    '批次保存 (每150首歌)',
                    '斷點續爬功能',
                    '進度追蹤和統計',
                    '安全關閉處理'
                ],
                'status': '✅ 穩定運行',
                'data_collected': '150萬+首歌曲',
                '适用性': '🎯 適合大規模數據收集',
                'compatibility_new_task': '✅ 完全適用'
            },
            
            'browser_scraper.py': {
                'description': 'Selenium瀏覽器爬蟲 - 突破JavaScript限制',
                'features': [
                    '無頭Chrome WebDriver',
                    'JavaScript執行能力',
                    '真實瀏覽器環境模擬',
                    '頁面截圖功能',
                    '動態內容爬取'
                ],
                'status': '✅ 可用但較慢',
                'data_collected': '98首唯一歌曲/10頁',
                '适用性': '🔧 適合特殊網站分析',
                'compatibility_new_task': '⚠️ 需調整但有用'
            },
            
            'real_search_analyzer.py': {
                'description': '真實搜尋行為分析器',
                'features': [
                    '測試真實搜尋關鍵字',
                    '分析搜尋機制差異',
                    'POST/GET方法測試',
                    '公司搜尋 vs 用戶搜尋對比'
                ],
                'status': '✅ 分析完成',
                'data_collected': '搜尋機制分析報告',
                '适用性': '📊 用於策略分析',
                'compatibility_new_task': '🎯 完美適配新歌手搜尋'
            },
            
            'taiwan_songking_api_crawler.py': {
                'description': 'API接口爬蟲',
                'features': [
                    'RESTful API調用',
                    'JSON數據處理',
                    '高效數據獲取',
                    'API限制處理'
                ],
                'status': '⚠️ 需確認API可用性',
                'data_collected': '依API而定',
                '适用性': '🚀 高效但依賴API',
                'compatibility_new_task': '✅ 如API支援歌手搜尋則完美'
            }
        }
        
        self.tools_analysis['scrapers'] = scrapers
        return scrapers
    
    def analyze_frontend(self):
        """分析前端工具"""
        print("🖥️ 分析前端工具...")
        
        frontend = {
            'app.py': {
                'description': 'Flask主應用 - 完整的KTV搜尋系統',
                'features': [
                    'Flask Web框架',
                    '歌曲搜尋API',
                    '歌手搜尋功能',
                    'JSON數據接口',
                    'CORS跨域支援',
                    '即時搜尋建議'
                ],
                'status': '✅ 完整可用',
                '適用場景': 'Web應用後端',
                'compatibility_new_task': '🎯 完美適配 - 可直接使用新歌手數據庫'
            },
            
            'standalone_frontend.html': {
                'description': '獨立前端頁面 - 完整的用戶界面',
                'features': [
                    '響應式設計',
                    '即時搜尋',
                    '歌曲卡片顯示',
                    '分頁功能',
                    '美觀的UI設計',
                    '無需後端獨立運行'
                ],
                'status': '✅ 完整可用',
                '適用場景': '獨立展示頁面',
                'compatibility_new_task': '⚠️ 需更新數據源指向新資料庫'
            },
            
            'new_frontend.html': {
                'description': '新版前端界面',
                'features': [
                    '現代化UI設計',
                    '增強用戶體驗',
                    '優化搜尋流程'
                ],
                'status': '✅ 可用',
                '適用場景': '升級版前端',
                'compatibility_new_task': '✅ 可配合新資料庫使用'
            },
            
            'api/': {
                'description': 'API接口模組',
                'features': [
                    'live-search.js - 即時搜尋',
                    'taiwan-ktv.js - 台灣KTV API',
                    'taiwan-search.js - 搜尋接口',
                    'test.js - 測試模組'
                ],
                'status': '✅ 模組化設計',
                '適用場景': '前後端分離架構',
                'compatibility_new_task': '✅ 完全適用新歌手搜尋需求'
            }
        }
        
        self.tools_analysis['frontend'] = frontend
        return frontend
    
    def analyze_database(self):
        """分析資料庫工具"""
        print("🗄️ 分析資料庫工具...")
        
        database = {
            'FINAL_singer_database_20250811_200210.json': {
                'description': '最終整合歌手資料庫 - 989位歌手',
                'features': [
                    '989位去重歌手',
                    '1063個搜尋關鍵字',
                    '11個完整分類',
                    '地區、年代、類型全覆蓋',
                    '關鍵字變體支援'
                ],
                'status': '✅ 最新完整版',
                'data_size': '989位歌手',
                'compatibility_new_task': '🎯 完美匹配 - 專為歌手搜尋設計'
            },
            
            '音圓完整數據_20250810_221337.json': {
                'description': '音圓公司歌曲完整數據',
                'features': [
                    '150萬+首歌曲',
                    '完整歌曲資訊',
                    '歌手、歌名、編號',
                    '時間戳記錄'
                ],
                'status': '✅ 大型歌曲數據集',
                'data_size': '150萬+首歌曲',
                'compatibility_new_task': '✅ 可作為歌曲資料來源'
            },
            
            'database_unifier.py': {
                'description': '資料庫統一工具',
                'features': [
                    '多資料庫合併',
                    '數據格式統一',
                    '重複數據清理'
                ],
                'status': '✅ 工具可用',
                '適用場景': '資料庫整合',
                'compatibility_new_task': '✅ 可用於未來數據合併'
            },
            
            'data_quality_checker.py': {
                'description': '數據品質檢查器',
                'features': [
                    '數據完整性檢查',
                    '重複數據檢測',
                    '格式驗證',
                    '統計報告生成'
                ],
                'status': '✅ 品質保證工具',
                '適用場景': '數據驗證',
                'compatibility_new_task': '✅ 可用於新資料庫品質檢查'
            }
        }
        
        self.tools_analysis['database'] = database
        return database
    
    def analyze_monitoring(self):
        """分析監控工具"""
        print("📊 分析監控工具...")
        
        monitoring = {
            'quick_status.py': {
                'description': '快速狀態監控 - 一行式進度報告',
                'features': [
                    '實時進度顯示',
                    '剩餘時間估算',
                    '歌曲統計',
                    '簡潔輸出格式'
                ],
                'status': '✅ 核心監控工具',
                'output_format': '🟢 進度:52.6% 第13,140頁 歌曲:112,950首 剩餘:8.0h',
                'compatibility_new_task': '⚠️ 需調整適配新爬蟲邏輯'
            },
            
            'check_progress.py': {
                'description': '詳細進度檢查器',
                'features': [
                    '多線程進度分析',
                    '文件統計',
                    '完成時間預估',
                    '進程狀態檢查'
                ],
                'status': '✅ 詳細監控工具',
                '適用場景': '深度分析',
                'compatibility_new_task': '⚠️ 需調整適配新任務'
            },
            
            'stop_scraper.py': {
                'description': '安全停止爬蟲工具',
                'features': [
                    '保護數據安全',
                    '優雅關閉進程',
                    '狀態保存'
                ],
                'status': '✅ 安全工具',
                '適用場景': '爬蟲管理',
                'compatibility_new_task': '✅ 通用安全工具'
            },
            
            'simple_monitor.py': {
                'description': '簡易監控器',
                'features': [
                    '基礎狀態監控',
                    '輕量級設計'
                ],
                'status': '✅ 輔助工具',
                '適用場景': '簡單監控',
                'compatibility_new_task': '✅ 可用'
            }
        }
        
        self.tools_analysis['monitoring'] = monitoring
        return monitoring
    
    def analyze_analysis_tools(self):
        """分析分析工具"""
        print("🔍 分析分析工具...")
        
        analysis = {
            'viewstate_analyzer.py': {
                'description': 'ViewState分析器 - 深度網站結構分析',
                'features': [
                    'HTML結構分析',
                    'ViewState字段提取',
                    'PostBack機制檢測',
                    'JavaScript模式分析'
                ],
                'status': '✅ 專業分析工具',
                '適用場景': '網站逆向工程',
                'compatibility_new_task': '🔧 可用於分析新目標網站'
            },
            
            'ajax_analyzer.py': {
                'description': 'AJAX分析器 - 動態請求分析',
                'features': [
                    'AJAX端點檢測',
                    'JavaScript深度分析',
                    'PostBack測試',
                    '網絡模式分析'
                ],
                'status': '✅ 深度分析工具',
                '適用場景': 'AJAX網站分析',
                'compatibility_new_task': '🔧 可用於複雜網站分析'
            },
            
            'company_analyzer.py': {
                'description': '公司數據分析器',
                'features': [
                    '多公司數據對比',
                    '重複數據分析',
                    '統計報告生成'
                ],
                'status': '✅ 數據分析工具',
                '適用場景': '跨公司分析',
                'compatibility_new_task': '⚠️ 需調整適配歌手分析'
            },
            
            'scraper_comparison_analysis.py': {
                'description': '爬蟲比較分析器',
                'features': [
                    '多爬蟲效能比較',
                    '數據質量分析',
                    '優化建議'
                ],
                'status': '✅ 性能分析工具',
                '適用場景': '爬蟲優化',
                'compatibility_new_task': '✅ 可用於評估新爬蟲'
            }
        }
        
        self.tools_analysis['analysis'] = analysis
        return analysis
    
    def analyze_deployment(self):
        """分析部署工具"""
        print("🚀 分析部署工具...")
        
        deployment = {
            'vercel.json': {
                'description': 'Vercel部署配置',
                'features': [
                    '自動部署配置',
                    '靜態文件服務',
                    'API路由設置'
                ],
                'status': '✅ 雲端部署配置',
                '適用場景': 'Web應用部署',
                'compatibility_new_task': '✅ 可用於新系統部署'
            },
            
            'Procfile': {
                'description': 'Heroku部署配置',
                'features': [
                    '進程定義',
                    '啟動命令配置'
                ],
                'status': '✅ 平台部署配置',
                '適用場景': 'Heroku平台',
                'compatibility_new_task': '✅ 通用部署配置'
            },
            
            'requirements.txt': {
                'description': 'Python依賴管理',
                'features': [
                    '完整依賴列表',
                    '版本鎖定'
                ],
                'status': '✅ 依賴管理',
                '適用場景': 'Python環境',
                'compatibility_new_task': '✅ 完全適用'
            },
            
            'auto_deploy.log': {
                'description': '自動部署日誌',
                'features': [
                    '部署記錄',
                    '錯誤追蹤'
                ],
                'status': '✅ 部署追蹤',
                '適用場景': '運維監控',
                'compatibility_new_task': '✅ 可用於新系統監控'
            }
        }
        
        self.tools_analysis['deployment'] = deployment
        return deployment
    
    def evaluate_compatibility(self):
        """評估與新任務的兼容性"""
        print("🎯 評估工具兼容性...")
        
        compatibility_analysis = {
            '完全適用 (🎯)': [],
            '需要調整 (⚠️)': [],
            '部分適用 (🔧)': [],
            '不適用 (❌)': []
        }
        
        for category, tools in self.tools_analysis.items():
            for tool_name, tool_info in tools.items():
                compatibility = tool_info.get('compatibility_new_task', '未評估')
                
                if '🎯' in compatibility or '完全適用' in compatibility:
                    compatibility_analysis['完全適用 (🎯)'].append({
                        'name': tool_name,
                        'category': category,
                        'reason': compatibility
                    })
                elif '⚠️' in compatibility or '需要調整' in compatibility:
                    compatibility_analysis['需要調整 (⚠️)'].append({
                        'name': tool_name,
                        'category': category,
                        'reason': compatibility
                    })
                elif '🔧' in compatibility or '部分適用' in compatibility:
                    compatibility_analysis['部分適用 (🔧)'].append({
                        'name': tool_name,
                        'category': category,
                        'reason': compatibility
                    })
                else:
                    compatibility_analysis['不適用 (❌)'].append({
                        'name': tool_name,
                        'category': category,
                        'reason': compatibility
                    })
        
        return compatibility_analysis
    
    def generate_recommendations(self, compatibility):
        """生成使用建議"""
        print("💡 生成使用建議...")
        
        recommendations = {
            '立即可用工具': [],
            '需要修改工具': [],
            '建議新增功能': [],
            '整合方案': []
        }
        
        # 立即可用工具
        for tool in compatibility['完全適用 (🎯)']:
            recommendations['立即可用工具'].append({
                'tool': tool['name'],
                'purpose': self.get_tool_purpose(tool['name']),
                'priority': '高'
            })
        
        # 需要修改的工具
        for tool in compatibility['需要調整 (⚠️)']:
            recommendations['需要修改工具'].append({
                'tool': tool['name'],
                'modifications': self.get_modification_suggestions(tool['name']),
                'priority': '中'
            })
        
        # 建議新增功能
        recommendations['建議新增功能'] = [
            {
                'feature': '歌手搜尋爬蟲',
                'description': '基於新歌手資料庫的專用爬蟲',
                'priority': '高'
            },
            {
                'feature': '搜尋結果驗證器',
                'description': '驗證歌手搜尋結果的準確性',
                'priority': '中'
            },
            {
                'feature': '多關鍵字批次搜尋',
                'description': '同時測試多個歌手關鍵字',
                'priority': '高'
            }
        ]
        
        # 整合方案
        recommendations['整合方案'] = [
            {
                'scenario': '快速測試方案',
                'tools': ['real_search_analyzer.py', 'FINAL_singer_database_20250811_200210.json', 'quick_status.py'],
                'description': '使用現有工具快速測試歌手搜尋'
            },
            {
                'scenario': '完整系統方案',
                'tools': ['app.py', 'standalone_frontend.html', '新歌手搜尋爬蟲'],
                'description': '建立完整的歌手搜尋系統'
            },
            {
                'scenario': '數據收集方案',
                'tools': ['auto_scraper.py (修改版)', 'browser_scraper.py', 'monitoring tools'],
                'description': '大規模歌手數據收集'
            }
        ]
        
        return recommendations
    
    def get_tool_purpose(self, tool_name):
        """獲取工具用途"""
        purposes = {
            'app.py': '提供Web API接口，支援歌手搜尋功能',
            'FINAL_singer_database_20250811_200210.json': '提供989位歌手的完整搜尋關鍵字',
            'real_search_analyzer.py': '分析和測試歌手搜尋機制',
            'standalone_frontend.html': '提供用戶友好的搜尋界面',
            'stop_scraper.py': '安全管理爬蟲進程'
        }
        return purposes.get(tool_name, '通用工具')
    
    def get_modification_suggestions(self, tool_name):
        """獲取修改建議"""
        suggestions = {
            'quick_status.py': '調整進度監控邏輯，適配歌手搜尋任務',
            'check_progress.py': '修改統計邏輯，追蹤歌手搜尋進度',
            'standalone_frontend.html': '更新數據源，指向新歌手資料庫',
            'company_analyzer.py': '調整分析邏輯，適配歌手數據分析'
        }
        return suggestions.get(tool_name, '需要評估具體修改需求')
    
    def save_analysis_report(self):
        """保存分析報告"""
        compatibility = self.evaluate_compatibility()
        recommendations = self.generate_recommendations(compatibility)
        
        report = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tools_analysis': self.tools_analysis,
            'compatibility_analysis': compatibility,
            'recommendations': recommendations,
            'summary': {
                'total_tools_analyzed': sum(len(tools) for tools in self.tools_analysis.values()),
                'fully_compatible': len(compatibility['完全適用 (🎯)']),
                'needs_modification': len(compatibility['需要調整 (⚠️)']),
                'partially_useful': len(compatibility['部分適用 (🔧)']),
                'not_applicable': len(compatibility['不適用 (❌)'])
            }
        }
        
        filename = f"tools_analysis_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"💾 分析報告已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存失敗: {e}")
        
        return report, filename
    
    def print_summary_report(self, report):
        """打印摘要報告"""
        print("\n" + "=" * 70)
        print("📊 KTV專案工具分析摘要報告")
        print("=" * 70)
        
        summary = report['summary']
        print(f"\n📈 分析統計:")
        print(f"   🔧 總工具數量: {summary['total_tools_analyzed']} 個")
        print(f"   🎯 完全適用: {summary['fully_compatible']} 個")
        print(f"   ⚠️ 需要調整: {summary['needs_modification']} 個")
        print(f"   🔧 部分適用: {summary['partially_useful']} 個")
        print(f"   ❌ 不適用: {summary['not_applicable']} 個")
        
        compatibility = report['compatibility_analysis']
        
        print(f"\n🎯 完全適用工具 ({len(compatibility['完全適用 (🎯)'])} 個):")
        for tool in compatibility['完全適用 (🎯)'][:5]:
            print(f"   ✅ {tool['name']} ({tool['category']})")
        
        if len(compatibility['完全適用 (🎯)']) > 5:
            print(f"   ... 還有 {len(compatibility['完全適用 (🎯)']) - 5} 個工具")
        
        print(f"\n⚠️ 需要調整工具 ({len(compatibility['需要調整 (⚠️)'])} 個):")
        for tool in compatibility['需要調整 (⚠️)'][:5]:
            print(f"   🔧 {tool['name']} ({tool['category']})")
        
        if len(compatibility['需要調整 (⚠️)']) > 5:
            print(f"   ... 還有 {len(compatibility['需要調整 (⚠️)']) - 5} 個工具")
        
        recommendations = report['recommendations']
        
        print(f"\n💡 核心建議:")
        print(f"   🚀 立即可用: {len(recommendations['立即可用工具'])} 個工具")
        print(f"   🔧 需要修改: {len(recommendations['需要修改工具'])} 個工具") 
        print(f"   ➕ 建議新增: {len(recommendations['建議新增功能'])} 個功能")
        print(f"   🏗️ 整合方案: {len(recommendations['整合方案'])} 個方案")
        
        print(f"\n🏆 推薦整合方案:")
        for i, scenario in enumerate(recommendations['整合方案'][:3], 1):
            print(f"   {i}. {scenario['scenario']}")
            print(f"      📋 {scenario['description']}")
            print(f"      🛠️ 工具: {', '.join(scenario['tools'][:3])}")
            if len(scenario['tools']) > 3:
                print(f"          ... 還有 {len(scenario['tools']) - 3} 個工具")

def main():
    analyzer = ToolsAnalyzer()
    
    print("🔍 開始KTV專案工具分析")
    print("=" * 50)
    
    # 分析各類工具
    analyzer.analyze_scrapers()
    analyzer.analyze_frontend()
    analyzer.analyze_database()
    analyzer.analyze_monitoring()
    analyzer.analyze_analysis_tools()
    analyzer.analyze_deployment()
    
    # 評估兼容性並生成報告
    report, filename = analyzer.save_analysis_report()
    
    # 打印摘要報告
    analyzer.print_summary_report(report)
    
    print(f"\n🎯 分析完成:")
    print(f"   📄 詳細報告: {filename}")
    print(f"   📊 工具總數: {report['summary']['total_tools_analyzed']} 個")
    print(f"   ✅ 可用工具: {report['summary']['fully_compatible'] + report['summary']['partially_useful']} 個")
    print(f"\n🚀 建議: 可以使用現有工具快速開始歌手搜尋測試！")

if __name__ == "__main__":
    main()