// docs/.vitepress/theme/index.js
import DefaultTheme from 'vitepress/theme'
import './assets/custom.css'  // 可选：自定义样式

export default {
  extends: DefaultTheme,
  enhanceApp({ app, router, siteData }) {
    // 在这里可以注册全局组件或添加其他配置
  }
}