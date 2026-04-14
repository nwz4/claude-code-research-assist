# 可选 API 配置模板

本文件只是建议，不会自动生效。

## 你需要自行配置的内容

### Exa
- `EXA_API_KEY`
- `EXA_API_BASE`（可选）

### Tavily
- `TAVILY_API_KEY`
- `TAVILY_API_BASE`（可选）

### Grok bridge（推荐通过 Grok2API 获取）
- `GROK_BRIDGE_BASE_URL`
- `GROK_BRIDGE_API_KEY`
- `GROK_BRIDGE_MODEL`

### 受限站点 fallback
- 本地 Playwright 环境
- 你自己的学术站点登录态（按需）

## 推荐职责分工

- Exa：论文 / 项目页 / 作者页发现
- Tavily：背景资料与开放网页补充
- Grok bridge：综合分析、对比、扩展和下一轮查询建议
- Playwright：IEEE / ACM / Springer 等受限站点补抓

## 注意

- Grok 能力在本项目中默认来自 **Grok2API** 兼容桥接层，而不是直接原生对接官方 Grok API
- 这些配置项只是供你在本地脚本或外部工具里统一读取
- Claude Code skill 本身不会自动代替你保存或注入这些密钥
