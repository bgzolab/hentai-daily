import DefaultTheme from 'vitepress/theme'
import './assets/custom.css'
import toastification from './toastification'
import googleAnalytics from 'vitepress-plugin-google-analytics'

export default {
    extends: DefaultTheme,
    enhanceApp({app, router, siteData}) {
        // 注册 toastification 插件
        app.use(toastification)
        // 可选：添加全局方法
        app.config.globalProperties.$toast = app.config.globalProperties.$toast || {
            success: (msg) => app.config.globalProperties.$toast.success(msg),
            error: (msg) => app.config.globalProperties.$toast.error(msg),
            info: (msg) => app.config.globalProperties.$toast.info(msg),
            warning: (msg) => app.config.globalProperties.$toast.warning(msg)
        },
        // google analyse
        googleAnalytics({
            id: 'G-E5GDS1JNWM',
        })

    }
}