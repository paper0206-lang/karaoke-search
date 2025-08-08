import fetch from 'node-fetch';

// 台灣點歌王實時搜尋 API
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
        
        const results = await performLiveSearch(keyword.trim(), searchType);
        
        console.log(`✅ 搜尋完成: 找到 ${results.length} 首歌曲`);
        
        return res.status(200).json({
            success: true,
            keyword: keyword.trim(),
            searchType,
            results,
            timestamp: new Date().toISOString(),
            total: results.length
        });
        
    } catch (error) {
        console.error('❌ 搜尋失敗:', error);
        return res.status(500).json({ 
            error: '搜尋失敗', 
            message: error.message 
        });
    }
}

async function performLiveSearch(keyword, searchType) {
    const baseUrl = "https://song.corp.com.tw";
    const allResults = [];
    
    // 所有卡拉OK公司
    const companies = ['全部', '錢櫃', '好樂迪', '銀櫃', '音圓', '金嗓', '弘音', '星據點', '音霸', '大東', '點將家'];
    
    // 搜尋策略
    const searchStrategies = getSearchStrategies(keyword, searchType);
    
    for (const company of companies) {
        console.log(`  🏢 搜尋 ${company}...`);
        
        for (const strategy of searchStrategies) {
            try {
                const url = `${baseUrl}/api/song.aspx`;
                const params = new URLSearchParams({
                    'company': company,
                    'cusType': strategy.type,
                    'keyword': strategy.keyword
                });
                
                const response = await fetch(`${url}?${params}`, {
                    method: 'GET',
                    headers: {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                        'Referer': 'https://song.corp.com.tw/',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    timeout: 8000 // 8秒超時
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    if (Array.isArray(data) && data.length > 0) {
                        // 過濾相關結果
                        const filteredResults = filterRelevantSongs(data, keyword, searchType);
                        allResults.push(...filteredResults);
                        
                        console.log(`    ✅ ${strategy.name}: ${filteredResults.length} 首`);
                    }
                }
                
                // 短暫延遲避免被封鎖
                await sleep(300);
                
            } catch (error) {
                console.log(`    ❌ ${strategy.name}: ${error.message}`);
            }
        }
        
        // 公司間延遲
        await sleep(500);
    }
    
    // 去重並排序
    return deduplicateAndSort(allResults);
}

function getSearchStrategies(keyword, searchType) {
    const strategies = [];
    
    if (searchType === 'song' || searchType === 'auto') {
        // 歌名搜尋策略
        strategies.push(
            { name: '歌名搜尋', type: 'searchList', keyword: keyword },
            { name: '新歌搜尋', type: 'newSong', keyword: keyword }
        );
        
        // 如果關鍵字較長，嘗試部分搜尋
        if (keyword.length > 2) {
            for (let i = 0; i < keyword.length - 1; i++) {
                const partial = keyword.substring(i, i + 2);
                if (partial.length === 2) {
                    strategies.push({ 
                        name: `部分搜尋(${partial})`, 
                        type: 'searchList', 
                        keyword: partial 
                    });
                }
            }
        }
    }
    
    if (searchType === 'singer' || searchType === 'auto') {
        // 歌手搜尋策略  
        strategies.push(
            { name: '歌手搜尋', type: 'searchList', keyword: keyword },
            { name: '熱門歌手', type: 'hotSong', keyword: keyword }
        );
        
        // 歌手名部分搜尋
        if (keyword.length > 2) {
            for (let i = 0; i < keyword.length - 1; i++) {
                const partial = keyword.substring(i, i + 2);
                if (partial.length === 2) {
                    strategies.push({ 
                        name: `歌手部分(${partial})`, 
                        type: 'searchList', 
                        keyword: partial 
                    });
                }
            }
        }
    }
    
    // 去重策略
    const uniqueStrategies = [];
    const seen = new Set();
    
    for (const strategy of strategies) {
        const key = `${strategy.type}-${strategy.keyword}`;
        if (!seen.has(key)) {
            seen.add(key);
            uniqueStrategies.push(strategy);
        }
    }
    
    return uniqueStrategies;
}

function filterRelevantSongs(songs, keyword, searchType) {
    return songs.filter(song => {
        const songName = (song.name || '').toLowerCase();
        const singerName = (song.singer || '').toLowerCase();
        const keywordLower = keyword.toLowerCase();
        
        if (searchType === 'song') {
            // 歌名搜尋：歌名必須包含關鍵字
            return songName.includes(keywordLower);
        } else if (searchType === 'singer') {
            // 歌手搜尋：歌手名必須包含關鍵字
            return singerName.includes(keywordLower);
        } else {
            // 自動搜尋：歌名或歌手名包含關鍵字即可
            return songName.includes(keywordLower) || singerName.includes(keywordLower);
        }
    });
}

function deduplicateAndSort(songs) {
    const songMap = new Map();
    
    // 按公司優先順序排序
    const companyPriority = ['錢櫃', '好樂迪', '銀櫃', '音圓', '金嗓', '弘音', '星據點', '音霸', '大東', '點將家'];
    
    songs.forEach(song => {
        const key = `${song.name || ''}-${song.singer || ''}`;
        
        if (!songMap.has(key)) {
            songMap.set(key, {
                歌名: song.name || '',
                歌手: song.singer || '',
                語言: song.lang || '',
                編號資訊: []
            });
        }
        
        const songData = songMap.get(key);
        
        // 添加編號資訊
        if (song.code && song.company) {
            const existing = songData.編號資訊.find(info => 
                info.公司 === song.company && info.編號 === song.code
            );
            
            if (!existing) {
                songData.編號資訊.push({
                    公司: song.company,
                    編號: song.code
                });
            }
        }
    });
    
    // 轉換為陣列並排序編號資訊
    const result = Array.from(songMap.values()).map(song => {
        song.編號資訊.sort((a, b) => {
            const aPriority = companyPriority.indexOf(a.公司);
            const bPriority = companyPriority.indexOf(b.公司);
            
            if (aPriority !== -1 && bPriority !== -1) {
                return aPriority - bPriority;
            } else if (aPriority !== -1) {
                return -1;
            } else if (bPriority !== -1) {
                return 1;
            } else {
                return a.公司.localeCompare(b.公司);
            }
        });
        
        return song;
    });
    
    return result;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}