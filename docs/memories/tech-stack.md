# 技术栈选择与规范

1. 技术栈保持最简单、最健壮；允许脚本语言（如 Python、shell），但需保证效率、可读、可维护与可追溯。
2. 注重模块化（多文件），禁止单体巨文件（monolith）。
3. 写任何代码前，必须完整阅读设计文档 `docs/memories/design.md`、项目架构 `docs/memories/architecture.md`（以及根目录 `AGENTS.md`）。
4. 任何代码必须包含单元测试，覆盖率尽量达到 100%（离线 fixture 见 `debug/`）。
5. 每完成一个重大功能或里程碑后，必须更新 `docs/memories/architecture.md` 中的架构设计文档。
6. 产出必须落地到项目内，保证日后可追溯（严格禁止在 `/tmp` 目录黑箱操作）。
