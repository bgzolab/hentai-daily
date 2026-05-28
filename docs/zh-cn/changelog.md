---
title: 更新日志
outline: deep
---

## 20260528 新布局

删除了原来的卡片布局，因为觉得有点妨碍到阅读了，改成了更平整的列表布局，同时支持了按站点过滤的功能。

## 20260519 CI/CD暂时不可用

由于上周[瞎折腾](https://blog.bgzo.cc/20260516-mv-repo-to-github-organization)，把项目转移到了沙箱里面（新组织），在检查github action 一切正常后，我把这个事情给忘了，回去又去vibe 新的项目去了，我以为一切都会正常运行，但我错了。我忘了检查这个网站的构建了（cloudflare/vercel）。所以在过去的三天里，网站没有实时更新新的帖子。

非常抱歉给您带来不便。我今晚已经修好了，这个网站在Cloudflare/Vercel上的构建恢复正常了。

伤心的事，过去三天，没人提醒我，跟以前一样，对吧？如果你发现了什么错误，请创建一个[ISSUE](https://github.com/bgzo-sandbox/hentai-daily/issues/new)或给我留言（snitch-bulk-caviar#duck.com）。

我认为这个项目其实还有人在看吧，最近好像掉了一颗 Star 🌟，但也许无人在意？

无论如何，谢谢你的关注，我会尽量保持让这个项目走的远一些的。

![](https://pub-89c11651a8434f18a530bd6f93e399da.r2.dev/2026/20260519234533673.webp)

## 20260307 同步改造

这两天更新不太稳定，需要说声抱歉，这两天改造脚本没有做完整的测试，导致了部分时间段不可用，目前已经修复了这个问题（大概）。本次改造着重于：

1. 同步频率提高，从每天一次到每两小时一次，确保数据更及时。
2. 归档输出结构调整，按分类分流，支持历史数据合并（昨天与今天的JSON）与去重（URL），丢弃（前天），避免数据膨胀。
3. 前端展示过滤优化，Resources 与 News 仅显示昨天 24 小时内的条目。
4. Ranking 分类保持原有展示逻辑不变。

但还是有一些问题无法解决，比如越来越多的源拒绝了 GitHub 爬虫访问，返回403错误，导致数据拉取不到，比较影响体验，后面可能需要在我本地部署一个爬虫补偿这部分数据。


## 20260305 目录与热力图改善

1. 目录格式大改善，基本做到了Vitepress原生的效果；
2. HeatMap 组件的起始时间写死导致今年基本不可用；
3. 增加按钮卡片按钮，符合直觉；

最难过的是，竟然没有人给我提Issue，这个项目真的没人看了么？

好难过

![](https://syimg.3dmgame.com/uploadimg/xiaz/2022/1011/1665477061696.jpg)

## 20260304 脆弱的互联网

其实这次没有什么更新的内容，纯粹想发发牢骚。

上周，我翻收藏夹，发现灵梦御所的 TG 频道 @lmys8 没了，我很慌，以为它变成私有了，后来才发现它的新频道 @lmys88，才知道原来十来万的频道直接无法访问。

能说什么呢？这大概率是 Web2 的常态，中心化的一个最大的问题就是合法合规，因为我最近没有什么空闲时间，所以什么内容都不怎么看了，包括这个项目。我很怀念自己上学放假那会儿，整整 1 个月的时间，我可以自由地泡在这些社区，沉浸在自己的世界中，饿了随时能吃到家里的饭菜，日复一日。

扯远了，其实我想如果去年我把链接提取这件事情做了之后，也许就可以一定程度上避免这种事情发生，但我不太想做这样的事情，因为源站流量会减少，这几乎是独立网站最致命的问题；再来就是爆链的问题，如果我把链接提取出来放在 GitHub，是不是会让链接更容易爆炸？

我不知道，写下来算不算是一种答案？

## 20250809 中文国际化

翻译了主要文档，翻译比较随性，大家看个乐呵。

## 20250620 项目面向社区发布

1. https://bgm.tv/group/topic/427051
2. https://www.v2ex.com/t/1140027


##  20250615 用 [VitePress](https://github.com/vuejs/vitepress) 重写前端 #Developing

不再用 Jekyll 自动构建的静态站点，采用更加现代化的 Vue 框架 VitePress 来重写前端。

Favicon 和 logo 来自于 [@猛禽bot](https://weibo.com/n/%E7%8C%9B%E7%A6%BDbot) 的表情包；

如果你对旧站点感兴趣，可以访问 https://github.com/bGZo/hentai-daily/tree/v1.0

## 20240121 ~ 20241123 项目存档

由于没有什么人看，加上使用了 [telegram RSS bot](https://github.com/Rongronggg9/RSS-to-Telegram-Bot) 来替代我的 RSS 阅读器，所以项目没有什么存在的必要了，就存档了。 但我慢慢意识到一个问题，时间线的信息流会打乱你输入信息的节奏，消息是碎片且不连续的，这对你的注意力是个黑洞。

这样一来，我更没有心思去看了。尤其是如果你尝试把 [RSS 和 第二大脑结合起来的话](https://bgzo.github.io/vault/weekly/1218-giving-up-logseq)，碎片化的信息流会让你更难以专注于手头的任务。

我还是重启这个项目吧。

### 20240521 名器之家

https://mingqiceping.com 关闭了 RSS 输出

### 20240307 灵梦御所

https://blog.reimu.net 全站数据丢失。

内容分发策略转移，全部面向 Telegram 频道。


### 20240301 RSShub 重构

RSSHub 的路由重构导致了部分 RSS 源失效（http://home.gamer.com.tw）。[^rsshub-pr]

[^rsshub-pr]: via: https://github.com/DIYgod/RSSHub/commit/6f57c02538bd2faefbe77566465c2c2c3f3caf3b

## 20231201 终点论坛被封禁

https://bbs.drdian.net 的作者被中国警方逮捕，最终被判保释候审。[^end-of-drdian]

[^end-of-drdian]: via: https://bgm.tv/group/topic/390528

随后没几天，https://www.south-plus.net/rss.php?fid=135 的中文汉化区也被站长隐藏了，至今未恢复。RSS源也自然倒闭了。


## 20230613 项目原型诞生

### 来源列表

- [x] https://www.dlsite.com
- [x] https://www.4gamers.com.tw
- [x] https://mingqiceping.com
- [x] https://blog.reimu.net
- [x] https://gmgard.com
- [x] https://www.tiangal.com
- [x] https://www.south-plus.net
