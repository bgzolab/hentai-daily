# Hentai Reader

Hentai posts all in one. 

![](https://raw.githack.com/bGZo/assets/dev/2025/202502150013399.png)


## Develop

```shell
npm install
npx tailwindcss -i ./assets/css/custom.css -o ./assets/css/output.css --watch
jekyll s
```

## Roadmap

- [ ] Support more sources:
  - [x] DLSITE
  - [x] 4GAMER
- [x] Support APIs.


<!--## APIs

Request Address: `http://rss.bgzo.cc`

| Name | Route | Description | Method | Note |
|-------|------|------|------|------|
| Feed  | `/feeds/${tag_name_with_hyphen_and_lower}` | RSS feed, return xml | `GET` | `${tag_name_with_slash_and_lower}` is the url string handle by `lower()` and hyphen(`-`). <br/>For example, we have a `DLsite Game Ranking.xml` file in server, then the correct full url address will be `http://rss.bgzo.cc/feeds/alsite-game-ranking.xml`; |
| Contents | `/archives/${year}/${month}/${day}.json` | Contents, return JSON response | `GET` | **NOTE**: The timezone of response is GMT, format it whatever you want |
-->