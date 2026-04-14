# research-assist

面向**科研检索、论文对比、idea 发散与结论核验**的统一 Claude Code skill。

English version: [`README.en.md`](./README.en.md)

## 一眼看懂

`research-assist` 不是单纯的“搜论文”工具，而是一套**证据优先**的科研工作流。

它把研究任务统一成四类：

| 模式 | 解决的问题 | 典型输出 |
| --- | --- | --- |
| `paper-search` | 找论文、综述、benchmark、项目页、代码 | 代表论文清单、来源链接、补充资源 |
| `research-think` | 发散科研 idea、拆分研究方向、规划下一轮检索 | 候选方向、open problems、next queries |
| `paper-compare` | 比较不同方法、设定、数据集、指标与结论 | 差异点、优缺点、分歧来源 |
| `claim-verify` | 核验某个说法是否可信 | supported / partial / unverified |

## 核心价值

- **统一入口**：搜索、对比、思考、核验不再分散在多个 skill
- **证据优先**：尽量让结论绑定 URL，而不是只给口头总结
- **双通道互补**：搜索通道负责证据，Grok 通道负责综合与补漏
- **受限站点可处理**：必要时可配合 Playwright 补抓 IEEE / ACM / Springer / ScienceDirect

## 工作方式

### 1. 搜索证据通道
负责：
- 用 Exa / Tavily / WebSearch 发现来源
- 以 URL 为中心组织证据
- 去重、聚合、排序

### 2. Grok 综合通道
负责：
- query expansion
- claims / disagreements / next_queries
- 方法对比、方向归纳、反证线索补充

## 你需要自行配置的内容

这个仓库**不会**自带可直接使用的密钥、登录态或远程服务。若要启用增强能力，需要你自己准备：

### 必需
- `EXA_API_KEY`
- `TAVILY_API_KEY`

### 若要启用 Grok 综合能力
- `GROK_BRIDGE_BASE_URL`
- `GROK_BRIDGE_API_KEY`
- `GROK_BRIDGE_MODEL`（建议 `auto`）

### 若要启用受限站点补抓
- 本地可用的 Playwright 浏览器环境
- 你自己的 IEEE / ACM / Springer / ScienceDirect 登录态（按需）

### 建议
- `python3`
- 由 `templates/research.env.example` 复制出的私有配置文件，例如 `templates/research.local.env`

## Grok API 在本项目中的来源

本项目**不是直接调用原生官方 Grok API**，而是通过 **Grok2API** 获取 Grok 能力。

参考实现：
- `https://github.com/chenyme/grok2api`

这意味着：
- 你需要自行部署或提供一个 Grok2API 服务
- `research-assist` 通过 OpenAI 风格兼容接口访问它
- 主要使用的接口是：
  - `GET /v1/models`
  - `POST /v1/chat/completions`

如果你没有部署 Grok2API：
- Exa / Tavily / WebSearch / WebFetch / Playwright 仍可继续使用
- 但 Grok 相关模式不会生效

## 3 分钟上手

### 1) 复制配置模板

```bash
cp "research-assist/templates/research.env.example" "research-assist/templates/research.local.env"
```

### 2) 填写自己的配置

主要变量：
- `EXA_API_KEY`
- `TAVILY_API_KEY`
- `GROK_BRIDGE_BASE_URL`
- `GROK_BRIDGE_API_KEY`
- `GROK_BRIDGE_MODEL=auto`

### 3) 运行一次聚合

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --query "multimodal retrieval augmented generation survey" \
  --max-results 5
```

## 常用示例

### 查看 CLI 帮助

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" --help
```

### idea 发散

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --mode think-idea \
  --query "efficient multimodal rag for long documents" \
  --max-results 5
```

### 方法对比

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --mode think-compare \
  --query "AAA interpolation for electromagnetics" \
  --compare-target "vector fitting" \
  --max-results 5
```

### 结论核验

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --mode think-verify \
  --query "multimodal RAG reliability" \
  --max-results 5
```

## 输出重点

后端采用 evidence-first schema，常见字段包括：

- `results`
- `lanes.search_lane.evidence`
- `lanes.search_lane.playwright_hints`
- `lanes.grok_lane.claims`
- `synthesis.validated_claims`
- `synthesis.disagreements`
- `synthesis.next_queries`

## 仓库结构

```text
research-assist/
├─ LICENSE
├─ SKILL.md
├─ README.md
├─ README.en.md
├─ README.zh-CN.md
├─ .gitignore
├─ scripts/
│  └─ research_aggregate.py
├─ templates/
│  ├─ research.env.example
│  ├─ api-config-template.md
│  └─ search_aggregator_template.py
└─ references/
   ├─ api-setup.md
   ├─ dedup-rules.md
   ├─ grok-bridge.md
   ├─ login-fallback.md
   ├─ research-report-template.md
   └─ source-priority.md
```

## 建议发布哪些文件

建议发布：
- `research-assist/README.md`
- `research-assist/README.en.md`
- `research-assist/README.zh-CN.md`
- `research-assist/.gitignore`
- `research-assist/LICENSE`
- `research-assist/SKILL.md`
- `research-assist/scripts/research_aggregate.py`
- `research-assist/templates/research.env.example`
- `research-assist/templates/api-config-template.md`
- `research-assist/templates/search_aggregator_template.py`
- `research-assist/references/api-setup.md`
- `research-assist/references/dedup-rules.md`
- `research-assist/references/grok-bridge.md`
- `research-assist/references/login-fallback.md`
- `research-assist/references/research-report-template.md`
- `research-assist/references/source-priority.md`

不要发布：
- `research-assist/templates/research.local.env`

## 进一步说明

详见：
- `references/api-setup.md`
- `references/grok-bridge.md`
- `references/dedup-rules.md`
- `references/login-fallback.md`
- `references/source-priority.md`
- `references/research-report-template.md`

## 一句话总结

> 把“搜索来源、组织证据、比较方法、扩展思路、核验结论、处理受限站点”收敛为一个统一、可复用、可发布的科研 skill。
