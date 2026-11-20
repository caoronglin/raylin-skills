# Cherry Custom Skills

五个自建的 Agent 技能（[Cherry Studio](https://cherry-ai.com/) / Claude Agent Skills 格式），
从真实工作流里提炼出来的——不是通用模板，每条规则背后都有踩过的坑。

## 技能列表

| 技能 | 用途 | 提炼自 |
|---|---|---|
| **maize-gwas-ewas-annotation** | 玉米 GWAS/EWAS 峰注释与候选基因鉴定全流程：OSCA `.linear` 结果聚类 → 玉米 v5 基因组注释 → 拟南芥同源映射与证据分级 → IGV 可视化 → 可信度门禁 | 2026-08 至 09 的 GWAS/EWAS 批次（含 64 个真实 `.linear` 文件的批量验证） |
| **daily-self-evolution-review** | 每日复盘 SOP：回顾完成 → 提炼可复用模式 → 沉淀策略 → 修正认知偏差 → 挂起项闭环。含「当日无新日志禁止复读」去重规则 | 21 条复盘记录 |
| **docx-report-delivery** | 中文公文/报告 DOCX 交付：以真实模板为基底重建文档、自动编号跑偏修复、调研报告多轮迭代、配图批量筛选 | 思政报告 / 三下乡 / 调研报告 / 实验报告交付批次 |
| **obsidian-vault-maintenance** | Obsidian 库体检与修复：目录结构核实、`.gitignore` 静默失效排查、obsidian-git 同步行为、插件受限模式、git filter-repo 瘦身纪律 | Obsidian 库维护记录 |
| **cumcm-delivery-gate** | 数学建模竞赛支撑材料打包与多层门禁：交付包结构、SHA256 新鲜度校验、体积硬上限、四问统一重跑、四类门禁校验 | CUMCM 2026 C 题 |

## 每个技能都带「反例黑名单」

这些技能的价值不在正面流程（那部分网上都有），而在**明确写出「不要做什么」**。
例如：

- 玉米基因 ID 的位数（`Zm00001d` + 6 位，不是 8 位）
- 家族判定关键词必须加词边界——裸 `ERF` 会命中 NCBI 里的 "sup**erf**amily protein"
- 表格里 `.gitignore` 静默失效的三种表现
- 门禁脚本「静默跳过」导致的假通过

## 格式

每个目录下是一个 `SKILL.md`，YAML frontmatter 声明 `name` 与 `description`，
其中 `description` 遵循 **TRIGGER / DO-NOT-TRIGGER** 双段式写法：

```yaml
---
name: skill-name
description: "做什么。TRIGGER：什么时候用。DO-NOT-TRIGGER：什么时候不用（以及该走哪个技能）。"
metadata:
  version: "1.0.0"
  category: ...
---
```

`DO-NOT-TRIGGER` 段很关键——它让 Agent 在多个技能重叠时能正确路由，
而不是靠试。

## 安装

将目录复制到你的 skills 目录即可：

```bash
# Cherry Studio
cp -r <skill-name> ~/文档/cherry/Data/Skills/

# Claude Code / 兼容 Agent SDK
cp -r <skill-name> ~/.claude/skills/
```

技能不含任何可执行脚本，纯 Markdown 指令，按需阅读即可。

## 说明

- 已脱敏：本地绝对路径替换为占位符（如 `<项目根>/`）
- 不含任何凭证
- 技能内容针对中文科研 / 办公场景，命令与工具链以 Linux 为准

## 许可

自由取用。若你的场景与某个技能高度重合，建议先读它的「反例黑名单」——那是最省时间的部分。
