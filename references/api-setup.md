# Research API 本地配置与测试

这个项目现在按统一核心 skill **research-assist** 来理解；目录名、对外简介、说明和发布名建议统一使用 `research-assist`。

这个 skill 的联网增强能力依赖你**自行配置**本地凭据、代理地址和按需的浏览器登录态。

## 1. 你需要自行准备的内容

### 必需：本地 API 凭据
- `EXA_API_KEY`
- `TAVILY_API_KEY`

### 若要启用 Grok 综合能力
- `GROK_BRIDGE_BASE_URL`
- `GROK_BRIDGE_API_KEY`
- `GROK_BRIDGE_MODEL`

### 若要启用受限站点 fallback
- 本地可用的 Playwright 环境
- 你自己的 IEEE / ACM / Springer / ScienceDirect 登录态（按需）

### 建议
- 本地可用的 `python3`
- 私有 env 文件（例如 `research-assist/templates/research.local.env`）

## 2. 推荐方式：本地 env 文件

已提供模板：
- `research-assist/templates/research.env.example`

建议你复制一份，例如：
- `research-assist/templates/research.local.env`

然后自行填入：
- `EXA_API_KEY`
- `TAVILY_API_KEY`
- `GROK_BRIDGE_BASE_URL`
- `GROK_BRIDGE_API_KEY`
- `GROK_BRIDGE_MODEL`（建议 `auto`）

## 3. 推荐环境变量

### Exa
- `EXA_API_KEY`
- `EXA_API_BASE`（可选，默认 `https://api.exa.ai`）

### Tavily
- `TAVILY_API_KEY`
- `TAVILY_API_BASE`（可选，默认 `https://api.tavily.com`）

### Grok bridge
- `GROK_BRIDGE_BASE_URL`
- `GROK_BRIDGE_API_KEY`
- `GROK_BRIDGE_MODEL`

建议：
- `GROK_BRIDGE_BASE_URL` 填到 `/v1` 这一层，例如：`http://127.0.0.1:8000/v1`
- `GROK_BRIDGE_MODEL=auto`，脚本会自动选择可用文本模型

## 4. Grok API 来源说明（重要）

本项目里的 Grok 能力**不是直接来自原生官方 Grok API 接入**。

推荐方式是使用 **Grok2API** 作为兼容桥接层，参考实现：
- `https://github.com/chenyme/grok2api`

也就是说：
- 你需要自行部署或提供一个 Grok2API 服务
- `research-assist` 通过 OpenAI 风格兼容接口访问它
- 当前脚本主要使用：
  - `GET /v1/models`
  - `POST /v1/chat/completions`

如果你没有准备 Grok2API 服务，那么：
- Exa / Tavily / WebSearch / WebFetch / Playwright 仍然可以继续使用
- 但 Grok 相关模式不会生效

## 5. Grok bridge 运行建议

如果你采用 `chenyme/grok2api`：
- 本地启动后，确认这些接口可用：
  - `GET /v1/models`
  - `POST /v1/chat/completions`
- 再把 `GROK_BRIDGE_BASE_URL` 指向该服务

## 6. 聚合脚本

脚本：
- `research-assist/scripts/research_aggregate.py`

它是 unified research-assist backend，可支持两类模式：

### A) `aggregate`（默认）
- 调 Exa / Tavily 检索
- 调 Grok 生成扩展检索词
- 输出去重后的候选结果

### B) `think-*`（双通道综合）
- `think-idea`
- `think-compare`
- `think-verify`

在 `think-*` 中会做：
- 搜索通道（Exa + Tavily）形成 evidence 列表
- Grok 通道产出 claims / disagreements / next_queries
- 对 claims 做“与搜索通道 URL 证据”的匹配校验（supported/partial/unverified）
- 对疑似受限站点输出 Playwright hints

## 7. 测试命令

### 检查 Python 是否可运行
```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" --help
```

### 默认聚合（Exa + Tavily + Grok）
```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --query "multimodal retrieval augmented generation survey" \
  --max-results 5
```

### 思考模式：科研 idea
```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --mode think-idea \
  --query "efficient multimodal rag for long documents" \
  --max-results 5
```

### 思考模式：对比
```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --mode think-compare \
  --query "AAA interpolation for electromagnetics" \
  --compare-target "vector fitting" \
  --max-results 5
```

### 仅 Grok（用于看 query 扩展或 claim 草案）
```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --query "graph rag for scientific literature" \
  --sources grok
```

## 8. 返回结果说明

核心字段：
- `configured`: 哪些后端已配置
- `source_reports`: 每个源是否成功、失败原因是什么
- `results`: Exa/Tavily 去重后的候选结果
- `result_count`: 去重后数量

`think-*` 额外字段：
- `lanes.search_lane.evidence`: 搜索通道证据（必须带 URL）
- `lanes.search_lane.playwright_hints`: 建议补抓的受限站点页面
- `lanes.grok_lane.claims`: Grok 通道观点+证据
- `synthesis.validated_claims`: 支持度校验结果
- `synthesis.disagreements`: 分歧点
- `synthesis.next_queries`: 下一轮检索建议

## 9. 项目级建议

如果你准备发布这个 skill：
- 对外名称统一用 `research-assist`
- 如果后续加 `research-think` 入口，它应只是薄封装，不应复制 backend 与规则

## 10. 重要限制

- 当前脚本仍是“检索聚合 + 综合分析”层，不会自动驱动浏览器登录流程
- IEEE / ACM / Springer 等站点若公开信息不足，仍建议通过 Playwright 单独补抓
- `think-*` 里的结论必须结合 `evidence` URL 复查，不应直接当最终事实
