const fs = require('fs');
const path = require('path');

// 讀取所有公司的歌曲資料並合併
function mergeSongs() {
  const allSongs = [];
  const dataDir = path.join(__dirname, 'data');
  
  // 讀取每個公司目錄下的 songs.json
  const companies = fs.readdirSync(dataDir, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => dirent.name);
  
  console.log(`找到 ${companies.length} 個公司目錄`);
  
  for (const company of companies) {
    const songsFile = path.join(dataDir, company, 'songs.json');
    if (fs.existsSync(songsFile)) {
      try {
        const songs = JSON.parse(fs.readFileSync(songsFile, 'utf8'));
        console.log(`${company}: ${songs.length} 首歌曲`);
        
        // 轉換格式並添加到總列表
        for (const song of songs) {
          allSongs.push({
            "歌名": song.name || song.歌名 || '',
            "歌手": song.singer || song.歌手 || '',
            "編號": song.code || song.編號 || '',
            "公司": song.company || company
          });
        }
      } catch (error) {
        console.error(`讀取 ${company} 資料失敗:`, error.message);
      }
    }
  }
  
  // 去重 (根據歌名、歌手、編號)
  const uniqueSongs = [];
  const seen = new Set();
  
  for (const song of allSongs) {
    const key = `${song.歌名}-${song.歌手}-${song.編號}`;
    if (!seen.has(key)) {
      seen.add(key);
      uniqueSongs.push(song);
    }
  }
  
  console.log(`合併前: ${allSongs.length} 首`);
  console.log(`去重後: ${uniqueSongs.length} 首`);
  
  // 儲存合併後的資料
  fs.writeFileSync('public/songs_simplified.json', JSON.stringify(uniqueSongs, null, 2));
  console.log('✅ 合併完成！儲存到 public/songs_simplified.json');
  
  return uniqueSongs.length;
}

// 執行合併
const totalSongs = mergeSongs();