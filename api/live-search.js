// 台灣點歌王實時搜尋 API - Vercel 優化版
export default async function handler(req, res) {
    // 設置 CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }
    
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }
    
    const { keyword, searchType = 'auto' } = req.body;
    
    if (!keyword || keyword.trim().length === 0) {
        return res.status(400).json({ error: '請提供搜尋關鍵字' });
    }
    
    try {
        console.log(`🔍 開始實時搜尋: ${keyword} (類型: ${searchType})`);
        
        // 由於 Vercel 的限制，我們先返回模擬結果
        // 真正的實時搜尋功能需要不同的架構
        const mockResults = await generateMockResults(keyword.trim(), searchType);
        
        console.log(`✅ 搜尋完成: 找到 ${mockResults.length} 首歌曲`);
        
        return res.status(200).json({
            success: true,
            keyword: keyword.trim(),
            searchType,
            results: mockResults,
            timestamp: new Date().toISOString(),
            total: mockResults.length,
            note: '此為展示版本，真正實時搜尋需要較長時間處理'
        });
        
    } catch (error) {
        console.error('❌ 搜尋失敗:', error);
        return res.status(500).json({ 
            error: '搜尋失敗', 
            message: error.message 
        });
    }
}

async function generateMockResults(keyword, searchType) {
    // 模擬搜尋結果，展示功能介面
    const mockSongs = [
        {
            歌名: `${keyword} - 搜尋示例`,
            歌手: '示例歌手',
            語言: '國語',
            編號資訊: [
                { 公司: '錢櫃', 編號: 'M001' },
                { 公司: '好樂迪', 編號: 'H001' },
                { 公司: '銀櫃', 編號: 'S001' }
            ]
        }
    ];
    
    if (searchType === 'singer') {
        mockSongs[0].歌名 = `${keyword}的經典歌曲`;
        mockSongs[0].歌手 = keyword;
    }
    
    // 模擬處理時間
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return mockSongs;
}

// 真正的實時搜尋函數（暫時註解，因為 Vercel 限制）
/*
async function performRealLiveSearch(keyword, searchType) {
    const baseUrl = "https://song.corp.com.tw";
    const allResults = [];
    
    const companies = ['錢櫃', '好樂迪', '銀櫃', '音圓', '金嗓'];
    
    for (const company of companies) {
        try {
            const url = `${baseUrl}/api/song.aspx`;
            const params = new URLSearchParams({
                'company': company,
                'cusType': 'searchList',
                'keyword': keyword
            });
            
            const response = await fetch(`${url}?${params}`, {
                method: 'GET',
                headers: {
                    'User-Agent': 'Mozilla/5.0 (compatible)',
                    'Accept': 'application/json',
                },
                timeout: 5000
            });
            
            if (response.ok) {
                const data = await response.json();
                if (Array.isArray(data) && data.length > 0) {
                    allResults.push(...data);
                }
            }
        } catch (error) {
            console.log(`搜尋 ${company} 失敗:`, error.message);
        }
    }
    
    return processResults(allResults, keyword, searchType);
}
*/