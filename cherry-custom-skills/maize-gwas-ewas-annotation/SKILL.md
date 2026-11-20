---
name: maize-gwas-ewas-annotation
description: "玉米 GWAS/EWAS 峰注释与候选基因鉴定全流程：从 OSCA .linear 结果聚类显著峰 → 玉米 v5 基因组基因注释 → 拟南芥同源映射与证据分级 → IGV 可视化 → 可信度门禁。含 P 值列位置、坐标换算、家族关键词词边界等已踩实的坑清单。TRIGGER：用户给出 .linear/.assoc/GWAS 结果文件、要求找显著峰/候选基因/曼哈顿峰注释/EWAS 分析、玉米基因 ID（Zm00001eb/Zm00001d/GRMZM2G）注释、QTL/峰-基因映射、拟南芥同源比对、IGV 峰图。DO-NOT-TRIGGER：只做通用统计/绘图、非玉米物种的全新组装注释、单纯文献检索（走 academic-researcher）。"
metadata:
  version: "1.0.0"
  category: bioinformatics
  species: maize
  source: "由 2026-08 至 2026-09 的 GWAS/EWAS 批次记忆提炼（gwas 标签 24 条）；脚本来源 projects/20260815_gwas_peak_annotation/"
---

# 玉米 GWAS/EWAS 峰注释与候选基因鉴定

> 全流程可复现流水线。**零第三方 Python 依赖**（仅标准库），外部依赖只有 DIAMOND 与参考基因组文件。

---

## 适用 / 不适用

| 适用 | 不适用 |
|---|---|
| OSCA `.linear` EWAS 结果、`.assoc`、任何 `Chr/Pos/P` 三列表 | 只用通用统计脚本画个图 |
| 玉米 v4/v5 基因 ID 注释、峰内基因筛选 | 人类/小鼠等非玉米物种注释 |
| 拟南芥同源映射、QTL 证据分级 | 全新基因组从头注释（走 BRAKER/AUGUSTUS） |
| IGV 峰区可视化截图 | 单纯查文献（走 `academic-researcher`） |

---

## Phase 0：输入校验（🛑 STOP 门）

**读入任何结果文件前，先打印表头并确认列序。这不是可选项。**

```python
# 必须先做
with open(f) as fh:
    header = fh.readline().rstrip("\n").split("\t")
print(header)          # 逐列核对
print(len(header))
```

**OSCA `.linear` 列序（已实测）**：

```
Chr  Probe  bp  Gene  Orientation  b  se  p  NMISS
 0     1     2    3        4       5   6  7    8
```

🛑 **P 值 = 倒数第二列**（`se` 之后、`NMISS` 之前）。**曾把 `se` 列当 P 值扫，导致误判"无显著位点"——本流水线最贵的一次错误。**

**Probe 列语义**：10kb 窗口命名，形如 `chr1-21000-22000`；`bp` 列是**窗口起点**，不是峰值。**峰中心 = 窗口中点**（`bp + 5000`）。

---

## Phase 1：显著峰聚类

```bash
python3 work/gwas_peak_annotator.py \
  --input  <trait>.linear \
  --outdir output/ \
  --p-threshold 1e-10 \
  --max-gap 15000 \
  --min-probes 3
```

规则（均已实测校准）：

1. `p < --p-threshold` 的探针为显著探针。
2. 按 `--max-gap`（默认 15kb）聚簇。
3. **夹在两个显著探针之间的非显著探针不阻断聚类**——早期实现误当断层，是第二个已知 bug。
4. 簇内显著探针数 `< --min-probes`（默认 3）则丢弃。
5. `--top-n N` 模式：绕过阈值取最显著 N 个探针再合并，用于阈值过严时的探索。

---

## Phase 2：基因注释

### 参考文件（MaizeGDB v5 / NAM-5.0）

| 文件 | 路径要点 |
|---|---|
| GFF3 | `..._Zm00001eb.1.gff3`（152MB，**无 .gz 版**）；gene 行属性仅 `ID`/`biotype`/`logic_name`，**无功能描述** |
| 蛋白 FASTA | 头格式 `Zm00001eb..._P001`（P 蛋白与 T 转录本同号）；mRNA 行有 `canonical_transcript=1` |
| `Zm00001eb.1.fulldata.txt.gz` | 第 11 列 = RefSeq LOC 编号或旧命名别名（**非 LOC 值不能查 NCBI**）；第 13 列 = GO 词条（含名称） |
| `interproscan.tsv.gz` | 以**转录本**为键；`f[5]`=Pfam 描述、`f[11]`=IPR、`f[12]`=IPR 描述 |

### 注释三源组合

1. **本地**：GO（fulldata 第 13 列）+ Pfam/IPR（interproscan）
2. **NCBI E-utilities**：用 LOC 编号查 Gene db，批量 ≤200/请求，无 key 限速 ~3 req/s
3. **Ensembl Plants REST**：**不支持 v5 `Zm00001eb` ID**，仅 v4 风格（`Zm00001d`/`GRMZM2G`）可用；脚本应**自动跳过并记录**，不要静默失败

### 同源映射（DIAMOND 2.2.5）

```bash
diamond makedb --in <ref>.protein.fa -d ref
diamond blastp -d ref -q <query>.fa --outfmt 6 -o out.tsv --threads 16
```

**拟南芥 TAIR10**（`GCF_000001735.4`）要点：CDS 行含 `protein_id`→`locus_tag`/`product`/`GeneID` 映射；**`product`/`symbol` 字段含 URL 编码（`%3B`=分号）需 `unquote`**；基因符号在 `gene` 行 `Name=`。

### 证据分级（拟南芥同源双选，2026-08-19 批次方法）

| 层级 | 判据 | 说明 |
|---|---|---|
| `L1_direct_hit` | 标题直接含该基因 symbol / AGI | 最强 |
| `L2_func_keyword` | 标题含功能关键词 | 中 |
| `L3_trait_match` | 仅性状词匹配 | 弱 |
| `L4_best_fallback` | 泛功能基因取最佳 | 需标注 |

---

## Phase 3：可视化（IGV）

```bash
python3 work/igv_report.py --regions windows.bed --dl-ref --serve
```

- 从 GFF3 提取窗口内基因 → refbed（12 列 BED，含外显子块）→ 内嵌 IGV.js 的 HTML
- 内置 stdlib HTTP 服务器支持 **HTTP Range + CORS**（实测 206 Partial Content）
- 截图：页面按钮 / `--auto-screenshot` / `--puppeteer`
- 参数全可调：`--flank` `--width` `--height` `--track-height` `--color` `--display-mode` `--max-regions` `--wait-ms`

⚠️ **MaizeGDB 不返回 CORS 头**（`curl -sI` 无 `access-control-allow-origin`）→ 浏览器跨域加载远程 FASTA 会被拦，**必须 `--dl-ref` 下载参考到本地**。
⚠️ **假版本号陷阱**：`igv@2.17.4` 是假版本，全 CDN 404。用 jsdelivr `https://cdn.jsdelivr.net/npm/igv@<真实版本>/dist/igv.min.js`，改版本前先 curl 验证。

---

## Phase 4：可信度门禁（🔴 CHECKPOINT）

⚠️ **在把结果称为"显著"之前必须过这道门。**（2026-08-17 独立审计结论）

| 检查 | 门槛 | 不过怎么办 |
|---|---|---|
| lambda GC | 应接近 1.0 | 实测 64 表型中位 **1.234** → 存在膨胀，必须讨论 |
| QQ 图 / 置换检验 | 必须做 | 缺失则降级为"探索性" |
| 多重检验 | 单表型 Bonferroni **或** 全局 Bonferroni | 实测 95 峰过单表型、仅 **23** 峰过全局 64 扫描 |
| 参数敏感性 | 改 `min-probes`/`max-gap` 看峰是否稳定 | 实测 418 峰对二者**高度敏感** |
| `p < 1e-5` | **仅探索性**，不得写成显著 | 换更严阈值或标注 |

🔴 **必须区分**：发布包内部的坐标/CDS 一致性 ≠ 生物学因果验证。**前者过不等于后者过**，不得混为一谈。

🛑 **禁止**：把未经 QQ/lambda/多重检验门禁的结果包装为"最终版"。

---

## 已知坑清单（全部为实测踩过的）

| # | 坑 | 修正 |
|---|---|---|
| 1 | `.linear` 的 P 值列位置 | **倒数第二列**，不是 `se` 列 |
| 2 | 家族关键词裸匹配 | `ERF` 会命中 "sup**erf**amily protein"（Kinesin/Exonuclease 被误判为 AP2/ERF）；裸 `PIN` 命中 PINHEAD；裸 `ARF` 命中 ARF-GAP。**必须加 `\b` 词边界**，或只认 "auxin response factor\|ARF DNA-binding" |
| 3 | 坐标换算 | peak 中心 bp↔Mb 换算错 + chr 未匹配 → 全表"无候选基因"。**修正为 ±1.5Mb 且同 chr** |
| 4 | 回调引用全局变量 | `annotate` 回调引用全局 `pts_genes` 致分图映射错乱 → **改显式传参** |
| 5 | 像素统计验证 | 深色像素统计在布局变化下不可靠 → **改 matplotlib text 对象计数** |
| 6 | `pkill -f` 自杀 | 会匹配自身命令行导致误杀当前 shell → **用 `ss -tlnp` 找端口 PID 再 kill** |
| 7 | 运行长任务 | 输出管道给 `tail` 导致无回显被误判卡死 → **实时回显、分阶段执行** |

---

## 输出约定

- 双文件拆分，**互斥不重复**：`{名}.peaks_genes_{小窗口}bp.txt`（峰中心 ±100bp）与 `{名}.peaks_genes_{大窗口}kb.txt`（±100kb 内且不在小窗口的其余基因）
- 辅助开关：`--verify-gene`（确定性验证基因存在性 + 是否落入峰窗口）、`--bed-out`（导出 `windows.bed`/`genes.bed`）、`--outdir`
- 交付目录遵循 `projects/YYYYMMDD_<slug>/`：`input/` 原始 `.linear`、`work/` 脚本、`output/` 结果、`notes/` 日志

---

## 反例黑名单

1. ❌ 直接读 `.linear` 不看表头就取 P 值 → 列错位，全盘皆错
2. ❌ 把"发布包自洽"说成"生物学验证通过"
3. ❌ 用论文标题命中当同源功能证据（会误留泛功能基因）
4. ❌ 对泛功能基因（转运蛋白/磷酸酶/微管蛋白）强行给性状特异结论 → 数据没有就该清空并**如实说明**
5. ❌ 保留间接基因不标注（如 CKX4/YUC9 对 TBN 应标"间接"）
6. ❌ 忽略 lambda GC 膨胀仍称显著
7. ❌ DOI 不核 Crossref 就写进结论（同一论文常有标题变体，用 `difflib` ≥0.9 去重）

---

## 参考路径

- 主脚本：`<项目根>/work/gwas_peak_annotator.py`
- IGV 报告：同目录 `work/igv_report.py`
- 已跑通数据：`<EWAS结果目录>/`（64 个 `*.linear`）
- 生物学自检锚点：`35_Cobcolor`（chr1 43.8–47.8Mb 单主效 QTL）、`36_Kernelcolor`（chr9:158.4Mb / chr6:91.6Mb，命中 `y1`→PSY、`wc1`→CCD1）
