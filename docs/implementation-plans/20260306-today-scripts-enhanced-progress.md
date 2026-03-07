
## 改造总括

1. `src/sync.py` 的 `output_archive` 已重构为按分类分流：
	- `Resources` 与 `News`：合并历史并按 `url` 去重，支持多次执行累计；
	- `DLsite Game Ranking`、`DLsite Voice Ranking`、`DLsite Comic Ranking`：仅当本次抓取数量为 `5` 时覆盖，否则保留旧值。
2. `Resources` 与 `News` 新增时间窗口控制：
	- 写入前会额外尝试合并“昨日归档”（若存在）；
	- 同时丢弃“前天及更早”数据，仅保留昨天及之后内容，避免 JSON 体积持续膨胀。
3. 归档输出顺序固定为：`Resources` -> `News` -> `DLsite Game Ranking` -> `DLsite Voice Ranking` -> `DLsite Comic Ranking`。
4. 仅 `Resources` 与 `News` 在归档阶段按 `timestamp` 倒序排序，Ranking 分类不参与排序。
5. 前端 `docs/.vitepress/theme/components/today.vue` 已调整展示过滤：
	- `Resources` 与 `News` 只显示“昨天 00:00 ~ 今天 00:00”的条目；
	- 三个 Ranking 保持原有展示逻辑不变。
6. CI 定时任务 `/.github/workflows/sync.yml` 的 `cron` 已改为每 2 小时执行一次（`0 */2 * * *`）。
