# 项目架构

## 前置要求：项目结构与含义

架构需要对项目的整体结构进行说明，明确每个文件夹和文件的作用，以及它们之间的关系。以下是项目的部分架构设计，要求有：

1) 通过 Tree 结构展示每个文件的作用。
2) 每个文件的作用要清晰、具体，最好列出调用结构。

## 项目结构

```shell
.
├── .github
│   ├── agents # 智能体，copilot 左下角可选择
│   ├── copilot-instructions.md # 项目全局生效
│   ├── instructions # 项目默认加载指令
│   ├── ISSUE_TEMPLATE # 项目 issue 模板
│   ├── prompts # 使用slash 调用的预制提示词
│   └── workflows # GitHub CI/CD
├── docs # 项目文档，包含项目的设计文档、架构文档、技术栈规范、实施计划等
│   ├── implement-plans # 项目的实施计划，每次修BUG、新增改能全部记录在这里，包含每个功能的分步指令和验证正确性的测试
│   │   ├── feature-a.md # feature-a 的实施计划，包含分步指令和验证正确性的测试
│   │   └── feature-a-progress.md # feature-a 的实施进度，包含每个步骤的完成情况和测试结果
│   ├── memories # 项目的记忆库，包含项目的设计文档、架构文档、技术栈规范等，是 LLM 必须加载的上下文；
│   │   ├── architecture.md # 项目架构设计文档，包含项目的整体架构设计、模块划分、数据库结构等；
│   │   ├── design.md # 项目设计文档，包含项目的功能设计、接口设计、数据流设计等；
│   │   └── tech-stack.md # 项目技术栈规范，包含项目的技术栈选择、编码规范、测试规范等；
│   └── prompts # 项目的提示词库，包含项目的提示词设计、提示词优化、提示词测试等，LLM 不必理会
│       ├── init-project.md # 初始化项目提示词
│       └── new-feature.md # 新增功能提示词
├── LICENCE # 项目许可证，包含项目的开源许可证信息
└── README.md # 项目自述文件，包含项目的简介、安装使用说明、贡献指南等
```

## 日报页面组件拆分（2026-05-28）

- `docs/.vitepress/theme/components/today.vue`：仅保留日报页的数据获取、日期切换、热力图、布局编排与 TOC。
- `docs/.vitepress/theme/components/today/TodayFeedSection.vue`：负责 `Resources` 与 `News` 的分区头部、订阅入口和头像占位。
- `docs/.vitepress/theme/components/today/TodayFeedItem.vue`：负责单条信息流内容，采用更接近“朋友圈”的平面动态布局。
- `docs/.vitepress/theme/components/today/TodayRankingSection.vue`：负责三个排行榜分区，采用 Top 3 + 后续榜单行的分层结构。
- `docs/.vitepress/theme/components/today/summary.ts`：负责从 summary HTML 中提取首图与纯文本，避免布局直接依赖原始 HTML。

## 日报页面职责边界

- 父组件不再持有任何 feed/ranking 具体视觉样式，避免再次演变为 monolith。
- feed 和 ranking 的视觉系统分别在子组件内部演进，但共享同一份 archive 数据与锚点命名规则。
- 当前日报采用“朋友圈式信息流 + 榜单公告板”的双视觉策略，以降低与 VitePress 文档外壳的冲突。

## 直接数据源接入（2026-05-28）

- `src/sources/kungal.py`：新增 KUNGal JSON 源，负责调用 `https://www.kungal.com/api/galgame`，过滤 `contentLimit = nsfw` 的条目，并映射为统一的 `title/url/summary/timestamp` 结构。
- `src/sources/asmr_one.py`：新增 ASMR.one JSON 源，负责调用 `https://api.asmr-200.com/api/works`，过滤 `nsfw = true` 的条目，并将 `title/source_id/create_date/mainCoverUrl/name/vas` 映射为统一的 `title/url/summary/timestamp` 结构。
- `src/sources/nysoure.py`：新增 nysoure JSON 源，负责调用 `https://nysoure.com/api/resource?page=1&sort=7`，将 `id/title/release_date/image.id` 映射为统一的 `title/url/summary/timestamp` 结构，并对缺图条目做文本降级。
- `src/sources/ylms.py`：新增 ylms 混合源，优先使用带 `cf_clearance`、`Referer`、浏览器 `User-Agent` 的 HTML 直连抓取 `https://blog.reimu.net/`，按 WordPress 首页结构提取统一 `title/url/summary/timestamp`；当直连失败、缺失 cookie 或命中 Cloudflare 挑战页时，自动回滚到 `http://reimu.bgzo.cc` RSS。
- `src/sync.py`：通过 `add_sources(rss_content_dict, 'Resources', get_kungal_posts(), 'kungal')` 将 KUNGal 接入 `Resources` 聚合链，不新增 archive 顶层分类。
- `src/sync.py`：通过 `add_sources(rss_content_dict, 'Resources', get_asmr_one_posts(), 'asmr-one')` 将 ASMR.one 接入 `Resources` 聚合链，并输出 `api/feeds/asmr-one.xml`。
- `src/sync.py`：通过 `add_sources(rss_content_dict, 'Resources', get_nysoure_posts(), 'nysoure')` 将 nysoure 接入 `Resources` 聚合链，并输出 `api/feeds/nysoure.xml`。
- `src/sync.py`：通过 `add_sources(rss_content_dict, 'Resources', get_ylms_posts(), 'ylms')` 将 ylms 接入 `Resources` 聚合链；在 ylms 注入前用 `dedupe_entries_by_url()` 做最小 URL 去重，避免与当前 `Resources` 已有条目重复。
- `tests/test_kungal.py`：负责离线验证标题优先级、summary 拼接、单条映射与列表抓取行为；`debug/kungal.json` 作为固定回放样本。
- `tests/test_asmr_one.py`：负责离线验证 ASMR.one 的日期解析、summary 拼接、NSFW 过滤、单条映射与 monkeypatch 抓取行为；`debug/asmr_one.json` 作为固定回放样本。
- `tests/test_nysoure.py`：负责离线验证 nysoure 的时间解析、summary 拼接、单条映射与 monkeypatch 抓取行为；`debug/nysoure.json` 作为固定回放样本。
- `tests/test_ylms.py`：负责离线验证 ylms 的 HTML 解析、Cloudflare 误判控制、请求异常回滚、无 cookie 回滚与 RSS 回滚映射；[docs/implement-plans/ylms.html](/home/bgzo/workspaces/hentai/docs/implement-plans/ylms.html) 与 [debug/ylms-rss.xml](/home/bgzo/workspaces/hentai/debug/ylms-rss.xml) 作为固定样本。
