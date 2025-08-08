// Import Firebase functions
import { initializeApp } from "firebase/app";
import { getFirestore, collection, query, where, getDocs } from "firebase/firestore";

// Firebase 設定
const firebaseConfig = {
  apiKey: process.env.VITE_FIREBASE_API_KEY || "AIzaSyDFznjhmqmOL8Y7tlV2MQn7voK7-ugmrvE",
  authDomain: process.env.VITE_FIREBASE_AUTH_DOMAIN || "karaoke-search-87e08.firebaseapp.com",
  projectId: process.env.VITE_FIREBASE_PROJECT_ID || "karaoke-search-87e08",
  storageBucket: process.env.VITE_FIREBASE_STORAGE_BUCKET || "karaoke-search-87e08.appspot.com",
  messagingSenderId: process.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "174274481830",
  appId: process.env.VITE_FIREBASE_APP_ID || "1:174274481830:web:02498e216f31f15933ae67",
  measurementId: process.env.VITE_FIREBASE_MEASUREMENT_ID || "G-H1HCNJ609E"
};

// 初始化 Firebase
const app = initializeApp(firebaseConfig);

// 初始化 Firestore（這是我們要用來存放與查詢歌曲資料的資料庫）
const db = getFirestore(app);

// 匯出 Firestore 相關功能，讓其他 Vue 檔案可以使用
export { db, collection, query, where, getDocs };
