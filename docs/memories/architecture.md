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
│   ├── implementation-plans # 项目的实施计划，每次修BUG、新增改能全部记录在这里，包含每个功能的分步指令和验证正确性的测试
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

