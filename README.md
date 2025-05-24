# Hentai Reader

Hentai news all in one. Support RSS subscribe.


![](https://raw.githack.com/bGZo/assets/dev/2025/202502150013399.png)


## Why

1. Separate NSFW contents from pay attention, so you can focus on more real things.
2. RSSHub official instance had been banned or limit by many servers' provider. You could always get the response like: `address no respon`.
3. Re-release the rss feed with custom function like translate / media replace / web-hook and more.

## Roadmap

- [ ] Sources:
  - [x] https://www.dlsite.com
  - [x] https://www.4gamers.com.tw
  - [x] https://mingqiceping.com
  - [x] https://blog.reimu.net
  - [x] https://gmgard.com
- [ ] Support APIs.
  - [x] RSS subscribe: discovered the folder in https://github.com/bGZo/hentai/tree/main/api/feeds to get the feed address. They should update daily.
- [ ] Rewrite UI/UX using vue. (replace jekyll)
- [ ] Custom funciotn
  - [ ] Translate 
- [ ] n8n replace?

Wants more custom sources support? Welcome to create any [issue](https://github.com/bGZo/hentai/issues/new), or choose contribute it.

<!--## APIs

Request Address: `http://rss.bgzo.cc`

| Name | Route | Description | Method | Note |
|-------|------|------|------|------|
| Feed  | `/feeds/${tag_name_with_hyphen_and_lower}` | RSS feed, return xml | `GET` | `${tag_name_with_slash_and_lower}` is the url string handle by `lower()` and hyphen(`-`). <br/>For example, we have a `DLsite Game Ranking.xml` file in server, then the correct full url address will be `http://rss.bgzo.cc/feeds/alsite-game-ranking.xml`; |
| Contents | `/archives/${year}/${month}/${day}.json` | Contents, return JSON response | `GET` | **NOTE**: The timezone of response is GMT, format it whatever you want |
-->


## Contribute

```shell
npm install
npx tailwindcss -i ./assets/css/custom.css -o ./assets/css/output.css --watch
jekyll s
```
