<template>
  <div>
    <h1>🎤 卡拉OK 點歌本查詢</h1>
    <p>輸入歌曲名稱，查找各家卡拉OK機台的點歌編號</p>

    <div class="search-container">
      <input 
        v-model="songName" 
        placeholder="輸入歌曲名稱或歌手（例：愛情、周杰倫）" 
        @keyup.enter="searchBySongName"
        @input="clearSearch"
        class="search-input"
      />
      <button @click="searchBySongName" class="search-btn" :disabled="!songName.trim()">
        🔍 查詢
      </button>
    </div>

    <!-- 只在有搜尋關鍵字但還沒搜尋時顯示提示 -->
    <div v-if="songName.trim() && searchResults.length === 0 && !loading" class="search-hint">
      請按「查詢」按鈕或按 Enter 鍵開始搜尋
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      搜尋中，請稍候...
    </div>
    
    <!-- 本地搜尋結果 -->
    <div v-if="!loading && searchResults.length > 0" class="results">
      <div class="results-header">
        <h3>📚 本地資料庫：找到 {{ searchResults.length }} 首相關歌曲</h3>
        <button @click="clearSearch" class="clear-btn">清除結果</button>
      </div>
      <div v-for="(song, index) in searchResults" :key="index" class="song-card">
        <h4>{{ song.歌名 }}</h4>
        <p><strong>歌手：</strong>{{ song.歌手 }}</p>
        <p><strong>{{ song.公司 }}：</strong><span class="song-code">{{ song.編號 }}</span></p>
      </div>
    </div>

    <!-- 沒有本地結果時顯示台灣點歌王搜尋選項 -->
    <div v-if="!loading && songName.trim() && searchResults.length === 0 && hasSearched" class="no-results">
      <h3>😔 本地資料庫沒有找到相關歌曲</h3>
      <p>試試搜尋台灣點歌王線上資料庫？</p>
      
      <div class="taiwan-options">
        <a :href="getTaiwanKtvUrl()" target="_blank" class="taiwan-link-btn">
          🎤 前往台灣點歌王搜尋
          <span class="external-icon">↗</span>
        </a>
        
        <p class="taiwan-hint">
          💡 將在新視窗開啟台灣點歌王官網，自動搜尋「{{ songName.trim() }}」
        </p>
      </div>
    </div>

    <div class="info">
      <p>💡 提示：支援模糊搜尋，輸入部分歌名即可</p>
      <p>🏢 本地資料庫：錢櫃、好樂迪、音圓、金嗓等各大卡拉OK品牌</p>
      <p>🎤 台灣點歌王：當本地找不到歌曲時，可前往官網搜尋最新歌曲</p>
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
    const hasSearched = ref(false);

    // 載入歌曲資料
    const loadSongs = async () => {
      try {
        console.log('開始載入歌曲資料...');
        const response = await fetch('/songs_simplified.json');
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers.get('content-type'));
        
        if (response.ok) {
          const data = await response.json();
          allSongs.value = data;
          console.log('✅ 歌曲資料載入成功！共', allSongs.value.length, '首');
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        console.log('❌ 載入歌曲資料失敗:', error.message);
        console.log('使用示例資料作為備用方案');
        // 如果載入失敗，使用示例資料
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
          { "歌名": "記得", "歌手": "張惠妹", "編號": "88888", "公司": "金嗓" },
          { "歌名": "漂洋過海來看你", "歌手": "蔡琴", "編號": "99999", "公司": "音圓" },
          { "歌名": "被遺忘的時光", "歌手": "蔡琴", "編號": "10101", "公司": "錢櫃" }
        ];
        console.log('示例資料已載入，共', allSongs.value.length, '首');
      }
    };

    // 搜尋歌曲 - 只在手動觸發時執行
    const searchBySongName = () => {
      if (!songName.value.trim()) {
        searchResults.value = [];
        hasSearched.value = false;
        return;
      }

      loading.value = true;
      
      setTimeout(() => {
        const keyword = songName.value.trim().toLowerCase();
        searchResults.value = allSongs.value.filter(song => 
          song.歌名.toLowerCase().includes(keyword) ||
          song.歌手.toLowerCase().includes(keyword)
        );
        loading.value = false;
        hasSearched.value = true;
      }, 300);
    };

    // 清除搜尋結果
    const clearSearch = () => {
      searchResults.value = [];
      hasSearched.value = false;
    };

    // 生成台灣點歌王搜尋URL
    const getTaiwanKtvUrl = () => {
      const keyword = songName.value.trim();
      if (!keyword) return 'https://song.corp.com.tw/';
      
      const params = new URLSearchParams({
        company: '全部',
        cusType: 'searchList',
        keyword: keyword
      });
      
      return `https://song.corp.com.tw/?${params}`;
    };


    onMounted(async () => {
      await loadSongs();
    });

    return { 
      songName, 
      searchResults, 
      loading,
      hasSearched,
      searchBySongName,
      clearSearch,
      getTaiwanKtvUrl
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

.search-btn:disabled {
  background: #cbd5e0;
  color: #a0aec0;
  cursor: not-allowed;
}

.search-hint {
  text-align: center;
  color: #667eea;
  background: #e6fffa;
  padding: 12px;
  border-radius: 8px;
  margin: 20px 0;
  font-size: 14px;
  border: 1px solid #b2f5ea;
}

.loading {
  text-align: center;
  color: #667eea;
  font-size: 18px;
  margin: 20px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.clear-btn {
  padding: 6px 12px;
  background: #e53e3e;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.3s;
}

.clear-btn:hover {
  background: #c53030;
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
  margin: 30px 0;
  padding: 25px;
  background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.no-results h3 {
  color: #d63031;
  margin: 0 0 15px 0;
  font-size: 1.3em;
}

.no-results p {
  color: #636e72;
  margin: 15px 0 20px 0;
  font-size: 16px;
}

.taiwan-search-btn {
  padding: 12px 25px;
  background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 auto;
  box-shadow: 0 4px 15px rgba(253, 121, 168, 0.4);
}

.taiwan-search-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(253, 121, 168, 0.6);
}

.taiwan-search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.taiwan-options {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}

.taiwan-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%);
  color: white;
  text-decoration: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(253, 121, 168, 0.4);
}

.taiwan-link-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(253, 121, 168, 0.6);
  text-decoration: none;
  color: white;
}

.external-icon {
  font-size: 14px;
  opacity: 0.8;
}

.taiwan-hint {
  font-size: 14px;
  color: #7f8c8d;
  text-align: center;
  margin: 0;
  padding: 8px 16px;
  background: rgba(253, 121, 168, 0.1);
  border-radius: 8px;
  border-left: 3px solid #fd79a8;
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
