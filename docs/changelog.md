---
title: Changelog
outline: deep
---

## What's Next

Wants more custom sources support? Welcome to create any [issue](https://github.com/bGZo/hentai/issues/new), or choose contribute it.

- [ ] Custom functions
  - [ ] Translate 
- [ ] n8n replace?


##  2025.06.15 (Develop) Rewrite with [VitePress](https://github.com/vuejs/vitepress)

Rewrite UI/UX using vue to replace jekyll.

Old site archived via: https://github.com/bGZo/hentai-daily/tree/v1.0

## 2024.01.21 ~ 2024.11.23 Project archived

Archived due to using [telegram RSS bot](https://github.com/Rongronggg9/RSS-to-Telegram-Bot). But I realised this is a black hell when all messages messed up. I have no time to read anyone.

And also RSS integrate with Logseq also brings much garbage messages, which [brother me a lot](https://bgzo.github.io/vault/weekly/1218-giving-up-logseq).

So I have to restart it.

### 2024.05.21 名器之家

https://mingqiceping.com has close RSS output.

### 2024.03.07 灵梦御所

The server of https://blog.reimu.net had been down. 

Then the release of resource changed to telegram.

### 2024.03.01 RSShub

The refactor of RSSHub break the route of http://home.gamer.com.tw.[^rsshub-pr]

[^rsshub-pr]: via: https://github.com/DIYgod/RSSHub/commit/6f57c02538bd2faefbe77566465c2c2c3f3caf3b

## 2023.12.01 Somthing happened

The owner of a https://bbs.drdian.net was arrested by the police in China, and ultimately sentenced to bail pending trial. [^end-of-drdian]

[^end-of-drdian]: via: https://bgm.tv/group/topic/390528

Then the module of https://www.south-plus.net/rss.php?fid=135 had been hidden. The rss source was down as well

## 2023.06.13 Release prototype with Jekyll 

### Source List

- [x] https://www.dlsite.com
- [x] https://www.4gamers.com.tw
- [x] https://mingqiceping.com
- [x] https://blog.reimu.net
- [x] https://gmgard.com
- [x] https://www.tiangal.com
- [x] https://www.south-plus.net

### APIs & RSS subscribe support

Address: `https://raw.githubusercontent.com/bGZo/hentai-daily/refs/heads/vitepress/api/`

| Name | Route | Description | Method | Note |
|-------|------|------|------|------|
| Feed  | `/feeds/${tag_name_with_hyphen_and_lower}` | RSS feed, return xml | `GET` | `${tag_name_with_slash_and_lower}` is the url string handle by `lower()` and hyphen(`-`). <br/>For example, we have a `DLsite Game Ranking.xml` file in server, then the correct full url address will be `http://hentai.bgzo.cc/feeds/alsite-game-ranking.xml`; |
| Contents | `/archives/${year}/${month}/${day}.json` | Contents, return JSON response | `GET` | **NOTE**: The timezone of response is GMT, format it whatever you want |

More you could discovered the folder in https://github.com/bGZo/hentai/tree/main/api/feeds to get the feed address. They should update daily.
