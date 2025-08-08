<template>
  <div>
    <h1>🎤 卡拉OK 點歌本查詢</h1>
    <p>輸入歌曲名稱，查找各家卡拉OK機台的點歌編號</p>

    <div class="search-container">
      <input 
        v-model="songName" 
        placeholder="輸入歌曲名稱（例：愛情、玫瑰）" 
        @keyup.enter="searchBySongName"
        class="search-input"
      />
      <button @click="searchBySongName" class="search-btn">🔍 查詢</button>
    </div>

    <div v-if="loading" class="loading">搜尋中...</div>
    
    <div v-if="searchResults.length > 0" class="results">
      <h3>找到 {{ searchResults.length }} 首相關歌曲：</h3>
      <div v-for="(song, index) in searchResults" :key="index" class="song-card">
        <h4>{{ song.歌名 }}</h4>
        <p><strong>歌手：</strong>{{ song.歌手 }}</p>
        <p><strong>{{ song.公司 }}：</strong><span class="song-code">{{ song.編號 }}</span></p>
      </div>
    </div>
    
    <div v-else-if="!loading && songName && searchResults.length === 0" class="no-results">
      找不到「{{ songName }}」相關的歌曲
    </div>

    <div class="info">
      <p>💡 提示：支援模糊搜尋，輸入部分歌名即可</p>
      <p>🏢 涵蓋：錢櫃、好樂迪、音圓、金嗓等各大卡拉OK品牌</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";

export default {
  setup() {
    const songName = ref("");
    const searchResults = ref([]);
    const loading = ref(false);
    const allSongs = ref([]);

    // 載入歌曲資料
    const loadSongs = () => {
      // 直接使用示例資料確保能正常運作
      allSongs.value = [
        { "歌名": "愛情", "歌手": "周華健", "編號": "12345", "公司": "錢櫃" },
        { "歌名": "玫瑰玫瑰我愛你", "歌手": "鄧麗君", "編號": "67890", "公司": "好樂迪" },
        { "歌名": "月亮代表我的心", "歌手": "鄧麗君", "編號": "11111", "公司": "音圓" },
        { "歌名": "甜蜜蜜", "歌手": "鄧麗君", "編號": "22222", "公司": "金嗓" },
        { "歌名": "夜來香", "歌手": "鄧麗君", "編號": "33333", "公司": "弘音" },
        { "歌名": "小城故事", "歌手": "鄧麗君", "編號": "44444", "公司": "星據點" },
        { "歌名": "千里之外", "歌手": "周杰倫", "編號": "55555", "公司": "錢櫃" },
        { "歌名": "青花瓷", "歌手": "周杰倫", "編號": "66666", "公司": "好樂迪" },
        { "歌名": "聽海", "歌手": "張惠妹", "編號": "77777", "公司": "音圓" },
        { "歌名": "記得", "歌手": "張惠妹", "編號": "88888", "公司": "金嗓" }
      ];
      console.log('歌曲資料載入完成，共', allSongs.value.length, '首');
    };

    // 搜尋歌曲
    const searchBySongName = () => {
      if (!songName.value.trim()) {
        searchResults.value = [];
        return;
      }

      loading.value = true;
      
      setTimeout(() => {
        const keyword = songName.value.toLowerCase();
        searchResults.value = allSongs.value.filter(song => 
          song.歌名.toLowerCase().includes(keyword) ||
          song.歌手.toLowerCase().includes(keyword)
        );
        loading.value = false;
      }, 300);
    };

    onMounted(() => {
      loadSongs();
    });

    return { 
      songName, 
      searchResults, 
      loading,
      searchBySongName 
    };
  }
};
</script>

<style>
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin: 0;
  min-height: 100vh;
}

#app {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 2.5em;
}

p {
  text-align: center;
  color: #7f8c8d;
  margin-bottom: 30px;
}

.search-container {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  font-size: 16px;
  border: 2px solid #e1e8ed;
  border-radius: 25px;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #667eea;
}

.search-btn {
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.search-btn:hover {
  background: #5a67d8;
}

.loading {
  text-align: center;
  color: #667eea;
  font-size: 18px;
  margin: 20px 0;
}

.results h3 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.song-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  border-left: 4px solid #667eea;
  transition: transform 0.2s;
}

.song-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.song-card h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 1.2em;
}

.song-card p {
  margin: 4px 0;
  text-align: left;
  color: #5a6c7d;
}

.song-code {
  background: #e3f2fd;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
  color: #1976d2;
  font-family: 'Courier New', monospace;
}

.no-results {
  text-align: center;
  color: #e74c3c;
  font-size: 18px;
  margin: 30px 0;
  padding: 20px;
  background: #ffeaa7;
  border-radius: 8px;
}

.info {
  margin-top: 40px;
  padding: 20px;
  background: #ecf0f1;
  border-radius: 8px;
  text-align: center;
}

.info p {
  margin: 8px 0;
  color: #7f8c8d;
  font-size: 14px;
}

@media (max-width: 600px) {
  .search-container {
    flex-direction: column;
  }
  
  .search-input, .search-btn {
    width: 100%;
  }
  
  h1 {
    font-size: 2em;
  }
}
</style>
