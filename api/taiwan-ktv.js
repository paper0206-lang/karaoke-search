export default async function handler(req, res) {
  try {
    // 設定CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    
    // 處理OPTIONS請求 (CORS預檢)
    if (req.method === 'OPTIONS') {
      return res.status(200).end();
    }
    
    // 只處理GET請求
    if (req.method !== 'GET') {
      return res.status(405).json({ 
        success: false, 
        error: '只支援GET請求' 
      });
    }
    
    const keyword = req.query.keyword;
    
    if (!keyword) {
      return res.status(400).json({ 
        success: false, 
        error: '請輸入搜尋關鍵字' 
      });
    }
    
    console.log(`🔍 收到搜尋請求: ${keyword}`);
    
    // 台灣點歌王API請求
    const taiwanUrl = 'https://song.corp.com.tw/api/song.aspx';
    const searchParams = new URLSearchParams({
      company: '全部',
      cusType: 'searchList',
      keyword: keyword
    }).toString();
    
    const fullUrl = `${taiwanUrl}?${searchParams}`;
    console.log(`📡 請求URL: ${fullUrl}`);
    
    const response = await fetch(fullUrl, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://song.corp.com.tw/',
        'X-Requested-With': 'XMLHttpRequest'
      },
      timeout: 15000
    });
    
    console.log(`📄 台灣點歌王回應狀態: ${response.status}`);
    
    if (!response.ok) {
      console.error(`❌ 台灣點歌王API錯誤: ${response.status}`);
      return res.status(500).json({
        success: false,
        error: `台灣點歌王API錯誤: ${response.status}`
      });
    }
    
    const responseText = await response.text();
    console.log(`📄 回應長度: ${responseText.length}`);
    console.log(`📄 回應開頭: ${responseText.substring(0, 100)}`);
    
    let songs;
    try {
      songs = JSON.parse(responseText);
    } catch (parseError) {
      console.error(`❌ JSON解析失敗: ${parseError.message}`);
      console.error(`📄 原始內容: ${responseText.substring(0, 500)}`);
      return res.status(500).json({
        success: false,
        error: '資料格式錯誤'
      });
    }
    
    if (!Array.isArray(songs)) {
      console.log(`⚠️ 不是陣列格式: ${typeof songs}`);
      return res.status(200).json({
        success: true,
        data: [],
        total: 0
      });
    }
    
    // 限制返回數量
    const limitedSongs = songs.slice(0, 50);
    
    console.log(`✅ 搜尋成功: ${songs.length} 首，返回 ${limitedSongs.length} 首`);
    
    return res.status(200).json({
      success: true,
      data: limitedSongs,
      total: songs.length
    });
    
  } catch (error) {
    console.error(`❌ API錯誤: ${error.message}`);
    console.error(error.stack);
    
    return res.status(500).json({
      success: false,
      error: '服務器錯誤: ' + error.message
    });
  }
}