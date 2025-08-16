// 在瀏覽器控制台執行這個代碼來調試搜尋問題

async function debugSearch() {
    console.log('🔍 開始調試搜尋功能...');
    
    try {
        // 1. 測試資料載入
        console.log('1. 測試資料載入...');
        const songsRes = await fetch('/songs_simplified.json');
        const singersRes = await fetch('/singers_data.json');
        
        console.log('歌曲資料狀態:', songsRes.status);
        console.log('歌手資料狀態:', singersRes.status);
        
        if (!songsRes.ok || !singersRes.ok) {
            console.error('❌ 資料載入失敗');
            return;
        }
        
        const allSongs = await songsRes.json();
        const singersData = await singersRes.json();
        
        console.log('✅ 資料載入成功');
        console.log('歌曲總數:', allSongs.length);
        console.log('歌手總數:', Object.keys(singersData).length);
        
        // 2. 測試搜尋邏輯
        console.log('2. 測試搜尋邏輯...');
        const query = '周杰倫';
        
        // 測試歌曲搜尋
        const songResults = allSongs.filter(song => 
            song.歌名?.includes(query) || 
            song.歌手?.includes(query)
        );
        
        console.log(`🎵 歌曲搜尋結果: ${songResults.length} 首`);
        
        // 測試歌手搜尋
        const singerMatch = singersData[query];
        if (singerMatch) {
            console.log(`🎤 歌手資料庫: ${singerMatch.歌曲清單.length} 首`);
        } else {
            console.log('❌ 歌手資料庫中沒有找到周杰倫');
        }
        
        // 3. 模擬前端搜尋邏輯
        console.log('3. 模擬前端搜尋邏輯...');
        let finalResults = songResults; // 優先使用歌曲搜尋結果
        
        if (singerMatch && (finalResults.length < 50 || finalResults.length < singerMatch.歌曲清單.length)) {
            console.log('合併歌手資料庫結果...');
            const singerSongs = singerMatch.歌曲清單.map(song => ({
                歌名: song.歌名,
                歌手: query,
                語言: song.語言,
                編號資訊: song.編號資訊
            }));
            
            // 合併去重
            const combined = [...finalResults];
            singerSongs.forEach(singerSong => {
                const exists = combined.find(localSong => 
                    localSong.歌名 === singerSong.歌名 && 
                    localSong.歌手?.includes(query)
                );
                if (!exists) {
                    combined.push(singerSong);
                }
            });
            
            finalResults = combined;
        }
        
        console.log(`✅ 最終結果: ${finalResults.length} 首`);
        console.log('前5首:', finalResults.slice(0, 5));
        
        // 4. 測試歌曲歸納
        console.log('4. 測試歌曲歸納...');
        const groups = {};
        finalResults.forEach(song => {
            const key = `${song.歌名}_${song.歌手}`;
            if (!groups[key]) {
                groups[key] = {
                    歌名: song.歌名,
                    歌手: song.歌手,
                    語言: song.語言 || '',
                    編號資訊: []
                };
            }
            
            const codeInfo = {
                公司: song.公司 || song.編號資訊?.[0]?.公司 || '',
                編號: song.編號 || song.編號資訊?.[0]?.編號 || ''
            };
            
            if (song.編號資訊 && Array.isArray(song.編號資訊)) {
                song.編號資訊.forEach(code => {
                    if (!groups[key].編號資訊.some(existing => 
                        existing.公司 === code.公司 && existing.編號 === code.編號)) {
                        groups[key].編號資訊.push(code);
                    }
                });
            } else {
                if (codeInfo.公司 && codeInfo.編號 && 
                    !groups[key].編號資訊.some(existing => 
                      existing.公司 === codeInfo.公司 && existing.編號 === codeInfo.編號)) {
                    groups[key].編號資訊.push(codeInfo);
                }
            }
        });
        
        const groupedResults = Object.values(groups);
        console.log(`📊 歸納後: ${groupedResults.length} 首獨特歌曲`);
        console.log('前3首歸納結果:', groupedResults.slice(0, 3));
        
        return {
            songsCount: allSongs.length,
            singersCount: Object.keys(singersData).length,
            searchResults: finalResults.length,
            groupedResults: groupedResults.length
        };
        
    } catch (error) {
        console.error('❌ 調試失敗:', error);
    }
}

// 執行調試
debugSearch().then(result => {
    if (result) {
        console.log('🎯 調試總結:', result);
    }
});

console.log('請複製這段代碼到瀏覽器控制台執行，查看詳細的搜尋調試資訊');