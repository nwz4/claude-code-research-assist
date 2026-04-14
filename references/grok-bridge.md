# Grok bridge 接入说明

本项目中的 Grok 能力推荐通过 **Grok2API** 获取，而不是直接对接原生官方 Grok API。

推荐参考实现：
- `https://github.com/chenyme/grok2api`

## 核心说明

`research-assist` 里的 Grok 接入并不是“原生 Grok SDK / 原生 Grok REST API”模式，而是把 Grok2API 当成一个 **OpenAI 风格兼容代理层**。

因此，本项目中的 Grok 配置本质上是：
- 你自行部署或提供一个 Grok2API 服务
- 本项目通过 OpenAI 风格接口访问它
- 脚本侧主要使用：
  - `GET /v1/models`
  - `POST /v1/chat/completions`

## 为什么这样接

- Grok2API 可以提供 OpenAI 风格接口，便于统一接入
- 更适合做 research-assist 的“综合分析通道”后端
- 适合做 query expansion、claims、disagreements、next_queries
- 不适合作为唯一论文发现来源

## 你需要自行配置的内容

通过环境变量提供：
- `GROK_BRIDGE_BASE_URL`
- `GROK_BRIDGE_API_KEY`
- `GROK_BRIDGE_MODEL`

示例：
- `GROK_BRIDGE_BASE_URL=http://127.0.0.1:8000/v1`
- `GROK_BRIDGE_API_KEY=your_key`
- `GROK_BRIDGE_MODEL=auto`

## 推荐职责

Grok bridge 适合用于：
- 生成下一轮检索词
- 总结研究主线与候选假设
- 做方法对比与分歧归纳
- 给出 claim-verify 的反证方向

不建议用于：
- 单独发现全部论文
- 替代正式来源页面
- 在没有来源支撑时直接给学术结论

## 降级原则

如果 Grok bridge 不可用：
- 继续使用 Exa / Tavily / WebSearch / WebFetch / Playwright
- 整个 `research-assist` 流程不应阻塞
- 只是 Grok 相关能力会缺失
