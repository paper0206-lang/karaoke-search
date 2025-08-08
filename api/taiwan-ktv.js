export default async function handler(req, res) {
  // 設定CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept');
  
  // 處理OPTIONS請求 (CORS預檢)
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  // 只處理GET請求
  if (req.method !== 'GET') {
    return res.status(405).json({ error: '只支援GET請求' });
  }
  
  try {
    const { keyword } = req.query;
    
    if (!keyword) {
      return res.status(400).json({ error: '請輸入搜尋關鍵字' });
    }
    
    console.log(`🔍 正在搜尋台灣點歌王: ${keyword}`);
    
    // 設定請求標頭，模擬正常瀏覽器請求
    const headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept': 'application/json, text/javascript, */*; q=0.01',
      'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
      'Referer': 'https://song.corp.com.tw/',
      'X-Requested-With': 'XMLHttpRequest',
    };
    
    // 台灣點歌王API URL
    const taiwanApiUrl = 'https://song.corp.com.tw/api/song.aspx';
    const params = new URLSearchParams({
      company: '全部',
      cusType: 'searchList',
      keyword: keyword
    });
    
    const url = `${taiwanApiUrl}?${params}`;
    
    // 發送請求到台灣點歌王API
    const response = await fetch(url, {
      method: 'GET',
      headers: headers
    });
    
    if (response.ok) {
      try {
        // 先獲取文字內容，然後手動解析
        const textContent = await response.text();
        console.log(`📄 台灣點歌王原始回應: ${textContent.substring(0, 200)}...`);
        
        // 嘗試解析JSON
        let data;
        try {
          data = JSON.parse(textContent);
        } catch (parseError) {
          console.error(`❌ JSON解析失敗: ${parseError.message}`);
          console.error(`📄 無法解析的內容: ${textContent}`);
          return res.status(500).json({
            success: false,
            error: '搜尋結果格式錯誤，無法解析'
          });
        }
        
        if (Array.isArray(data)) {
          // 限制結果數量，避免過多資料
          const limitedData = data.slice(0, 50);
          
          console.log(`✅ 台灣點歌王搜尋成功: 找到 ${data.length} 首歌曲，回傳前 ${limitedData.length} 首`);
          
          return res.status(200).json({
            success: true,
            data: limitedData,
            total: data.length
          });
        } else {
          console.warn(`⚠️ 台灣點歌王回傳非陣列資料: ${typeof data}`);
          return res.status(200).json({
            success: true,
            data: [],
            total: 0
          });
        }
        
      } catch (error) {
        console.error(`❌ 台灣點歌王回應處理失敗: ${error.message}`);
        return res.status(500).json({
          success: false,
          error: '搜尋結果處理失敗'
        });
      }
    } else {
      console.error(`❌ 台灣點歌王API請求失敗: HTTP ${response.status} ${response.statusText}`);
      
      // 嘗試獲取錯誤訊息
      try {
        const errorText = await response.text();
        console.error(`📄 錯誤回應內容: ${errorText}`);
      } catch (e) {
        console.error('無法讀取錯誤回應內容');
      }
      
      return res.status(500).json({
        success: false,
        error: `台灣點歌王API請求失敗: HTTP ${response.status}`
      });
    }
    
  } catch (error) {
    if (error.name === 'AbortError' || error.message.includes('timeout')) {
      console.error('❌ 台灣點歌王API請求超時');
      return res.status(500).json({
        success: false,
        error: '搜尋請求超時，請稍後再試'
      });
    }
    
    if (error.message.includes('fetch')) {
      console.error(`❌ 台灣點歌王API請求錯誤: ${error.message}`);
      return res.status(500).json({
        success: false,
        error: '無法連接到台灣點歌王服務'
      });
    }
    
    console.error(`❌ 台灣點歌王搜尋未知錯誤: ${error.message}`);
    return res.status(500).json({
      success: false,
      error: '搜尋過程發生未知錯誤'
    });
  }
}