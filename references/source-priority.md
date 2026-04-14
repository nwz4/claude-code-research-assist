# 论文与研究来源优先级

默认从高到低：

1. 出版方正式页面 / DOI 落地页
2. arXiv / OpenReview / 会议官网 / ACL Anthology / CVF / PMLR
3. 作者主页 / 项目主页 / 官方代码仓库
4. Semantic Scholar / DBLP / Crossref / Google Scholar 结果页
5. 高质量综述文章 / 技术博客 / 课程资料
6. 普通网页转载、聚合站、摘要搬运页

## 适用规则

- 若正式页面信息少、arXiv 信息更全，可同时保留二者，但以 DOI/正式 venue 确认出版信息。
- 同一论文有多个入口时，优先保留：
  - 正式出版信息
  - 最完整摘要页
  - 官方代码或项目页
- 对“找近期论文”，年份和 venue 权重提高。
- 对“找基础入门资料”，综述、教程和 benchmark 页权重提高。
- 对 compare / verify 任务，来源可靠性权重应高于覆盖面。

## 登录态来源

对于 IEEE / ACM / Springer / ScienceDirect：
- 未登录时把它们当“可能需要补抓的高级来源”
- 已登录可访问时，优先抽取摘要、元信息、DOI、下载入口
- 若无法稳定读取全文，不要假装已经读过全文

## Grok 通道的使用边界

- Grok 适合补充候选 claim、分歧点、反证方向与下一轮查询
- Grok 不是来源优先级体系中的正式来源
- Grok 给出的判断应回落到 URL evidence 上核验
