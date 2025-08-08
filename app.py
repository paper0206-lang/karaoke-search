from flask import Flask, jsonify, request
from flask_cors import CORS
from karaoke_scraper import KaraokeScraper
import logging

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

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 