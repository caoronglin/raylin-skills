---
name: cumcm-delivery-gate
description: "数学建模竞赛（CUMCM 等）支撑材料打包与多层门禁验证：交付包结构、SHA256 新鲜度校验、体积硬上限、四问统一重跑、测试/图 QA/锚点/链接四类门禁。TRIGGER：用户要重建/打包支撑材料、交付包、验证交付包、跑门禁、统一重跑四问、检查锚点与文档链接、准备数模竞赛提交。DO-NOT-TRIGGER：单个模型的调参（走建模流程）、非竞赛类项目的打包。"
metadata:
  version: "1.0.0"
  category: competition
  source: "由 caf829b8 agent 记忆提炼（CUMCM 2026 C 题，2026-09-11 至 09-13，30 条）"
---

# 数模交付包打包与门禁

> 核心风险不是"算错"，而是**门禁报绿但实际没校验**。

---

## Phase 1：打包交付包

标准顶层结构：

```
交付包/
  1_文件清单.md
  2_代码/
  3_结果/
  4_图表/
  5_数据/
  6_文档/
```

```bash
python3 scripts/pack_delivery.py            # 生成
python3 scripts/pack_delivery.py --verify   # 校验（比对 SHA256）
```

### 硬约束（🔴 CHECKPOINT）

| 项 | 阈值 | 违反后果 |
|---|---|---|
| 包体积 | **20 MB 硬上限** | 脚本退出码 **6**，必须瘦身 |
| 新鲜度 | 所有产物 SHA256 与清单一致 | 不一致即**陈旧包**，禁止提交 |
| 清单项数 | 实测从 49 项演进到 50 项 | 结构变更必须同步更新清单 |

🛑 **`verify_delivery.py` 必须全通过才能交付。**（实测曾跑出 49/49，后扩到 50/50）

---

## Phase 2：四问统一重跑门禁

```bash
export PYTHONPATH=.rlc_deps                      # ← 见坑 #1，漏了会假失败
python3 -m unittest discover -s code/tests       # 实测 122 → 140 OK
pytest code/tests/test_official_export.py        # 18 passed
python3 build_docs.py --check                    # 文档构建一致性
python3 code/check_qa_fw.py                      # 图 QA（逐问）
python3 code/check_qa_q2.py
python3 code/check_qa_q3.py
python3 code/check_qa_q1opt.py
```

门禁四项：**测试 / 图 QA / 锚点 / 文档链接**。

实测基线：锚点 **27/27**、链接 **41 份**、unittest **140 OK**、pytest **18 passed**。

---

## Phase 3：独立审计（subagent 并行）

```text
启动 4 个背景 subagent（Q1—Q4 各一名）
  ├─ 只读范围限定（各自限定到本问目录）
  ├─ 写入所有权分离（避免互踩）
  └─ 产出 problems/qN/docs/模型说明与模型对比.md
```

配套守护脚本（实测如 `rlc_q2_audit_check.py`，196 项）。

🛑 **审计者不得修改被审计对象**——只读 + 独立复算。

---

## 已知坑（全部实测踩过）

| # | 坑 | 表现 | 修正 |
|---|---|---|---|
| 1 | **假失败** | 不 `export PYTHONPATH=.rlc_deps` 跑 unittest，缺 pytest 报 1 ERROR | 跑测试前必 export |
| 2 | **门禁静默跳过** ⚠️最危险 | Q1 锚点因取顶层 `cash_cost_yuan` 而实际被 `if cash1` 跳过，**门禁仍报 17/17** | 门禁必须校验**头条数字**，不能只数条目 |
| 3 | 0 基段号偏移 | 段号 `t` 是 0 基，写成 `t+1` 致指定时段整体偏移一段 | 确认基址再写 |
| 4 | 变量覆盖 | 生成器里 `for i in range(...)` 覆盖外层 `enumerate` 的 `i`，标题编成 2.112/2.132/2.140 | 换变量名 |
| 5 | 反引号内路径被判死链 | Markdown 反引号里写 `problems/…json::字段` 被链接检查判失效（6 条） | 死链检查器要排除行内代码 |
| 6 | 验证记录自指死循环 | 验证记录装进交付包 → 校验自己 → 无限自指 | **验证记录不进包** |
| 7 | 库存口径污染 | 完美信息臂每天重置 6000 kWh 库存，含 747,938.39 元库存补贴 | 口径定义写进模型说明 |
| 8 | 符号/语义错位 | 场景残差符号写反致计划过度购电 +15%；末端约束语义错位 | 残差符号与约束语义单测覆盖 |
| 9 | 长跑 pipe 给 tail | 无回显被误判卡死 | **实时回显、分阶段执行** |
| 10 | "独立复算"陷阱 | 对本就不唯一的分解（光伏充电/电网充电拆分）写独立复算 | 避开非唯一分解 |
| 11 | 磁盘句柄 | `localsearch-3.service` 持有 995M 已删除句柄 | `systemctl --user restart` |
| 12 | 未核 mtime 就删 | 删了并行会话的 `/tmp/q3deps` 工作目录 | 删前核 mtime + 属主 |
| 13 | `blkid` 无 root 静默失败 | 返回空字符串，`sed` 静默不匹配 | 检查命令退出码与输出非空 |

---

## 反例黑名单

1. ❌ 门禁全绿就认为数据正确（坑 #2 的教训：条目数对不代表内容被校验）
2. ❌ 跳过 `export PYTHONPATH` 后把 ERROR 当真实缺陷
3. ❌ 把验证记录打进交付包（自指）
4. ❌ 体积超 20MB 仍尝试提交
5. ❌ 审计 subagent 有写权限
6. ❌ 交付"陈旧包"（SHA256 未重新校验）
7. ❌ 用 `tail` 跑长任务然后判断卡死

---

## 交付去向

- 交付包 → 项目 `output/`
- 打包脚本 → 项目 `scripts/`
- 赛事合规事项（如 2026 新规的 AI 工具使用声明、`AI工具使用详情.pdf`、身份净化）→ 单列文档，🛑 **提交前必须核对当届规则原文**
