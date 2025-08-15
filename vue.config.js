const { defineConfig } = require('@vue/cli-service')
const { copyFileSync } = require('fs')
const path = require('path')

module.exports = defineConfig({
  transpileDependencies: true,
  chainWebpack: config => {
    // 在建置過程中複製資料檔案
    config.plugin('copy-data').use(require('copy-webpack-plugin'), [{
      patterns: [
        {
          from: path.resolve(__dirname, 'public/songs_simplified.json'),
          to: path.resolve(__dirname, 'dist/songs_simplified.json')
        },
        {
          from: path.resolve(__dirname, 'public/singers_data.json'), 
          to: path.resolve(__dirname, 'dist/singers_data.json')
        }
      ]
    }])
  },
  configureWebpack: {
    plugins: [
      {
        apply: (compiler) => {
          compiler.hooks.afterEmit.tap('CopyDataFiles', () => {
            try {
              copyFileSync('public/songs_simplified.json', 'dist/songs_simplified.json')
              copyFileSync('public/singers_data.json', 'dist/singers_data.json')
              console.log('✅ 資料檔案已複製到 dist 目錄')
            } catch (err) {
              console.warn('⚠️ 資料檔案複製失敗:', err.message)
            }
          })
        }
      }
    ]
  }
})
