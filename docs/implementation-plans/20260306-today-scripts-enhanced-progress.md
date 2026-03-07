
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


#### 布局优化

1. 单双栏切换与交互优化
   - 新增 `isTwoColumn` 状态控制布局模式切换
   - 热力图下方新增操作栏 `.actions-bar`，水平居右布局
   - 实现 VPSwitch 风格切换器：椭圆轨道 (40×22px) + 圆形滑块 (18×18px)，滑块平滑滑动配合图标淡入淡出
   - 双栏布局从 column 改回 Grid (`grid-template-columns: repeat(2, 1fr)`)，避免 CSS 属性冲突警告
   - 卡片内图片添加深度样式 `:deep(.message img)`，宽度突破内边距占满卡片 (`width: calc(100% + 3rem)`)
2. 渲染逻辑修复
   - 修复双栏模式过滤不生效：从"遍历全量+内层 v-if"改为"先过滤再遍历"(`v-for` 直接使用 `getVisibleEntries`)
   - 首个分类标题去除 border-top (`:not(:first-of-type)`)，视觉更整洁
3. 双栏布局改造为瀑布流
   - 从 CSS Grid 改为 `column-count: 2` 多栏布局
   - 实现卡片从上到下紧密排列，左右列自动平衡高度
   - 添加 `break-inside: avoid` 防止卡片跨栏分割
4. 解决 hover 动画重排问题
   - 问题：scale/rotate 变换和按钮区域高度变化导致 column 布局重新计算
   - 方案：引入固定高度容器层（`.card-item` + `.card-wrapper`）
   - `.card-item` 添加 padding 预留动画缓冲空间，高度固定
   - `.card-wrapper` 设置 `overflow: hidden` 限制动画范围
   - 所有动画和按钮变化在 wrapper 内部，不影响外层布局
5. 视觉效果优化
   - 恢复 `rotate(0.5deg)` 旋转动画
   - 按钮区域正常流式布局，添加背景色、圆角和间距
   - 图标从 20px 调整为 24px，添加 hover scale 效果
   - 单栏模式间距优化：margin 从 40px 减至 20px，padding 从 20px 减至 15px

