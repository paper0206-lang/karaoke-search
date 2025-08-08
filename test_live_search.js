// 測試實時搜尋 API
const testLiveSearch = async () => {
    console.log('🧪 測試實時搜尋功能');
    
    const testCases = [
        { keyword: '周杰倫', searchType: 'singer', expected: '應該找到周杰倫的多首歌曲' },
        { keyword: '愛情', searchType: 'song', expected: '應該找到包含"愛情"的歌曲' },
        { keyword: '告白氣球', searchType: 'auto', expected: '應該找到告白氣球這首歌' }
    ];
    
    for (const testCase of testCases) {
        console.log(`\n🔍 測試: ${testCase.keyword} (${testCase.searchType})`);
        console.log(`預期: ${testCase.expected}`);
        
        try {
            const startTime = Date.now();
            
            const response = await fetch('/api/live-search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    keyword: testCase.keyword,
                    searchType: testCase.searchType
                }),
            });
            
            const endTime = Date.now();
            const duration = endTime - startTime;
            
            if (response.ok) {
                const data = await response.json();
                
                console.log(`✅ 成功 (${duration}ms)`);
                console.log(`   找到 ${data.results.length} 首歌曲`);
                
                if (data.results.length > 0) {
                    console.log(`   範例歌曲:`);
                    data.results.slice(0, 3).forEach((song, index) => {
                        const codes = song.編號資訊.map(info => `${info.公司}:${info.編號}`).join(', ');
                        console.log(`     ${index + 1}. ${song.歌名} - ${song.歌手} (${codes})`);
                    });
                }
            } else {
                console.log(`❌ 失敗 (${duration}ms): HTTP ${response.status}`);
                const errorText = await response.text();
                console.log(`   錯誤: ${errorText}`);
            }
            
        } catch (error) {
            console.log(`💥 例外錯誤: ${error.message}`);
        }
        
        // 延遲避免過度請求
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    console.log('\n🎉 測試完成!');
};

// 在瀏覽器控制台中執行
if (typeof window !== 'undefined') {
    window.testLiveSearch = testLiveSearch;
    console.log('💡 在瀏覽器控制台執行 testLiveSearch() 來測試實時搜尋');
}

// 在 Node.js 環境中執行
if (typeof require !== 'undefined') {
    const fetch = require('node-fetch');
    testLiveSearch();
}