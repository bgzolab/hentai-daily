import { defineConfig } from "vitepress";
import taskLists from "markdown-it-task-lists";
// https://github.com/vuejs/vitepress/discussions/704
import footnote from "markdown-it-footnote";

// https://vitepress.dev/reference/site-config
export default defineConfig({
  description: "Hentai contents combined with multi sources",
  themeConfig: {
    socialLinks: [
      { icon: "github", link: "https://github.com/bGZo/hentai-daily" },
      { icon: "telegram", link: "https://t.me/imbGZo" },
    ],
    footer: {
      message:
        'Found this useful? Give me a <a href="https://github.com/bGZo/hentai-daily">Ciallo ～(∠・ω< )⌒</a> ⭐',
      copyright: "Copyright © 2023-present 華仔",
    },
    search: {
      // provider: 'local'
    },
  },
  locales: {
    root: {
      title: "Hentai Daily",
      label: "English",
      lang: "en",
      link: "/",
      themeConfig: {
        // https://vitepress.dev/reference/default-theme-config
        nav: [
          { text: "Home", link: "/" },
          { text: "Today", link: "/today" },
          { text: "API", link: "/rss" },
          {
            text: "About",
            items: [
              { text: "Changelog", link: "/changelog" },
              { text: "Q&A", link: "/faq" },
            ],
          },
        ],
      },
    },
    "zh-cn": {
      title: "绅士日报",
      label: "简体中文",
      lang: "zh-CN",
      link: "/zh-cn/",
      themeConfig: {
        nav: [
          { text: "首页", link: "/zh-cn/" },
          { text: "日报", link: "/zh-cn/today" },
          { text: "API", link: "/zh-cn/rss" },
          {
            text: "关于",
            items: [
              { text: "更新日志", link: "/zh-cn/changelog" },
              { text: "问答", link: "/zh-cn/faq" },
            ],
          },
        ],
        footer: {
          message:
            '有帮到你吗? 鼓励一下我吧 <a href="https://github.com/bGZo/hentai-daily">Ciallo ～(∠・ω< )⌒</a> ⭐ ',
          copyright: "Copyright © 2023-present 華仔",
        },
      },
    },
  },

  head: [
    ["link", { rel: "icon", href: "/favicon.ico" }],
    [
      "link",
      { rel: "apple-touch-icon", size: "57x57", href: "/favicon-57x57.png" },
    ],
    [
      "link",
      { rel: "apple-touch-icon", size: "60x60", href: "/favicon-60x60.png" },
    ],
    [
      "link",
      { rel: "apple-touch-icon", size: "72x72", href: "/favicon-72x72.png" },
    ],
    [
      "link",
      { rel: "apple-touch-icon", size: "76x76", href: "/favicon-76x76.png" },
    ],
    [
      "link",
      {
        rel: "apple-touch-icon",
        size: "114x114",
        href: "/favicon-114x114.png",
      },
    ],
    [
      "link",
      {
        rel: "apple-touch-icon",
        size: "120x120",
        href: "/favicon-120x120.png",
      },
    ],
    [
      "link",
      {
        rel: "apple-touch-icon",
        size: "144x144",
        href: "/favicon-144x144.png",
      },
    ],
    [
      "link",
      {
        rel: "apple-touch-icon",
        size: "152x152",
        href: "/favicon-152x152.png",
      },
    ],
    [
      "link",
      {
        rel: "apple-touch-icon",
        size: "180x180",
        href: "/favicon-180x180.png",
      },
    ],
    [
      "link",
      {
        rel: "icon",
        type: "image/png",
        size: "16x16",
        href: "/favicon-16x16.png",
      },
    ],
    [
      "link",
      {
        rel: "icon",
        type: "image/png",
        size: "32x32",
        href: "/favicon-32x32.png",
      },
    ],
    [
      "link",
      {
        rel: "icon",
        type: "image/png",
        size: "96x96",
        href: "/favicon-96x96.png",
      },
    ],
    [
      "link",
      {
        rel: "icon",
        type: "image/png",
        size: "192x192",
        href: "/favicon-192x192.png",
      },
    ],
    [
      "link",
      { rel: "shortcut icon", type: "image/x-icon", href: "/favicon.ico" },
    ],
    ["link", { rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
    ["link", { rel: "manifest", href: "/manifest.json" }],
    ["meta", { name: "msapplication-TileColor", content: "#ffffff" }],
    [
      "meta",
      { name: "msapplication-TileImage", content: "/favicon-144x144.png" },
    ],
    ["meta", { name: "msapplication-config", content: "/browserconfig.xml" }],
    ["meta", { name: "theme-color", content: "#ffffff" }],
  ],

  cleanUrls: true,

  srcExclude: ["memories/**/*.md", "implementation-plans/**/*.md"],

  // via: https://github.com/vuejs/vitepress/issues/1923#issuecomment-1431479500
  markdown: {
    config: (md) => {
      md.use(footnote);
      md.use(taskLists, {
        disabled: false,
        divWrap: false,
        divClass: "checkbox",
        idPrefix: "cbx_",
        ulClass: "task-list",
        liClass: "task-list-item",
      });
    },
  },

  sitemap: {
    hostname: "https://hentai.bgzo.cc",
    lastmodDateOnly: false,
  },

  lastUpdated: true,

  vite: {
    ssr: {
      noExternal: ["vue-toastification"],
    },
    server: {
      proxy: {
        // 测试
        "/get": {
          target: "http://httpbin.org",
          changeOrigin: true,
          secure: false,
          // rewrite: (path) => path.replace(/^\/test/, '/'),
          configure: (proxy, options) => {
            proxy.on("proxyReq", (proxyReq, req, res) => {
              console.log("🚀 测试代理请求:");
              console.log("  - 原始URL:", req.url);
              console.log("  - 目标:", options.target);
              console.log(
                "  - 最终URL:",
                `${options.target}${req.url.replace("/test", "")}`,
              );
            });

            proxy.on("proxyRes", (proxyRes, req, res) => {
              console.log("📥 测试代理响应:", proxyRes.statusCode);
            });
            proxy.on("error", (err, req, res) => {
              console.log("❌ 测试代理错误:", err.message);
            });
          },
        },

        "/api": {
          // target: 'http://hentai.bgzo.cc', // 500 ERROR
          // target: 'https://raw.githubusercontent.com/bGZo/hentai-daily/refs/heads/vitepress/',
          // target: 'https://cdn.jsdelivr.net/gh/bGZo/hentai-daily@refs/heads/vitepress/',
          // target:  'http://192.168.31.20:8080',
          target: "http://127.0.0.1:8080",
          changeOrigin: true,
          secure: true, // 如果是 https,
          timeout: 30000, // 增加超时时间到30秒
          proxyTimeout: 30000,
          configure: (proxy, options) => {
            // 可以在这里添加额外的配置
            proxy.on("proxyReq", (proxyReq, req, res) => {
              // 修改请求头，让它更像 API 请求而不是页面请求
              proxyReq.setHeader("Accept", "application/json, text/plain, */*");
              proxyReq.setHeader("Sec-Fetch-Dest", "empty");
              proxyReq.setHeader("Sec-Fetch-Mode", "cors");
              proxyReq.setHeader("Sec-Fetch-Site", "cross-site");
              proxyReq.setHeader("accept-encoding", "deflate");
              // 移除一些可能有问题的头
              proxyReq.removeHeader("upgrade-insecure-requests");
              proxyReq.removeHeader("sec-fetch-user");
              console.log("=== 代理请求信息 ===");
              console.log("原始请求URL:", req.url);
              console.log("代理目标:", options.target);
              console.log("最终请求URL:", `${options.target}${req.url}`);
              console.log("请求方法:", proxyReq.method);
              console.log("请求头:", proxyReq.getHeaders());
              console.log("========================");
              // console.log('响应状态:', proxyRes.statusCode)
              proxyReq.setTimeout(30000);
            });

            proxy.on("proxyRes", (proxyRes, req, res) => {
              console.log("响应状态:", proxyRes.statusCode);
              if (proxyRes.statusCode === 308) {
                console.log("重定向到:", proxyRes.headers.location);
              }
            });

            proxy.on("error", (err, req, res) => {
              console.error("=== 代理错误 ===");
              console.error("错误:", err);
              console.error("请求URL:", req.url);
              console.error("================");
            });
          },
        },
      },
    },
  },
});
