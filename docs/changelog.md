---
title: Changelog
outline: deep
---

## 20260528 New layout

Remove the card layout, use a more simple list layout, support the filter by sites.

## 20260519 Temporary Unavailability

Due some [reason](https://blog.bgzo.cc/20260516-mv-repo-to-github-organization), I transfer this project to my new organization, and after checking github action, I go back to vibe coding new project again, I used to think it would be fine, but I was wrong. I forget to check the build status of this website(on cloudflare and vercel). So in the past few days, the sites are not updated for new posts.

Very sorry for the inconvenience. I have fixed it tonight, and the build of this website on Cloudflare/Vercel is back to normal. 

And past three days, nobody notice me, just like before, right? Very sad about that. If you found something mistake, please create a [issue](https://github.com/bgzo-sandbox/hentai-daily/issues/new) or drop me a line(snitch-bulk-caviar#duck.com).

I thought this project is still being looked at, but maybe not?...

![](https://pub-89c11651a8434f18a530bd6f93e399da.r2.dev/2026/20260519234533673.webp)

Anyway, thanks for your attention, and I will try to keep it up to date as much as possible.

## 20260307 Sync Script Enhancement

I apologize for the instability in updates over the past two days. The script modification wasn't fully tested during this period, causing unavailability at that times. This issue has now been largely fixed. 

This modification focused on:

1. Increasing the synchronization frequency from once a day to once every two hours to ensure more timely data.
2. Adjusting the archive output structure, splitting data by category, supporting historical data merging (yesterday's and today's JSON) and deduplication (URL), discarding (from the day before yesterday) to prevent data bloat.
3. Optimizing front-end display filtering; Resources and News now only display entries from the past 24 hours.
4. The Ranking category maintains its original display logic.

However, some issues remain unresolved. For example, an increasing number of sources are rejecting GitHub crawler access, returning 403 errors, resulting in unavailable data and significantly impacting the user experience. I may need to deploy a local crawler to compensate for this data shortfall.

## 20260305 TOC & HeatMap Improvement

1. The directory style has been greatly improved, basically achieving the feeling of native Vitepress;
2. The hard-coded start time of the HeatMap component has rendered it essentially unusable this year;
3. Card button improvements for better accessibility and minimalist design

The most disheartening thing is that no one has raised any issues with me. Is this project really no longer being looked at?

So sad.

![](https://pub-89c11651a8434f18a530bd6f93e399da.r2.dev/2026/20260519234038378.webp)

## 20260304 Weak Internet

Actually, there's nothing new this time, just wanted to complain.

Last week, I was checking my bookmarks on TG and found that LMYS's Telegram channel(@lmys8) had gone. I panicked, thinking it had become private. Then I found their new channel(@lmys88), and I realized that hundreds of thousands of channels were inaccessible, how simply!

What can I say? This is probably the norm for Web2. One of the biggest problems with centralization is legality and compliance. Because I haven't had much free time lately months, I haven't been looking at much content, including this. I miss the time when I still in school, the whole holidays, I could freely immerse myself in these communities, lost in my own world, and always have home-cooked meals whenever I was hungry, day after day.

That's getting off-topic. Sorry. Actually, I think if I had extracted the links last year when this project refactor, maybe we could avoid this situation, right? But I didn't want to do that because it would reduce traffic to their server, which is almost the most fatal problem for an independent website. Then there's the issue of link explosions. If I extracted the links and put them on GitHub, wouldn't that make the link explosions even more fast to invaild?

I don't know, maybe writing this down counts is an answer?

## 20250809 `i8n` for Chinese

Translate the main documents to Chinese, except the today component.

## 20250620 Publish to commun

1. https://bgm.tv/group/topic/427051
2. https://www.v2ex.com/t/1140027


##  20250615 Rewrite with [VitePress](https://github.com/vuejs/vitepress) #Developing

Rewrite UI/UX using vue to replace jekyll.

Favicon & logo from meme created by [@猛禽bot](https://weibo.com/n/%E7%8C%9B%E7%A6%BDbot)

Old site had archived on https://github.com/bgzo-sandbox/hentai-daily/tree/v1.0

## 20240121 ~ 20241123 Project archivedc

Archived due to using [telegram RSS bot](https://github.com/Rongronggg9/RSS-to-Telegram-Bot). But I realised this is a black hell when all messages messed up. I have no time to read anyone.

And also RSS integrate with Logseq also brings much garbage messages, which [brother me a lot](https://bgzo.github.io/vault/weekly/1218-giving-up-logseq).

So I have to restart it.

### 20240521 名器之家

https://mingqiceping.com has close RSS output.

### 20240307 灵梦御所

The server of https://blog.reimu.net had been down. 

Then the release of resource changed to telegram.

### 20240301 RSShub

The refactor of RSSHub break the route of http://home.gamer.com.tw.[^rsshub-pr]

[^rsshub-pr]: via: https://github.com/DIYgod/RSSHub/commit/6f57c02538bd2faefbe77566465c2c2c3f3caf3b

## 20231201 Somthing happened

The owner of a https://bbs.drdian.net was arrested by the police in China, and ultimately sentenced to bail pending trial. [^end-of-drdian]

[^end-of-drdian]: via: https://bgm.tv/group/topic/390528

Then the module of https://www.south-plus.net/rss.php?fid=135 had been hidden. The rss source was down as well

## 20230613 Release prototype with Jekyll 

### Source List

- [x] https://www.dlsite.com
- [x] https://www.4gamers.com.tw
- [x] https://mingqiceping.com
- [x] https://blog.reimu.net
- [x] https://gmgard.com
- [x] https://www.tiangal.com
- [x] https://www.south-plus.net
