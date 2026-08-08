---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "绅士日报"
  text: "对不良诱惑说"
  tagline: 今天是戒色第一天
  image:
    src: /favicon-512x512.png
    alt: VitePress
  actions:
    - theme: brand
      text: 快给我
      link: /zh-cn/today
    - theme: alt
      text: 我有更好的点子💡
      link: https://github.com/bgzo/hentai-daily/issues

features:
  - title: 足够 Hentai
    details: 聚合各个Hentai源，提供昨天更新的内容，无需辗转各个网站，不够Hentai 不考虑；
  - title: 比较稳定
    details: GitHub Action + Cloudflare Worker，想方设法拉取，比 RSSHub 更加轻量，更少的429提示；不做链接提取，对上游友好；
  - title: 公开 API
    details: 提供对外封装好的 RSS 地址，支持外部重新订阅，自由使用本项目 API
    link: /zh-cn/rss
  - title: 翻译
    details: 支持日文到中文翻译，支持由 https://mymemory.translated.net 提供
  # - title: 集成 (Next)
  #   details: 周报、月报、年报、下一步集成方向
---

