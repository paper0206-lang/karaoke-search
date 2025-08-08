const admin = require('firebase-admin');
const fs = require('fs');
const path = require('path');

// 初始化 Firebase Admin SDK
// 請先從 Firebase Console 下載 service account key 並重命名為 serviceAccountKey.json
const serviceAccount = require('./serviceAccountKey.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

async function uploadSongsToFirestore() {
  try {
    // 讀取歌曲資料
    const dataPath = path.join(__dirname, 'data', 'songs_simplified.json');
    
    if (!fs.existsSync(dataPath)) {
      console.error('找不到歌曲資料檔案:', dataPath);
      console.log('請先執行爬蟲程式生成歌曲資料');
      return;
    }

    const songsData = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    console.log(`準備上傳 ${songsData.length} 首歌曲到 Firestore...`);

    const batch = db.batch();
    let count = 0;

    for (const song of songsData) {
      // 使用歌曲編號作為文件 ID
      const docRef = db.collection('songs').doc(song.編號 || `song_${count}`);
      
      // 準備資料
      const songData = {
        name: song.歌名 || '',
        singer: song.歌手 || '',
        code: song.編號 || '',
        company: song.公司 || '',
        createdAt: admin.firestore.FieldValue.serverTimestamp()
      };

      batch.set(docRef, songData);
      count++;

      // Firebase 批次操作限制 500 個
      if (count % 500 === 0) {
        await batch.commit();
        console.log(`已上傳 ${count} 首歌曲...`);
      }
    }

    // 提交剩餘的資料
    if (count % 500 !== 0) {
      await batch.commit();
    }

    console.log(`✅ 成功上傳 ${count} 首歌曲到 Firestore!`);

  } catch (error) {
    console.error('上傳失敗:', error);
  }
}

// 執行上傳
uploadSongsToFirestore().then(() => {
  console.log('上傳完成');
  process.exit(0);
});