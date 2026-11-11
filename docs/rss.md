# API & RSS

All data lives in the committed [`api/`](https://github.com/bgzolab/hentai-daily/tree/vitepress/api) folder and is served as-is by every deployment. Every route below is `GET`.

| Base URL | |
| --- | --- |
| `https://hentai.bgzo.cc/api` | primary |
| `https://hentai-daily.vercel.app/api` | mirror |
| `https://hentai-daily.lfh010618.workers.dev/api` | mirror |
| `https://raw.githubusercontent.com/bgzolab/hentai-daily/refs/heads/vitepress/api` | raw GitHub |

## Archives

`/archives/${year}/${month}/${day}.json` — one day of every source, newest first. `year` is 4 digits, `month`/`day` are zero-padded.

```jsonc
{
  "Resources": [
    {
      "title": "…",
      "url": "https://…",
      "summary": "<img src=\"…\" /> …", // raw HTML
      "timestamp": 1794297615          // Unix seconds, UTC
    }
  ],
  "News": [],
  "DLsite Game Ranking": [],
  "DLsite Voice Ranking": [],
  "DLsite Comic Ranking": []
}
```

## Heatmap counts

`/count.json` — `[{ "date": "2026-11-10", "value": 42 }]`, one entry per day; used by the Today page heatmap.

## RSS

Feeds are regenerated into `api/feeds/` on every sync. Subscribe with a base URL from above plus the feed path, e.g. `https://hentai.bgzo.cc/api/feeds/resources.xml`.

### Merged feeds

| Feed | Covers |
| --- | --- |
| `/feeds/resources.xml` | all `Resources` sources |
| `/feeds/news.xml` | all `News` sources |
| `/feeds/dlsite-game-ranking.xml` | DLsite game ranking, top 5 |
| `/feeds/dlsite-voice-ranking.xml` | DLsite voice ranking, top 5 |
| `/feeds/dlsite-comic-ranking.xml` | DLsite comic ranking, top 5 |

### Per-source feeds

| Feed | Source |
| --- | --- |
| `/feeds/4gamers.xml` | 4Gamers (TW) |
| `/feeds/asmr-one.xml` | ASMR One |
| `/feeds/bahamut-a1102kevin.xml` | Bahamut creator `a1102kevin` |
| `/feeds/dlsite-news.xml` | DLsite news |
| `/feeds/llss.xml` | 琉璃神社 (hacg.icu) |
| `/feeds/mingqiceping.xml` | 名器测评 |
| `/feeds/nysoure.xml` | Nysoure |
| `/feeds/ylms.xml` | Reimu (blog.reimu.net) |

Feeds not listed here are leftovers from disabled sources and are no longer refreshed.
