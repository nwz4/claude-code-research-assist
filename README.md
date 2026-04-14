# research-assist

面向科研检索、论文对比、idea 发散与结论核验的统一 Claude Code skill。

English version: [`README.en.md`](./README.en.md)

## 它能做什么

`research-assist` 是一个统一核心 skill，面向科研工作流，覆盖四类常见任务：

- **paper-search**：发现论文、综述、benchmark、项目页、代码仓库
- **research-think**：发散科研 idea、识别 open problems、规划下一轮检索
- **paper-compare**：对比方法、假设、数据集、指标与结论
- **claim-verify**：核验某个说法是否被支持、部分支持或仍未证实

它采用**双通道工作流**：

### 1. 搜索证据通道
- 用 Exa / Tavily / WebSearch 发现来源
- 以 URL 为中心组织证据
- 做去重、聚合和来源排序

### 2. Grok 综合通道
- 做 query expansion
- 产出 claims / disagreements / next_queries
- 做对比、归纳和假设生成

当公开页面信息不足时，它还可以给出 **Playwright fallback** 提示，用于处理 IEEE、ACM、Springer、ScienceDirect 等受限学术站点。

## 你需要自行配置的内容

这个仓库**不会**自带可直接使用的密钥、登录态或远程服务。若要启用增强能力，需要你自己配置以下内容：

### 本地聚合所需
- `EXA_API_KEY`
- `TAVILY_API_KEY`

### 启用 Grok 综合能力所需
- `GROK_BRIDGE_BASE_URL`
- `GROK_BRIDGE_API_KEY`
- `GROK_BRIDGE_MODEL`（建议 `auto`）

### 启用受限站点补抓所需
- 本地可用的 Playwright 浏览器环境
- 你自己的 IEEE / ACM / Springer / ScienceDirect 登录态（按需）

### 建议准备
- 可用的 `python3`
- 由 `templates/research.env.example` 复制出的私有本地配置文件，例如 `templates/research.local.env`

## 本项目中的 Grok API 获取方式

本项目**不是直接调用原生官方 Grok API**，而是通过 **Grok2API** 获取 Grok 能力。

推荐参考实现：
- `https://github.com/chenyme/grok2api`

也就是说，本项目里的 Grok 访问方式是：
- 你自己部署或提供一个 Grok2API 服务
- `research-assist` 通过 OpenAI 风格兼容接口访问它
- 主要使用的接口是：
  - `GET /v1/models`
  - `POST /v1/chat/completions`

因此：
- `GROK_BRIDGE_BASE_URL` 应当指向你自己的 Grok2API 地址，通常到 `/v1`
- 如果你没有部署 Grok2API，那么 Grok 相关模式不会工作

## 设计原则

- **证据优先**：尽量让结论绑定 URL
- **来源分级**：正式论文页、DOI、arXiv、会议官网优先
- **模型不替代来源**：Grok 不能直接取代正式证据
- **Playwright 只做 fallback**：公开页面足够时不优先启用浏览器抓取
- **统一核心 skill**：后续如需 `research-think` 等入口，应做薄封装，而不是重复维护逻辑

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

## 快速开始

复制示例 env 文件，并填写你自己的本地配置：

```bash
cp "research-assist/templates/research.env.example" "research-assist/templates/research.local.env"
```

主要变量：
- `EXA_API_KEY`
- `TAVILY_API_KEY`
- `GROK_BRIDGE_BASE_URL`
- `GROK_BRIDGE_API_KEY`
- `GROK_BRIDGE_MODEL=auto`

详见：
- `research-assist/references/api-setup.md`
- `research-assist/references/grok-bridge.md`
- `research-assist/templates/api-config-template.md`

## 使用示例

### 查看 CLI 帮助

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" --help
```

### 聚合模式

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --query "multimodal retrieval augmented generation survey" \
  --max-results 5
```

### 思考模式：idea 发散

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --mode think-idea \
  --query "efficient multimodal rag for long documents" \
  --max-results 5
```

### 思考模式：方法对比

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --mode think-compare \
  --query "AAA interpolation for electromagnetics" \
  --compare-target "vector fitting" \
  --max-results 5
```

### 思考模式：结论核验

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --mode think-verify \
  --query "multimodal RAG reliability" \
  --max-results 5
```

## 输出结构

后端采用 evidence-first schema，常见字段包括：

- `results`
- `lanes.search_lane.evidence`
- `lanes.search_lane.playwright_hints`
- `lanes.grok_lane.claims`
- `synthesis.validated_claims`
- `synthesis.disagreements`
- `synthesis.next_queries`

## 发布时应包含

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

## 一句话总结

> 把“搜索来源、组织证据、比较方法、扩展思路、核验结论、处理受限站点”收敛为一个统一、可复用、可发布的科研 skill。