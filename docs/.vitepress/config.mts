import { defineConfig } from 'vitepress'
import taskLists from 'markdown-it-task-lists'

//
// https://vitepress.dev/reference/site-config
export default defineConfig({
  vite: {
    server: {
      // 启用 HTTPS
      // https: true,
      // {}, // 使用空对象而不是 true
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
          // target: 'http://hentai.bgzo.cc', // 7
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

  title: "Hentai Daily",
  description: "Hentai contents combined with multi sources Debug",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      {text: 'Home', link: '/'},
      {text: 'Today', link: '/today'},
      {text: 'Changelog', link: '/changelog'},
    ],

    // sidebar: [
    //   {
    //     text: 'Examples',
    //     items: [
    //       { text: 'Markdown Examples', link: '/markdown-examples' },
    //       { text: 'Runtime API Examples', link: '/api-examples' }
    //     ]
    //   }
    // ],

    socialLinks: [
      {icon: 'github', link: 'https://github.com/bGZo/hentai-daily'}
    ],
  },

  // via: https://github.com/vuejs/vitepress/issues/1923#issuecomment-1431479500
  markdown: {
    config: (md) => {
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

})
