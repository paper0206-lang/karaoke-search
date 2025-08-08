# 🚀 卡拉OK搜尋系統部署指南

## 📋 部署前準備

### 1. 建立 GitHub 倉庫
```bash
# 在 GitHub.com 建立新的倉庫 "karaoke-search"
# 然後執行以下命令：
git remote add origin https://github.com/你的使用者名稱/karaoke-search.git
git branch -M main
git push -u origin main
```

## 🌐 前端部署 (Vercel)

### 步驟 1: 連結 GitHub
1. 前往 [Vercel.com](https://vercel.com) 註冊/登入
2. 點擊 "New Project"
3. 選擇你的 `karaoke-search` 倉庫
4. Vercel 會自動偵測為 Vue.js 專案

### 步驟 2: 環境變數設定
在 Vercel Dashboard → Settings → Environment Variables 加入：
```
VITE_FIREBASE_API_KEY=你的API_KEY
VITE_FIREBASE_AUTH_DOMAIN=你的項目.firebaseapp.com  
VITE_FIREBASE_PROJECT_ID=你的項目ID
VITE_FIREBASE_STORAGE_BUCKET=你的項目.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=你的SENDER_ID
VITE_FIREBASE_APP_ID=你的APP_ID
VITE_FIREBASE_MEASUREMENT_ID=你的MEASUREMENT_ID
```

### 步驟 3: 部署
點擊 "Deploy" - 幾分鐘後會得到類似網址：
**前端網址: `https://karaoke-search-xxx.vercel.app`**

## 🖥️ 後端部署 (Railway)

### 步驟 1: 連結 GitHub
1. 前往 [Railway.app](https://railway.app) 註冊/登入
2. 點擊 "New Project" → "Deploy from GitHub repo"
3. 選擇你的 `karaoke-search` 倉庫

### 步驟 2: 配置
- Railway 會自動偵測 Python 專案
- 確認 Root Directory 是專案根目錄
- 確認 Start Command 是 `python app.py`

### 步驟 3: 部署
部署完成後會得到類似網址：
**後端 API: `https://karaoke-search-production.railway.app`**

## 🔥 Firebase 資料匯入

### 步驟 1: 下載 Service Account Key
1. 前往 [Firebase Console](https://console.firebase.google.com)
2. 專案設定 → 服務帳戶 → 產生新的私密金鑰
3. 下載檔案並重命名為 `serviceAccountKey.json`

### 步驟 2: 安裝依賴並執行上傳
```bash
npm install firebase-admin
node upload_to_firebase.js
```

### 步驟 3: 設定 Firestore 規則
在 Firebase Console → Firestore Database → Rules：
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /songs/{document} {
      allow read: if true;
      allow write: if false;
    }
  }
}
```

## 🔧 最終設定

### 更新前端 API 端點
在 `src/App.vue` 中（如果有使用後端 API），將 API 網址改為：
```javascript
const API_BASE_URL = 'https://your-railway-app.railway.app';
```

## 📱 測試連結

部署完成後的測試步驟：
1. 開啟前端網址
2. 輸入歌名進行搜尋
3. 確認能正確顯示各機台編號

## 🎯 預期結果

- **前端**: `https://karaoke-search-xxx.vercel.app`
- **後端**: `https://karaoke-search-xxx.railway.app`
- **資料庫**: Firebase Firestore 雲端資料庫

---

## ⚡ 快速部署命令

```bash
# 1. 推送到 GitHub
git add .
git commit -m "準備部署"
git remote add origin https://github.com/USERNAME/karaoke-search.git
git push -u origin main

# 2. 前往 Vercel.com 和 Railway.app 完成部署

# 3. 匯入資料到 Firebase
npm install firebase-admin
node upload_to_firebase.js
```