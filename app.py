from flask import Flask, jsonify, request
from flask_cors import CORS
from karaoke_scraper import KaraokeScraper
import logging
import requests
import json

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app)  # 允許跨域請求

# 初始化爬蟲實例
scraper = KaraokeScraper()
scraper.init_session()

@app.route('/api/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({'error': '請輸入搜尋關鍵字'}), 400
        
    try:
        results = scraper.search_song(keyword)
        if results is None:
            return jsonify({'error': '搜尋失敗'}), 500
            
        # 格式化結果
        formatted_results = []
        for song in results:
            formatted_song = {
                '歌名': song.get('name', ''),
                '歌手': song.get('singer', ''),
                '編號': song.get('code', ''),
                '公司': song.get('company', ''),
                'youtubeID': song.get('youtubeID', '')
            }
            formatted_results.append(formatted_song)
            
        return jsonify({
            'success': True,
            'data': formatted_results
        })
        
    except Exception as e:
        logging.error(f"搜尋出錯: {str(e)}")
        return jsonify({'error': '搜尋過程發生錯誤'}), 500

@app.route('/api/taiwan-ktv', methods=['GET'])
def taiwan_ktv_search():
    """台灣點歌王搜尋代理API"""
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({'error': '請輸入搜尋關鍵字'}), 400
        
    try:
        # 設定請求標頭，模擬正常瀏覽器請求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://song.corp.com.tw/',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        # 台灣點歌王API URL
        taiwan_api_url = 'https://song.corp.com.tw/api/song.aspx'
        params = {
            'company': '全部',
            'cusType': 'searchList',
            'keyword': keyword
        }
        
        logging.info(f"正在搜尋台灣點歌王: {keyword}")
        
        # 發送請求到台灣點歌王API
        response = requests.get(taiwan_api_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    # 限制結果數量，避免過多資料
                    limited_data = data[:50]
                    
                    logging.info(f"台灣點歌王搜尋成功: 找到 {len(data)} 首歌曲，回傳前 {len(limited_data)} 首")
                    
                    return jsonify({
                        'success': True,
                        'data': limited_data,
                        'total': len(data)
                    })
                else:
                    logging.warning(f"台灣點歌王回傳非陣列資料: {type(data)}")
                    return jsonify({
                        'success': False,
                        'error': '搜尋結果格式錯誤'
                    }), 500
                    
            except Exception as json_error:
                logging.error(f"台灣點歌王回傳資料解析失敗: {str(json_error)}")
                return jsonify({
                    'success': False,
                    'error': '搜尋結果解析失敗'
                }), 500
        else:
            logging.error(f"台灣點歌王API請求失敗: HTTP {response.status_code}")
            return jsonify({
                'success': False,
                'error': f'台灣點歌王API請求失敗: HTTP {response.status_code}'
            }), 500
            
    except requests.exceptions.Timeout:
        logging.error("台灣點歌王API請求超時")
        return jsonify({
            'success': False,
            'error': '搜尋請求超時，請稍後再試'
        }), 500
        
    except requests.exceptions.RequestException as e:
        logging.error(f"台灣點歌王API請求錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'error': '無法連接到台灣點歌王服務'
        }), 500
        
    except Exception as e:
        logging.error(f"台灣點歌王搜尋未知錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'error': '搜尋過程發生未知錯誤'
        }), 500

def search_taiwan_ktv(keyword):
    """搜尋台灣點歌王的函數"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://song.corp.com.tw/',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        api_url = 'https://song.corp.com.tw/api/song.aspx'
        params = {
            'company': '全部',
            'cusType': 'searchList',
            'keyword': keyword
        }
        
        logging.info(f"正在搜尋台灣點歌王: {keyword}")
        
        response = requests.get(api_url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                # 轉換資料格式，與本地資料庫格式統一
                results = []
                for song in data:
                    result = {
                        '歌名': song.get('name', ''),
                        '歌手': song.get('singer', ''),
                        '編號': song.get('code', ''),
                        '公司': song.get('company', ''),
                        '語言': song.get('lang', ''),
                    }
                    results.append(result)
                
                logging.info(f"台灣點歌王搜尋成功: 找到 {len(results)} 首歌曲")
                return results
            else:
                logging.warning(f"台灣點歌王回傳非陣列資料: {type(data)}")
                return []
        else:
            logging.error(f"台灣點歌王API請求失敗: HTTP {response.status_code}")
            return []
            
    except Exception as e:
        logging.error(f"台灣點歌王搜尋錯誤: {str(e)}")
        return []

@app.route('/api/taiwan-search', methods=['GET'])
def taiwan_search():
    """台灣點歌王搜尋API端點"""
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({'error': '請輸入搜尋關鍵字'}), 400
    
    try:
        results = search_taiwan_ktv(keyword)
        
        if results:
            # 限制結果數量
            limited_results = results[:50]
            return jsonify({
                'success': True,
                'data': limited_results,
                'total': len(results),
                'source': '台灣點歌王'
            })
        else:
            return jsonify({
                'success': True,
                'data': [],
                'total': 0,
                'source': '台灣點歌王'
            })
            
    except Exception as e:
        logging.error(f"台灣點歌王搜尋API錯誤: {str(e)}")
        return jsonify({'error': '搜尋過程發生錯誤'}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 