#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版搜尋API - 整合所有資料源的智能搜尋
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import requests
import logging
import re
from datetime import datetime
from difflib import SequenceMatcher

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app)

class EnhancedSearchEngine:
    def __init__(self):
        self.songs_db = []
        self.singers_db = {}
        self.unified_db = {}
        self.load_all_databases()
    
    def load_all_databases(self):
        """載入所有本地資料庫"""
        try:
            # 載入歌曲資料庫
            if os.path.exists('public/songs_simplified.json'):
                with open('public/songs_simplified.json', 'r', encoding='utf-8') as f:
                    self.songs_db = json.load(f)
                logging.info(f"載入歌曲資料庫: {len(self.songs_db)} 首歌")
            
            # 載入歌手資料庫
            if os.path.exists('public/singers_data.json'):
                with open('public/singers_data.json', 'r', encoding='utf-8') as f:
                    self.singers_db = json.load(f)
                logging.info(f"載入歌手資料庫: {len(self.singers_db)} 位歌手")
            
            # 載入統一資料庫
            if os.path.exists('public/unified_karaoke_db.json'):
                with open('public/unified_karaoke_db.json', 'r', encoding='utf-8') as f:
                    self.unified_db = json.load(f)
                logging.info(f"載入統一資料庫: {self.unified_db.get('metadata', {}).get('total_songs', 0)} 首歌")
                    
        except Exception as e:
            logging.error(f"載入資料庫失敗: {e}")
    
    def similarity(self, a, b):
        """計算字串相似度"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def smart_search_local(self, query, max_results=300):
        """智能本地搜尋"""
        results = []
        query_lower = query.lower().strip()
        
        # 搜尋策略1: 歌手資料庫 (優先)
        for singer_name, singer_data in self.singers_db.items():
            if (query in singer_name or 
                query in singer_name.lower() or 
                self.similarity(query, singer_name) > 0.6):
                
                # 找到匹配的歌手，返回所有歌曲
                for song in singer_data.get('歌曲清單', []):
                    results.append({
                        'source': 'singer_db',
                        'match_type': 'singer_match',
                        'confidence': 0.9,
                        **song
                    })
        
        # 搜尋策略2: 統一資料庫
        if 'songs' in self.unified_db:
            for song_id, song_data in self.unified_db['songs'].items():
                song_name = song_data.get('歌名', '')
                singer_name = song_data.get('歌手', '')
                
                if (query in song_name or query in singer_name or
                    self.similarity(query, song_name) > 0.7 or
                    self.similarity(query, singer_name) > 0.7):
                    
                    results.append({
                        'source': 'unified_db',
                        'match_type': 'song_match',
                        'confidence': 0.8,
                        **song_data
                    })
        
        # 搜尋策略3: 歌曲資料庫
        for song in self.songs_db:
            song_name = song.get('歌名', '')
            singer_name = song.get('歌手', '')
            
            # 精確匹配
            if query in song_name or query in singer_name:
                results.append({
                    'source': 'songs_db',
                    'match_type': 'exact_match',
                    'confidence': 0.95,
                    **song
                })
            # 模糊匹配
            elif (self.similarity(query, song_name) > 0.6 or 
                  self.similarity(query, singer_name) > 0.6):
                results.append({
                    'source': 'songs_db', 
                    'match_type': 'fuzzy_match',
                    'confidence': 0.7,
                    **song
                })
        
        # 按信心度排序並去重
        results.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # 簡單去重 (基於歌名+歌手)
        seen = set()
        unique_results = []
        for result in results:
            key = f"{result.get('歌名', '')}_{result.get('歌手', '')}"
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        return unique_results[:max_results]
    
    def search_taiwan_ktv(self, query):
        """搜尋台灣點歌王API"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'X-Requested-With': 'XMLHttpRequest',
            }
            
            api_url = 'https://song.corp.com.tw/api/song.aspx'
            params = {
                'company': '全部',
                'cusType': 'searchList',
                'keyword': query
            }
            
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # 標記來源並添加信心度
                    for item in data:
                        item['source'] = 'taiwan_ktv'
                        item['match_type'] = 'api_result'
                        item['confidence'] = 0.85
                    return data[:200]  # 限制結果數量
            return []
            
        except Exception as e:
            logging.error(f"台灣KTV搜尋失敗: {e}")
            return []
    
    def comprehensive_search(self, query):
        """綜合搜尋 - 整合所有資料源"""
        if not query or not query.strip():
            return []
        
        query = query.strip()
        logging.info(f"開始綜合搜尋: {query}")
        
        # 並行搜尋各資料源
        local_results = self.smart_search_local(query)
        api_results = self.search_taiwan_ktv(query)
        
        # 合併結果
        all_results = local_results + api_results
        
        # 統一格式並去重
        unified_results = self.unify_results(all_results)
        
        logging.info(f"搜尋完成: 本地 {len(local_results)} + API {len(api_results)} = 總計 {len(unified_results)} 首歌")
        
        return unified_results
    
    def unify_results(self, results):
        """統一結果格式並進行智能去重"""
        unified = {}
        
        for item in results:
            # 標準化字段名稱
            song_name = (item.get('歌名') or item.get('name') or '').strip()
            singer_name = (item.get('歌手') or item.get('singer') or '').strip()
            
            if not song_name or not singer_name:
                continue
            
            # 創建唯一鍵
            key = f"{song_name}||{singer_name}"
            
            if key not in unified:
                unified[key] = {
                    '歌名': song_name,
                    '歌手': singer_name,
                    '語言': item.get('語言') or item.get('lang') or '',
                    '編號資訊': [],
                    'sources': [],
                    'confidence': item.get('confidence', 0.5)
                }
            
            # 添加編號資訊
            if '編號資訊' in item and isinstance(item['編號資訊'], list):
                # 已經是編號資訊格式
                for code_info in item['編號資訊']:
                    if code_info not in unified[key]['編號資訊']:
                        unified[key]['編號資訊'].append(code_info)
            else:
                # 單一編號格式
                company = item.get('公司') or item.get('company') or ''
                code = item.get('編號') or item.get('code') or ''
                
                if company and code:
                    code_info = {'公司': company, '編號': code}
                    if code_info not in unified[key]['編號資訊']:
                        unified[key]['編號資訊'].append(code_info)
            
            # 記錄來源
            source = item.get('source', 'unknown')
            if source not in unified[key]['sources']:
                unified[key]['sources'].append(source)
        
        # 排序編號資訊
        company_priority = ['錢櫃', '好樂迪', '銀櫃', '音圓', '金嗓', '弘音', '星據點', 'MV']
        
        for item in unified.values():
            item['編號資訊'].sort(key=lambda x: (
                company_priority.index(x['公司']) if x['公司'] in company_priority else 999,
                x['公司'],
                x['編號']
            ))
        
        # 按信心度和編號數量排序
        result_list = list(unified.values())
        result_list.sort(key=lambda x: (x['confidence'], len(x['編號資訊'])), reverse=True)
        
        return result_list

# 初始化搜尋引擎
search_engine = EnhancedSearchEngine()

@app.route('/api/enhanced-search', methods=['GET'])
def enhanced_search():
    """增強版搜尋API"""
    query = request.args.get('keyword', '').strip()
    
    if not query:
        return jsonify({
            'success': False,
            'error': '請輸入搜尋關鍵字'
        }), 400
    
    try:
        results = search_engine.comprehensive_search(query)
        
        return jsonify({
            'success': True,
            'query': query,
            'total': len(results),
            'data': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"增強搜尋失敗: {str(e)}")
        return jsonify({
            'success': False,
            'error': '搜尋過程發生錯誤'
        }), 500

@app.route('/api/singer-search', methods=['GET'])
def singer_search():
    """專門的歌手搜尋"""
    query = request.args.get('singer', '').strip()
    
    if not query:
        return jsonify({'success': False, 'error': '請輸入歌手名稱'}), 400
    
    try:
        # 專門搜尋歌手
        singer_results = []
        
        for singer_name, singer_data in search_engine.singers_db.items():
            if query in singer_name or search_engine.similarity(query, singer_name) > 0.7:
                songs = singer_data.get('歌曲清單', [])
                singer_results.extend(songs)
        
        return jsonify({
            'success': True,
            'singer': query,
            'total': len(singer_results),
            'data': singer_results
        })
        
    except Exception as e:
        logging.error(f"歌手搜尋失敗: {str(e)}")
        return jsonify({'success': False, 'error': '搜尋失敗'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """取得資料庫統計"""
    try:
        stats = {
            'songs_db_count': len(search_engine.songs_db),
            'singers_count': len(search_engine.singers_db),
            'unified_db_songs': search_engine.unified_db.get('metadata', {}).get('total_songs', 0),
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))  # 使用不同端口避免衝突
    app.run(debug=False, host='0.0.0.0', port=port)