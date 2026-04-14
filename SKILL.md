---
name: research-assist
description: 面向科研检索、论文对比、idea 发散与结论核验的统一核心 skill。通过“搜索证据通道 + Grok 综合通道”组织研究流程，并在必要时使用 Playwright 处理受限学术站点。
allowed-tools: WebFetch WebSearch Bash(playwright-cli:*) Bash(curl:*) Bash(python:*) Bash(python3:*)
---

# Research Assist

这个目录现在应被视为一个**统一核心 research skill 项目**，对外定位统一使用 **`research-assist`**：它既负责论文发现，也负责科研思考、方法对比、claim 核验与受限站点补抓。

这个 skill 的目标不是单纯“找几个论文链接”，而是形成一套可复查、可扩展、可复用的科研辅助流程。

它统一覆盖四类任务：

1. **paper-search**：找论文、综述、项目页、代码、作者页
2. **research-think**：发散科研 idea、列出研究假设、形成下一轮查询计划
3. **paper-compare**：对比方法、数据集、指标、结论与局限
4. **claim-verify**：核验某个说法是否被公开来源支持，识别证据冲突

如果以后要做更细的 skill（例如 `research-think`），它们应只是这个 skill 的**薄封装入口**，不应各自维护独立抓取和去重逻辑。

---

## 项目定位与命名

- **推荐发布名**：`research-assist`
- **当前目录名**：`research-assist`
- **推荐理解方式**：skill 名称、目录名和简介保持一致，统一按 `research-assist` 对外表述

如果以后新增 `research-think`，应只作为 `research-assist` 的薄封装入口，而不是新的独立核心。

---

## 使用前提（需要用户自行配置）

本 skill 不自带可用的密钥、登录态或远程服务。若要启用完整能力，用户需要自行准备：

- `EXA_API_KEY`
- `TAVILY_API_KEY`
- `GROK_BRIDGE_BASE_URL`
- `GROK_BRIDGE_API_KEY`
- `GROK_BRIDGE_MODEL`
- 按需可用的 Playwright 浏览器环境
- 按需可用的 IEEE / ACM / Springer / ScienceDirect 登录态

其中 Grok 相关能力默认按 **Grok2API** 兼容桥接层来理解，而不是直接使用原生官方 Grok API。

---

## 设计目标

- **统一底层能力**：搜索、去重、证据绑定、Grok 综合、Playwright fallback 只维护一套
- **证据优先**：有效信息必须尽量绑定 URL
- **双通道互补**：模型内置 web 能力与 Grok 形成对比和补充，而不是互相替代
- **可扩展**：后续可接更多 provider，而不改上层工作流
- **可发布**：skill 本身应自解释，脚本和参考文档是增强项，不是阅读门槛

---

## 适用场景

当用户提出以下请求时，使用本 skill：

- “帮我找这个方向的代表论文 / survey / benchmark”
- “总结某方向近两年的研究脉络”
- “对比 AAA、VF 和其他插值方法的差异”
- “围绕这个问题发散几个可做的科研 idea”
- “验证某篇论文/某个 claim 是否可信，有没有反例”
- “从 IEEE / ACM 页面补抓摘要、DOI、作者、下载入口”

---

## 核心原则

### 1. 统一双通道

本 skill 总是把研究过程拆成两条通道：

#### A. 搜索通道（evidence lane）
负责：
- Exa / Tavily / WebSearch 发现候选来源
- 提取公开页面与论文落地页
- 去重、聚合、排序
- 形成可复查的 evidence 列表

这一通道的输出重点是：
- `title`
- `url`
- `canonical_url`
- `source`
- `snippet`
- `doi/arxiv_id`（如可得）

#### B. Grok 通道（synthesis lane）
负责：
- query expansion
- 子主题拆分
- 生成 claims / disagreements / next_queries
- 对方向做发散、比较与综合

这一通道**不能单独充当事实来源**。它的价值是：
- 补漏
- 形成候选假设
- 主动发现分歧与反证方向

### 2. URL 证据优先

- 结论、对比、推荐尽量都要绑定 URL
- 无 URL 的内容最多只能作为“待核实线索”
- 最终报告里，事实与建议必须区分

### 3. 登录态站点走 fallback

对于 IEEE / ACM / Springer / ScienceDirect 等：
- 先看公开落地页
- 公开信息不足时，再走 Playwright
- Playwright 抓到的内容要明确标记为登录态来源

### 4. 不把搜索排序当学术结论

搜索结果只提供候选线索，不等于：
- 学术影响力排序
- 方法优劣结论
- 实验真实性证明

---

## 推荐工作流

### 模式一：paper-search
适用于：论文发现、survey、benchmark、代码资源整理。

流程：
1. 将问题转成 5–8 个英文子查询
2. 通过 Exa / Tavily / WebSearch 收集候选来源
3. 对候选结果做 URL、标题、DOI、arXiv 去重
4. 对高价值页面进一步抓摘要/元数据
5. 输出核心论文、综述、项目页、代码仓库

### 模式二：research-think
适用于：科研 idea 发散与方向探索。

流程：
1. 用搜索通道收集近期工作和代表路线
2. 用 Grok 通道提出候选 claims / opportunities / open problems
3. 用公开 evidence 交叉验证
4. 输出：
   - 值得做的方向
   - 分歧点
   - 下一轮检索词

### 模式三：paper-compare
适用于：方法对比、结果对比、定位差异。

流程：
1. 明确 compare target（例如 A vs B）
2. 收集两侧的正式论文页、摘要、项目页、代码页
3. 按方法、假设、数据集、指标、优点、局限做结构化比较
4. 若搜索通道与 Grok 通道不一致，显式列出 disagreement

### 模式四：claim-verify
适用于：核验说法、找反例、评估可靠性。

流程：
1. 将用户 claim 拆为若干可验证子命题
2. 搜索正式来源和公开权威页面
3. 用 Grok 通道补充反证线索和歧义点
4. 输出 supported / partial / unverified 结论

---

## 推荐输出契约

默认输出应尽量包含以下结构：

```json
{
  "mode": "paper-search | research-think | paper-compare | claim-verify",
  "query": "...",
  "evidence": [
    {
      "title": "...",
      "url": "https://...",
      "canonical_url": "https://...",
      "source": "exa | tavily | web | publisher | arxiv | openreview | github",
      "snippet": "..."
    }
  ],
  "claims": [
    {
      "claim": "...",
      "confidence": "low | medium | high",
      "support": "supported | partial | unverified",
      "evidence_urls": ["https://..."],
      "note": "..."
    }
  ],
  "disagreements": [
    {
      "topic": "...",
      "lane_a": "...",
      "lane_b": "...",
      "status": "active | unresolved | weakly_supported"
    }
  ],
  "next_queries": ["..."],
  "playwright_hints": [
    {
      "url": "https://...",
      "reason": "likely_login_or_paywall"
    }
  ]
}
```

约束：
- `evidence.url` 必须是有效 `http/https`
- 无 URL 的 evidence 不进入最终 evidence 列表
- claim 若无证据，必须标记为 `unverified`

---

## 信息源优先级

默认优先级：

1. DOI / 出版方正式页面
2. arXiv / OpenReview / 会议官网 / ACL Anthology / CVF
3. 作者主页 / 项目主页 / 官方 GitHub
4. Semantic Scholar / DBLP / Crossref 等索引页
5. 高质量综述页 / 教程页 / 技术博客
6. 普通转载内容

如果存在冲突：
- 以正式论文页、出版方页、官方项目页优先
- Grok 总结不能覆盖正式来源

---

## Playwright 使用规则

以下情况应考虑触发 Playwright：
- 目标页面是 IEEE / ACM / Springer / ScienceDirect 等常见受限域名
- 搜索结果只有标题或摘要片段，没有足够元信息
- 用户明确说自己有登录态

Playwright 的目标优先级：
1. 抓论文落地页
2. 抓标题、作者、摘要、DOI、venue、年份
3. 识别 PDF / 导出 / 引用入口
4. 只在必要时继续点击全文入口

不要：
- 先猜 PDF 直链
- 把登录态页面抓取当成默认第一步

---

## 与当前脚本的关系

如果仓库中存在：
- `scripts/research_aggregate.py`

则它是本 skill 的本地增强后端，可用于：
- Exa / Tavily 聚合
- Grok query expansion
- Grok think / compare / verify
- evidence 校验
- Playwright hint 生成

但**脚本不是 skill 的定义本体**。skill 文档本身应足以说明：
- 何时使用
- 如何组织证据
- 何时调用 Playwright
- 如何处理分歧

---

## 发布与复用建议

如果以后拆分外层入口，推荐这样设计：

- `research-assist`：唯一核心 skill
- `research-think`：薄封装，默认偏 research-think / paper-compare / claim-verify

这些外层 skill 不应重复定义：
- provider 逻辑
- evidence schema
- 去重规则
- Playwright fallback 规则

---

## 严格限制

- 不伪造论文、作者、项目、DOI
- 不把无 URL 的模型总结当作事实
- 不把博客转载当论文原文
- 不把同名/近似标题论文错误合并
- 不把搜索相关度当成学术影响力
- 登录态页面信息必须明确说明来源性质
- 若只能看到摘要，看不到全文，要明确说明

---

## 推荐最小发布内容

如果你要发布这个 skill，最少建议打包：

1. `research-assist/SKILL.md`
2. `research-assist/scripts/research_aggregate.py`
3. `research-assist/templates/research.env.example`
4. `research-assist/references/api-setup.md`
5. `research-assist/references/dedup-rules.md`
6. `research-assist/references/login-fallback.md`
7. `research-assist/references/source-priority.md`
8. `research-assist/references/research-report-template.md`

其中：
- **必须**：`SKILL.md`
- **强烈建议**：脚本、env 模板、api/setup、去重与 fallback 规则
- **可选**：其余参考文档

如果你只想发布“一个最小可用 skill 包”，至少带：
- `SKILL.md`
- `scripts/research_aggregate.py`
- `templates/research.env.example`
- `references/api-setup.md`

---

## 对 GitHub 上同类 skill/模板的对比后建议

综合同类 Claude Code skill / prompt-style research helpers，常见优点是：
- 说明清楚“何时用”
- 给出明确输出格式
- 强调 sources / citations
- 把浏览器抓取当作 fallback，而非默认流程

你这个 skill 现在最值得保留和强化的部分是：
- **双通道思路**：搜索通道 + Grok 通道
- **URL 证据约束**
- **Playwright hint 机制**
- **compare / verify 模式化输出**

最需要避免的部分是：
- 把它继续写成“只搜论文”的 skill
- 让不同 skill 各自维护重复逻辑
- 让 Grok 只做 query expansion 而不参与分歧分析

因此，发布时建议：
- 名称直接用统一核心名 `research-assist`
- 不再把“search”和“think”拆成两个并列重型 skill
- 若要保留旧名，只做薄封装别名
