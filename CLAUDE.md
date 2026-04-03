# resume-markdown-mcp

## 项目初衷

市面上的简历工具要么是重型 SaaS，要么需要用户手动维护 CSS 和构建流程。这个项目的目标是：让 AI 直接参与简历的撰写、格式转换和导出，用户只需描述自己的经历，AI 负责生成格式规范的 Markdown，并一键导出为 PDF。

核心理念：**简历内容归用户，格式和样式归工具**。

## 设计方向

### MCP 优先

项目以 MCP 服务器为主要接口，CLI 作为辅助工具保留。AI 客户端（Claude Code / Claude Desktop）通过 MCP 协议调用工具，完成"撰写 → 导出"的完整流程。

### CSS 层对用户屏蔽

用户和 AI 只需关注 Markdown 内容。CSS 作为内部实现细节：
- 默认使用内置样式，零配置
- 需要自定义时通过 tool 参数传入（`css_path` 或 `css_content`），不依赖外部文件约定
- AI 可通过 `resume://style` resource 读取默认 CSS，在此基础上帮用户定制

### Tool 双输入模式

`export_resume_pdf` 工具同时支持两种输入，覆盖不同场景：
- `file_path`：用户已有 `.md` 文件时直接传路径，不消耗 token
- `markdown_content`：AI 生成或修改后的内容直接传入

AI 应根据内容是否符合格式规范来决定走哪条路径（见 server.py 中的 tool description）。

## MCP 接口

| 类型 | 名称 | 说明 |
|------|------|------|
| Tool | `export_resume_pdf` | 将 Markdown 简历导出为 PDF |
| Resource | `resume://template` | 内置 Markdown 简历模板，AI 按需读取以了解格式 |
| Resource | `resume://style` | 内置默认 CSS，AI 读取后可帮用户定制样式 |

## Markdown 简历格式约定

本项目依赖以下 Markdown 约定来生成正确样式的 PDF：

```markdown
# 姓名                          ← h1：页面标题 + 姓名显示

- email@example.com             ← h1 后紧跟的列表：联系方式（内联显示）
- 电话
- 城市

一句话简介（可选）               ← 联系方式后的段落：摘要

## 工作经历                     ← h2：章节标题

### <span>职位, 公司</span> <span>2022 – 2025</span>   ← h3 + 两个 span：左右弹性布局

- 成就描述

## 教育背景
## 技能
```

关键：h3 中的两个 `<span>` 标签是必须的，CSS 用 flexbox 实现标题左对齐、日期右对齐。

## 技术栈

- **Python** ≥ 3.12
- **mcp** ≥ 1.27.0（FastMCP）
- **markdown**（python-markdown，带 `smarty` 和 `abbr` 扩展）
- **hatch-vcs**（git tag 动态版本号）
- **headless Chrome / Chromium**（运行时依赖，用于 PDF 渲染）

## 开发命令

```bash
# 安装为本地工具
uv tool install --force --reinstall .

# CLI 测试
resume-markdown init
resume-markdown build resume.md

# MCP server 启动（stdio）
resume-markdown-mcp

# 或通过 uvx 运行（无需预安装）
uvx --from . resume-markdown-mcp
```

## 文件结构

```
src/resume_markdown/
    __init__.py      # 包入口，导出 main 和 mcp_main
    __main__.py      # CLI：init 和 build 命令
    server.py        # MCP 服务器：tool + resources
    converter.py     # 核心转换逻辑：Markdown → HTML → PDF
    resume.css       # 内置默认样式
    resume.md        # 内置简历模板
```
