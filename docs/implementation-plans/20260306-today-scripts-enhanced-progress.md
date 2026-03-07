
## 改造总括

### 后端

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

### 前端

#### 重构

主要优化如下：

1. 统一并强化数据结构，避免空对象带来的潜在异常
   1. 新增空数据工厂，保证各分类始终存在：docs/.vitepress/theme/components/today.vue:28
   2. data 从可空/不完整结构改为稳定结构：docs/.vitepress/theme/components/today.vue:77
   3. 请求失败时不再 {} as hentaiAPI，改为安全回退：docs/.vitepress/theme/components/today.vue:163
2. 移除冗余状态与未使用逻辑，降低复杂度
   1. 删除未使用的 loading / error / tocCountLimit / showAllItems
   2. 删除未使用的 filterToday、isValidRssEntity
   3. clickCopyLink 去掉无用回调参数：docs/.vitepress/theme/components/today.vue:193
3. 减少模板重复过滤计算，提升渲染效率
   1. 新增 visibleData 计算属性，统一做分类过滤：docs/.vitepress/theme/components/today.vue:256
   2. 模板从多次 getVisibleEntries(...) 改为直接使用 entries：docs/.vitepress/theme/components/today.vue:439、docs/.vitepress/theme/components/today.vue:558
4. 简化暗色模式监听实现
   1. 去掉 MutationObserver 包装函数，直接 watch(isDark, ...)：docs/.vitepress/theme/components/today.vue:373
5. 小幅类型完善与逻辑收敛
   1. rssEntity 增加可选 translate，匹配模板使用：docs/.vitepress/theme/components/today.vue:15
   2. handleCardCss 从冗长 switch 改为数组映射+兜底：docs/.vitepress/theme/components/today.vue:206
   3. 日期显示去掉尾部多余 /：docs/.vitepress/theme/components/today.vue:146


