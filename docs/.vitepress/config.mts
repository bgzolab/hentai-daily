import {defineConfig} from 'vitepress'
import taskLists from 'markdown-it-task-lists'
// https://github.com/vuejs/vitepress/discussions/704
import footnote from 'markdown-it-footnote'

// https://vitepress.dev/reference/site-config
export default defineConfig({
    title: "Hentai Daily",
    description: "Hentai contents combined with multi sources",
    themeConfig: {
        // https://vitepress.dev/reference/default-theme-config
        nav: [
            {text: 'Home', link: '/'},
            {text: 'Today', link: '/today'},
            {text: 'Changelog', link: '/changelog'},
        ],
        socialLinks: [
            {icon: 'github', link: 'https://github.com/bGZo/hentai-daily'},
            {icon: 'mastodon', link: 'https://mastodon.social/@bgzo'},
            {icon: 'bluesky', link: 'https://bsky.app/profile/bgzo.bsky.social'},
        ],
        footer: {
            message: 'Found this useful? Give me a ⭐ on <a href="https://github.com/bGZo/hentai-daily">Github</a>.',
            copyright: 'Copyright © 2023-present 菜就多練練',
        },
    },

    head: [
        ['link', {rel: 'icon', href: '/favicon.ico'}],
        ['link', {rel: 'apple-touch-icon', size: "57x57", href: '/favicon-57x57.png'}],
        ['link', {rel: 'apple-touch-icon', size: '60x60', href: '/favicon-60x60.png'}],
        ['link', {rel: 'apple-touch-icon', size: '72x72', href: '/favicon-72x72.png'}],
        ['link', {rel: 'apple-touch-icon', size: '76x76', href: '/favicon-76x76.png'}],
        ['link', {rel: 'apple-touch-icon', size: '114x114', href: '/favicon-114x114.png'}],
        ['link', {rel: 'apple-touch-icon', size: '120x120', href: '/favicon-120x120.png'}],
        ['link', {rel: 'apple-touch-icon', size: '144x144', href: '/favicon-144x144.png'}],
        ['link', {rel: 'apple-touch-icon', size: '152x152', href: '/favicon-152x152.png'}],
        ['link', {rel: 'apple-touch-icon', size: '180x180', href: '/favicon-180x180.png'}],
        ['link', {rel: 'icon', type: 'image/png', size: '16x16', href: '/favicon-16x16.png'}],
        ['link', {rel: 'icon', type: 'image/png', size: '32x32', href: '/favicon-32x32.png'}],
        ['link', {rel: 'icon', type: 'image/png', size: '96x96', href: '/favicon-96x96.png'}],
        ['link', {rel: 'icon', type: 'image/png', size: '192x192', href: '/favicon-192x192.png'}],
        ['link', {rel: 'shortcut icon', type: 'image/x-icon', href: '/favicon.ico'}],
        ['link', {rel: 'icon', type: 'image/x-icon', href: '/favicon.ico'}],
        ['link', {rel: 'manifest', href: '/manifest.json'}],
        ['meta', {name: 'msapplication-TileColor', content: '#ffffff'}],
        ['meta', {name: 'msapplication-TileImage', content: '/favicon-144x144.png'}],
        ['meta', {name: 'msapplication-config', content: '/browserconfig.xml'}],
        ['meta', {name: 'theme-color', content: '#ffffff'}],
    ],

    cleanUrls: true,

    // via: https://github.com/vuejs/vitepress/issues/1923#issuecomment-1431479500
    markdown: {
        config: (md) => {
            md.use(footnote)
            md.use(taskLists, {
                disabled: false,
                divWrap: false,
                divClass: 'checkbox',
                idPrefix: 'cbx_',
                ulClass: 'task-list',
                liClass: 'task-list-item'
            })
        }
    },



    vite: {
        server: {
            proxy: {
                // 测试
                '/get': {
                    target: 'http://httpbin.org',
                    changeOrigin: true,
                    secure: false,
                    // rewrite: (path) => path.replace(/^\/test/, '/'),
                    configure: (proxy, options) => {
                        proxy.on('proxyReq', (proxyReq, req, res) => {
                            console.log('🚀 测试代理请求:')
                            console.log('  - 原始URL:', req.url)
                            console.log('  - 目标:', options.target)
                            console.log('  - 最终URL:', `${options.target}${req.url.replace('/test', '')}`)
                        })

                        proxy.on('proxyRes', (proxyRes, req, res) => {
                            console.log('📥 测试代理响应:', proxyRes.statusCode)
                        })
                        proxy.on('error', (err, req, res) => {
                            console.log('❌ 测试代理错误:', err.message)
                        })
                    }
                },

                '/api': {
                    // target: 'http://hentai.bgzo.cc', // 500 ERROR
                    target: 'https://raw.githubusercontent.com/bGZo/hentai-daily/refs/heads/vitepress/',
                    changeOrigin: true,
                    secure: true, // 如果是 https,
                    // timeout: 30000, // 增加超时时间到30秒
                    // proxyTimeout: 30000,
                    // rewrite: (path) => path.replace(/^\/api/, '/api'),
                    // configure: (proxy, options) => {
                    //   // 可以在这里添加额外的配置
                    //   proxy.on('proxyReq', (proxyReq, req, res) => {
                    //     // 修改请求头，让它更像 API 请求而不是页面请求
                    //     proxyReq.setHeader('Accept', 'application/json, text/plain, */*')
                    //     proxyReq.setHeader('Sec-Fetch-Dest', 'empty')
                    //     proxyReq.setHeader('Sec-Fetch-Mode', 'cors')
                    //     proxyReq.setHeader('Sec-Fetch-Site', 'cross-site')
                    //     proxyReq.setHeader('accept-encoding', 'deflate')
                    //     proxyReq.setHeader('referer', 'https://hentai.bgzo.cc')
                    //
                    //     // 移除一些可能有问题的头
                    //     proxyReq.removeHeader('upgrade-insecure-requests')
                    //     proxyReq.removeHeader('sec-fetch-user')
                    //     console.log('=== 代理请求信息 ===')
                    //     console.log('原始请求URL:', req.url)
                    //     console.log('代理目标:', options.target)
                    //     console.log('最终请求URL:', `${options.target}${req.url}`)
                    //     console.log('请求方法:', proxyReq.method)
                    //     console.log('请求头:', proxyReq.getHeaders())
                    //     console.log('========================')
                    //     // console.log('响应状态:', proxyRes.statusCode)
                    //     proxyReq.setTimeout(30000)
                    //   })
                    //
                    //   proxy.on('proxyRes', (proxyRes, req, res) => {
                    //     console.log('响应状态:', proxyRes.statusCode)
                    //     if (proxyRes.statusCode === 308) {
                    //       console.log('重定向到:', proxyRes.headers.location)
                    //     }
                    //   })
                    //
                    //
                    //   // proxy.on('error', (err, req, res) => {
                    //   //   console.error('=== 代理错误 ===')
                    //   //   console.error('错误:', err)
                    //   //   console.error('请求URL:', req.url)
                    //   //   console.error('================')
                    //   // })
                    // }
                }
            }
        }
    },

})
