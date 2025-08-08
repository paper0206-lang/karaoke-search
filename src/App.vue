<template>
  <div>
    <div class="tab-content">
      <h1>🎵 卡拉OK 點歌本查詢</h1>
      <p>輸入歌曲名稱或歌手名稱，智能搜尋各家KTV點歌編號</p>

      <div class="search-container">
        <input 
          v-model="searchQuery" 
          placeholder="輸入歌曲名稱或歌手名稱（例：愛情、周杰倫、告五人）" 
          @keyup.enter="intelligentSearch"
          @input="clearSearch"
          class="search-input"
        />
        <button @click="intelligentSearch" class="search-btn" :disabled="!searchQuery.trim()">
          🔍 智能搜尋
        </button>
      </div>

      <!-- 搜尋提示 -->
      <div v-if="searchQuery.trim() && searchResults.length === 0 && !loading" class="search-hint">
        請按「智能搜尋」按鈕或按 Enter 鍵開始搜尋
      </div>

      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        搜尋中，請稍候...
      </div>
      
      <!-- 智能搜尋結果 -->
      <div v-if="!loading && searchResults.length > 0" class="results">
        <div class="results-header">
          <h3>
            {{ searchMode === 'singer' ? '🎤' : '🎵' }} 
            {{ searchMode === 'singer' ? '歌手作品' : '搜尋結果' }}：
            找到 {{ totalSongs }} 首歌曲
            <span v-if="searchMode === 'singer'" class="singer-name">({{ searchQuery }})</span>
          </h3>
          <div class="header-info">
            <span v-if="searchMode === 'singer'" class="search-mode">歌手完整作品集</span>
            <span v-else class="search-mode">智能搜尋結果</span>
            <button @click="clearSearch" class="clear-btn">清除結果</button>
          </div>
        </div>

        <!-- 歌曲卡片 - 自動歸納同一首歌 -->
        <div v-for="(songGroup, index) in groupedResults" :key="index" class="song-card">
          <div class="song-header">
            <h4>{{ songGroup.歌名 }}</h4>
            <span class="song-meta">
              <strong>{{ songGroup.歌手 }}</strong>
              <span v-if="songGroup.語言" class="song-lang">{{ songGroup.語言 }}</span>
            </span>
          </div>
          
          <!-- 各家KTV編號 -->
          <div class="song-codes">
            <div 
              v-for="(codeInfo, codeIndex) in songGroup.編號資訊" 
              :key="codeIndex" 
              :class="['code-item', getCompanyClass(codeInfo.公司)]"
            >
              <span class="company-name">{{ codeInfo.公司 }}</span>
              <span class="song-code">{{ codeInfo.編號 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 沒有結果時的提示 -->
      <div v-if="!loading && searchQuery.trim() && searchResults.length === 0 && hasSearched" class="no-results">
        <h3>😔 沒有找到相關歌曲</h3>
        <div class="suggestions">
          <p>💡 建議：</p>
          <ul>
            <li>嘗試搜尋歌手名稱 (如：周杰倫、蔡依林、告五人)</li>
            <li>使用部分歌詞或歌名關鍵字</li>
            <li>檢查是否有拼字錯誤</li>
            <li>嘗試簡化搜尋詞彙</li>
          </ul>
          
          <div class="quick-suggestions">
            <p>🔥 熱門搜尋:</p>
            <div class="suggestion-tags">
              <button 
                v-for="suggestion in quickSuggestions" 
                :key="suggestion"
                @click="quickSearch(suggestion)"
                class="suggestion-tag"
              >
                {{ suggestion }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="info">
        <p>💡 提示：支援歌曲名稱和歌手名稱搜尋，自動歸納同一首歌的各家編號</p>
        <p>🏢 涵蓋KTV品牌：錢櫃、好樂迪、音圓、金嗓、銀櫃、弘音等21家</p>
        <p>📊 目前收錄：{{ allSongs.length.toLocaleString() }} 首歌曲，{{ totalSingers.toLocaleString() }} 位歌手，持續更新中</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";

export default {
  setup() {
    const searchQuery = ref("");
    const searchResults = ref([]);
    const groupedResults = ref([]);
    const loading = ref(false);
    const allSongs = ref([]);
    const singersData = ref({});
    const hasSearched = ref(false);
    const searchMode = ref(""); // 'singer' or 'song'
    const totalSongs = ref(0);
    const totalSingers = ref(0);
    
    const quickSuggestions = ref([
      "周杰倫", "蔡依林", "五月天", "告五人", "茄子蛋", "持修", "愛情", "想念", "青春", "晴天"
    ]);

    // 載入歌曲資料
    const loadSongs = async () => {
      try {
        console.log('載入歌曲資料...');
        const response = await fetch('/songs_simplified.json');
        
        if (response.ok) {
          const data = await response.json();
          allSongs.value = data;
          console.log('✅ 歌曲資料載入成功！共', allSongs.value.length, '首');
        }
      } catch (error) {
        console.log('❌ 載入歌曲資料失敗:', error.message);
      }
    };

    // 載入歌手資料
    const loadSingers = async () => {
      try {
        console.log('載入歌手資料...');
        const response = await fetch('/singers_data.json');
        
        if (response.ok) {
          const data = await response.json();
          singersData.value = data;
          totalSingers.value = Object.keys(data).length;
          console.log('✅ 歌手資料載入成功！共', totalSingers.value, '位');
        }
      } catch (error) {
        console.log('❌ 載入歌手資料失敗:', error.message);
      }
    };

    // 智能搜尋
    const intelligentSearch = async () => {
      if (!searchQuery.value.trim()) return;
      
      loading.value = true;
      hasSearched.value = true;
      
      try {
        // 先檢查是否為歌手搜尋
        const singerMatch = findSingerMatch(searchQuery.value.trim());
        
        if (singerMatch) {
          // 歌手搜尋模式
          searchMode.value = 'singer';
          searchResults.value = singerMatch.歌曲清單;
          totalSongs.value = searchResults.value.length;
          console.log(`🎤 歌手搜尋: ${singerMatch.歌手名稱}, ${totalSongs.value} 首歌曲`);
        } else {
          // 歌曲搜尋模式
          searchMode.value = 'song';
          searchResults.value = searchSongs(searchQuery.value.trim());
          totalSongs.value = searchResults.value.length;
          console.log(`🎵 歌曲搜尋: ${searchQuery.value}, ${totalSongs.value} 首歌曲`);
        }
        
        // 歸納相同歌曲
        groupResults();
        
      } catch (error) {
        console.error('搜尋失敗:', error);
      } finally {
        loading.value = false;
      }
    };

    // 尋找歌手匹配
    const findSingerMatch = (query) => {
      for (const [singerName, singerData] of Object.entries(singersData.value)) {
        if (singerName.includes(query) || query.includes(singerName)) {
          return singerData;
        }
      }
      return null;
    };

    // 搜尋歌曲
    const searchSongs = (query) => {
      return allSongs.value.filter(song => 
        song.歌名?.includes(query) || 
        song.歌手?.includes(query)
      );
    };

    // 歸納相同歌曲的不同編號
    const groupResults = () => {
      const groups = {};
      
      searchResults.value.forEach(song => {
        const key = `${song.歌名}_${song.歌手}`;
        
        if (!groups[key]) {
          groups[key] = {
            歌名: song.歌名,
            歌手: song.歌手,
            語言: song.語言 || '',
            編號資訊: []
          };
        }
        
        // 添加編號資訊 (避免重複)
        const codeInfo = {
          公司: song.公司 || song.編號資訊?.[0]?.公司 || '',
          編號: song.編號 || song.編號資訊?.[0]?.編號 || ''
        };
        
        if (song.編號資訊 && Array.isArray(song.編號資訊)) {
          // 如果是歌手搜尋結果 (有編號資訊陣列)
          song.編號資訊.forEach(code => {
            if (!groups[key].編號資訊.some(existing => 
              existing.公司 === code.公司 && existing.編號 === code.編號)) {
              groups[key].編號資訊.push(code);
            }
          });
        } else {
          // 如果是歌曲搜尋結果 (單一編號)
          if (codeInfo.公司 && codeInfo.編號 && 
              !groups[key].編號資訊.some(existing => 
                existing.公司 === codeInfo.公司 && existing.編號 === codeInfo.編號)) {
            groups[key].編號資訊.push(codeInfo);
          }
        }
      });
      
      // 排序編號資訊 (優先公司排前面)
      const companyPriority = ['錢櫃', '好樂迪', '銀櫃', '音圓', '金嗓', '弘音', '星據點'];
      
      Object.values(groups).forEach(group => {
        group.編號資訊.sort((a, b) => {
          const aIndex = companyPriority.indexOf(a.公司);
          const bIndex = companyPriority.indexOf(b.公司);
          
          if (aIndex !== -1 && bIndex !== -1) {
            return aIndex - bIndex;
          } else if (aIndex !== -1) {
            return -1;
          } else if (bIndex !== -1) {
            return 1;
          } else {
            return a.公司.localeCompare(b.公司);
          }
        });
      });
      
      groupedResults.value = Object.values(groups);
    };

    // 取得公司樣式
    const getCompanyClass = (company) => {
      const classMap = {
        '錢櫃': 'primary',
        '好樂迪': 'secondary', 
        '銀櫃': 'success',
        '音圓': 'warning',
        '金嗓': 'info',
        '弘音': 'light',
        '星據點': 'dark'
      };
      return classMap[company] || 'default';
    };

    // 清除搜尋
    const clearSearch = () => {
      searchResults.value = [];
      groupedResults.value = [];
      hasSearched.value = false;
      searchMode.value = '';
      totalSongs.value = 0;
    };

    // 快速搜尋
    const quickSearch = (suggestion) => {
      searchQuery.value = suggestion;
      intelligentSearch();
    };

    onMounted(async () => {
      await Promise.all([loadSongs(), loadSingers()]);
    });

    return {
      searchQuery,
      searchResults,
      groupedResults,
      loading,
      allSongs,
      hasSearched,
      searchMode,
      totalSongs,
      totalSingers,
      quickSuggestions,
      intelligentSearch,
      clearSearch,
      quickSearch,
      getCompanyClass
    };
  }
};
</script>

<style scoped>
.tab-content {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 10px;
}

p {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

.search-container {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.search-input {
  flex: 1;
  padding: 12px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  outline: none;
}

.search-input:focus {
  border-color: #3498db;
}

.search-btn {
  padding: 12px 24px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  white-space: nowrap;
}

.search-btn:hover:not(:disabled) {
  background: #2980b9;
}

.search-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.search-hint {
  text-align: center;
  color: #7f8c8d;
  font-size: 14px;
  margin: 10px 0;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #3498db;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.results {
  margin-top: 30px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.results-header h3 {
  margin: 0;
  color: #2c3e50;
}

.singer-name {
  color: #e74c3c;
  font-weight: normal;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.search-mode {
  font-size: 14px;
  color: #7f8c8d;
  background: white;
  padding: 4px 8px;
  border-radius: 4px;
}

.clear-btn {
  padding: 6px 12px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.clear-btn:hover {
  background: #c0392b;
}

.song-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.song-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.song-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
}

.song-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.song-lang {
  background: #3498db;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
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
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 14px;
}

.code-item.primary { background: #e3f2fd; border-left: 4px solid #2196f3; }
.code-item.secondary { background: #f3e5f5; border-left: 4px solid #9c27b0; }
.code-item.success { background: #e8f5e8; border-left: 4px solid #4caf50; }
.code-item.warning { background: #fff8e1; border-left: 4px solid #ff9800; }
.code-item.info { background: #e0f2f1; border-left: 4px solid #00bcd4; }
.code-item.light { background: #fafafa; border-left: 4px solid #9e9e9e; }
.code-item.dark { background: #f5f5f5; border-left: 4px solid #424242; }
.code-item.default { background: #f8f9fa; border-left: 4px solid #6c757d; }

.company-name {
  font-weight: bold;
  min-width: 50px;
}

.song-code {
  font-family: monospace;
  font-weight: bold;
  color: #2c3e50;
}

.no-results {
  text-align: center;
  padding: 40px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 30px;
}

.no-results h3 {
  color: #e74c3c;
  margin-bottom: 20px;
}

.suggestions {
  text-align: left;
  max-width: 500px;
  margin: 0 auto;
}

.suggestions ul {
  color: #666;
  line-height: 1.6;
}

.quick-suggestions {
  margin-top: 20px;
  text-align: center;
}

.suggestion-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 10px;
}

.suggestion-tag {
  padding: 6px 12px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.suggestion-tag:hover {
  background: #2980b9;
}

.info {
  margin-top: 40px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  text-align: center;
}

.info p {
  margin: 8px 0;
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .search-container {
    flex-direction: column;
  }
  
  .results-header {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .song-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .song-codes {
    justify-content: center;
  }
}
</style>