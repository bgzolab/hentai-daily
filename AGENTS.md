# AGENTS.md

Two independent halves in one repo — there is **no unified build**:
- **Python data pipeline** (`src/`) — scrapes/fetches RSS + HTML/JSON sources and writes the committed `api/` data.
- **VitePress docs site** (`docs/`) — the public web UI, built from that data.

Generated data is **committed to git** and served directly from `api/` (see `docs/api.md`). Changing the pipeline usually means regenerating + committing data.

## Python pipeline (`src/`)

- Entry point: `src/sync.py` (`python3 src/sync.py` from repo root — Python auto-adds the script's dir to `sys.path`, which is why `from sources.*` / `from common.*` work). Then `python3 src/heatmap-count.py`.
- Source adapters live in `src/sources/*.py`. Each exposes a `get_*()` returning a list of unified dicts: `{title, url, summary, timestamp}`. Wire a new source into `src/sync.py` via `add_sources(rss_content_dict, '<Category>', get_xxx(), '<feed-name>')`.
  - Category keys: `Resources`, `News`, `DLsite Game/Voice/Comic Ranking`. The feed-name argument writes `api/feeds/<feed-name>.xml`; pass `None` to skip that.
  - DLsite ranking getters default `limit=10`; `sync.py` calls them with `DLSITE_LIMIT = 5`.
- Runtime deps in `src/requirements.txt`; use the repo `.venv/` (has python 3.12/3.14 + pytest).
- **Proxy required for live scraping**: export proxy vars to `http://127.0.0.1:10800` (example in `.env.bak`; `.env` is gitignored). Offline tests don't need it.
- **Brotli**: `src/sync.py` deliberately sends `Accept-Encoding: gzip, deflate` (no `br`) to avoid missing-brotli failures in CI, and manually decompresses `br` responses via `brotlicffi` as a fallback. `src/sources/dlsite.py` still sends `br`. `src/interceptor/request.py` (`MySession`) adds retry/timeout and logs every request — useful when debugging.

### Archive merge gotchas (in `output_archive`, `src/sync.py`) — read before editing
- `Resources`/`News` merge by URL and carry over yesterday's entries, dropping anything older than ~yesterday.
- DLsite ranking categories are **only overwritten when exactly 5 entries are fetched**; otherwise the existing archive value is preserved (with a warning). Don't "fix" this unless you understand it.
- Output JSON key order is forced: `Resources, News, DLsite Game Ranking, DLsite Voice Ranking, DLsite Comic Ranking`, then others.

### Tests
- Offline pytest suite in `tests/`, using fixtures in `debug/` (`*.html`, `*.json`, `*.xml`) — no network. Tests inject `src/` into `sys.path` themselves.
- Run: `python3 -m pytest tests/` (`.vscode` sets `python.testing.pytestArgs = ["tests"]`).
- A few tests do real network + proxy (e.g. `test_dlsite.py::test_run_dlsite_ranking`) and can fail/hang without the proxy — skip `*_run_*` tests when iterating offline, e.g. `-k "not run_"`.
- Convention (from `docs/memories/tech-stack.md`): every source change should ship with unit tests targeting ~100% coverage; refactor into modules, avoid monolith files.

## Docs site (`docs/`)

- VitePress, bilingual: root `en`, `zh-cn/` locale (see `docs/.vitepress/config.mts`).
- Commands (`package.json`):
  - `npm run docs:dev` — vitepress dev **plus** `http-server -p 8080`; the `/api` dev proxy targets `http://127.0.0.1:8080`, so keep both running for live API data.
  - `npm run docs:build` — `vitepress build docs && npm run copy-files` (copies `./api` into `docs/.vitepress/dist/`).
  - `npm run docs:preview` — preview the built site.
- `docs/.vitepress/config.mts` excludes `memories/**` and `implement-plans/**` from the build (`srcExclude`) — they are design/context docs, not pages.
- `docs/today.md` and `docs/zh-cn/today.md` render the `<Today />` Vue component; the pipeline rewrites their `update:` frontmatter on each sync.
- Today page UI lives in `docs/.vitepress/theme/components/today*.vue` + `today/summary.ts`. See `docs/memories/architecture.md` and `design.md` for the intended component boundaries (Resources/News = feed style, DLsite rankings = board style).

## CI / deployment

- `.github/workflows/sync.yml`: scheduled (Asia/Singapore, every 2h) + on push to `vitepress-dev`. Runs `sync.py` + `heatmap-count.py`, reformats all `api/archives/**/*.json` with `jq --indent 2`, then `git pull --rebase && git push` (concurrency group prevents overlapping syncs). Needs `contents: write` permission.
- Deploy: Cloudflare Workers (`wrangler.jsonc`, assets from `docs/.vitepress/dist/`) and Vercel (`vercel.json`, `cleanUrls: true`).
- Current working branch is `vitepress`; `main` is the release branch.
- Commit style is conventional-ish: `ci(sync):`, `chore(docs):`, `feat(module): ...`, plus auto-generated `chore(ci): sync feed by GitHub actions` and `Sync feed`.

## Key instruction sources already in repo
- `docs/memories/architecture.md`, `design.md`, `tech-stack.md` — authoritative architecture/design/tech conventions for LLM work.
- `docs/implement-plans/*.md` — per-feature plans + verification tests (gitignored path but tracked).
