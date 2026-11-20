---
name: obsidian-vault-maintenance
description: "Obsidian 笔记库体检与修复：目录结构核实、.gitignore 静默失效排查、obsidian-git 同步行为、插件受限模式、leveldb 修复、git filter-repo 瘦身纪律。TRIGGER：用户提到 Obsidian 库/笔记库/vault 的同步、备份、插件不加载、git 异常、仓库瘦身、目录整理、体检。DO-NOT-TRIGGER：纯 Markdown 文件读写（直接读写即可）、非 Obsidian 的 git 操作。"
metadata:
  version: "1.0.0"
  category: knowledge-management
  source: "由 41c34c16 agent 记忆提炼（obsidian 6 条 + git 4 条，2026-09-08 至 09-11）"
---

# Obsidian 库维护

> 这个库踩过的坑集中在**静默失效**：不报错，但事情没做成。

---

## Phase 0：动手前必须 `ls` 核实真实结构（🛑 STOP）

🛑 **禁止基于上一轮的结论或记忆中的结构直接动手。**

> 2026-09-11 实测：用户已把 `notes/` `muban/` `panel/` 从 `vault/` 移回库根，**推翻了上一轮方案**。若不先 `ls` 就按旧结构操作，会写错位置。

```bash
ls -la <vault_root>
find <vault_root> -maxdepth 2 -type d | sort
```

🔴 **先确认"库根在哪、哪些目录在库根、哪些在 vault/ 下"**，再谈方案。

---

## 体检清单（按静默失效风险排序）

### 1 · `.gitignore` 静默吃掉备份（最高危）

**症状**：备份看起来在跑，实际什么都没提交，**可以持续 40 天无人察觉**。

**根因**：`**/vault/` 这类通配规则把整个目录忽略了。

```bash
git check-ignore -v <path>        # 逐个确认关键目录是否被忽略
git status --ignored --short | head -30
```

🛑 **体检必须显式检查 `git check-ignore`**，不能只看 `git status` 干净就以为没事。

### 2 · obsidian-git 的推送行为

⚠️ **常见误解**：`autoPushInterval = 0` **不代表不推送**——`commitAndSync` 内部包含 push。（2026-09-11 自我纠正）

**核实方式**：查插件的**设置项语义**，不要按参数名猜。

### 3 · 插件受限模式静默失效

**症状**：所有插件都不加载，**无任何提示**。

**根因**：leveldb 中受限模式键为 `false`。

**修复**：
1. 🛑 **完全退出 Obsidian**（不是关窗口）
2. 再编辑 leveldb 对应键
3. 重启验证

⚠️ Obsidian 运行时编辑 leveldb 会被覆盖。

### 4 · git filter-repo 瘦身纪律

🛑 **重写历史后做 `checkout` 会删除"已跟踪但被移除"的文件。** 实测一次丢了 24M zip / 7.7M docx / 4.8M fa，只能逐文件还原。

**纪律**：
1. 瘦身前**全量物理备份**（不要只靠 git）
2. 记下文件清单（`git ls-files` 快照）
3. 重写后**逐项比对**再 checkout
4. 恢复时**逐文件**做，不用通配符

### 5 · 插件与字体

- 插件安装后需确认**实际加载**（不是"已启用"字样）
- VSCode 侧：Profile 隔离、latex-workshop 用**绝对路径**、字体 JetBrainsMono

---

## 已知坑

| # | 坑 | 修正 |
|---|---|---|
| 1 | `**/vault/` 忽略规则致备份静默失效 | `git check-ignore -v` 显式核查 |
| 2 | 凭上一轮结论操作目录 | 动手前 `ls` 核实 |
| 3 | filter-repo 后 checkout 删文件 | 先全量备份 + 逐项比对 |
| 4 | 受限模式无提示 | 查 leveldb 键值 |
| 5 | 运行时编辑 leveldb | 先完全退出 Obsidian |
| 6 | 把 `autoPushInterval=0` 当不推送 | 查设置语义，别猜 |
| 7 | 颜色/批量替换漏大小写变体 | 一次替换曾漏 31 处 → 替换后**复核计数** |

---

## 反例黑名单

1. ❌ 不 `ls` 就按记忆中的结构动手
2. ❌ 只看 `git status` 干净就判定备份正常
3. ❌ 瘦身前不做全量物理备份
4. ❌ 恢复文件用通配符（可能误删/漏删）
5. ❌ 凭参数名推断插件行为

---

## 交付去向

- 体检报告与恢复清单 → `projects/YYYYMMDD_obsidian_check/output/`
- 一次性修复记录 → `mcp__agent-memory__memory` → `append`
- 长期有效的配置事实（库根路径、托管平台）→ `FACT.md`
