[![Contributors](https://img.shields.io/github/contributors/bGZo/hentai-daily.svg?style=for-the-badge)](https://github.com/bGZo/hentai-daily/graphs/contributors)
[![Forks](https://img.shields.io/github/forks/bGZo/hentai-daily.svg?style=for-the-badge)](https://github.com/bGZo/hentai-daily/network/members)
[![Stargazers](https://img.shields.io/github/stars/bGZo/hentai-daily.svg?style=for-the-badge)](https://github.com/bGZo/hentai-daily/stargazers)
[![Issues](https://img.shields.io/github/issues/bGZo/hentai-daily.svg?style=for-the-badge)](https://github.com/bGZo/hentai-daily/issues)
[![Licence](https://img.shields.io/github/license/bGZo/hentai-daily.svg?style=for-the-badge)](https://github.com/bGZo/hentai-daily/blob/template/LICENCE)
[![Telegram](https://img.shields.io/badge/-telegram-black.svg?style=for-the-badge&logo=telegram&colorB=555)](https://t.me/imbGZo)

> [!WARNING]
> This project may contain violence, pornography, sexual descriptions, or other content intended for readers aged 18 and over only.
>
> Please read it with caution and discretion. If you are under 18 years old, please do not read this project. The author and publisher of this article do not take any responsibility for any consequences arising from reading this article.

![](https://pub-89c11651a8434f18a530bd6f93e399da.r2.dev/2026/20260514220009609.webp)
<!--
![](https://pub-89c11651a8434f18a530bd6f93e399da.r2.dev/2025/202506162245177.png)
# Hentai Daily
-->

Hentai news all in one. Support RSS subscribe.

## Why

> [!NOTE]
> TL;DR:
>
> 1. Separate NSFW contents from pay attention, so you can focus on more real things.
> 2. RSSHub official instance had been banned or limit by many servers' provider. You could always get the response like: `address no respon`.
> 3. Re-release the rss feed with custom function like translate / media replace / web-hook and more.

I enjoy porn, but if I put it alongside other subscriptions, I definitely won't spend any more time exploring other people's blogs. Meanwhile, I'm easily aroused pron, so pron context needs to be kept separate for me.

So why not just use RSShub and write your own rules in Python?

1. Customization: I need to add additional logic to the downloaded sources, such as filters, preview image replacement, and hotlinking prevention.
2. Copyright: RSShub is already a well-known project and is conservative about copyright-related PRs. Being a big name attracts attention; I think you understand.
3. Development Cycle: The development cycle is often held up by RSShub's upstream infrastructure, or I need to deploy an RSShub instance locally, which is quite troublesome. Plus, I'm not very skilled, so I'll just treat it as practice.

Of course, this project cannot be profitable, just for fun and love.

## Getting Started

- https://hentai.bgzo.cc
- https://hentai-daily.vercel.app/
- https://hentai-daily.lfh010618.workers.dev/
- Self build and deploy by yourself, see [Contributing](#contributing) section below.

## API Usage

Except the daily updates, the API also provides access to historical data and various filters for customizing your feed. See the `api/archives` folder for more details.

And more, this project also provides a RSS fetch function, just like RSSHub, which including the website don't have RSS or close it. Check list in `api/feed` folder.

| Name     | Route                                      | Description                    | Method | Note                                                                                                                                                                                                                                                          |
| -------- | ------------------------------------------ | ------------------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Feed     | `/feeds/${tag_name_with_hyphen_and_lower}` | RSS feed, return xml           | `GET`  | `${tag_name_with_slash_and_lower}` is the url string handle by `lower()` and hyphen(`-`). <br/>For example, we have a `DLsite Game Ranking.xml` file in server, then the correct full url address will be `http://rss.bgzo.cc/feeds/alsite-game-ranking.xml`; |
| Contents | `/archives/${year}/${month}/${day}.json`   | Contents, return JSON response | `GET`  | **NOTE**: The timezone of response is GMT, format it whatever you want                                                                                                                                                                                        |

## Contributing

Any contributions made are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Install Dependencies and Develop your Feature (`npm install` and `run docs:dev`)
4. Working hard on your Feature and Test it.
5. Commit your Changes (`git commit -m 'feat(module):add some AmazingFeature'`)
6. Push to the Branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

Top contributors:

<a href="https://github.com/bGZo/hentai-daily/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=bGZo/hentai-daily" alt="contrib.rocks image" />
</a>

## License

All code is licensed under the AGPL-3.0 license. See `LICENSE` for more information.
