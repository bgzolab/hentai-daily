# 项目架构

> 目录结构、入口与数据流以根目录 `AGENTS.md` 为准（Python 数据管道 `src/` + VitePress 站点 `docs/`，无统一构建）。本文件只记录 AGENTS.md 未覆盖的组件职责边界。

## 日报页面组件职责（`docs/.vitepress/theme/components/`）

- `today.vue`：仅保留日报页的数据获取、日期切换、热力图、布局编排与 TOC。
- `today/TodayFeedSection.vue`：`Resources` 与 `News` 的分区头部、订阅入口和头像占位。
- `today/TodayFeedItem.vue`：单条信息流，采用接近「朋友圈」的平面动态布局。
- `today/TodayRankingSection.vue`：三个排行榜分区，采用 Top 3 + 后续榜单行的分层结构。
- `today/summary.ts`：从 summary HTML 提取首图与纯文本，避免布局直接依赖原始 HTML。
- 另有辅助组件/模块：`avatar.ts`、`translation.ts`、`TodayInlineTranslation.vue`、`TodayPreviewImage.vue`。

## 职责边界

- 父组件不持有 feed/ranking 的具体视觉样式，避免演变为 monolith。
- feed 与 ranking 的视觉系统分别在各自子组件内部演进，共享同一份 archive 数据与锚点命名规则。
- 当前视觉策略：feed 用「朋友圈式信息流」，ranking 用「榜单公告板」，以降低与 VitePress 文档外壳的冲突。
