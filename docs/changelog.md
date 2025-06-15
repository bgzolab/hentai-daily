---
title: Changelog
outline: deep
---

## What's Next

Wants more custom sources support? Welcome to create any [issue](https://github.com/bGZo/hentai/issues/new), or choose contribute it.

- [ ] Rewrite UI/UX using vue. (replace jekyll)
  - [ ] 2025.06.15 (Develop) Rewrite with [VitePress](https://github.com/vuejs/vitepress)
- [ ] Custom functions
  - [ ] Translate 
- [ ] n8n replace?


## 2024.01.21 ~ 2024.11.23 Archived

Archived due to using [telegram RSS bot](https://github.com/Rongronggg9/RSS-to-Telegram-Bot). But I realised this is a black hell when all messages messed up. I have no time to read anyone.

And also RSS integrate with Logseq also brings much garbage messages, which [brother me a lot](https://bgzo.github.io/vault/weekly/1218-giving-up-logseq).

So I have to restart it.

## 2023.06.13 Release prototyoe with Jekyll 


### Source List

- [x] https://www.dlsite.com
- [x] https://www.4gamers.com.tw
- [x] https://mingqiceping.com
- [x] https://blog.reimu.net
- [x] https://gmgard.com
- [x] https://www.tiangal.com

### APIs & RSS subscribe support

Address: `https://raw.githubusercontent.com/bGZo/hentai-daily/refs/heads/vitepress/api/`

| Name | Route | Description | Method | Note |
|-------|------|------|------|------|
| Feed  | `/feeds/${tag_name_with_hyphen_and_lower}` | RSS feed, return xml | `GET` | `${tag_name_with_slash_and_lower}` is the url string handle by `lower()` and hyphen(`-`). <br/>For example, we have a `DLsite Game Ranking.xml` file in server, then the correct full url address will be `http://hentai.bgzo.cc/feeds/alsite-game-ranking.xml`; |
| Contents | `/archives/${year}/${month}/${day}.json` | Contents, return JSON response | `GET` | **NOTE**: The timezone of response is GMT, format it whatever you want |

More you could discovered the folder in https://github.com/bGZo/hentai/tree/main/api/feeds to get the feed address. They should update daily.
