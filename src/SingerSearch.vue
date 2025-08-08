<template>
  <div class="singer-search">
    <h2>🎤 歌手專區</h2>
    <p>搜尋歌手名稱，查看完整歌曲清單</p>

    <div class="search-container">
      <input 
        v-model="singerName" 
        placeholder="輸入歌手名稱（例：周杰倫、鄧紫棋）" 
        @keyup.enter="searchSinger"
        @input="clearResults"
        class="search-input"
      />
      <button @click="searchSinger" class="search-btn" :disabled="!singerName.trim()">
        🔍 查詢歌手
      </button>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      搜尋中，請稍候...
    </div>

    <!-- 搜尋結果 -->
    <div v-if="!loading && singerResults.length > 0" class="results">
      <div class="results-header">
        <h3>🎵 {{ searchedSinger }}：找到 {{ singerResults.length }} 首歌曲</h3>
        <div class="header-info">
          <span class="update-time">{{ updateTime }}</span>
          <button @click="clearResults" class="clear-btn">清除結果</button>
        </div>
      </div>

      <!-- 歌曲列表 -->
      <div v-for="(song, index) in singerResults" :key="index" class="song-card singer-card">
        <div class="song-header">
          <h4>{{ song.歌名 }}</h4>
          <span v-if="song.語言" class="song-lang">{{ song.語言 }}</span>
        </div>
        
        <div class="song-codes">
          <div 
            v-for="(codeInfo, codeIndex) in song.編號資訊" 
            :key="codeIndex" 
            :class="['code-item', getCompanyClass(codeInfo.公司)]"
          >
            <span class="company-name">{{ codeInfo.公司 }}</span>
            <span class="song-code">{{ codeInfo.編號 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 沒有結果 -->
    <div v-if="!loading && singerName.trim() && singerResults.length === 0 && hasSearched" class="no-results">
      <h3>😔 找不到歌手「{{ singerName }}」的資料</h3>
      <p>可能原因：</p>
      <ul>
        <li>歌手名稱拼寫錯誤</li>
        <li>該歌手尚未收錄到資料庫</li>
        <li>可以嘗試搜尋歌手的代表作品</li>
      </ul>
    </div>

    <!-- 熱門歌手推薦 -->
    <div v-if="!loading && singerResults.length === 0" class="hot-singers">
      <h4>🔥 熱門歌手推薦</h4>
      <div class="singer-tags">
        <button 
          v-for="singer in hotSingers" 
          :key="singer"
          @click="searchHotSinger(singer)"
          class="singer-tag"
        >
          {{ singer }}
        </button>
      </div>
    </div>

    <div class="info">
      <p>💡 提示：歌手資料定期更新，每位歌手包含完整的歌曲清單</p>
      <p>📊 編號排序：錢櫃 → 好樂迪 → 銀櫃 → 其他品牌</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";

export default {
  name: "SingerSearch",
  setup() {
    const singerName = ref("");
    const singerResults = ref([]);
    const loading = ref(false);
    const hasSearched = ref(false);
    const searchedSinger = ref("");
    const updateTime = ref("");
    const allSingersData = ref({});

    const hotSingers = [
      "周杰倫", "蔡依林", "林俊傑", "張惠妹", "五月天", "鄧紫棋", 
      "林宥嘉", "田馥甄", "楊丞琳", "孫燕姿", "告五人", "茄子蛋"
    ];

    // 載入歌手資料
    const loadSingersData = async () => {
      try {
        console.log('載入歌手資料...');
        const response = await fetch('/singers_data.json');
        
        if (response.ok) {
          const data = await response.json();
          allSingersData.value = data;
          console.log('✅ 歌手資料載入成功！', Object.keys(data).length, '位歌手');
        } else {
          console.log('❌ 載入歌手資料失敗');
          allSingersData.value = {};
        }
      } catch (error) {
        console.log('❌ 載入歌手資料失敗:', error.message);
        allSingersData.value = {};
      }
    };

    // 搜尋歌手
    const searchSinger = () => {
      if (!singerName.value.trim()) {
        singerResults.value = [];
        hasSearched.value = false;
        return;
      }

      loading.value = true;
      
      setTimeout(() => {
        const keyword = singerName.value.trim();
        searchedSinger.value = keyword;
        
        // 在歌手資料庫中搜尋
        const singerData = allSingersData.value[keyword];
        
        if (singerData && singerData.歌曲清單) {
          singerResults.value = singerData.歌曲清單;
          updateTime.value = singerData.更新時間 ? `更新於 ${singerData.更新時間}` : '';
        } else {
          // 模糊搜尋
          singerResults.value = [];
          updateTime.value = '';
          
          // 檢查是否有部分匹配的歌手
          for (const [singerKey, data] of Object.entries(allSingersData.value)) {
            if (singerKey.includes(keyword) || keyword.includes(singerKey)) {
              singerResults.value = data.歌曲清單 || [];
              searchedSinger.value = singerKey;
              updateTime.value = data.更新時間 ? `更新於 ${data.更新時間}` : '';
              break;
            }
          }
        }
        
        loading.value = false;
        hasSearched.value = true;
      }, 500);
    };

    // 搜尋熱門歌手
    const searchHotSinger = (singer) => {
      singerName.value = singer;
      searchSinger();
    };

    // 清除結果
    const clearResults = () => {
      singerResults.value = [];
      hasSearched.value = false;
      searchedSinger.value = "";
      updateTime.value = "";
    };

    // 取得公司樣式類別
    const getCompanyClass = (company) => {
      const priorityCompanies = ['錢櫃', '好樂迪', '銀櫃'];
      if (priorityCompanies.includes(company)) {
        return 'priority-company';
      }
      return 'regular-company';
    };

    onMounted(async () => {
      await loadSingersData();
    });

    return { 
      singerName,
      singerResults,
      loading,
      hasSearched,
      searchedSinger,
      updateTime,
      hotSingers,
      searchSinger,
      searchHotSinger,
      clearResults,
      getCompanyClass
    };
  }
};
</script>

<style scoped>
.singer-search {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.singer-search h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 2.2em;
}

.singer-search p {
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.search-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
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
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
}

.results-header h3 {
  margin: 0;
  color: white;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.update-time {
  font-size: 12px;
  opacity: 0.8;
}

.clear-btn {
  padding: 6px 12px;
  background: rgba(255,255,255,0.2);
  color: white;
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.3s;
}

.clear-btn:hover {
  background: rgba(255,255,255,0.3);
}

.singer-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  border-left: 4px solid #667eea;
  transition: all 0.3s;
}

.singer-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}

.song-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.song-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3em;
}

.song-lang {
  background: #e3f2fd;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  color: #1976d2;
}

.song-codes {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.code-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
}

.priority-company {
  background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%);
  color: white;
  font-weight: 600;
}

.regular-company {
  background: #e9ecef;
  color: #495057;
}

.code-item:hover {
  transform: scale(1.05);
}

.company-name {
  font-size: 12px;
  opacity: 0.9;
}

.song-code {
  font-family: 'Courier New', monospace;
  font-weight: bold;
  padding: 2px 6px;
  background: rgba(255,255,255,0.3);
  border-radius: 4px;
}

.no-results {
  text-align: center;
  margin: 30px 0;
  padding: 30px;
  background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
  border-radius: 12px;
}

.no-results h3 {
  color: #d63031;
  margin: 0 0 15px 0;
}

.no-results ul {
  text-align: left;
  max-width: 300px;
  margin: 0 auto;
  color: #636e72;
}

.hot-singers {
  margin: 30px 0;
  padding: 20px;
  background: #f1f3f4;
  border-radius: 12px;
}

.hot-singers h4 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 15px;
}

.singer-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.singer-tag {
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.singer-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
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
  
  .results-header {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .song-codes {
    flex-direction: column;
  }
  
  .singer-tags {
    gap: 6px;
  }
  
  .singer-tag {
    font-size: 12px;
    padding: 6px 12px;
  }
}
</style>